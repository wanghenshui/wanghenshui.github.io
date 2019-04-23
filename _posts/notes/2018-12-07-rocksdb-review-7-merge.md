---
layout: post
category : database
title: rocksdb 初探 6: wal
tags : [rocksdb,c++]
---
{% include JB/setup %}



一个堆栈信息，merge_test

```bash
(gdb) bt
#0  CountMergeOperator::Merge (this=0xebe410, key=..., existing_value=0x7fffffffd350, value=..., new_value=0x7fffffffd150, logger=0xebd220)
    at db/merge_test.cc:39
#1  0x00000000006123a4 in rocksdb::AssociativeMergeOperator::FullMergeV2 (this=0xebe410, merge_in=..., merge_out=0x7fffffffd1d0)
    at db/merge_operator.cc:62
#2  0x000000000060d3e4 in rocksdb::MergeHelper::TimedFullMerge (merge_operator=merge_operator@entry=0xebe410, key=...,
    value=value@entry=0x7fffffffd350, operands=..., result=0x7fffffffd9e0, logger=0xebd220, statistics=0x0,
    env=0xbc9340 <rocksdb::Env::Default()::default_env>, result_operand=0x0, update_num_ops_stats=true) at db/merge_helper.cc:81
#3  0x0000000000604b7f in rocksdb::SaveValue (arg=0x7fffffffd550, entry=<optimized out>) at db/memtable.cc:735
#4  0x00000000006a81ea in rocksdb::(anonymous namespace)::SkipListRep::Get (this=<optimized out>, k=..., callback_args=0x7fffffffd550,
    callback_func=0x604680 <rocksdb::SaveValue(void*, char const*)>) at memtable/skiplistrep.cc:77
#5  0x0000000000603c4f in rocksdb::MemTable::Get (this=0xed7150, key=..., value=0x7fffffffd9e0, s=s@entry=0x7fffffffd9d0,
    merge_context=merge_context@entry=0x7fffffffd680, range_del_agg=range_del_agg@entry=0x7fffffffd700, seq=0x7fffffffd670, read_opts=...,
    callback=0x0, is_blob_index=0x0) at db/memtable.cc:856
#6  0x0000000000580822 in Get (is_blob_index=0x0, callback=0x0, read_opts=..., range_del_agg=0x7fffffffd700, merge_context=0x7fffffffd680,
    s=0x7fffffffd9d0, value=<optimized out>, key=..., this=<optimized out>) at ./db/memtable.h:203
#7  rocksdb::DBImpl::GetImpl (this=0xec3730, read_options=..., column_family=<optimized out>, key=..., pinnable_val=0x7fffffffd920,
    value_found=0x0, callback=0x0, is_blob_index=0x0) at db/db_impl.cc:1163
#8  0x0000000000580fb7 in rocksdb::DBImpl::Get (this=<optimized out>, read_options=..., column_family=<optimized out>, key=...,
    value=<optimized out>) at db/db_impl.cc:1098
#9  0x0000000000517da5 in rocksdb::DB::Get (this=this@entry=0xec3730, options=..., column_family=0xed0800, key=...,
    value=value@entry=0x7fffffffd9e0) at ./include/rocksdb/db.h:335
#10 0x00000000005196bc in Get (value=0x7fffffffd9e0, key=..., options=..., this=0xec3730) at ./include/rocksdb/db.h:345
#11 Counters::get (this=this@entry=0x7fffffffde10, key=..., value=value@entry=0x7fffffffda68) at db/merge_test.cc:172
#12 0x0000000000519a5c in Counters::assert_get (this=this@entry=0x7fffffffde10, key=...) at db/merge_test.cc:209
#13 0x000000000051296f in (anonymous namespace)::testCounters (counters=..., db=0xec3730, test_compaction=test_compaction@entry=false)
    at db/merge_test.cc:280
#14 0x0000000000513c62 in (anonymous namespace)::runTest (argc=argc@entry=1, dbname=..., use_ttl=use_ttl@entry=false) at db/merge_test.cc:433
#15 0x000000000040ebe0 in main (argc=1) at db/merge_test.cc:510

```

