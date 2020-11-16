---
layout: post
categories : database
title: rocksdb 初探 2：基本概念
tags : [rocksdb,c++]
---
  

### why

理清概念，快速梳理一下rocksdb的模块间交互

---

`术语`<sup>1</sup> 下面这些是我个人的理解补充，建议结合原文，如果看完觉得被误导了，可以看翻译或者英语原文

`Column Family` 

这个不是Cassandra那个CF，就是键空间。这个用来实现多种需求，比如上层元数据拆分。这涉及到编码的定制。我也不很懂

`CRUD`

插入就是插入，更新是追加插入，删除也是更新，value空。支持writebatch，原子性

put <https://www.jianshu.com/p/daa18eebf6e1>

<https://glitterisme.github.io/2018/07/03/%E6%89%8B%E6%92%95RocksDB-1/>

myrocks put <http://mysql.taobao.org/monthly/2017/07/05/>

wirte详解？ <https://blog.csdn.net/wang_xijue/article/details/46521605>

<http://mysql.taobao.org/monthly/2018/07/04/>

并发写？

<http://www.pandademo.com/2016/10/parallel-write-rocksdb-source-dissect-3/>

<https://www.jianshu.com/p/fd7e98fd5ee6>

<https://youjiali1995.github.io/rocksdb/write-batch/>

write stall？ 什么时候会write stall？

`Gets Iterators Snapshots `

iterator 和snapshot是一致的。底层引用计数保证不被删除。但是这个数据是不被持久化的，对比git，这就是拉个分支，然后在分支上修改，但是这个分支信息不记录，不保存就丢，可以在这基础上创建checkpoint然后搞备份

？疑问 checkpoint实现？ backupdb实现？是不是基于checkpoint

`minifest`

这东西就是个一个index 内部实现， 一致性保证

文件具体为

- MANIFEST-xx 内部是相关的一堆version edit
- CURRENT 记录最新的MANIFEST-xx（类似git里的head）

这里要说下version edit version set 和version

version 和versionset version这就是个snapshot snapshot这东西就是版本号啦，或者可以理解成git里的commit，每个commit都能抽出来一个分支，这就是snapshot了，version由version edit组成，version edit可以理解成 modify。git中的相关思想在大多kv中都有。

version是某个状态，version set就是所有状态的集合（一个branch？）

 参考<sup>3</sup> ，介绍了实现，一个cv队列，versionSet 拥有manifest写，新的mannifest入队列，判断current。另外ldd文件可以导出内容，一个例子

```shell
 ../ldb manifest_dump --path=./MANIFEST-000006
--------------- Column family "default"  (ID 0) --------------
log number: 15
comparator: leveldb.BytewiseComparator
--- level 0 --- version# 1 ---
 16:31478713['00010' seq:5732151, type:1 .. '0004999995' seq:6766579, type:1]
 14:31206213['00011000020' seq:4753765, type:1 .. '00049999990' seq:4266837, type:1]
 12:31367971['00011000023' seq:3559804, type:1 .. '00049999988' seq:3516765, type:1]
 10:31331378['00011000025' seq:560662, type:1 .. '00049999994' seq:1786954, type:1]
--- level 1 --- version# 1 ---
...省略60行打印
--- level 63 --- version# 1 ---

next_file_number 18 last_sequence 7515368  prev_log_number 0 max_column_family 0 min_log_number_to_keep 15
```



`WAL`

这东西就是oplog一种表达，有编码。可以看参考链接<sup>3</sup>中的实现

什么时候调用NewWritableFile？

- 打开db，肯定要生成对应的log
- 切换memtable，写满了，生成新的memtable，旧的imm等持久化，wal日志的生命周期结束

什么时候清理？ FIndObsoleteFiles 和sst manifest文件一起清理。

谁负责写？当然是dbimpl，对于memtable切换时全程感知的

考虑场景，WAL文件已经写满，但是memtable还没写满怎么办？

至于内容编码和配置选项，以及相关优化选项，又是另一个话题

内容一例

```shell
../ldb dump_wal --walfile=./000015.log |tail -f

7515329,4,76,495457,NOOP PUT(0) : 0x3030303334383431343337 PUT(0) : 0x3030303431353233363738 PUT(0) : 0x30303032383839343733 PUT(0) : 0x3030303135373830323031
```



` 事务`

这又是个复杂的话题，见参考链接

`memtable`

一般为了支持并发写，会使用skiplist 

 `compaction`

leveldb的由来，compaction gc

什么时候会compaction？

compaction原则？

compaction中的snapshot？



<https://yq.aliyun.com/articles/655902>

`flush`

什么时候会flush？







---

### reference

1. 术语 英语<https://github.com/facebook/rocksdb/wiki/Terminology>
   1. 中文<https://rocksdb.org.cn/doc/Terminology.html>
2. manifest 介绍 和实现<http://mysql.taobao.org/monthly/2018/05/08/>
   1. manifest 相关的一个bug pr 介绍<https://www.jianshu.com/p/d1b38ce0d966>
3. WAL 实现<http://mysql.taobao.org/monthly/2018/04/09/>
   1. WAL 刷盘机制 <http://kernelmaker.github.io/Rocksdb_WAL>
   2. WAL恢复 https://blog.csdn.net/dongfengxueli/article/details/66975838
   3. WAL生命周期 <https://www.jianshu.com/p/40a4f2521e0a>
   4. WAL调研，这哥们写了一半 <https://youjiali1995.github.io/rocksdb/wal/>
4. 事务 <https://github.com/facebook/rocksdb/wiki/Transactions>
   1. rocksdb 事务实现分析 <https://yq.aliyun.com/articles/257424>
   2. 更进一步 <https://github.com/facebook/rocksdb/wiki/WritePrepared-Transactions>
      1. <https://yq.aliyun.com/articles/627737#>
   3. myrocks 事务<http://mysql.taobao.org/monthly/2016/11/02/?spm=a2c4e.11153940.blogcont627737.14.d47c5ce5SNWg8r>
      1. mysql xa事务<http://mysql.taobao.org/monthly/2017/09/05/>
      2. binlog xa <https://blog.51cto.com/wangwei007/2323844>
5. level compaction<http://mysql.taobao.org/monthly/2018/10/08/>
6. flush <https://yq.aliyun.com/articles/643754>



看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。