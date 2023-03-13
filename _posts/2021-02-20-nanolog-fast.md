---
layout: post
title: 为什么nanolog这么快
categories: [language]
tags: [c++, nanolog, spdlog, binlog]

---



- 没有锁，spdlog是mpmc+锁的模式，nanolog是spsc组合模式

- 二进制日志写入，没有写放大

论文地址 https://www.usenix.org/system/files/conference/atc18/atc18-yang.pdf

这里有一篇介绍 https://zhuanlan.zhihu.com/p/136208506还有很多优化的点子，比如cache miss，比如tsc读时间


---

