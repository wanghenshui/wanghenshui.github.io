---
layout: post
title: C++11 High-Level Threading
categories: c++
tags: [c++, boost, cppnow, thread]
---

  

#### cppnow2012 John Wiegley C++11 High-Level Threading

 这个ppt讲的是std::thread, 算是一个教学指南

 构造函数声明是这个样子的

```c++
 struct thread{
 template<class F, class ...Args> explicit
         thread(F&&f, Args&&... args);
 };
```

一例

```c++
#include <thread>
std::map<std::string, std::string> french 
{ {"hello","bonjour"},{"world","tout le monde"} };

int main(){
    std::string greet = french["hello"];
    std::thread t([&]{std::cout<<greet<<", ";});
    std::string audience = freanch["world"];
    t.join();
    std::cout<< audience<<std::endl;
}
```



这是普通用法，如果想传参数引用，而不是捕获怎么办 ->转成ref，std::ref

 ```c++
std::thread t([](const std::string& s){std::cout<<s<<", ";}, std::ref(greet));
 ```



` std::thread overreview`

不可复制 ->移动语义

系统相关的细节不涉及（调度，优先级）

`joinability`

几个条件

- 肯定有线程id，不是默认的
- 可以join或detach的，或者调用过的，肯定是joinable的, 如果joinable没调用join/detach，析构就会调用std::terminate
- 当析构或移动了之后肯定不是joinable的，这时候去访问(join)肯定会挂的。

所以这就有几个典型异常场景

- system_error
- 资源耗尽导致launch fail
- detach /join fail，比如不是joinable，或者死锁了，join挂掉
- 线程函数抛异常，这个就比较傻逼了，肯定调不到join或者detach

就上面的例子，第八行如果挂掉，线程就忘记join了。这样thread析构会直接调用std::terminate，所以需要catch住，在catch里join一下，然后把join转发出去

```c++
try {
    std::string audience = french["world"];
} catch(...) {
    t.join; 
    throw;
}
```

可真难看啊。



`this_thread`

接口是这样的

```c++
namespace this_thread{
    thread::id get_id() noexcept;
    void yield() noexcept;
    
    template <class Clock class Duration>
    void sleep_until(
      const chrono::time_point<Clock, Duration>& abs_time);
    
    template <class Rep, class Period>
    void sleep_for(
      const chrono::duration<Rep,Period>& rel_time);
}
```

太长了不好记

后面两个可以记成

```c++
void sleep_until(time_point);
void sleep_for(duration);
```



`std::async std::future`

上面例子的写法很难看，作者使用async 和future重写了一下

```c++
#include <future>
...
std::fucure<void> f = std:;async([&]{std::cout<< greet<<", ";});
std::string audience = french["world"];
f.get();
...
```

Or...

```c++
...
auto greet = std::async([]{return french["hellp"];});
std::string audience = french["world"];
std::cout<<greet.get()<<", "<<audience<<std::endl;
```

这样好看多了

 async的launch逻辑

async|deferred

一个例子

```c++
template <class Iter>
void parallel_merge_sort(Iter start, Itera finish) {
    std::size_t d = std::distance(start, finish);
    if(d<=1) return;
    Iter mid = start; std::advance(mid, d/2);
    auto f = std::async(
        d<768?std::launch::deferred
        : std::launch:deferred | std::launch::async,
        [=]{parallel_merge_sort(start,mid);});
    parallel_merge_sort(mid, finish);
    f.get();
    std::inplace_merge(start,mid,finish);
}
```

`std::future`

api是这个样子

```c++
enum class future_status{ready, timeout, deferred};
template <class R> struct future {
    future() noexcept;
    bool valid() const noexcept;// ready
    R get();
    void wait() const;// wait for ready
    future_status wait_for(duration) const;
    future_status wait_untile(time_point) const;
    shared_future<R> share();
};
```

整体是move-only的，有个share接口用于共享

`std::shared_future`

接口和future差不多，提供copy干脏活的

