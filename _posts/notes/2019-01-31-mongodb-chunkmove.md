---
layout: post
title: mongodb move chunk缓慢。
category: 技术
tags: mongodb
---

有几个参考链接可以学习下
[同时添加多个shard](https://stackoverflow.com/questions/49420465/mongodb-sharding-adding-multiple-shards-at-the-same-time/49434444#49434444)
[mongodb调试慢的迁移](https://stackoverflow.com/questions/40494330/how-i-can-debug-mongodb-slow-chunk-migration)
[迁移13天...](https://dba.stackexchange.com/questions/81545/mongodb-shard-chunk-migration-500gb-takes-13-days-is-this-slow-or-normal)

第三个链接，提供了一个check list

```
If it is slow, there are a number of possible reasons why that is the case, but the most common for a system that is not busy are:

Source Disk I/O - if the data is not in active memory when it is read, it must be paged in from disk
Network - if there is latency, rate limiting, packet loss etc. then the read may take quite a while
Target Disk I/O - the data and indexes have to be written to disk, lots of indexes can make this worse, but usually this is not a problem on a lightly loaded system
Problems with migrations causing aborts and failed migrations (issues with config servers, issues with deletes on primaries)
Replication lag - for migrations to replica sets, write concern w:2 or w:majority is used by default and requires up to date secondaries to satisfy it.
```
前三项一般没啥问题，第四条，也不是放弃迁移，可能会导致反复迁移

考虑movechunk的流程，先打快照，把当前备份复制过去，然后再复制增量
如果这个增量没完没了的话，迁移时间必然会延长，有点像第五条的场景，第五条应该就是oplog赶不上了

再考虑oplog一直增长的情形 -> 插入。如果是顺序插入应该很快。如果是删除之类的操作可能会耗时过长，但是也不至于很慢，
再考虑什么会导致插入过慢 ->  索引过多，引用我老大的一句话，“索引过多导致插入变慢是数据库常识”，只要有索引，以前索引优化以及影响的那套理论还是成立的。
