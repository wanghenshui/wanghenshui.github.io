---
layout: post
categories: database
title: rocksdb 初探 6：wal
tags : [rocksdb, c++]
---
  



对RocksDB的每一次update都会写入两个位置：1） 内存表（内存数据结构，后续会flush到SST file） 2）磁盘中的write ahead log（WAL）。在故障发生时，WAL可以用来恢复内存表中的数据。默认情况下，RocksDB通过在每次用户写时调用fflush WAL文件来保证一致性。

# 1、 Life Cycle of a WAL

举个例子，RocksDB实例创建了两个column families，分别是 new_cf和default。一旦db被open，就会在磁盘上创建一个WAL来持久化所有的写操作。

```
DB* db;
std::vector<ColumnFamilyDescriptor> column_families;
column_families.push_back(ColumnFamilyDescriptor(
    kDefaultColumnFamilyName, ColumnFamilyOptions()));
column_families.push_back(ColumnFamilyDescriptor(
    "new_cf", ColumnFamilyOptions()));
std::vector<ColumnFamilyHandle*> handles;
s = DB::Open(DBOptions(), kDBPath, column_families, &handles, &db);
```

添加一些kv对数据

```
db->Put(WriteOptions(), handles[1], Slice("key1"), Slice("value1"));
db->Put(WriteOptions(), handles[0], Slice("key2"), Slice("value2"));
db->Put(WriteOptions(), handles[1], Slice("key3"), Slice("value3"));
db->Put(WriteOptions(), handles[0], Slice("key4"), Slice("value4"));
```

此时，WAL已经记录了所有的写操作。WAL文件会保持打开状态，一直记录后续所有的写，直到WAL 大小达到DBOptions::max_total_wal_size为止。
 如果用户决定要flush new_cf中的数据时，会有以下操作：1) new_cf的数据 key1和key3会flush到一个新的SST file。 2)新建一个WAL，后续对所有列族的写都通过新的WAL记录。3)老的WAL不再记录新的写

```
db->Flush(FlushOptions(), handles[1]);
// key5 and key6 will appear in a new WAL
db->Put(WriteOptions(), handles[1], Slice("key5"), Slice("value5"));
db->Put(WriteOptions(), handles[0], Slice("key6"), Slice("value6"));
```

此时，会有两个WAL文件，老的WAL会包含key1、key2、key3和key4，新的WAL文件包含key5和key6。因为老的WAL仍然含有default 列族的数据，所以还没有被删除。只有当用户决定flush default列族的数据之后，老的WAL 才会被归档然后从磁盘中删除。

```
db->Flush(FlushOptions(), handles[0]);
// The older WAL will be archived and purged separetely
```

总之，在以下情况下会创建一个WAL：

- 新打开一个DB
- flush了一个column family。一个WAL文件只有当所有的列族数据都已经flush到SST file之后才会被删除，或者说，所有的WAL中数据都持久化到SST file之后，才会被删除。归档的WAL文件会move到一个单独的目录，后续从磁盘中删除。

# 2、WAL Configurations

- DBOptions::wal_dir ： RocksDB保存WAL file的目录，可以将目录与数据目录配置在不同的路径下。
- DBOptions::WAL_ttl_seconds, DBOptions::WAL_size_limit_MB：这两个选项影响归档WAL被删除的快慢。
- DBOptions::max_total_wal_size ： 为了限制WALs的大小，RocksDB使用该配置来触发 column family flush到SST file。一旦，WALs超过了这个大小，RocksDB会强制将所有列族的数据flush到SST file，之后就可以删除最老的WALs。
- DBOptions::avoid_flush_during_recovery
- DBOptions::manual_wal_flush： 这个参数决定了WAL flush是否在每次写之后自动执行，或者是纯手动执行（用户调用FlushWAL来触发）。
- DBOptions::wal_filter：在恢复数据时可以过滤掉WAL中某些记录
- WriteOptions::disableWAL： 打开或者关闭WAL支持

# 3、WAL LOG File Format

## 3.1 OverView

WAL将内存表的操作记录序列化后持久化存储到日志文件。当DB故障时可以使用WAL 文件恢复到DB故障前的一致性状态。当内存表的数据安全地flush到持久化存储文件中后，对应的WAL log(s)被归档，然后在某个时刻被删除。

## 3.2 WAL Manager

在WAL目录中，WAL文件按照序列号递增命名。为了重建数据库故障之前的一致性状态，必须按照序号号递增的顺序读取WAL文件。WAL manager封装了读WAL文件的操作。WAL manager内部使用Reader or Writer abstraction 来读取WAL file。

