---
layout: post
title: Optimizing Bulk Load in RocksDB
categories: [database]
tags: [rocksdb,tuning, rockset]
---




还是rockset的文章，讲他们怎么优化批量载入rocksdb的速度

几个优化

##### 在延迟和吞吐之间的取舍

批量加载的时候，调高writebatch大小，其他场景，writebatch不要太大。

##### 并发写

正常的对数据库的操作，保证只有一个写线程。这样不会有多线程写入阻塞问题。怕影响查询操作延迟，但对于这种加载场景，不需要考虑查询操作影响，把writebatch分配到不同的写线程做并发写，注意，要考虑共享的数据，尽可能让writebatch之间不影响不阻塞

##### 不写memtable

构造的数据直接调用 [IngestExternalFile()](https://rocksdb.org/blog/2017/02/17/bulkoad-ingest-sst-file.html) api，(rocksdb文档见[这里](https://github.com/facebook/rocksdb/wiki/Creating-and-Ingesting-SST-files)) 避免写入memtable来同步memtable，这个动作速度快，且干净

但是有局限，这样构造，sst文件只有一层，如果有零星的大sst文件，后台compaction会非常慢。解决方法，一个writebatch写成一个sst文件。

##### 停掉compaction

 [RocksDB Performance Benchmarks](https://github.com/facebook/rocksdb/wiki/Performance-Benchmarks#test-1-bulk-load-of-keys-in-random-order). 官方也建议，使用批量加载最好先停掉compaction然后最后做一次大的compaction，这样避免影响读写，但是

- sst文件增多，点查很慢，加上定制bloomfilter有所改善可是查bloomfilter开销也很大
- 最后一次compaction通常是单线程来做，虽然可以通过 [max_subcompactions](https://github.com/facebook/rocksdb/blob/d61d4507c0980b544e87fd0aa5ed2990a45dad5e/include/rocksdb/options.h#L563-L567)来改，但是效果有限，因为只有一层文件，文件是有重叠的，compaction算法找不到合并区间，所以最后还是一个线程遍历来搞，解决办法，手动对几个小范围做[CompactFiles()](https://github.com/facebook/rocksdb/wiki/Manual-Compaction#compactfiles).，生成不是L0层的文件，这样就有区间，就能并发compaction了。前文<sup>2</sup>提到，他们L1 L0是不压缩的 （为什么压缩会影响写速率？）

##### 结论

在这些优化前提下，加载200g未压缩数据（Lz4压缩后80g） 需要52分钟（70MB/s 18核）初始化加载用了35分钟，最后compaction用例17分钟，如果没有这些优化需要18小时，如果只增加writebatch大小以及并发写线程，用了5个小时 

所有试验，只用了一个rocksdb实例

##### ref

1. https://rockset.com/blog/optimizing-bulk-load-in-rocksdb/

2. https://rockset.com/blog/how-we-use-rocksdb-at-rockset/

3. https://rocksdb.org/blog/2017/02/17/bulkoad-ingest-sst-file.html

   

---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>