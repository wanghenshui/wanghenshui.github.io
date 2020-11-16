---
layout: post
title: 线程池/任务队列调研
categories: [c++]
tags: [c++, rocksdb, folly]
---
  

---

解决什么问题：`资源隔离，不同的任务通过不同的线程(池)/任务队列 来做`

需要一个能动态调整(弹性线程数调整)，区分优先级，且能做到绑核(一个核一个线程池?) 租户隔离的线程池/任务队列

优先级更进一步：动态调整线程的优先级？如何判定？

更更进一步：租户级别优先级？



解决方案：

1. 线程池 (内部有任务队列) 比如rocksdb的线程池 每个线程有自己的优先级（IO有IO优先级，CPU有CPU优先级），不同的任务，IO的和cpu的放到不同的池子里，注意rocksdb的线程池是没有主动schedule的，设置线程的优先级，然后通过系统调用来调度(仅支持linux)

2. 异步事件处理 + future/promise+线程池 ，线程池纯粹一点，就是资源池。资源池分成不同的种类，future/promise调用能穿起不同的资源，比如folly ，没有线程级别的优先级，但可以指定不同的线程池，比如IO线程池，CPU线程池等等，一个future可以串多个线程池，把任务分解掉

3. 异步事件框架 +线程池 线程池没有别的作用，就是资源池，事件框架可以是reactor/proactor，有调度器 schedule，负责选用资源 比如boost::asio

4. 异步事件处理(一个主事件线程+一个工作线程+一个无锁队列) + future/promise + 任务队列  比如seastar (侵入比较强，系统级)



以rocksdb的线程池做基线

|                           | 动态调整线程池        | 任务可以区分优先级                                           | 内部有队列？                                                 | 统计指标                         | 使用负担                                     |
| ------------------------- | --------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | -------------------------------- | -------------------------------------------- |
| rocksdb的线程池           | ✅<br>可以调整池子大小 | ✅ rocksdb线程池的优先级是系统级别的优先级，有系统调用的。而不是自定义schedule循环，自己维护优先级的 | ✅ std::duque\<BGItem>                                        | worker线程的各种状态统计idle等待 | 组件级，可以理解成高级点的任务队列           |
| boost::asio::thread_pool  | X                     | X                                                            | 没有队列，一般使用不需要队列，如果有任务队列需要自己维护<br/>结合post使用静态的池子 | X                                | 组件级，但是得配合asio使用，摘出来没什么意义 |
| Folly::threadpoolExecutor | ✅                     | X                                                            | 没有队列，add直接选线程调用可以定制各种类型的executor 结合future使用 future then串起队列 | worker线程的各种状态统计idle等待 | 单独用相当于epoll + 多线程worker             |
| seastar                   | X                     | X                                                            | 有队列，每个核一个reator一个队列，核间通信靠转发，而不是同步 | X                                | 系统级，想用必须得用整个框架来组织应用       |






调整优先级

```c++
//cpu 优先级

    if (cpu_priority < current_cpu_priority) {
      TEST_SYNC_POINT_CALLBACK("ThreadPoolImpl::BGThread::BeforeSetCpuPriority",
                               &current_cpu_priority);
      // 0 means current thread.
      port::SetCpuPriority(0, cpu_priority);
      current_cpu_priority = cpu_priority;
      TEST_SYNC_POINT_CALLBACK("ThreadPoolImpl::BGThread::AfterSetCpuPriority",
                               &current_cpu_priority);
    }
//IO优先级
#ifdef OS_LINUX
    if (decrease_io_priority) {
#define IOPRIO_CLASS_SHIFT (13)
#define IOPRIO_PRIO_VALUE(class, data) (((class) << IOPRIO_CLASS_SHIFT) | data)
      // Put schedule into IOPRIO_CLASS_IDLE class (lowest)
      // These system calls only have an effect when used in conjunction
      // with an I/O scheduler that supports I/O priorities. As at
      // kernel 2.6.17 the only such scheduler is the Completely
      // Fair Queuing (CFQ) I/O scheduler.
      // To change scheduler:
      //  echo cfq > /sys/block/<device_name>/queue/schedule
      // Tunables to consider:
      //  /sys/block/<device_name>/queue/slice_idle
      //  /sys/block/<device_name>/queue/slice_sync
      syscall(SYS_ioprio_set, 1,  // IOPRIO_WHO_PROCESS
              0,                  // current thread
              IOPRIO_PRIO_VALUE(3, 0));
      low_io_priority = true;
    }
#else
    (void)decrease_io_priority;  // avoid 'unused variable' error
#endif
```








