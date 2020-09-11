---
layout: post
title: memcached源码剖析笔记
category: [c]
tags: [c,kv,cache,memcache, linux]
---
{% include JB/setup %}

---

[toc]

---

memcache特点

- 协议简单
  - add/set/replace/get/get/delete
- 基于libevent
- 内存存储，LRU，抗干扰？

内存存储机制

slab allocation，感觉像linux系统的slab

- page 1M chunk内存空间slab 特定大小的chunk组
- 解决内存碎片但是空间利用存在浪费
  - chunk可以动态増缩？
- 增长因子可以设定 growth factor

![image-20200911173653707](https://wanghenshui.github.io/assets/image-20200911173653707.png)

---

### ref





---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。