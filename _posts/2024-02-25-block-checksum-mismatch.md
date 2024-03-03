---
layout: post
title: block checksum mismatch
categories: [database]
tags: [rocksdb]
---


大概率盘的问题，看了一遍全网案例

<!-- more -->


block checksum mismatch

大概率盘坏，搜到的解决方案都是重建为主

- ceph案例
  - https://tracker.ceph.com/issues/48002 重建
  - https://forums.percona.com/t/unable-to-run-due-to-rocksdb-error/16654  重建

- google group邮件
  - https://groups.google.com/g/rocksdb/c/io7y5AqxDkk/m/VnTLHbq5AQAJ 认为是硬件问题
  - https://groups.google.com/g/rocksdb/c/gUD4kCGTw-0/m/SpTzOgS8AgAJ 尝试scan 重建sst结果搞坏两份备份，幽默

- https://github.com/apache/bookkeeper/pull/3568 7.4有bug升级到7.5

> fixed after 7.4.0. The fix is followed
>   Fixed a bug in WriteBatchInternal::Append() where WAL termination point in write batch was not considered and the function appends an incorrect number of checksums.

- https://github.com/arangodb/arangodb/issues/9801 结论？

- rocksdb的论文 https://blog.mwish.me/2023/01/22/Fast21-RocksDB/ 还是备份。数据损坏是一种必然

> RocksDB 面临着下面的错误：
> 
>    SSD 盘故障  由于性能原因，用户可能不会开启 DIF/DIX 等校验方式
> 
>    内存 / CPU 故障：发现原因较少，不过我姑且也碰到过几次
> 
>    软件故障
> 
>    网络传输的时候产生的问题（网卡等）
> 
> 根据 RocksDB 的统计
> 
>     在 FB，每 100PB 数据，一个月会出现三次 corrupt
> 
>     40% 的情况下，这些 Corrupt 已经扩散到了别的机器上
> 
>     网络系统可能会有每 PB 17次 checksum mismatch
> 
> 基于以上的情况，FB 认为，需要尽早找到 Corrupt，来减少因为 Corrupt 产生的 Downtime。在分布式系统中，还是能够用正确副本代替错误副本来修正数据的

注意这个数据，在公有云场景下，概率还得翻倍吧

- tidb案例
    - https://asktug.com/t/topic/782830?replies_to_post_number=3 盘坏，阿里云是ceph改
    - https://asktug.com/t/topic/1022009 云盘坏
    - https://tidb.net/blog/54e388c8?_gl=1*k883y2*_ga*MjA3MTYxNTczMS4xNzA5MTAxODM4*_ga_D02DELFW09*MTcwOTEwMTgzNy4xLjEuMTcwOTEwMjE5OC4wLjAuMA..  修复方案 删数据 删副本 tidb是混合的单个db，后面拆开了，但最开始的region设计是单db的
    - https://asktug.com/t/topic/1009328?replies_to_post_number=20 
    - 盘坏 https://asktug.com/t/topic/69009/21?page=2

- rocksdb案例
  - https://github.com/facebook/rocksdb/issues/2882 hdd坏盘
  - https://github.com/facebook/rocksdb/issues/10531 重建
  - https://github.com/facebook/rocksdb/issues/3509 内存坏
  - https://github.com/facebook/rocksdb/issues/6435 无结论，怀疑导入的数据就是有问题的
    - ingest file开启checksum


其他挽救方案 
- https://github.com/facebook/rocksdb/pull/6955 重建sst，没合入
- ajkr说有unsafe_remove_sst_file可以用，需要测试，这里标记TODO