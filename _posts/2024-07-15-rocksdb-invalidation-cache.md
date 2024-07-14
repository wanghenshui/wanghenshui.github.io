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

rocksdb本身不好解决这个问题，rocksdb rowcache有兼容性问题(deleterange breaking ,v9)，不能用


<!-- more -->


结论 本身rocksdb信息不足以感知这些。这种太业务了，应该业务来搞

### Leaper: a learned prefetcher for cache invalidation in LSM-tree based storage engines

北京大学，vldb‘20 [18]，采用机器学习方法解决X-Engine中cache miss问题


在X-Engine实际运行中，由于后台异步数据合并任务造成的大面积缓存失效问题。之前也有论文提出这种问题，具体解决是多增一个buffer cache，空间换效率。

Leaper采用机器学习算法，预测一个 compaction 任务在执行过程中和刚刚结束执行时，数据库上层 SQL 负载可能会访问到数据记录并提前将其加载进 cache 中，从而实现降低 cache miss，提高 QPS 稳定性的目的

rocksdb本身没有这种信息输入接口，只能根据blockcache存在过这个信息来来加载

可以提供一个predict_op, 给上层判定是否回填

显然是业务驱动


###