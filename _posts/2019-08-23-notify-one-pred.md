---
layout: post
title: std::condition_variable::notify_one 使用细节
categories: [c++]
tags: [c++, condition_variable]
---
  

---

官方的这个例子，真给我看傻了

```c++
#include <iostream>
#include <string>
#include <thread>
#include <mutex>
#include <condition_variable>
 
std::mutex m;
std::condition_variable cv;
std::string data;
bool ready = false;
bool processed = false;
 
void worker_thread()
{
    // Wait until main() sends data
    std::unique_lock<std::mutex> lk(m);
    cv.wait(lk, []{return ready;});
 
    // after the wait, we own the lock.
    std::cout << "Worker thread is processing data\n";
    data += " after processing";
 
    // Send data back to main()
    processed = true;
    std::cout << "Worker thread signals data processing completed\n";
 
    // Manual unlocking is done before notifying, to avoid waking up
    // the waiting thread only to block again (see notify_one for details)
    lk.unlock();
    cv.notify_one();
}
 
int main()
{
    std::thread worker(worker_thread);
 
    data = "Example data";
    // send data to the worker thread
    {
        std::lock_guard<std::mutex> lk(m);
        ready = true;
        std::cout << "main() signals data ready for processing\n";
    }
    cv.notify_one();
 
    // wait for the worker
    {
        std::unique_lock<std::mutex> lk(m);
        cv.wait(lk, []{return processed;});
    }
    std::cout << "Back in main(), data = " << data << '\n';
 
    worker.join();
}
```

为什么在notify_one之前需要unlock?

为什么notify_one不用在锁里？不怕丢吗（当然这个例子里不会丢，一共就俩线程）

 notify_one有这么个注释

>The effects of `notify_one()`/`notify_all()` and each of the three atomic parts of  `wait()`/`wait_for()`/`wait_until()` (unlock+wait, wakeup, and lock) take place in a single total order that can be viewed as [modification order](https://en.cppreference.com/w/cpp/atomic/memory_order#Modification_order) of an atomic variable: the order is specific to this individual condition_variable. This makes it impossible for `notify_one()` to, for example, be delayed and unblock a thread that started waiting just after the call to `notify_one()` was made. 
>
>**The notifying thread does not need to hold the lock on the same  mutex as the one held by the waiting thread(s)**; in fact doing so is a  pessimization, since the notified thread would immediately block again,  **waiting for the notifying thread to release the lock**. However, some  implementations (in particular many implementations of pthreads)  recognize this situation and avoid this "hurry up and wait" scenario by  transferring the waiting thread from the condition variable's queue  directly to the queue of the mutex within the notify call, without  waking it up.
>
>Notifying while under the lock may nevertheless be necessary when precise scheduling of events is required, e.g. if the waiting thread  would exit the program if the condition is satisfied, causing  destruction of the notifying thread's condition_variable. A spurious  wakeup after mutex unlock but before notify would result in notify  called on a destroyed object.



这个注释能解释第一个notify_one不加锁



另外，wait必须要有条件，无条件wait容易丢失notify 已经写到官方建议里了  https://github.com/isocpp/CppCoreGuidelines/blob/master/CppCoreGuidelines.md#cp42-dont-wait-without-a-condition

主要是notify_one多线程消费场景，不知道被谁消费了，所以指定某个满足条件的去wait wait一个触发条件。这样配对用

在这个[讨论](https://github.com/isocpp/CppCoreGuidelines/issues/554)里, 有个结论，也有人[提问](https://github.com/isocpp/CppCoreGuidelines/issues/1272)了 

> unlocking the mutex before notifying is an optimisation, and not  essential. I intentionally didn't do that, to keep the example simple.  There could be a second guideline about that point, but it's not related to the "always use a predicate" rule. I would object strongly to  complicating the example by doing that.





anyway 提前unlock算是个人选择(有优化)，不提前unlock也没啥大的影响





---

说句题外话

最近在看一个时间队列实现，这个cond var用的让我有点迷惑

```c++
class TimerQueue {
public:
    TimerQueue() {
        m_th = std::thread([this] { run(); });
    }
 
    ~TimerQueue() {
        cancelAll();
        add(0, [this](bool) { m_finish = true; });
        m_th.join();
    }
 
    uint64_t add(int64_t milliseconds, std::function<void(bool)> handler) {
        WorkItem item;
        item.end = Clock::now() + std::chrono::milliseconds(milliseconds);
        item.handler = std::move(handler);
 
        std::unique_lock<std::mutex> lk(m_mtx);
        uint64_t id = ++m_idcounter;
        item.id = id;
        m_items.push(std::move(item));
        lk.unlock();
 
        // Something changed, so wake up timer thread
        m_checkWork.notify();
        return id;
    }
  ....
```

注意是先lk.unlock再notify,这个unlock有必要么？

后来发现是用cond var封装了一个 信号量，自己用内部的mtx。和这个没啥关系。

这个代码给我整晕了。rocksdb的timerqueue抄了这个，但是体验没那么迷糊


---

### ref

- https://www.crazygaze.com/blog/2016/03/24/portable-c-timer-queue/
- https://en.cppreference.com/w/cpp/thread/condition_variable

---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。