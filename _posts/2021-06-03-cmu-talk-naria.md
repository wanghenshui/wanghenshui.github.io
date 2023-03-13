---
layout: post
title: Noria Fast Materialized Views for Fast Websites
categories: [database,review]
tags: [cmu, noria, rust]
---

CMU技术分享

Noria Fast Materialized Views for Fast Websites

这个在monringpaper有提到过，最近又在cmu有techtalk

避免不了解，先看一下文档预习一下概念

[morning paper链接](https://blog.acolyer.org/2018/10/29/noria-dynamic-partially-stateful-data-flow-for-high-performance-web-applications/)

看不懂有[中文翻译](https://zhuanlan.zhihu.com/p/119566854)

代码这里 https://github.com/mit-pdos/noria-mysql

https://github.com/mit-pdos/noria/

<!-- more -->

<iframe width="560" height="315" src="https://www.youtube.com/embed/kVv9Pik6QGY" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>



这个讲的是一个dataflow数据库方案。看起来这种方案是未来啊，已经见到好几个了



dataflow就是保存一个个视图到内存中，响应肯定快。对比memcache的不可扩展问题通过db层来解决，memecache这种东西除非大公司比如facebook这种能有各种轮子(mrouter)组件维护运维，小公司还是选择db一整套解决方案要好得多



<img src="https://wanghenshui.github.io/assets/image-20210603163417744.png" alt=""  width="100%">

关键概念 partial state -> partial stateful dataflow



主要设计点

- upqueries through dataflow
- live dataflow changes
  - detect overlapping queries
  - resue state and dataflow
  - Add new operators
- partial state correctness
- concurrency for performence





主要还是得看代码，说的很范范


---


