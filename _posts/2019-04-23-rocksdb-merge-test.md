---
layout: post
categories : database
title: rocksdb merge_test 单测不过问题定位
tags : [rocksdb,c++]
---
  

背景，给key加了个字段，改写了了WriteBatch, 每组数据会重写，加这个字段。

问题就是mergetest不能过，具体未通过的代码片

```c++
  {
    std::cout << "Test merge in memtable... \n";
    size_t max_merge = 5;
    auto db = OpenDb(dbname, use_ttl, max_merge);
    MergeBasedCounters counters(db, 0);
    testCounters(counters, db.get(), compact);
    testSuccessiveMerge(counters, max_merge, max_merge * 2);
    testSingleBatchSuccessiveMerge(db.get(), 5, 7);
    DestroyDB(dbname, Options());
  }
```

其中，testSuccessiveMerge未通过，代码是这样的

```c++
void testSuccessiveMerge(Counters& counters, size_t max_num_merges,
                         size_t num_merges) {

  counters.assert_remove("z");
  uint64_t sum = 0;

  for (size_t i = 1; i <= num_merges; ++i) {
    resetNumMergeOperatorCalls();
    counters.assert_add("z", i);
    sum += i;

    if (i % (max_num_merges + 1) == 0) {
      assert(num_merge_operator_calls == max_num_merges + 1);
    } else {
      assert(num_merge_operator_calls == 0);
    }

    resetNumMergeOperatorCalls();
    assert(counters.assert_get("z") == sum);
    assert(num_merge_operator_calls == i % (max_num_merges + 1));
  }
}
```

 正常情况下，i=6的时候，会触发内部的merge，此时num_merge_operator_calls==6

测试代码逻辑：定义了MergeOperator，实际上assert_add调用是MergeBasedCounters::add, 里面调用了merge

```c++
  // mapped to a rocksdb Merge operation
  virtual bool add(const std::string& key, uint64_t value) override {
    char encoded[sizeof(uint64_t)];
    EncodeFixed64(encoded, value);
    Slice slice(encoded, sizeof(uint64_t));
    auto s = db_->Merge(merge_option_, key, slice);
...
  }
```

其实merge底层还是write，但是在内部会判断key是否存在，有seek get动作

我开始一直在在merge_test.cc中加各种打印，猜测是不是数据集的问题，排除，编了个原生的merge_test，然后gdb，

```gdb
watch num_merge_operator_calls=6
```

抓到了正常流程下的堆栈