## 3.3 Reader/Writer

Writer提供了将log记录append到log 文件的操作接口（内部使用WriteableFile接口）。Reader提供了从log文件中顺序读日志记录的操作接口（内部使用SequentialFile接口）。

## 3.4 Log File Format

日志文件保安了一系列不停长度的记录。Record按照kBlockSize分配。如果一个特定的记录不能完全适配剩余的空间，那么就会将剩余的空间补零。writer按照kBlockSize去写一个数据库，reader按照kBlockSIze去读一个数据库。

```
       +-----+-------------+--+----+----------+------+-- ... ----+
 File  | r0  |        r1   |P | r2 |    r3    |  r4  |           |
       +-----+-------------+--+----+----------+------+-- ... ----+
       <--- kBlockSize ------>|<-- kBlockSize ------>|

  rn = variable size records
  P = Padding
```

## 3.5 Record Format

```
+---------+-----------+-----------+--- ... ---+
|CRC (4B) | Size (2B) | Type (1B) | Payload   |
+---------+-----------+-----------+--- ... ---+

CRC = 32bit hash computed over the payload using CRC
Size = Length of the payload data
Type = Type of record
       (kZeroType, kFullType, kFirstType, kLastType, kMiddleType )
       The type is used to group a bunch of records together to represent
       blocks that are larger than kBlockSize
Payload = Byte stream as long as specified by the payload size
```

日志文件由连续的32KB大小的block组成。唯一的例外是文件尾部数据包含一个不是完整的block。
 每一个block包含连续的Records：

```
block := record* trailer?
record :=
  checksum: uint32  // crc32c of type and data[]
  length: uint16
  type: uint8       // One of FULL, FIRST, MIDDLE, LAST 
  data: uint8[length]
```

record type

```
FULL == 1
FIRST == 2
MIDDLE == 3
LAST == 4
```

FULL 表示包含了全部用户record记录
 FIRST、MIDDLE、LAST用户表示一个record太大然后拆分为多个数据片。FIRST表示是用户record的第一块数据，LAST表示最后一个，MID是用户Record中间部分的数据。
 Example

```
A: length 1000
B: length 97270
C: length 8000
```

A会在第一个block中存储一个完整的Record。
 B会被拆分为3个分片，第一个分片占用了第一个block的剩余全部空间，第二个分片占用第二个block的全部空间，第三个分片占用第三个block的前面部分空间。会在第三个block中预留6个字节，置为空来表示结束。
 C将会完整存储在第四个block。FULL Record

# 4、WAL Recovery Modes

每个应用都是唯一的，都需要RocksDB保证特定状态的一致性。RocksDB中每一个提交的记录都是持久化的。没有提交的记录保存在WAL file中。当DB正常退出时，在退出之前会提交所有没有提交的数据，所以总是能够保证一致性。当RocksDB进程被kill或者服务器重启时，RocksDB需要恢复到一个一致性状态。最重要的恢复操作之一就是replay所有WAL中没有提交的记录。不同的WAL recovery 模式定义了不同的replay WAL的行为。

## kTolerateCorruptedTailRecords

在这种模式下，WAL replay 会忽视日志文件末尾的任何error。这些error主要来源于不安全的进程退出后产生的不完全的写错误日志。这是一种启发式的或者探索式的模式，系统并不能区分是日志文件tail的data corruption还是不完全写操作。任何其他的IO error，都会被视作data corruption。

这种模式被大部分应用使用，这是因为该模式提供了一种比较合理的tradeoff between 不安全退出后重启和数据一致性。

## kAbsoluteConsistency

在这种模式下，在replay WAL过程中任何IO 错误都被视为data corruption。这种模式适用于以下场景：应用不能接受丢失任何记录，而且有方法恢复未提交的数据。

## kPointInTimeConsistency

在这种模式下，当发生IO errror时，WAL replay会stop，系统恢复到一个满足一致性的时间点上。这种模式适用于有副本的集群，来自另外一个副本的数据可以用来恢复当前的实例。

## kSkipAnyCorruptedRecord

在这种模式下，WAL replay会忽视日志文件中的任何错误。系统尝试恢复尽可能多的数据。适用于灾后重建的场景。



### reference

1. <https://github.com/facebook/rocksdb/wiki/Write-Ahead-Log>
2. https://www.jianshu.com/p/40a4f2521e0a
3. <http://kernelmaker.github.io/Rocksdb_WAL>

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。

