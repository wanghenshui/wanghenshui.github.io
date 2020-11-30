---
layout: post
title: threads safety annotations 以及std::priority_queue的一个小用法
categories: [language]
tags: [debug, thread]
---


---

 

我是随便浏览某个时间队列看到的类似的[代码](https://github.com/tensorflow/runtime/blob/a3a14da5f6615382785bf091564d04671a8c5221/include/tfrt/host_context/timer_queue.h)

```c++
  mutable mutex mu_;
  condition_variable cv_;
  std::thread timer_thread_;
  std::atomic<bool> stop_{false};
  std::priority_queue<RCReference<TimerEntry>,
                      std::vector<RCReference<TimerEntry>>,
                      TimerEntry::TimerEntryCompare>
      timers_ TFRT_GUARDED_BY(mu_);
```

这个GUARDED_BY让人好奇，简单查证了一番，发现是clang的工具

简单说就是clang编译器带的一个多线程的帮手，线程安全注解，原理是拓展  \__attribute__ 

比如  \__attribute__(guarded_by(mutex))

这样指明依赖关系，更能方便定位问题

使用的话编译带上 -Wthread-safety-analysis就可以了

没发现gcc有类似的工具。可惜。



另外这些时间队列的实现用的 std::priority_queue 很有意思，都指定了容器参数（因为不是内建的类型，没有实现operator <）

我看rocksdb的timequeue长这样

```c++
  // Inheriting from priority_queue, so we can access the internal container
  class Queue : public std::priority_queue<WorkItem, std::vector<WorkItem>,
                                           std::greater<WorkItem>> {
   public:
    std::vector<WorkItem>& getContainer() { return this->c; }
```

直接把容器参数暴漏出来。挺新颖的。这个数据结构设计保留了c就是为了这样暴露吧。

---

### ref

- https://clang.llvm.org/docs/ThreadSafetyAnalysis.html
  - 可以直接把这个宏抄过去 http://clang.llvm.org/docs/ThreadSafetyAnalysis.html#mutex-h
    - https://github.com/tensorflow/runtime/blob/1f60e4778e91d9932ac04647769a178a9646c0a7/include/tfrt/support/thread_annotations.h 直接抄的
- 原理论文 https://research.google.com/pubs/archive/42958.pdf
- ppt介绍 https://llvm.org/devmtg/2011-11/Hutchins_ThreadSafety.pdf
- 用法 1 https://stackoverflow.com/questions/40468897/clang-thread-safety-with-stdcondition-variable
- 用法 2 https://zhuanlan.zhihu.com/p/47837673
- std::priority_queue 看成员对象那一小节https://en.cppreference.com/w/cpp/container/priority_queue
- 定时器实现总结 https://www.ibm.com/developerworks/cn/linux/l-cn-timers/index.html 文章写得很棒

重点关注最小堆(优先队列) 来维护定时器组，以及时间轮 

- https://www.zhihu.com/question/68451392 管理定时器，不一定需要timerqueue 暴力扫也不是不可以 只要timer不多
- kafka中的事件轮 https://club.perfma.com/article/328984
- https://www.cnblogs.com/zhongwencool/p/timing_wheel.html 他这个博客做的不错。。。



---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>