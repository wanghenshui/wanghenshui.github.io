---
layout: post
title: sstdump出的数据和sstreader的数据不同 简单定位
categories: [database]
tags: [rocksdb]
---

TL;DR

sstreader的遍历用到了用户定义的comparetor，可能导致部分key被过滤了， sst_dump遍历用的迭代器没有这个问题

<!-- more -->

都是迭代器遍历，sst dump能拿到数据，但用sst reader遍历少key？

迭代器难道不相同？

代码分支 6.29.fb

## sst_file_dumper.cc

```cpp
Status SstFileDumper::ReadSequential(bool print_kv, uint64_t read_num,
                                     bool has_from, const std::string& from_key,
                                     bool has_to, const std::string& to_key,
                                     bool use_from_as_prefix) {
  if (!table_reader_) {
    return init_result_;
  }

  InternalIterator* iter = table_reader_->NewIterator(
      read_options_, moptions_.prefix_extractor.get(),
      /*arena=*/nullptr, /*skip_filters=*/false,
      TableReaderCaller::kSSTDumpTool);
  uint64_t i = 0;
  if (has_from) {
    InternalKey ikey;
    ikey.SetMinPossibleForUserKey(from_key);
    iter->Seek(ikey.Encode());
  } else {
    iter->SeekToFirst();
  }
  for (; iter->Valid(); iter->Next()) {
    Slice key = iter->key();
    Slice value = iter->value();
    ++i;
    if (read_num > 0 && i > read_num) break;

    ParsedInternalKey ikey;
    Status pik_status = ParseInternalKey(key, &ikey, true /* log_err_key */);
    if (!pik_status.ok()) {
      std::cerr << pik_status.getState() << "\n";
      continue;
    }

    // the key returned is not prefixed with out 'from' key
    if (use_from_as_prefix && !ikey.user_key.starts_with(from_key)) {
      break;
    }

    // If end marker was specified, we stop before it
    if (has_to && BytewiseComparator()->Compare(ikey.user_key, to_key) >= 0) {
      break;
    }

    if (print_kv) {
      if (!decode_blob_index_ || ikey.type != kTypeBlobIndex) {
        fprintf(stdout, "%s => %s\n",
                ikey.DebugString(true, output_hex_).c_str(),
                value.ToString(output_hex_).c_str());
      } else {
        BlobIndex blob_index;

        const Status s = blob_index.DecodeFrom(value);
        if (!s.ok()) {
          fprintf(stderr, "%s => error decoding blob index\n",
                  ikey.DebugString(true, output_hex_).c_str());
          continue;
        }

        fprintf(stdout, "%s => %s\n",
                ikey.DebugString(true, output_hex_).c_str(),
                blob_index.DebugString(output_hex_).c_str());
      }
    }
  }

  read_num_ += i;

  Status ret = iter->status();
  delete iter;
  return ret;
}
```

直接使用tabel reader iterator

## sst_file_reader.cc

```cpp
Iterator* SstFileReader::NewIterator(const ReadOptions& roptions) {
  auto r = rep_.get();
  auto sequence = roptions.snapshot != nullptr
                      ? roptions.snapshot->GetSequenceNumber()
                      : kMaxSequenceNumber;
  ArenaWrappedDBIter* res = new ArenaWrappedDBIter();
  res->Init(r->options.env, roptions, r->ioptions, r->moptions,
            nullptr /* version */, sequence,
            r->moptions.max_sequential_skip_in_iterations,
            0 /* version_number */, nullptr /* read_callback */,
            nullptr /* db_impl */, nullptr /* cfd */,
            true /* expose_blob_index */, false /* allow_refresh */);
  auto internal_iter = r->table_reader->NewIterator(
      res->GetReadOptions(), r->moptions.prefix_extractor.get(),
      res->GetArena(), false /* skip_filters */,
      TableReaderCaller::kSSTFileReader);
  res->SetIterUnderDBIter(internal_iter);
  return res;
}

```
可以看到，走的是DBIter的逻辑，内部使用的table reader的iterator

```cpp

void DBIter::Next() {
  assert(valid_);
  assert(status_.ok());

  PERF_CPU_TIMER_GUARD(iter_next_cpu_nanos, clock_);
  // Release temporarily pinned blocks from last operation
  ReleaseTempPinnedData();
  local_stats_.skip_count_ += num_internal_keys_skipped_;
  local_stats_.skip_count_--;
  num_internal_keys_skipped_ = 0;
  bool ok = true;
  if (direction_ == kReverse) {
    is_key_seqnum_zero_ = false;
    if (!ReverseToForward()) {
      ok = false;
    }
  } else if (!current_entry_is_merged_) {
    // If the current value is not a merge, the iter position is the
    // current key, which is already returned. We can safely issue a
    // Next() without checking the current key.
    // If the current key is a merge, very likely iter already points
    // to the next internal position.
    assert(iter_.Valid());
    iter_.Next();
    PERF_COUNTER_ADD(internal_key_skipped_count, 1);
  }
...
}
```

能看到，多了个`ReverseToForward`，这个是干嘛的？

```cpp
bool DBIter::ReverseToForward() {
  assert(iter_.status().ok());

  // When moving backwards, iter_ is positioned on _previous_ key, which may
  // not exist or may have different prefix than the current key().
  // If that's the case, seek iter_ to current key.
  if (!expect_total_order_inner_iter() || !iter_.Valid()) {
    IterKey last_key;
    ParsedInternalKey pikey(saved_key_.GetUserKey(), kMaxSequenceNumber,
                            kValueTypeForSeek);
    if (timestamp_size_ > 0) {
      // TODO: pre-create kTsMax.
      const std::string kTsMax(timestamp_size_, '\xff');
      pikey.SetTimestamp(kTsMax);
    }
    last_key.SetInternalKey(pikey);
    iter_.Seek(last_key.GetInternalKey());
    RecordTick(statistics_, NUMBER_OF_RESEEKS_IN_ITERATION);
  }

  direction_ = kForward;
  // Skip keys less than the current key() (a.k.a. saved_key_).
  while (iter_.Valid()) {
    ParsedInternalKey ikey;
    if (!ParseKey(&ikey)) {
      return false;
    }
    if (user_comparator_.Compare(ikey.user_key, saved_key_.GetUserKey()) >= 0) {
      return true;
    }
    iter_.Next();
  }

  if (!iter_.status().ok()) {
    valid_ = false;
    return false;
  }

  return true;
}
```
可以看到用到了`user_comparator.Compare` 很有可能是这个导致的key被过滤了。检查代码确实如此。问题结束

---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>