```bash
#0  CountMergeOperator::Merge (this=0x7fffe0001320, key=..., existing_value=0x7fffffffc520, value=..., new_value=0x7fffffffc530,
    logger=0x7fffe00034b0) at db/merge_test.cc:44
#1  0x000000000060ded4 in rocksdb::AssociativeMergeOperator::FullMergeV2 (this=0x7fffe0001320, merge_in=..., merge_out=0x7fffffffc5b0)
    at db/merge_operator.cc:62
#2  0x0000000000608f74 in rocksdb::MergeHelper::TimedFullMerge (merge_operator=0x7fffe0001320, key=..., value=value@entry=0x7fffffffc730,
    operands=..., result=0x7fffffffcdb0, logger=0x7fffe00034b0, statistics=0x0, env=0xbb8260 <rocksdb::Env::Default()::default_env>,
    result_operand=0x0, update_num_ops_stats=true) at db/merge_helper.cc:81
#3  0x0000000000600877 in rocksdb::SaveValue (arg=0x7fffffffc930, entry=<optimized out>) at db/memtable.cc:709
#4  0x00000000006a369a in rocksdb::(anonymous namespace)::SkipListRep::Get (this=<optimized out>, k=..., callback_args=0x7fffffffc930,
    callback_func=0x6000c0 <rocksdb::SaveValue(void*, char const*)>) at memtable/skiplistrep.cc:77
#5  0x00000000005ff6df in rocksdb::MemTable::Get (this=0x7fffe0013a80, key=..., value=0x7fffffffcdb0, s=s@entry=0x7fffffffcd50,
    merge_context=merge_context@entry=0x7fffffffca60, range_del_agg=range_del_agg@entry=0x7fffffffcae0, seq=0x7fffffffca50, read_opts=...,
    callback=0x0, is_blob_index=0x0) at db/memtable.cc:830
#6  0x000000000057c8fb in Get (is_blob_index=0x0, callback=0x0, read_opts=..., range_del_agg=0x7fffffffcae0, merge_context=0x7fffffffca60,
    s=0x7fffffffcd50, value=<optimized out>, key=..., this=<optimized out>) at ./db/memtable.h:203
#7  rocksdb::DBImpl::GetImpl (this=0x7fffe0002510, read_options=..., column_family=<optimized out>, key=..., pinnable_val=0x7fffffffce90,
    value_found=0x0, callback=0x0, is_blob_index=0x0) at db/db_impl.cc:1145
#8  0x000000000057d067 in rocksdb::DBImpl::Get (this=<optimized out>, read_options=..., column_family=<optimized out>, key=...,
    value=<optimized out>) at db/db_impl.cc:1084
#9  0x00000000006652cd in Get (value=0x7fffffffcdb0, key=..., column_family=0x7fffe000e8b8, options=..., this=0x7fffe0002510)
    at ./include/rocksdb/db.h:335
#10 rocksdb::MemTableInserter::MergeCF (this=0x7fffffffd170, column_family_id=0, key=..., value=...) at db/write_batch.cc:1497
#11 0x000000000065e491 in rocksdb::WriteBatch::Iterate (this=0x7fffffffd910, handler=handler@entry=0x7fffffffd170) at db/write_batch.cc:479
#12 0x00000000006623cf in rocksdb::WriteBatchInternal::InsertInto (write_group=..., sequence=sequence@entry=21, memtables=<optimized out>,
    flush_scheduler=flush_scheduler@entry=0x7fffe0002e80, ignore_missing_column_families=<optimized out>, recovery_log_number=0,
    db=0x7fffe0002510, concurrent_memtable_writes=false, seq_per_batch=false) at db/write_batch.cc:1731
#13 0x00000000005c203c in rocksdb::DBImpl::WriteImpl (this=0x7fffe0002510, write_options=..., my_batch=<optimized out>,
    callback=callback@entry=0x0, log_used=log_used@entry=0x0, log_ref=0, disable_memtable=false, seq_used=0x0, batch_cnt=0,
    pre_release_callback=0x0) at db/db_impl_write.cc:309
#14 0x00000000005c24c1 in rocksdb::DBImpl::Write (this=<optimized out>, write_options=..., my_batch=<optimized out>) at db/db_impl_write.cc:54
#15 0x00000000005c2972 in rocksdb::DB::Merge (this=this@entry=0x7fffe0002510, opt=..., column_family=column_family@entry=0x7fffe000ebf0,
    key=..., value=...) at db/db_impl_write.cc:1501
#16 0x00000000005c2a2f in rocksdb::DBImpl::Merge (this=0x7fffe0002510, o=..., column_family=0x7fffe000ebf0, key=..., val=...)
    at db/db_impl_write.cc:33
#17 0x0000000000512ecd in rocksdb::DB::Merge (this=0x7fffe0002510, options=..., key=..., value=...) at ./include/rocksdb/db.h:312
#18 0x00000000005121f8 in MergeBasedCounters::add (this=<optimized out>, key=..., value=<optimized out>) at db/merge_test.cc:236
---Type <return> to continue, or q <return> to quit---
#19 0x000000000050eda0 in assert_add (value=18, key=..., this=0x7fffffffdda0) at db/merge_test.cc:214
#20 (anonymous namespace)::testCounters (counters=..., db=0x7fffe0002510, test_compaction=test_compaction@entry=false) at db/merge_test.cc:287
#21 0x0000000000510119 in (anonymous namespace)::runTest (argc=argc@entry=1, dbname=..., use_ttl=use_ttl@entry=false) at db/merge_test.cc:442
#22 0x000000000040ebc0 in main (argc=1) at db/merge_test.cc:508

```

最终会调用之前已经添加到db中的merge_operator，merge_test里的merge_operator长这个样子

```c++
class CountMergeOperator : public AssociativeMergeOperator {
 public:
  CountMergeOperator() {
    mergeOperator_ = MergeOperators::CreateUInt64AddOperator();
  }

  virtual bool Merge(const Slice& key,
                     const Slice* existing_value,
                     const Slice& value,
                     std::string* new_value,
                     Logger* logger) const override {
    assert(new_value->empty());
    ++num_merge_operator_calls;
    if (existing_value == nullptr) {
      new_value->assign(value.data(), value.size());
      return true;
    }
      ...
```

开始我还给gdb给merge加断点。触发的场景太多，还需要先断点testSuccessMerge，然后在断点merge，单步走也看不清楚，不熟悉流程。

所以只要捋顺清除为什么出问题的版本没走到调用get，调用merge_operator就可以了



开始调试出问题的merge_test，顺着正常流程的堆栈一步一步走，走到insertto都是正常的，走到mergeCF也能证明编码数据是没问题的，下面看为什么没有走Get

memtableinserter::mergeCF长这样 在write_batch.cc中

