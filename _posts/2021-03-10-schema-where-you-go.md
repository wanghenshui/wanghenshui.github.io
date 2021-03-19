---
layout: post
title: 数据库的schema信息如何存储/维护？
categories: [database]
tags: [myrocks, rocksdb, tidb, cockroachdb]
---



<!-- more -->

## mysql myrocks

key value绑定

<img src="https://wanghenshui.github.io/assets/myrocks-key.png" alt=""  width="80%">

Memcomparable



myrocks的方案，一张图

<img src="https://wanghenshui.github.io/assets/myrocks-cf.png" alt=""  width="100%">

**多CF，schema/index信息都放在infomation_schema**

schema信息存到infomation_schema表中，也就是system这个cf，保存映射关系，正常来说放在默认CF里点查也没啥问题

注意primary key和secondary key的设计差距不大，所以导致secondary key需要另外的CF来存，不然会撞，其实可以设计成特殊前缀来区分

~~类似hbase这种 key-row模型不会有储存index的烦恼~~



另外，多CF比单CF多个灵活删除CF的功能，可以更快的删



### Q:  发生迁移schema信息是如何同步的？

没什么特别的。不涉及gateway路由的问题



## mongo-rocks

**单CF，特殊前缀**

mongo两种映射，chunk->表名，表本身->index分开存储

chunk和表名的映射关系单独放在config server用来记录，方便mongos来路由，本身的index信息直接存到具体的chunk内部，用特殊前缀做区分，0000是元数据，0001是索引0002是数据等等



### Q:  schema信息是如何同步的？

无schema，index信息直接和表存在一起，没有啥同步问题

请求访问到mongos，mongos从config server拉路由信息，然后根据路由信息广播请求，然后获取对应的key index信息进行计算



## TIDB

本身是多database 多副本

**单CF 特殊前缀** 存元数据(自身的ID， index做编码和数据放在一起， Memcomparable)，database映射信息放到PD

> TiDB 中每个Database和Table都有元信息，也就是其定义以及各项属性。这些信息也需要持久化，TiDB 将这些信息也存储在了 TiKV 中。每个Database/Table都被分配了一个唯一的 ID，这个 ID 作为唯一标识，并且在编码为 Key-Value 时，这个 ID 都会编码到 Key 中，再加上m_前缀。这样可以构造出一个 Key，Value 中存储的是序列化后的元信息。除此之外，TiDB 还用一个专门的 (Key, Value) 键值对存储当前所有表结构信息的最新版本号。这个键值对是全局的，每次DDL 操作的状态改变时其版本号都会加1。目前，TiDB 把这个键值对存放在 pd-server 内置的 etcd 中，其Key为"/tidb/ddl/global_schema_version"，Value 是类型为 int64 的版本号值。 TiDB 使用 Google F1 的 Online Schema 变更算法，有一个后台线程在不断的检查 etcd 中存储的表结构信息的版本号是否发生变化，并且保证在一定时间内一定能够获取版本的变化



路由信息是放在PD的，客户端需要从PD中拉到路由，根据这个路由来访问，PD内嵌etcd，维护一组版本信息

请求拿到需要的key和index计算就行了



### Q：DDL改动如何保证正确？

用Online Schema变更算法。lease+版本

这里应该展开讲一下

### Q:  schema信息是如何同步的？

所有的变动都是主动推给pd





## CockroachDB

无中心，gossip通信

保证最终一致性，时间窗内不保证DDL改动一致性

### Q：DDL改动如何保证正确？

用Online Schema变更算法。lease+版本

这里应该展开讲一下

### Q:  schema信息是如何同步的？

gossip，变更中总有一个时间窗期间是不同步的

这里应该展开讲一下





## 参考信息

- myrocks 图来自这里 https://github.com/wisehead/myrocks_notes/blob/master/10.CF/CF/index.md 代码分析记录的很详细，代码级别
- mongorocks整理自
- tidb vs crdb https://www.jianshu.com/p/8d0a99e198fb
- crdb 分布式事务演进 https://www.jianshu.com/p/a4604b012f31
- yugabyte-db介绍 https://ericfu.me/yugabyte-db-introduction/
- http://www.postgres.cn/downfiles/pgconf_2018/PostgresChina2018_%E8%B5%96%E5%AE%9D%E5%8D%8E_%E5%BC%80%E6%BA%90%E5%88%86%E5%B8%83%E5%BC%8FNewSQL%E6%95%B0%E6%8D%AE%E5%BA%93CockroachDB%E6%9E%B6%E6%9E%84%E5%8F%8A%E6%9C%80%E4%BD%B3%E5%AE%9E%E8%B7%B5.pdf
- https://iswade.github.io/translate/crdb/crdb_paper_cn/

---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>