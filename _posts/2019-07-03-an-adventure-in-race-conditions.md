---
layout: post
categories: c++
title: ACCU an adventure in race conditions
tags: [c++]
---

  

---

#### why

演讲人是 Felix Petriconi，这个ppt讲了几个典型的竞争场景，ppt见参考链接1

而且作者列了详尽的资料。够看一个月

---

作者的工作属性经常需要做图像处理，压缩等，就需要一个并发场景

一个典型的图像压缩场景

将图分成若干片 ->分别压缩 ->合并

如果用future就很简单

```c++
struct CompresssContext{} ctx;
bool compress(CompresssContext&){return true;}
void merge(CompresssContext&){}
int main(){
    vector<boost::future<void>> tasks{16};
    for(auto & f: tasks)
        f = async([]{compress(ctx);});
    auto done = boost::when_all(task.begin(),task.end())
        .then([]{merge(ctx);});
}
```

这套future使用组件已经进TS了，可能后续能用上 <sup>2</sup>



面对这种场景，简单粗暴的方法就是起线程

```c++
int main() {
  const int ThreadNumber = 2;
  vector <thread> threads{ThreadNumber};
  for (auto& item : threads)
    item = thread{ []{ compress(ctx); } };

  for (auto& item : threads)
    item.join();
  merge(ctx);
}
```

如果考虑到切换的开销，妥协方案就是线程池模型了

这也是作者的方向，然后作者遇到了三个竞争问题



1 

```c++
int main()
{
    const int TaskNumber{16};
    atomic_int to_do{TaskNumber};
    mutex block;
    condition_variable cv;
    for (int i = 0; i < TaskNumber; ++i)
        stlab::default_executor( // thread pool from stlab/concurrency
            [&]() {
                compress(ctx);
                --to_do;
                cv.notify_one();
            });

    unique_lock lock{block};
    while (to_do != 0)
        cv.wait(lock);

    merge(ctx);
}
```

第一稿是这个样子，注意executor是个线程池，直接把lambda放到后台执行。

这里的todo是条件变量用来wait的值，注意是原子量，没有加锁，这是错误的，本质上mutex就是个channel，保证这个访问的严格串行通知，如果不加锁，todo的load过程可能就会被上层切走，执行wait，然后又被切回来，导致wait值和notify_one不一致，丢掉唤醒。保证这种场景的要求就是控制在一个channel内，这样系统上层保证不yield

2

```c++
...
            [&]() {
                unique_lock l(lock);
                {
                    compress(ctx);
                    --to_do;
                }
                cv.notify_one();
            });
```



然后作者第二部改动是加了个unique_lock 锁住--todo，而没锁notify_one，作者可能考虑锁住判断条件就足够了。。。实际上原因和上面是一样的。notify_one不在lock下，在mutex外的执行区间可能就会被遗漏。第二版改进就是把notify_one挪到括号内



3

全局变量问题。

代码中的todo等等都是全局的，这会有一个问题，有的线程退出但是全局变量被污染了。解决办法就是引入上下文

```c++
struct CompressContext{} ctx;
bool compress(CompressContext&)
{ return true; }
void merge(CompressContext&) {}
struct ProcessContext
{
  mutex block;
  condition_variable cv;
  int to_do = 0;
  atomic_bool abort{false};
};
```



 ```c++
const int TaskNumber{16};
auto pctx = make_shared <ProcessContext >();
pctx->to_do = TaskNumber;
for (int i = 0; i < TaskNumber; ++i)
stlab::default_executor(
  [_weakContext = weak_ptr <ProcessContext >(pctx)] {
    auto p = _weakContext.lock();
    if (!p || p->abort)
      return;
    auto do_abort = !compress(ctx);
    {
      unique_lock guard{p->block};
      --p->to_do;
      p->abort = do_abort || p->abort;
      p->cv.notify_one();
    }
  });

unique_lock lock{pctx->block};
while (pctx->to_do != 0 && !pctx->abort)
  pctx->cv.wait(lock);
merge(ctx);
 ```

 作者的总结是这些底层原语相当难用容易用错，不如用future promise来的块些

另外，作者的引用文章很有分量，看不完



- Concurrency library https://github.com/stlab/libraries
- Documentation http://stlab.cc/libraries
-  Communicating Sequential Processes by C. A. R. Hoare
  http://usingcsp.com/cspbook.pdf
