---
layout: post
title: (译)redis核心数据结构的典型用法
categories: translation
tags : [redis]
---
  

---

 

> 本文是参考链接的简单总结。概述没有翻译

### Strings

主要使用场景

- `Session cache` 许多网站使用redis Strings来创建session cache，保存html或者网页来加速网站体验。这种数据基本都在内存中，使用redis再好不过，还有类似购物车的数据，临时缓存。
- `队列` 处理流量，消息，数据收集，任务管理，数据分发，使用redis 队列（https://www.infoworld.com/article/3230455/how-to-use-redis-for-real-time-metering-applications.html） 可以更好的管理
- 数据采集

### Redis Lists

主要使用场景

- 社交网站信息流推送，时间线推送，主页信息推送。
- Rss feeds。和上面一样
- leaderboards

### Redis Sets

- 分析商业数据，集合操作。比如统计销量等等
- Ip 流量访问统计
- 文本过滤，关键字屏蔽

### Redis Sorted Sets

- QA平台 答案权重排序
- 游戏积分排行榜 https://www.ionos.com/community/hosting/redis/how-to-implement-a-simple-redis-leaderboard/
- 任务调度服务 https://medium.com/@ApsOps/migrating-redis-sorted-sets-without-losing-data-f9e85f6549c5
- redis geo也是zset实现的



### Redis Hashes

- 用户档案信息。字段保存
- 用户发帖保存 https://instagram-engineering.com/storing-hundreds-of-millions-of-simple-key-value-pairs-in-redis-1091ae80f74c
- 多租户数据 https://divinglaravel.com/introduction-to-redis-hashes



上面的网址都没看。值得逐个看一眼放到这个帖子里

### 参考链接 

- http://highscalability.com/blog/2019/9/3/top-redis-use-cases-by-core-data-structure-types.html

---

