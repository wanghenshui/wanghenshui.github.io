---
layout: post
title: 学习/探索mongo
categories: [database]
tags: [c++, mongodb]
---


---

> [ppt地址](https://wanghenshui.github.io/mongo-ppt-cn/) ，资料都是整理

macos上安装和演示

```shell
#安装
brew tap mongodb/brew
brew install mongodb-community@4.4
#拉起
brew services start mongodb-community@4.4
#停止
brew services stop mongodb-community@4.4
# mongo shell
mongo 127.0.0.1:27017
```



mongo 和sql对应概念 区分



| SQL术语/概念                                   | MongoDB 术语/概念                                            |
| ---------------------------------------------- | ------------------------------------------------------------ |
| database                                       | [database](https://docs.mongodb.com/manual/reference/glossary/#term-database) |
| table                                          | [collection](https://docs.mongodb.com/manual/reference/glossary/#term-collection) |
| row                                            | [document](https://docs.mongodb.com/manual/reference/glossary/#term-document) 或 [BSON](https://docs.mongodb.com/manual/reference/glossary/#term-bson) document |
| column                                         | [field](https://docs.mongodb.com/manual/reference/glossary/#term-field) |
| index                                          | [index](https://docs.mongodb.com/manual/reference/glossary/#term-index) |
| table joins （表联接）                         | [$lookup](https://docs.mongodb.com/manual/reference/operator/aggregation/lookup/#pipe._S_lookup), `embedded documents （嵌入式文档）` |
| primary key 指定任何唯一的列或者列组合作为主键 | [primary key](https://docs.mongodb.com/manual/reference/glossary/#term-primary-key) 在 MongoDB 中, 主键自动设置为 [_id](https://docs.mongodb.com/manual/reference/glossary/#term-id) 字段 |
| aggregation (如：group by)                     | `aggregation pipeline （聚合管道）`参考：[SQL to Aggregation Mapping Chart](https://docs.mongodb.com/manual/reference/sql-aggregation-comparison/) |
| SELECT INTO NEW_TABLE                          | [$out](https://docs.mongodb.com/manual/reference/operator/aggregation/out/#pipe._S_out) 参考： [SQL to Aggregation Mapping Chart](https://docs.mongodb.com/manual/reference/sql-aggregation-comparison/) |
| MERGE INTO TABLE                               | [$merge](https://docs.mongodb.com/manual/reference/operator/aggregation/merge/#pipe._S_merge) （从MongoDB 4.2开始可用） 参考：[SQL to Aggregation Mapping Chart](https://docs.mongodb.com/manual/reference/sql-aggregation-comparison/) |
| transactions                                   | [transactions](https://docs.mongodb.com/manual/core/transactions/) |

二进制对应关系

|              | MongoDB | MySQL   |
| ------------ | ------- | ------- |
| 数据库服务端 | mongod  | mysqld  |
| 数据库客户端 | mongo   | mysql   |
| 复制日志     | oplog   | binlog  |
| 恢复用日志   | journal | redolog |





| 最新 oplog 时间戳 | snapshot  | 状态        |
| ----------------- | --------- | ----------- |
| t0                | snapshot0 | committed   |
| t1                | snapshot1 | uncommitted |
| t2                | snapshot2 | uncommitted |
| t3                | snapshot3 | uncommitted |

---

### ref

- https://www.runoob.com/mongodb/mongodb-osx-install.html
- https://aotu.io/notes/2020/06/07/sql-to-mongo-1/index.html


---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>

