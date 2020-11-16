---
layout: post
category: database
title: rocksdb一些杂项概念
tags: [rocksdb, c++]
---
  

**Write Buffer Manager**

其实rocksdb整体很多这种插件接口语义，比如Write Buffer Manager， 比如Merge Operator，比如Rate Limiter，sst_file_maniger，eventlistener，用户创建，传进指针（有默认的，也可以继承重写接口）

Write Buffer Manager正如名字，就是控制写入buffer的，这个正是memtable的总大小上限，没有设置的话会有个默认的设定比如两个memtable大小

什么时候会切换memtable？

- Memtable的大小在一次写入后超过write_buffer_size。
- 所有列族中的memtable大小超过db_write_buffer_size了，或者write_buffer_manager要求落盘。在这种场景，最大的memtable会被落盘
- WAL文件的总大小超过max_total_wal_size。在这个场景，有着最老数据的memtable会被落盘，这样才允许携带有跟这个memtable相关数据的WAL文件被删除。

![](https://bravoboy.github.io/images/memtable_switch.jpg)ScheduleFlushes | HandleWALFull |  HandleWriteBufferFull | FlushMemTable

条件

1. 当前线程持有db的大锁

2. 当前线程是写wal文件的leader

   - 如果开启了enable_pipelined_write选项(写wal和写memtable分开), 那么同时要等到成为写memtable的leader

   - 判断当前wal文件是否为空，如果不为空就创建新的wal文件(recycle_log_file_num选项开启就复用)，然后构建新memtable。刷盘当前wal文件
   - 把之前的memtable变成immutable，然后切到新memtable

   - 调用InstallSuperVersionAndScheduleWork函数，这个函数会更新super_version_

**memtable**

影响memtable的几个选项

影响memtable的最重要的几个选项是：

- memtable_factory: memtable对象的工厂。通过声明一个工厂对象，用户可以改变底层memtable的实现，并提供事先声明的选项。
- write_buffer_size：一个memtable的大小
- db_write_buffer_size：多个列族的memtable的大小总和。这可以用来管理memtable使用的总内存数。
- write_buffer_manager：除了声明memtable的总大小，用户还可以提供他们自己的写缓冲区管理器，用来控制总体的memtable使用量。这个选项会覆盖db_write_buffer_size
- max_write_buffer_number：内存中可以拥有刷盘到SST文件前的最大memtable数。

| Memtable类型             | SkipList                     | HashSkipList                                         | HashLinkList                                  | Vector                       |
| ------------------------ | ---------------------------- | ---------------------------------------------------- | --------------------------------------------- | ---------------------------- |
| 最佳使用场景             | 通用                         | 带特殊key前缀的范围查询                              | 带特殊key前缀，并且每个前缀都只有很小数量的行 | 大量随机写压力               |
| 索引类型                 | 二分搜索                     | 哈希+二分搜索                                        | 哈希+线性搜索                                 | 线性搜索                     |
| 是否支持全量db有序扫描？ | 天然支持                     | 非常耗费资源（拷贝以及排序一生成一个临时视图）       | 同HashSkipList                                | 同HashSkipList               |
| 额外内存                 | 平均（每个节点有多个指针）   | 高（哈希桶+非空桶的skiplist元数据+每个节点多个指针） | 稍低（哈希桶+每个节点的指针）                 | 低（vector尾部预分配的内存） |
| Memtable落盘             | 快速，以及固定数量的额外内存 | 慢，并且大量临时内存使用                             | 同HashSkipList                                | 同HashSkipList               |
| 并发插入                 | 支持                         | 不支持                                               | 不支持                                        | 不支持                       |
| 带Hint插入               | 支持（在没有并发插入的时候） | 不支持                                               | 不支持                                        | 不支持                       |

**Direct IO**

关于buffered IO和DirectIO可以看参考链接3, 这个图不错，偷过来

![](<http://blog.chinaunix.net/attachment/201310/13/29075379_138165232328pb.jpg>)

rocksdb属于自缓存应用，有memtable+blockcache来保证了一定的局部性。本身已经实现了缓存算法（LRU，clock）可以不使用系统的页缓存，使用DirectIO，在options中有配置

```c++
  // Use O_DIRECT for user reads
  // Default: false
  // Not supported in ROCKSDB_LITE mode!
  bool use_direct_reads = false;

  // Use O_DIRECT for both reads and writes in background flush and compactions
  // When true, we also force new_table_reader_for_compaction_inputs to true.
  // Default: false
  // Not supported in ROCKSDB_LITE mode!
  bool use_direct_io_for_flush_and_compaction = false;
```



对于use_direct_io_for_flush_and_compaction， compaction有个compaction block cache 不建议用，具体可以参考链接4



**Rate Limiter限流器**

Rocksdb内置控制写入速率降低延迟的

通过调用NewGenericRateLimiter创建一个RateLimiter对象，可以对每个RocksDB实例分别创建，或者在RocksDB实例之间共享，以此控制落盘和压缩的写速率总量。

```c++
RateLimiter* rate_limiter = NewGenericRateLimiter(
    rate_bytes_per_sec /* int64_t */, 
    refill_period_us /* int64_t */,
    fairness /* int32_t */);
```

参数：

- rate_bytes_per_sec：通常这是唯一一个你需要关心的参数。他控制压缩和落盘的总速率，单位为bytes/秒。现在，RocksDB并不强制限制除了落盘和压缩以外的操作（如写WAL）
- refill_period_us：这个控制令牌被填充的频率。例如，当rate_bytes_per_sec被设置为10MB/s然后refill_period_us被设置为100ms，那么就每100ms会从新填充1MB的限量。更大的数值会导致突发写，而更小的数值会导致CPU过载。默认数值100,000应该在大多数场景都能很好工作了
- fairness：RateLimiter接受高优先级请求和低优先级请求。一个低优先级任务会被高优先级任务挡住。现在，RocksDB把来自压缩的请求认为是低优先级的，把来自落盘的任务认为是高优先级的。如果落盘请求不断地过来，低优先级请求会被拦截。这个fairness参数保证低优先级请求，在即使有高优先级任务的时候，也会有1/fairness的机会被执行，以避免低优先级任务的饿死。默认是10通常是可以的。

尽管令牌会以refill_period_us设定的时间按照间隔来填充，我们仍然需要保证一次写爆发中的最大字节数，因为我们不希望看到令牌堆积了很久，然后在一次写爆发中一次性消耗光，这显然不符合我们的需求。GetSingleBurstBytes会返回这个令牌数量的上限。

这样，每次写请求前，都需要申请令牌。如果这个请求无法被满足，请求会被阻塞，直到令牌被填充到足够完成请求。比如：

```c++
// block if tokens are not enough
rate_limiter->Request(1024 /* bytes */, rocksdb::Env::IO_HIGH); 
Status s = db->Flush();
```

如果有需要，用户还可以通过SetBytesPerSecond动态修改限流器每秒流量。参考[include/rocksdb/rate_limiter.h](https://github.com/facebook/rocksdb/blob/master/include/rocksdb/rate_limiter.h) 了解更多细节

对那些RocksDB提供的原生限流器无法满足需求的用户，他们可以通过继承[include/rocksdb/rate_limiter.h](https://github.com/facebook/rocksdb/blob/master/include/rocksdb/rate_limiter.h) 来实现自己的限流器。



**memory**

主要几大块， blockcache，memtable，index & filter block， pinned by iterator

memtable也可以被write buffer manager来控制

table_options.block_cache->GetPinnedUsage()获得第四个

### reference

1.  官方文档 https://github.com/facebook/rocksdb/wiki/Write-Buffer-Manager
2. 上面的一个翻译<https://github.com/johnzeng/rocksdb-doc-cn/blob/master/doc/Write-Buffer-Manager.md>
3.  <https://www.ibm.com/developerworks/cn/linux/l-cn-directio/index.html>
4.  Direct IO官方文档https://github.com/facebook/rocksdb/wiki/Direct-IO>
5.  Rate Limiter <https://github.com/johnzeng/rocksdb-doc-cn/blob/master/doc/Rate-Limiter.md>
6.  memtable原理，看WriteBufferManager部分<https://bravoboy.github.io/2018/12/07/rocksdb-Memtable/>
    1.  <https://zhuanlan.zhihu.com/p/29277585>
    2.  <https://bravoboy.github.io/2018/11/30/SwitchMemtable/>
7.  官方文档翻译<https://github.com/johnzeng/rocksdb-doc-cn/blob/master/doc/MemTable.md>

看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。

