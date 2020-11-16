---
layout: post
title: memcached源码剖析笔记
categories: [c]
tags: [c,kv,cache,memcache, linux]
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

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
![微信转账](https://wanghenshui.github.io/assets/wepay.png)
</details>