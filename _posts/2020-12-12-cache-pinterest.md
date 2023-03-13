---
layout: post
title: (译)Scaling Cache Infrastructure at Pinterest
categories: [database, translation]
tags: [cache, mcrouter, memcache]
---


---

> 原文[链接](https://medium.com/pinterest-engineering/scaling-cache-infrastructure-at-pinterest-422d6d294ece/)

需求，业务激增，缓存不够，要分布式缓存

pinterest的业务架构图

<img src="https://wanghenshui.github.io/assets/pinterest-cache.png" alt="" width="100%"> 

分布式缓存，使用mcrouter + memcache架构，facebook的方案，他们还发了[paper](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170_update.pdf)

memcache可以开启[extstore](https://github.com/memcached/memcached/wiki/Extstore)，如果数据过大放不下，可以保存到硬盘里，flash nvme之类的

mcrouter的抽象能力非常好

- 解藕数据面控制面
- 提供上层更精细的控制 修改ttl之类

<img src="https://wanghenshui.github.io/assets/pinterest-cache2.png" alt="" width="100%"> 

这套方案mcrouter也高可用

- 背后的复制行为对上层来说也是透明的 双活等等
- 也可以接入测试流量，更好的隔离流量



主要风险

- 配置文件容易出错
- 瓶颈在proxy 得多个proxy
- 尽管业务侧可以灵活的设计key，热点key问题还是不可避免 （有没有mongodb的那种分裂range机制？如果没有，能引入吗？）





说实话这个软文没讲什么东西



---

### PS

我浏览的途中又一次看了眼beandb，原来也是mc的协议啊



一个db的列表 https://github.com/sdcuike/issueBlog/blob/master/%E5%AD%98%E5%82%A8%E5%BC%95%E6%93%8E.md

https://github.com/alibaba/tair


---

