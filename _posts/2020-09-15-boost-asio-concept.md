---
layout: post
title: (转)boost.asio新框架的设计概念总结
categories: [c++]
tags: [c++, boost, asio]

---
 

1.66版本，boost.asio库重新设计了框架，目前最新版为1.71。读了几天代码后，对框架中相关概念总结。因为是泛型编程的库，所以分析的概念层的设计。

可通过boost官方文档，strand的1.65和1.66两版本文档比较，查证ts和io_context, executor首次出现在1.66。

新框架有几个核心概念，Context，Scheduler，Service，Executor，Strand。

**Context**:

- asio所有功能都必需在一个***Context\*** 里调度执行
- 每个***Context*** 都有一个***Service*** 注册表，管理***Service***
-  每个***Context*** 下的***Service*** 都是唯一的
-  每个***Context*** 都有一个***Scheduler***
-  ***Context*** 必须通过在线程运行poll()或run()进入调度消费***Scheduler*** 执行队列并执行任务
-  io_context是一种对io操作优先的优化***Context***，将io事件复路分集方法做成内嵌任务
-  io_context的win版本对***Schdeluer*** 进行了优化，聚合了iocp。
-  可以在多线程上同时运行poll()或run()，并且线程安全

**Scheduler**:

- 首先是一个***Context*** 的一个服务
- 有一条op_queue执行队列
- 所有***Service*** 的调度都最终依赖***Scheduler*** 调度
- ***Scheduler*** 的dispatch()方法将任务调度到执行队列
  

**Service**:

- 为某种功能提供调度以及功能服务
- 最终依赖所在的 ***Context*** 的 ***Scheduler*** 调度服务
- 每种 ***Service*** 都有一个service_impl类，并为这个类提供服务

**Executor**:

- 相当于ios中的可并行的dispatch_queue
- 相当于一个 ***Context*** 的服务，或者对 ***Context*** 的 ***Execution*** 行为的委托
- 最终依赖所在的***Context***的***Scheduler***调度服务

**Strand**:

- 相当于ios中的串行化的dispatch_queue
- 分两种服务，绑定本io ***Context*** 以及可以指定***Executor*** (即不同类型***Context***)
- 每个***Strand*** 有独立的执行队列
- ***Strand*** 本身作为一个任务，必须在***Scheduler*** 进行调度分派。
- 同一个***Strand*** 同时只能在一条线程上分派执行队列
- 当多线程同时对***Strand*** 分派时，其它线程只能将任务缓冲到等待队列
- 利用本身强制串行化的特性，可代替同步锁，保护变量和代码，减少线程切换

---

### ref

- https://www.cnblogs.com/bbqzsl/p/11919502.html
- asio使用样例，不错 https://github.com/franktea/network
- 介绍实现的 https://zhuanlan.zhihu.com/p/55503053



---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
![微信转账](https://wanghenshui.github.io/assets/wepay.png)
</details>



