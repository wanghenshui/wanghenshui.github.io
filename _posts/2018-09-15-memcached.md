---
layout: post
title: memcached源码剖析笔记
categories: [language,database]
tags: [c,kv,cache,memcache]
---
  

---

 

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

