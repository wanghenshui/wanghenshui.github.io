---
layout: post
title: (译)Beyond Relational Databases:A Focus on Redis, MongoDB, and ClickHouse
categories: [database]
tags: [redis, mongodb, clickhouse, nosql]
---
  

---

 

> percona的什么白皮书，我看就是一堆吐槽



关系型数据库不是万金油，用错反而是瓶颈

数据模型万金油，反而限制了扩展能力

sql好用但是不够灵活，json人人爱

ACID很重要，但是代价也很大，这也是关系型数据库的采用点

由于保证事务可靠，也就限制了扩展能力，数据模型简单不要求事务，上内存kv数据库

mysql也能存大数据，但是能存不能用，没啥意义，所以去掉索引，去掉关系限制，列式数据库诞生了



---

### KV数据库

最开始的目的是做个数据库前端无状态缓存

要快，一般都是hashtable。不是为了替代关系型数据库，只是一项中间件技术

后来KV数据库发展成有简单协议的有命令有状态的服务了。不得不提redis

个人认为 redis能打败memcache，社区好，功能性强，memcache就是单纯的做无状态中间件。这种东西mysql内部也做小型cache，比如2Q啥的。不如一个组件强。但是组件本身也要考虑淘汰以及热点击穿的问题。这就是另一个话题了



典型代表redis提供了一些很好的特性，能让业务更简化，比如TTL,  list，比如lua支持，LRU淘汰策略，多key事务，阻塞命令等等

做mysql前端最好不过，做个纯粹的数据库也可以（不落盘不停机）

---

### 文档数据库

最早来自邮件存储需求

json对象，sparse index 不存在的key就不要，非常灵活

灵活模式不等于没有模式

典型代表 mongodb 不止提供文档接口，还提供了分片管理，方便水平扩展，加钱上机器就行了

还有一些牛逼特性，比如聚合动作方便map-reduce ，geo相关功能，以及可插拔引擎（wiretiger/rocksdb）



劣势

嵌套表效率低

多表join查询

多表事务

---

### 列式存储

只要几列数据为什么不用覆盖索引？

- 查询灵活难道要每一列都建索引吗？不现实
- 插入要改动索引，复杂度爆炸延迟爆炸

作者没用Cassandra和hbase举例，而是用了clickhouse

- 兼容大多数SQL
- 也有索引，针对MergeTree引擎，支持主键，支持range查
- Dictionaries 查表不用join
- 低延迟，查询不用担心阻塞
- 近似估计等等特殊特性

对于读敏感的大数据集，十分好用

OLTP



---

##### ref

1. https://learn.percona.com/hubfs/ExpertOpinion/Beyond%20Relational%20Databases.pdf

   

---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
![微信转账](https://wanghenshui.github.io/assets/wepay.png)
</details>