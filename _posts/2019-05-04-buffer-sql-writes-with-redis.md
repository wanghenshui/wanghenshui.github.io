---
layout: post
categories: database
title: Buffering SQL Writes with Redis
tags: [redis, postgresql]

---

  

---

### why

这篇文章Sentry公司的博客，介绍他们怎么用redis的(好像是一个运营监控服务软件公司)

----

Sentry公司大量使用pg，两个集群，一个集群存储事件元数据，另一个存储Sentry平台数据，都有冷备，只在灾备或者维护期间使用

数据流分成三类，时序数据

- 事件blob数据，不变的，直接存储到Riak集群里
- kv对，表示tag，通常是设备名，操作系统之类的
- 属性 聚合操作用

大多数数据是SQL，事件Blob数据存在Riak来保持扩展性，实际上也是用来做KV存储

`突发情况`

Sentry的数据信息有特征，比如突然传来一个错误事件，这些事件重复程度高，出现频率也高，所以需要一个去重-聚合动作，又分两种情况

- 相同错误出现多次
- 大量不同错误生成新的聚合

可以从下面两个属性来观测到

- 基数计数器 Cardinality counters，
- Latest Value 看聚合操作中出现key用个字段记录

第一种设置个counter

```sql
UPDATE table SET counter = counter + 1 WHERE key = %s;
```

第二种就设置个字段记录

 ```sql
UPDATE table SET last_seen = %s WHERE key = %s;
 ```

count 引入的锁还有可能影响性能，所以把count拆开，拆成多行，避免行锁竞争

下面这个例子是一百行的

```sql
UPDATE table SET counter = counter + 1 WHERE key = %s AND partition = ABS(RANDOM() * 100);
```

pg提供强一致，浪费很多时间在锁上，所以用buffer来省掉这些竞争

buffer write，先聚合一堆写，定时刷回去，需要考虑最低损失数据，据此来决定回写周期，Sentry实践是10秒一次

这引入两种问题

- UI不会自动更新，十秒需要触发一次更新
- 可能丢失数据，比如网络问题



使用Redis

- 每个entity 一个hash

- flush 一组hash集合

当数据来

- 对每个entity hashkey
  - hincrby counter
  - 更新其他字段，hset，比如last seen timestamp
- zadd 把pending key加入集合中

然后类似cron任务，10秒一次，zrange拿到集合，对于pending hash key 加入到队列，然后zrem移除集合

worker从队列中拿到job，开始写

- pipeline
  - zrem，保证没副作用
  - hgetall 拿到key
  - rem hashkey
- 转换成sql，直接执行最后结果 
  - set counter = counter +%d
  - set value = %s

限制条数，使用sorted set(zset)

可以水平扩展，加redis节点

这个模型保证一行sql就更新一次，降低锁竞争，达到预期

**~~问题：为什么不用时序数据库？~~**



博客还提到了几个提升的点子

- 通常优先级高的事情发生的概率比较低，当前是模型是LIFO，也可改成FIFO 用zadd nx
- 数据冲突踩踏，大量数据任务可能同时触发，虽然可能实际处理后和noop没区别，但还是有这种突发增加延迟的问题，当前是push模型，可以改成pull，控制主动权 ~~限流器也行~~ 实现上的复杂导致没能采用
- 丢写，加个备份集合

---


### ref

- <https://blog.sentry.io/2016/02/23/buffering-sql-writes-with-redis>

### contact

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
![微信转账](https://wanghenshui.github.io/assets/wepay.png)
</details>其他联系方式在主页