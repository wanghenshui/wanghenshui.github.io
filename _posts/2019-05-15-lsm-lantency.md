---
layout: post
title: lsm-tree延迟分析
categories: [database]
tags: [lsm, lantency]
---


---



- L0满， 无法接收 write-buffer不能及时Flush，阻塞客户端 
  - 高层压缩占用IO
  - L0 L1压缩慢
  - L0 空间少
- Flush 太慢，客户端阻塞 -> rate limiter限速



rocksdb的解决方案就是rate limiter限速



slik思路

（1）优先flushing和lower  levels的compaction，低level的compaction优先于高level的compaction，这样保证flushing能尽快的写入level 0，level 0尽快compaction level 1，（a）尽量避免因为memtable到达上限卡client  I/O，（b）尽量避免因为level 0的sstable文件数到达上限卡client  I/O。实际实现的时候会有一个线程池专门用于Flushing；另外一个线程池用于其他的Compaction

（2）Preempting  Compactions：支持抢占式Compaction，也就是高优先级的compaction可以抢占低优先级的compaction，也就是说另外一个用于L0~LN之间的compaction的线程池，优先级高的low level compaction可以抢占high  level的compaction，这样L0->L1在这个线程池，最高优先级的compaction就能够在必要的时候抢占执行，保证尽量不会出现level 0的sstable数量超过阈值

（3）在low load的时候，给Internal  Operation（compaction）分配更多的bandwidth，相反，在high load的时候，给Client  operation分配更多的带宽，这样可以保证Compaction在适当的时候也能得到更多的处理，减少read放大和空间放大，这个调度策略也是基于通常的client operation load是波动这事实来设计的，如下图，就是一个真实环境的workload变化规律：



## ref

1. https://blog.csdn.net/Z_Stand/article/details/109683804
2. https://zhuanlan.zhihu.com/p/77543818
3. 论文地址 https://www.usenix.org/system/files/atc19-balmau.pdf



---