```c++
enum class future_status{ready, timeout, deferred};
template <class R> struct shared_future {
    future() noexcept;
    bool valid() const noexcept;// ready
    R get();
    void wait() const;// wait for ready
    future_status wait_for(duration) const;
    future_status wait_untile(time_point) const;
    shared_future(future<R>&& f) noexcept;
};
```

`std::promise`

如果用promise来重构，能彻底异步解耦，代码更好看一些

```c++
int main() {
    std::promise<std::string> audience_send;
    auto greet = std::async(
        [](std::future<std::string> audience_rcv)
        {
            std::cout<<french["hello"]  <<", ";
            std::cout<<audience_rcv.get()<<std:;endl;
        },
        audience_send.get_future()//pull
    );
    
    audience_send_value(french["world"]);//push
    greet.wait();
}
```

 std::promise api 

```c++
template <class R>
struct promise{
    promise();
    template <class Allocator>
        promise(allocator_arg_t, const Allocator& a);
    future<R> get_future(); //pull the future
    void set_value(R); //push, make the future ready
    void set_exception(exception_ptr p);
    void set_value_at_thread_exit(R); //push result but defer readiness
    void set_exception_at_thread_exit(exception_ptr p);
};
```



`推迟异步动作,deferring launch, -> std::packaged_task`

更进一步，把 std::async   换成std::packaged_task, 必须显式调用operator()才会执行，不像async立即异步执行

```c++
int main(){
    std::packaged_task<std::sring()> do_lookup(
        []{return french["hello"];});
    auto greet = do_lookup.get_future();
    do_lookup();
    std::string audience = french["world"];
    std::cout<<greet.get()<<", "<<audience<<std::endl;
}
```

std::packaged_task长这个样子

```c++
template<class> class packaged_task;// undefined
template<class R, class... ArgTypes>
struct packaged_task<R(ArgTypes...)> {
  packaged_task() noexcept;
  template <class F> explicit packaged_task(F&& f);
  template <class F, class Alloc>
    explicit packaged_task(allocator_arg_t, const Alloc& a, F&& f);
  future<R> get_future();//pull
  bool valid() const noexcept;
  void operator()(ArgTypes...);//make the future ready(push)
  void make_ready_at_thread_exit(ArgTypes...);
  void reset();
};
```

`基于锁的数据共享`

基本概念，线程安全，强线程安全

`std::mutex`

实现一个强线程安全的堆栈

```c++
template <class T>
struct shared_stack{
    bool empty() const {
        std::lock_guard<std::mutex>  l(m);
        bool r = v.empty();
        return r;
    }
    T top() const{
        std::lock_guard<std::mutex>  l(m);
        T r = v.back();
        return r;
    }
    void pop();
    void push(T x);
private:
    mutable std::mutex m;
    std::vector<T> v;
};
```

 这里讨论了锁，lock_guard和unique_lock

实现一个线程安全的队列

```c++
template<unsigned size, class T>
struct bounded_msg_queue{
    bounded_msg_queue()
        :begin(0),end(0),buffered(0){}
    void send(T x){
        {
            std::unique_lock<std::mutex> lk(broker);
            while(buffered == size)
                not_full.wait(lk);
            buf[end] = x;
            end = (end +1)%size;
            ++buffered;
        }
        not_empty.notify_all();
    }
    T receive(){
        T r;
        {
            std::unique_lock<std::mutex> lk(broker);
            while (buffered == 0)
                not_empty.wait(lk);
            
            r = buf[begin];
            begin = (begin+1) % size;
            -- buffered;
        }
        not_full.notify_all();
        return r;
    }    
private:
    std::mutex broker;
    unsigned int begin, end, buffered;
    T buf[size];
    std::condition_variable not_full, not_empty;
};
```



`std::condition_variable` 这个api和pthread原语差不多，不说了

`boost::shared_mutex`

这个可以用于多读少写的场景，有点读写锁封装的感觉。具体没有研究

### ref

- <https://github.com/boostcon/cppnow_presentations_2012/blob/master/mon/concurrency.pdf>
- abbreviate，简写缩写，abbr


看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>