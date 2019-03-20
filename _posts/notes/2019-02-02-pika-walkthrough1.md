---
layout: post
title: pika 初探
category: database
tags: [redis,c++]
---

{% include JB/setup %}

### why

梳理思路，省着忘了

### 0. trivial

- 全局PikaServer对象，所有变量都用读写锁保护了。真的有必要吗。
- 模块拆分 （pika主程序，pink网络模块，blackwidow编码模块，slash公共组件（这个公共组件模块很坑爹），glog），底层模块又互相依赖。挺头疼的（需要画个图）
- 利用多线程优势，类似memcache用libevent哪种用法。主事件循环处理io事件，写pipe通知子线程搞定

- redis协议分析我以为得放在pika主程序中，结果没想到在pink里。糊一起了。之前还好奇，翻pika代码没发现redis代码，难道解析redis居然没用到redis源码自己搞的，结果在pink里。

### 1. 整体架构

![](https://wanghenshui.github.io/assets/68747470733a2f2f692e696d6775722e636f6d2f334564646374422e706e67.png)



一图胜千言 很多redis over rocksdb的实现都是在编码上有各种异同，比如ssdb ardb之类的，pika怎么做的？上图

![img](https://wanghenshui.github.io/assets/68747470733a2f2f692e696d6775722e636f6d2f6e71656c6975762e706e67.png)

复杂数据结构 set zset hash 是分成元数据和实体数据来做的。~~(大家都抄linux)~~



### reference

- 一个源码分析，已经有人做了。https://scottzzq.gitbooks.io/pika/content/
- 项目wiki https://github.com/Qihoo360/pika/wiki