```c++
 virtual Status MergeCF(uint32_t column_family_id, const Slice& key,
                         const Slice& value) override {
    assert(!concurrent_memtable_writes_);
    // optimize for non-recovery mode
    ...

    Status ret_status;
    MemTable* mem = cf_mems_->GetMemTable();
    auto* moptions = mem->GetImmutableMemTableOptions();
    bool perform_merge = false;

    // If we pass DB through and options.max_successive_merges is hit
    // during recovery, Get() will be issued which will try to acquire
    // DB mutex and cause deadlock, as DB mutex is already held.
    // So we disable merge in recovery
    if (moptions->max_successive_merges > 0 && db_ != nullptr &&
        recovering_log_number_ == 0) {
      LookupKey lkey(key, sequence_);

      // Count the number of successive merges at the head
      // of the key in the memtable
      size_t num_merges = mem->CountSuccessiveMergeEntries(lkey);

      if (num_merges >= moptions->max_successive_merges) {
        perform_merge = true;
      }
    }

    if (perform_merge) {
      // 1) Get the existing value
      std::string get_value;

      // Pass in the sequence number so that we also include previous merge
      // operations in the same batch.
      SnapshotImpl read_from_snapshot;
      read_from_snapshot.number_ = sequence_;
      ReadOptions read_options;
      read_options.snapshot = &read_from_snapshot;

      auto cf_handle = cf_mems_->GetColumnFamilyHandle();
      if (cf_handle == nullptr) {
        cf_handle = db_->DefaultColumnFamily();
      }
      db_->Get(read_options, cf_handle, key, &get_value);
      Slice get_value_slice = Slice(get_value);

      // 2) Apply this merge
      auto merge_operator = moptions->merge_operator;
      assert(merge_operator);

      std::string new_value;

      Status merge_status = MergeHelper::TimedFullMerge(
          merge_operator, key, &get_value_slice, {value}, &new_value,
          moptions->info_log, moptions->statistics, Env::Default());

      if (!merge_status.ok()) {
        // Failed to merge!
        // Store the delta in memtable
        perform_merge = false;
      } else {
        // 3) Add value to memtable
        bool mem_res = mem->Add(sequence_, kTypeValue, key, new_value);
        if (UNLIKELY(!mem_res)) {
          assert(seq_per_batch_);
          ret_status = Status::TryAgain("key+seq exists");
          const bool BATCH_BOUNDRY = true;
          MaybeAdvanceSeq(BATCH_BOUNDRY);
        }
      }
    }

    if (!perform_merge) {
      // Add merge operator to memtable
      bool mem_res = mem->Add(sequence_, kTypeMerge, key, value);
      if (UNLIKELY(!mem_res)) {
        assert(seq_per_batch_);
        ret_status = Status::TryAgain("key+seq exists");
        const bool BATCH_BOUNDRY = true;
        MaybeAdvanceSeq(BATCH_BOUNDRY);
      }
    }

...
  }
```

 上面的不相关代码省略了，出问题的merge_test没走get，直接走的add，也就没有merge，这两个分支的关键点就是perform_merge的值，也就是`mem->CountSuccessiveMergeEntries`的值,  加了断点打印了一下，结果是0，所以问题进一步缩小，这个函数在memtable.cc 中，长这个样子

```c++
size_t MemTable::CountSuccessiveMergeEntries(const LookupKey& key) {
  Slice memkey = key.memtable_key();

  // A total ordered iterator is costly for some memtablerep (prefix aware
  // reps). By passing in the user key, we allow efficient iterator creation.
  // The iterator only needs to be ordered within the same user key.
  std::unique_ptr<MemTableRep::Iterator> iter(
      table_->GetDynamicPrefixIterator());
  iter->Seek(key.internal_key(), memkey.data());
  size_t num_successive_merges = 0;

  for (; iter->Valid(); iter->Next()) {
    const char* entry = iter->key();
    uint32_t key_length = 0;
    const char* iter_key_ptr = GetVarint32Ptr(entry, entry + 5, &key_length);
    if (!comparator_.comparator.user_comparator()->Equal(
            UserKeyFromRawInternalKey(iter_key_ptr, key_length),
            key.user_key())) {
      break;
    }

    const uint64_t tag = DecodeFixed64(iter_key_ptr + key_length - 8);
    ValueType type;
    uint64_t unused;
    UnPackSequenceAndType(tag, &unused, &type);
    if (type != kTypeMerge) {
      break;
    }

    ++num_successive_merges;
  }

  return num_successive_merges;
}
```

我加了断点，根本没有进循环，也就是说 iter->Valid()=false  到这里，已经很清晰了，就是SeekKey的问题，之前添加的字段这个Prefixiterator可能处理不了，需要预处理一下



这里又涉及到了一个非常恶心的问题，userkey internal key memkey区别到底在哪里

本身一个key Slice，会被Lookupkey重新编码一下，编码内部的memkey就是原来的key。internalkey是带上sequence number的memkey

理清这些概念，注意到背景，修改lookupkey初始化。因为进入mergeCf之前已经编码了要加的字段，lookupkey有加了一次，需要预处理一下。结束。

```gdb
#  删除断点
delete 5
# 单步调试想返回，需要提前record
record
reverse-next
record stop
```



### reference

1.  官方文档 <https://github.com/facebook/rocksdb/wiki/Merge-Operator>

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。