其实实现上都是queue(cond var + mutex) + threads (+ event (reactor/proactor))

cond var可以隐藏在队列上，也可以隐藏在future里，当然，更高级点，不用cond var用原子变量



简单的线程池+队列实现

```c++
#include <condition_variable>  
#include <functional>
#include <list>
#include <mutex>  
#include <string>
#include <thread> 
#include <vector>

class ThreadPool {
 private:
  const int num_workers_;
  std::list<std::function<void()> > tasks_;
  std::mutex mutex_;
  std::condition_variable condition_;
  std::condition_variable capacity_condition_;
  bool waiting_to_finish_ = false;
  bool waiting_for_capacity_ = false;
  bool started_ = false;
  int queue_capacity_ = 2e9;
  std::vector<std::thread> all_workers_;

  void RunWorker(void* data) {
    ThreadPool* const thread_pool = reinterpret_cast<ThreadPool*>(data);
    std::function<void()> work = thread_pool->GetNextTask();
    while (work != NULL) {
      work();
      work = thread_pool->GetNextTask();
    }

 public:
  ThreadPool(const std::string& prefix, int num_workers)
      : num_workers_(num_workers) {}

  ~ThreadPool() {
    if (started_) {
      std::unique_lock<std::mutex> mutex_lock(mutex_);
      waiting_to_finish_ = true;
      mutex_lock.unlock();
      condition_.notify_all();
      for (int i = 0; i < num_workers_; ++i) {
        all_workers_[i].join();
      }
    }
  }

  void SetQueueCapacity(int capacity) {
    queue_capacity_ = capacity;
  }

  void StartWorkers() {
    started_ = true;
    for (int i = 0; i < num_workers_; ++i) {
      all_workers_.push_back(std::thread(&RunWorker, this));
    }
  }

  std::function<void()> GetNextTask() {
    std::unique_lock<std::mutex> lock(mutex_);
    for (;;) {
      if (!tasks_.empty()) {
        std::function<void()> task = tasks_.front();
        tasks_.pop_front();
        if (tasks_.size() < queue_capacity_ && waiting_for_capacity_) {
          waiting_for_capacity_ = false;
          capacity_condition_.notify_all();
        }
        return task;
      }
      if (waiting_to_finish_) {
        return nullptr;
      } else {
        condition_.wait(lock);
      }
    }
    return nullptr;
  }

  void Schedule(std::function<void()> closure) {
    std::unique_lock<std::mutex> lock(mutex_);
    while (tasks_.size() >= queue_capacity_) {
      waiting_for_capacity_ = true;
      capacity_condition_.wait(lock);
    }
    tasks_.push_back(closure);
    if (started_) {
      lock.unlock();
      condition_.notify_all();
    }
  }
};
```



work steal 概念

taskflow https://github.com/taskflow/work-stealing-queue

taskflow 文档 https://taskflow.github.io/taskflow/chapter2.html#C2_CreateAnExecutor


---

### ref

- https://www.jianshu.com/p/abf15e5e306b
- https://blog.csdn.net/weixin_36145588/article/details/78545778

---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
![微信转账](https://wanghenshui.github.io/assets/wepay.png)
</details>