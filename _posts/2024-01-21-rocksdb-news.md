---
layout: post
title: 2024-0101-0121 rocksdb 社区新闻
categories: [database]
tags: [rocksdb]
---
最近搞了个rocksdb每周动态更新！网址在这里 https://wanghenshui.github.io/rocksdb-doc-cn/

每周的新改动也放博客一份 https://wanghenshui.github.io/rocksdb-doc-cn/commit/2024-01-21.html



`<!-- more -->`

一些java api增强/工具增强/代码cleanup就不列举了

- 正式发布9.0版本，新的一年 https://github.com/facebook/rocksdb/pull/12256
- PREFETCH_BYTES_USEFUL 有bug，修正 https://github.com/facebook/rocksdb/pull/12251
- CompressionOptions 支持secondary cache，https://github.com/facebook/rocksdb/pull/12234
- Fix bug in auto_readahead_size that returned wrong key  (https://github.com/facebook/rocksdb/pull/12229)

这个assert能抓到, 重构修改字段引入，遍历时对应的key没及时更新

把iter 遍历和parsekey放一起，封个函数

- Fix blob files not reclaimed after deleting all SSTs (https://github.com/facebook/rocksdb/pull/12235)

这个修改还是很简单的

```cpp
  void SaveBlobFilesTo(VersionStorageInfo* vstorage) const {
    assert(vstorage);

    assert(base_vstorage_);
    vstorage->ReserveBlob(base_vstorage_->GetBlobFiles().size() +
                          mutable_blob_file_metas_.size());

    const uint64_t oldest_blob_file_with_linked_ssts =
        GetMinOldestBlobFileNumber();

+    // If there are no blob files with linked SSTs, meaning that there are no
+    // valid blob files
+    if (oldest_blob_file_with_linked_ssts == kInvalidBlobFileNumber) {
+      return;
+    }
+
```

这种场景没考虑到，没这个判断，0也merge到meta里了导致有关联

- Detect compaction pressure at lower debt ratios (https://github.com/facebook/rocksdb/pull/12236)

这个是改这个GetPendingCompactionBytesForCompactionSpeedup这个效果

原来逻辑

```cpp
      } else if (vstorage->estimated_compaction_needed_bytes() >=
                 GetPendingCompactionBytesForCompactionSpeedup(
                     mutable_cf_options, vstorage)) {
        write_controller_token_ =
            write_controller->GetCompactionPressureToken();
        ROCKS_LOG_INFO(
            ioptions_.logger,
            "[%s] Increasing compaction threads because of estimated pending "
            "compaction "
            "bytes %" PRIu64,
            name_.c_str(), vstorage->estimated_compaction_needed_bytes());
      } else {
```

显然，GetPendingCompactionBytesForCompactionSpeedup越小，越能加速写入速度

```cpp
uint64_t GetPendingCompactionBytesForCompactionSpeedup(
    const MutableCFOptions& mutable_cf_options,
    const VersionStorageInfo* vstorage) {
  // Compaction debt relatively large compared to the stable (bottommost) data
  // size indicates compaction fell behind.
  const uint64_t kBottommostSizeDivisor = 8;
  // Meaningful progress toward the slowdown trigger is another good indication.
  const uint64_t kSlowdownTriggerDivisor = 4;

  uint64_t bottommost_files_size = 0;
  for (const auto& level_and_file : vstorage->BottommostFiles()) {
    bottommost_files_size += level_and_file.second->fd.GetFileSize();
  }

  // Slowdown trigger might be zero but that means compaction speedup should
  // always happen (undocumented/historical), so no special treatment is needed.
  uint64_t slowdown_threshold =
      mutable_cf_options.soft_pending_compaction_bytes_limit /
      kSlowdownTriggerDivisor;

  // Size of zero, however, should not be used to decide to speedup compaction.
  if (bottommost_files_size == 0) {
    return slowdown_threshold;
  }

  uint64_t size_threshold = bottommost_files_size / kBottommostSizeDivisor;
  return std::min(size_threshold, slowdown_threshold);
}

```

原来的算法，倒数第二行是乘法，改成除了，数字小一些。。。

这个值是怎么定的？就全凭经验感觉

- Fix a case of ignored corruption in creating backups (https://github.com/facebook/rocksdb/pull/12200)

以前的逻辑可能忽略了部分损坏的文件，这里直接强制报错

- Refactor FilePrefetchBuffer code (https://github.com/facebook/rocksdb/pull/12097)
- Fix and defend against FilePrefetchBuffer combined with mmap reads (https://github.com/facebook/rocksdb/pull/12206)

这俩是重构FilePrefetchBuffer 更多是可读性提升，数据结构没有大改
