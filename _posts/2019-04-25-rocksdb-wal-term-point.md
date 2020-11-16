---
layout: post
categories: database
title: rocksdb 小知识 WalTerminationPoint
tags: [rocksdb, c++]
---
  

这个数据是在WriteBatch中的，和写WAL相关，数据结构是SavePoint

```c++
  // When sending a WriteBatch through WriteImpl we might want to
  // specify that only the first x records of the batch be written to
  // the WAL.
  SavePoint wal_term_point_;
```



```c++
struct SavePoint {
  size_t size;  // size of rep_
  int count;    // count of elements in rep_
  uint32_t content_flags;

  SavePoint() : size(0), count(0), content_flags(0) {}

  SavePoint(size_t _size, int _count, uint32_t _flags)
      : size(_size), count(_count), content_flags(_flags) {}

  void clear() {
    size = 0;
    count = 0;
    content_flags = 0;
  }

  bool is_cleared() const { return (size | count | content_flags) == 0; }
};
```



具体用法看这个测试用例，在db/fault_injection_test.cc

```c++
TEST_P(FaultInjectionTest, WriteBatchWalTerminationTest) {
  ReadOptions ro;
  Options options = CurrentOptions();
  options.env = env_;

  WriteOptions wo;
  wo.sync = true;
  wo.disableWAL = false;
  WriteBatch batch;
  batch.Put("cats", "dogs");
  batch.MarkWalTerminationPoint();
  batch.Put("boys", "girls");
  ASSERT_OK(db_->Write(wo, &batch));

  env_->SetFilesystemActive(false);
  NoWriteTestReopenWithFault(kResetDropAndDeleteUnsynced);
  ASSERT_OK(OpenDB());

  std::string val;
  ASSERT_OK(db_->Get(ro, "cats", &val));
  ASSERT_EQ("dogs", val);
  ASSERT_EQ(db_->Get(ro, "boys", &val), Status::NotFound());
}
```

能看到wal termination point 的作用，就是在WAL层的一层隔离，这个点之后的kv不写入wal，除非clear，从writebatch append能看出来

```c++
Status WriteBatchInternal::Append(WriteBatch* dst, const WriteBatch* src,
                                  const bool wal_only) {
  size_t src_len;
  int src_count;
  uint32_t src_flags;

  const SavePoint& batch_end = src->GetWalTerminationPoint();

  if (wal_only && !batch_end.is_cleared()) {
    src_len = batch_end.size - WriteBatchInternal::kHeader;
    src_count = batch_end.count;
    src_flags = batch_end.content_flags;
  } else {
    src_len = src->rep_.size() - WriteBatchInternal::kHeader;
    src_count = Count(src);
    src_flags = src->content_flags_.load(std::memory_order_relaxed);
  }

  SetCount(dst, Count(dst) + src_count);
  assert(src->rep_.size() >= WriteBatchInternal::kHeader);
  dst->rep_.append(src->rep_.data() + WriteBatchInternal::kHeader, src_len);
  dst->content_flags_.store(
      dst->content_flags_.load(std::memory_order_relaxed) | src_flags,
      std::memory_order_relaxed);
  return Status::OK();
}
```



### contact

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。