-  The Theory and Practice of Concurrency by A.W. Roscoe http://www.cs.ox.ac.uk/people/bill.roscoe/publications/68b.pdf
-  Towards a Good Future, C++ Standard Proposal by Felix Petriconi, David
  Sankel and Sean Parent http://open-std.org/JTC1/SC22/WG21/docs/papers/2017/p0676r0.pdf
- A Unified Futures Proposal for C++ by Bryce Adelstein Lelbach, et al
  http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p1054r0.html



Software Principles and Algorithms

- Elements of Programming by Alexander Stepanov, Paul McJones, Addison
  Wesley
-  From Mathematics to Generic Programming by Alexander Stepanov, Daniel
  Rose, Addison Wesley



Concurrency and Parallelism

-  HPX http://stellar-group.org/libraries/hpx/
-  C++CSP https://www.cs.kent.ac.uk/projects/ofa/c++csp
-  CAF C++ Actor Framework http://actor-framework.org/
-  C++ Concurrency In Action by Anthony Williams, Manning, 2nd Edition



- Goals for better code by Sean Parent:http://sean-parent.stlab.cc/papers-and-presentations

-  Goals for better code by Sean Parent: Concurrency:
  https://youtu.be/au0xX4h8SCI?t=16354
-  Future Ruminations by Sean Parent http://sean-parent.stlab.cc/2017/07/10/future-ruminations.html
-  CppCast with Sean Parent http://cppcast.com/2015/06/sean-parent/
-  Thinking Outside the Synchronization Quadrant by Kevlin Henney:
  https://vimeo.com/205806162
-  Inside Windows 8 Thread Pool https://channel9.msdn.com/Shows/Going+Deep/Inside-Windows-8-Pedro-Teixeira-Thread-pool

---

### ref

1. https://github.com/ACCUConf/PDFs_2019/blob/master/felix_petriconi_-_an_adventure_in_race_conditions.pdf

2. https://en.cppreference.com/w/cpp/experimental/when_all

3. 这里也介绍了pthread cv原语用法中的著名错误，但是例子不同，判断条件不是原子的。https://zhuanlan.zhihu.com/p/55123862

4. 这是个好问题，为什么pthread_cond_signal需要在mutex下执行，即使判断条件是原子的也是不行的 https://www.zhihu.com/question/53631897

   通过这个问题也能理解，为什么必须要锁，可以理解成mutex是channel，wait和signal通过channel来通信。如果不走这个channel，可能消息就会丢，metux保护的并不是判断条件，保护的是wait和signal之间的条件同步，即signal改动透过channel的维持让wait知道。否则wait很容易丢掉这个通知

5. https://stackoverflow.com/questions/41867228/why-do-i-need-to-acquire-a-lock-to-modify-a-shared-atomic-variable-before-noti?r=SearchResults

   这个答案进一步解释了这个问题

   代码

   ```c++
   static std::atomic_bool s_run {true};
   static std::atomic_bool s_hasEvent {false};
   static std::mutex s_mtx;
   static std::condition_variabel s_cv;
   // Thread A - the consumer thread
   function threadA()
   {
       while (s_run)
       {
           {
               std::unique_lock<std::mutex> lock(s_mtx);
               s_cv.wait(lock, [this]{
                   return m_hasEvents.load(std::memory_order_relaxed);
               });
           }
   
           // process event
           event = lockfree_queue.pop();
           ..... code to process the event ....
       }
   }
   // Thread B - publisher thread
   function PushEvent(event)
   {
       lockfree_queque.push(event)
       s_hasEvent.store(true, std::memory_order_release);
       s_cv.notify_one();
   }
   ```

   可能丢掉notify_one的场景

   1. Thread A locks the mutex.

   2. Thread A calls the lambda's closure which does `m_hasEvents.load(std::memory_order_relaxed);` and returns the value `false`.
   3. Thread A is interrupted by the scheduler and Thread B starts to run.
   4. Thread B pushes an event into the queue and stores to `s_hasEvent`
   5. Thread B runs `s_cv.notify_one()`.
   6. Thread B is interrupted by the scheduler and Thread A runs again.
   7. Thread A evaluates the `false` result returned by the closure, deciding there are no pending events.
   8. Thread A blocks on the condition variable, waiting for an event.

   其中第四步如果有锁，这个改动就不会丢，你改动是不是原子的无所谓，需要保证观测者是一个原子的状态，即通过这个channel来控制。

6. https://stackoverflow.com/questions/32978066/why-is-there-no-wait-function-for-condition-variable-which-does-not-relock-the-m/32978267#32978267

   这是上面的链接中提到的一个场景，yakk的代码不错


### contact

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。