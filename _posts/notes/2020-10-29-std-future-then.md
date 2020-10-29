---
layout: post
title: std::future 为什么没有then continuation
category: [c++]
tags: [cppcon, cppcon2019, c++]
---
{% include JB/setup %}

---

[toc]

本来concurrency-ts是做了future::then的，本计划要放在<experimental/future> 

asio作者的实现](https://github.com/chriskohlhoff/executors) 最终还是没合入

参考链接1里提到，这个方案作废了

参考链接2 的视频里说了这个then contination方案的缺陷，future-promise的都要求太高

由于future-promise之间是需要通信且共享状态的，需要一些资源

- condvar/mutex同步
- 堆内存使用
- 共享状态(shared_future)搞不好还得用引用计数
- 保存不同种类的future需要type-erasure技术(类似std::any)，这也是一笔浪费

作者的观点是lazy-future ，把资源动作全放在最后，把调用指定好，于是就有了一个泛化的std::then函数

Lazy future advantages

- Async tasks can be composed... 
  - ... without allocation
  - ... without synchronization 
  -  ... without type-erasure
- Composition is a generic algorithm 
- Blocking is a generic algorithm



展示的代码里没有future，就是各种lambda和execute和then 的结合

---

### ref

- https://stackoverflow.com/questions/63360248/where-is-stdfuturethen-and-the-concurrency-ts
- https://www.youtube.com/watch?v=tF-Nz4aRWAM
  - ppt https://github.com/CppCon/CppCon2019/blob/master/Presentations/a_unifying_abstraction_for_async_in_cpp/a_unifying_abstraction_for_async_in_cpp__eric_niebler_david_s_hollman__cppcon_2019.pdf
- ASIO作者的设计 http://chriskohlhoff.github.io/executors/ 还挺好用的，用post取代std::async生成future，可以指定不同的executor，然后executor切换可以通过wrap来换，就相当于folly里的via 基本功能和folly差不太多了
- executor设计还在推进中，我看计划是c++23，变化可能和eric说的差不多，https://github.com/executors/executors 
  - http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p0443r14.html
  - 文档看不下去？这有个介绍写的不错 https://cor3ntin.github.io/posts/executors/
- 有个介绍实现无需type erasure的future C++Now 2018: Vittorio Romeo “Futures Without Type Erasure” https://www.youtube.com/watch?v=Avvhs3PLP7o 简单说就是编译期确定调用链结构，用模版
  - 还有个文档解说 https://www.maxpagani.org/2018/07/31/it18-zero-allocation-and-no-type-erasure-futures/
---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。