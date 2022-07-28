---
layout: post
title: blog review 第十六期
categories: [review]
tags: [aio,io,SplinterDB,b-tree]
---
准备把blog阅读和paper阅读都归一，而不是看一篇翻译一篇，效率太低了

后面写博客按照 paper review，blog review，cppcon review之类的集合形式来写，不一篇一片写了。太水了

<!-- more -->

## [fork() without exec() is dangerous in large programs](https://www.evanjones.ca/fork-is-dangerous.html)

老生常谈了。fork完要立即exec。或者像nginx那样的用法，否则会有问题

## [Monarch: Google’s Planet-Scale In-Memory Time Series Database](https://www.micahlerner.com/2022/04/24/monarch-googles-planet-scale-in-memory-time-series-database.html)

![](https://www.micahlerner.com/assets/monarch/fig1.png)

很有意思，有点map-reduce的感觉。mixer无限扩，index负责一部分数据拉取

父mixer接受请求 推送给所有子mixer，子mixer再推送给子index，拿到数据 mixer汇总

## [Removing Double-Logging with Passive Data Persistence in LSM-tree based Relational Databases](https://www.usenix.org/conference/fast22/presentation/huang)

代码 https://github.com/ericaloha/MyRocks-PASV

改rocksdb，加上epoch。挺有意思。不过真的能保证数据不丢吗？

## [My Notes on GitLab Postgres Schema Design](https://shekhargulati.com/2022/07/08/my-notes-on-gitlabs-postgres-schema-design/)

一些PG使用经验

PK  选对类型，bigserial，bigint等等。考虑清楚

![](https://whyjava.files.wordpress.com/2022/06/pk_types.png)



使用两套id ，避免数据被猜到？

```sql	
CREATE TABLE issues (
    id integer NOT NULL,
    title character varying,
      project_id integer,
    iid integer,
    // rest of the columns removed
)
```

使用text加上条件

```sql
create table text_exp (id bigint primary key, 
s text default gen_random_uuid() not null,
CONSTRAINT check_15e644d856 CHECK ((char_length(s) <= 200)));
```
命名尽可能小写下划线，类别用前缀来搞定

时间戳加不加zone信息？create_at可以不加，但close_at得加。区别在用这个时间戳谁用，系统内部meta的话无所谓，但是外部用户可见的话可能得考虑用户体验

外键限制。不懂

```sql
ALTER TABLE ONLY todos
    ADD CONSTRAINT fk_rails_a27c483435 FOREIGN KEY (group_id) REFERENCES namespaces(id) ON DELETE CASCADE;
 
ALTER TABLE ONLY projects
    ADD CONSTRAINT fk_projects_namespace_id FOREIGN KEY (namespace_id) REFERENCES namespaces(id) ON DELETE RESTRICT;
 
ALTER TABLE ONLY authentication_events
    ADD CONSTRAINT fk_rails_b204656a54 FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;
```

三种分片模式

范围，比如时间范围，audit_events  web_hook_logs
？？这样倾斜很严重吧

list分区，这种要定制枚举列表，和范围差不太多其实 loose_foreign_keys_deleted_records

hash没啥说的

## [Persistent Storage of Adaptive Radix Trees in DuckDB](https://duckdb.org/2022/07/27/art-storage.html)

代码在这里 https://github.com/duckdb/duckdb/tree/2c623978d700443665d519282ee52891e4573a3d/src/include/duckdb/execution/index/art


## [小红书自研KV存储架构如何实现万亿量级存储与跨云多活](https://zhuanlan.zhihu.com/p/537691368)

proxy压缩网络包，挺有意思

## [DGraph: A Large-Scale Financial Dataset for Graph Anomaly Detection](https://zhuanlan.zhihu.com/p/546872168)

欺诈者和普通用户通常具有不同的图结构和邻居特征, 有意思

很多数据能说明问题，比如联系人多，比如使用共同的联系人/默认值等等。数据可以挖掘的点有很多。不过这种指向型怎么挖掘出来呢

## TODO

---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>
