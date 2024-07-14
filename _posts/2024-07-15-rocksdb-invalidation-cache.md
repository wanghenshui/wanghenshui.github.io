---
layout: post
title: rocksdb cache过期问题讨论
categories: [database]
tags: [rocksdb]
---
如果blockcache被compaction搞失效了，有没有一种逻辑自动重填blockcache，降低cache miss？

毕竟在blockcache中属于热数据

另外ingest文件能不能同时预热 blockcache？

结论:上层加row cache绕过

rocksdb本身不好解决这个问题，太业务了

另外 rocksdb rowcache有兼容性问题(deleterange breaking ,v9)，不能用


<!-- more -->

### LSbM-tree: Re-enabling Buffer Caching in Data Management for Mixed Reads and Writes

维护一个compaction buffer https://nan01ab.github.io/2018/07/FD-tree-and-LSbM-tree.html


###  X-Engine: An Optimized Storage Engine for Large-scale E-commerce Transaction Processing

改进LSM Row Cache缓存热点行

减少Compaction的粒度；减少Compaction过程中改动的数据；Compaction过程中针对已有的缓存数据做定点更新（增量替换）



### Leaper: a learned prefetcher for cache invalidation in LSM-tree based storage engines

北京大学，vldb‘20 [18]，采用机器学习方法解决X-Engine中cache miss问题


在X-Engine实际运行中，由于后台异步数据合并任务造成的大面积缓存失效问题。之前也有论文提出这种问题，具体解决是多增一个buffer cache，空间换效率。

Leaper采用机器学习算法，预测一个 compaction 任务在执行过程中和刚刚结束执行时，数据库上层 SQL 负载可能会访问到数据记录并提前将其加载进 cache 中，从而实现降低 cache miss，提高 QPS 稳定性的目的

rocksdb本身没有这种信息输入接口，只能根据blockcache存在过这个信息来来加载

可以提供一个predict_op, 给上层判定是否回填

显然是业务驱动


### AC-Key: Adaptive Caching for LSM-based Key-Value Stores

blockcache改成cache key/cache adderss并且2Q策略维护

有个公式判定，较复杂 https://linqy71.github.io/2020/12/22/AC-Key/

实现难度也比较大

如果考虑单独做一个2Q cache放在业务上层，外部数据导入就扫一遍 cache上，实现更简单

## 特殊的cache设计

### FrozenHot Cache: Rethinking Cache Management for Modern Hardware

我之前有个类似想法 FastCHD + 动态hashmap 定期重构

感觉内存不可控

另外cache的其他问题就不展开了，另一个话题

## 加兜底

### SAS-Cache: A Semantic-Aware Secondary Cache for LSM-based Key-Value Stores

blockcache miss了，磁盘swap再撑一下，最后查FS/S3