```bash
#0  rocksdb::AssociativeMergeOperator::FullMergeV2 (this=0xebe410, merge_in=..., merge_out=0x7fffffffd1d0) at db/merge_operator.cc:68
#1  0x000000000060d3e4 in rocksdb::MergeHelper::TimedFullMerge (merge_operator=merge_operator@entry=0xebe410, key=..., value=value@entry=0x0,
    operands=..., result=0x7fffffffd9e0, logger=0xebd220, statistics=0x0, env=0xbc9340 <rocksdb::Env::Default()::default_env>,
    result_operand=0x0, update_num_ops_stats=true) at db/merge_helper.cc:81
#2  0x0000000000604e2f in rocksdb::SaveValue (arg=0x7fffffffd550, entry=<optimized out>) at db/memtable.cc:757
#3  0x00000000006a81ea in rocksdb::(anonymous namespace)::SkipListRep::Get (this=<optimized out>, k=..., callback_args=0x7fffffffd550,
    callback_func=0x604680 <rocksdb::SaveValue(void*, char const*)>) at memtable/skiplistrep.cc:77
#4  0x0000000000603c4f in rocksdb::MemTable::Get (this=0xed7150, key=..., value=0x7fffffffd9e0, s=s@entry=0x7fffffffd9d0,
    merge_context=merge_context@entry=0x7fffffffd680, range_del_agg=range_del_agg@entry=0x7fffffffd700, seq=0x7fffffffd670, read_opts=...,
    callback=0x0, is_blob_index=0x0) at db/memtable.cc:856
#5  0x0000000000580822 in Get (is_blob_index=0x0, callback=0x0, read_opts=..., range_del_agg=0x7fffffffd700, merge_context=0x7fffffffd680,
    s=0x7fffffffd9d0, value=<optimized out>, key=..., this=<optimized out>) at ./db/memtable.h:203
#6  rocksdb::DBImpl::GetImpl (this=0xec3730, read_options=..., column_family=<optimized out>, key=..., pinnable_val=0x7fffffffd920,
    value_found=0x0, callback=0x0, is_blob_index=0x0) at db/db_impl.cc:1163
#7  0x0000000000580fb7 in rocksdb::DBImpl::Get (this=<optimized out>, read_options=..., column_family=<optimized out>, key=...,
    value=<optimized out>) at db/db_impl.cc:1098
#8  0x0000000000517da5 in rocksdb::DB::Get (this=this@entry=0xec3730, options=..., column_family=0xed0800, key=...,
    value=value@entry=0x7fffffffd9e0) at ./include/rocksdb/db.h:335
#9  0x00000000005196bc in Get (value=0x7fffffffd9e0, key=..., options=..., this=0xec3730) at ./include/rocksdb/db.h:345
#10 Counters::get (this=this@entry=0x7fffffffde10, key=..., value=value@entry=0x7fffffffda68) at db/merge_test.cc:172
#11 0x0000000000519a5c in Counters::assert_get (this=this@entry=0x7fffffffde10, key=...) at db/merge_test.cc:209
#12 0x0000000000512a1b in (anonymous namespace)::testCounters (counters=..., db=0xec3730, test_compaction=test_compaction@entry=false)
    at db/merge_test.cc:292
#13 0x0000000000513c62 in (anonymous namespace)::runTest (argc=argc@entry=1, dbname=..., use_ttl=use_ttl@entry=false) at db/merge_test.cc:433
#14 0x000000000040ebe0 in main (argc=1) at db/merge_test.cc:510

```



```bash

#0  (anonymous namespace)::UInt64AddOperator::Merge (this=0xec1500, existing_value=0x7fffffffd140, value=..., new_value=0x7fffffffd150,
    logger=0xebd220) at utilities/merge_operators/uint64add.cc:27
#1  0x00000000006123a4 in rocksdb::AssociativeMergeOperator::FullMergeV2 (this=0xebe410, merge_in=..., merge_out=0x7fffffffd1d0)
    at db/merge_operator.cc:62
#2  0x000000000060d3e4 in rocksdb::MergeHelper::TimedFullMerge (merge_operator=merge_operator@entry=0xebe410, key=..., value=value@entry=0x0,
    operands=..., result=0x7fffffffd9e0, logger=0xebd220, statistics=0x0, env=0xbc9340 <rocksdb::Env::Default()::default_env>,
    result_operand=0x0, update_num_ops_stats=true) at db/merge_helper.cc:81
#3  0x0000000000604e2f in rocksdb::SaveValue (arg=0x7fffffffd550, entry=<optimized out>) at db/memtable.cc:757
#4  0x00000000006a81ea in rocksdb::(anonymous namespace)::SkipListRep::Get (this=<optimized out>, k=..., callback_args=0x7fffffffd550,
    callback_func=0x604680 <rocksdb::SaveValue(void*, char const*)>) at memtable/skiplistrep.cc:77
#5  0x0000000000603c4f in rocksdb::MemTable::Get (this=0xed7150, key=..., value=0x7fffffffd9e0, s=s@entry=0x7fffffffd9d0,
    merge_context=merge_context@entry=0x7fffffffd680, range_del_agg=range_del_agg@entry=0x7fffffffd700, seq=0x7fffffffd670, read_opts=...,
    callback=0x0, is_blob_index=0x0) at db/memtable.cc:856
#6  0x0000000000580822 in Get (is_blob_index=0x0, callback=0x0, read_opts=..., range_del_agg=0x7fffffffd700, merge_context=0x7fffffffd680,
    s=0x7fffffffd9d0, value=<optimized out>, key=..., this=<optimized out>) at ./db/memtable.h:203
#7  rocksdb::DBImpl::GetImpl (this=0xec3730, read_options=..., column_family=<optimized out>, key=..., pinnable_val=0x7fffffffd920,
    value_found=0x0, callback=0x0, is_blob_index=0x0) at db/db_impl.cc:1163
#8  0x0000000000580fb7 in rocksdb::DBImpl::Get (this=<optimized out>, read_options=..., column_family=<optimized out>, key=...,
    value=<optimized out>) at db/db_impl.cc:1098
#9  0x0000000000517da5 in rocksdb::DB::Get (this=this@entry=0xec3730, options=..., column_family=0xed0800, key=...,
    value=value@entry=0x7fffffffd9e0) at ./include/rocksdb/db.h:335
#10 0x00000000005196bc in Get (value=0x7fffffffd9e0, key=..., options=..., this=0xec3730) at ./include/rocksdb/db.h:345
#11 Counters::get (this=this@entry=0x7fffffffde10, key=..., value=value@entry=0x7fffffffda68) at db/merge_test.cc:172
#12 0x0000000000519a5c in Counters::assert_get (this=this@entry=0x7fffffffde10, key=...) at db/merge_test.cc:209
#13 0x0000000000512a1b in (anonymous namespace)::testCounters (counters=..., db=0xec3730, test_compaction=test_compaction@entry=false)
    at db/merge_test.cc:292
#14 0x0000000000513c62 in (anonymous namespace)::runTest (argc=argc@entry=1, dbname=..., use_ttl=use_ttl@entry=false) at db/merge_test.cc:433
#15 0x000000000040ebe0 in main (argc=1) at db/merge_test.cc:510
```



### reference

1.  官方文档 <https://github.com/facebook/rocksdb/wiki/Merge-Operator>
2. 上面的一个翻译<https://www.jianshu.com/p/e13338a3f161>

看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。

