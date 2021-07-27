---
layout: post
title: compaction到底怎么做？
categories: [database]
tags: [blobdb, titandb, fasterkv, rocksdb]
---



## blobdb

6.22之后的rocksdb重新实现了blobdb，很有意思

简单介绍blobdb的原理 wisckey<sup>1</sup>

>WiscKey设计的4个idea:
>
>- kv分离，只有key在LSM树上
>- 在kv分离后，value是不做保序的，因此范围查询中，value的读取是随机io，为了解决这个问题，WiscKey利用了SSD磁盘并行随机读的特点
>- 使用crash-consistency 和 garbage-collection 方法管理value数据
>- 移除LSM树的log，并且不牺牲一致性
>
>**kv分离**
>
>**LSM的性能开销主要发生在compaction阶段**，**compaction只需要排序key，value可以单独管理**
>**因为key的大小一般会远小于value，分开管理后，在做compaction时，可以极大减少读取的数据量**
>**kv分离后，在做compaction时，写入的新的SST文件不包含具体的value，这样SST文件的size也比较小，这降低了写放大**
>
>**WiscKey的value也是append-only的，即value也是顺序写**
>
>**删除key时，只需要将key在LSM中删除，而vlog不需要改动**
>
>**vlog有效的数据，LSM中的key有记录，无效的value，等待垃圾回收就好**
>
>kv分离要点如下：
>
>- key存在LSM中
>- value存在单独的vlog中
>- 插入/更新数据的时候，首先将value append到vlog，然后将key插入LSM中
>- 删除数据的时候，只是将key在LSM中删除，vlog的数据不需要改变，因为wisckey会有垃圾回收机制处理对应的value
>- 读取数据时，先读LSM树，然后读vlog
>
> **挑战** 1**范围查询** **解决方法：value预取**
>
>1. 对于每个在迭代器上的Next或者Prev请求，WiscKey会认为这是范围查询的开始
>2. WiscKey会先将一部分key从LSM中读入，然后这些key对应的value的地址会放到一个队列中
>3. 后台的多个线程会从队列中获取value的地址，然后并行读取value的值
>
>**挑战2 垃圾回收，以及如何避免在垃圾回收过程中，系统故障导致的数据丢失？**
>
>vlog是append only 的，结构是ksize+vsize+key+value 拼出来的
>
>有线程在后台扫
>
>> 垃圾回收线程将从tail指向的位置开始，每次读取一个chunk的数据(比如几MB), 对于chunk中的每一个value_entry在LSM中查找以便判断该value_entry是否仍然有效。如果有效则将该数据append到head指针指向的位置，**并且需要更新LSM的kv记录(因为value的地址已经变了)**。如果无效，则将其舍弃。
>
>WiscKey通过保证在回收vlog的空间之前，确保新的value和tail记录已经做了持久化。具体的步骤如下：
>
>1. 按照上述说的步骤做垃圾回收，然后对vlog做fsync(),这个过程中即使系统crash，也不会对系统的数据稳定性造成影响，无非是复制一些数据到head指向的位置
>2. 接着，更新LSM树中的相关key对应的新的value地址以及tail。tail也存储在LSM中，<‘‘tail’’, tail-vLog-offset>
>3. 在回收vlog旧的数据空间



这里看代码，简单过一下读写/垃圾回收流程, 没有delete

### 写

- `BlobDBImpl::Put`/`BlobDBImpl::PutUntil`
  - `BlobDBImpl::PutBlobValue`，构造writebatch
    - 如果设定了min_blob_size，小于这个值走rocksdb原来的流程
      - 如果设定了ttl，走特殊的writebatch构造` BlobIndex::EncodeInlinedTTL `-> `WriteBatchInternal::PutBlobIndex`
    - blob流程 `GetCompressedSlice`，如果设定了compress会压缩一下value `CompressBlock`
    - `BlobLogWriter::ConstructBlobHeader `构造一个blog header，格式是ksize+vsize+ttl+headercrc + blobcrc
    - `CheckSizeAndEvictBlobFiles`，如果设置了db_max_size会提前终止写入，这里还有个fifo的evict机制 ~~那数据不就丢了么~~
    - `SelectBlobFile/SelectBlobFileTTL`
      - 拿到blobfile (`open_non_ttl_file_`/`FindBlobFileLocked`)  `assert(!(*blob_file)->Immutable());` 能拿到就直接返回
      - `CreateBlobFileAndWriter`
        - `NewBlobFile`
          - `std::make_shared<BlobFile>`
          - `LogFlush`
        - `CheckOrCreateWriterLocked`
          - `bfile->log_writer_ = std::make_shared<BlobLogWriter>`
        - `WriteHeader`
        - `SetFileSize`
      - `RegisterBlobFile` 内部的blob_files_ map保存一份，blob_file_number <--> blobfile
    - `AppendBlob`
      - `CheckOrCreateWriterLocked` 这个上面有，拿到BlobLogWriter
      - `writer->EmitPhysicalRecord`根据BlobLogWriter来写数据
      - `BlobIndex::EncodeBlob(index_entry, bfile->BlobFileNumber(), blob_offset,  value.size(), bdb_options_.compression)` index_entry是构造成writebatch的value
    - 针对ttl的`ExtendExpirationRange` 先忽略
    - `CloseBlobFileIfNeeded` 文件超过设定大小就` CloseBlobFile`
    - `WriteBatchInternal::PutBlobIndex`构造writebatch，结束 kTypeBlobIndex
  - `db_->Write`
    - `WriteLevel0Table` ->  `BuildTable` 
      - `BlobFileBuilder -> CompactionIterator`
        - `ExtractLargeValueIfNeededImpl`
          - `blob_file_builder_->Add`



能看到sst文件和blob file number已经有了关联，这也是后面GC的切入点



### GC工作原理

依赖compaction listener的机制，在compaction阶段进行blob file文件判定

- BlobDBListenerGC::OnCompactionCompleted
  - ProcessCompactionJobInfo
    - 遍历CompactionJobInfo sst文件，来获取blob file number(这个是在之前的writebatch中放进去的)，判定blob file是否关联，进行标记
      - LinkSstToBlobFile LinkSstToBlobFileImpl LinkSstFile
      - UnlinkSstFromBlobFile
    - MarkUnreferencedBlobFilesObsolete
      - MarkBlobFileObsoleteIfNeeded 当版本低于flush版本且没有任何sst文件关联才会真正的`ObsoleteBlobFile`
        - `blob_file->GetImmutableSequence() < flush_sequence_ &&blob_file->GetLinkedSstFiles().empty()`
        - 这里的`ObsoleteBlobFile`只是做个标记，后面有timer任务来去删Obsolete的blob file

### 后台任务

- ReclaimOpenFiles //周期性关文件
- DeleteObsoleteFiles 清理obsolete_files_ (在ObsoleteBlobFile中添加)，判断对应的blob file不在snapshot中，就可以删了

- EvictExpiredFiles ->ObsoleteBlobFile
- SanityCheck  查ttl的，就打印一下blob file状态



## [Titan](https://github.com/tikv/titan.git)

官方有文档来[解释原理](https://pingcap.com/blog-cn/titan-design-and-implementation)

不同点在于hook的地方，通过eventlistener来传hook，以及存储的改动，titan作为rocksdb一个上层，没法做到blobdb那种writebatch层侵入，所以外观上看就是直接调用rocksdb，但是在flush做hook分离value

```c++
void BaseDbListener::OnFlushCompleted(DB* /*db*/,
                                      const FlushJobInfo& flush_job_info) {
  if (db_impl_->initialized()) {
    db_impl_->OnFlushCompleted(flush_job_info);
  }
}

void BaseDbListener::OnCompactionCompleted(
    DB* /* db */, const CompactionJobInfo& compaction_job_info) {
  if (db_impl_->initialized()) {
    db_impl_->OnCompactionCompleted(compaction_job_info);
  }
}
```



### GC

这个流程很像rocksdb的compaction流程

- OnCompactionCompleted/DeleteFilesInRanges  ---->>> MaybeScheduleGC/BGWorkGC/BackgroundCallGC
  - PopFirstFromGCQueue
    - BackgroundGC
      -  blob_file_set_->GetBlobStorage
      - blob_gc_picker->PickBlobGC(blob_storage.get())
      - blob_gc_job.Prepare();  blob_gc_job.Run();  blob_gc_job.Finish(); blob_gc->ReleaseGcFiles();
      - blob_gc->trigger_next()...   -> AddToGCQueue(blob_gc->column_family_handle()->GetID());
    - log_buffer.FlushBufferToLog();
    - LogFlush
  - MaybeScheduleGC

## Badger

这里有个[文档可以参考](https://nxwz51a5wp.feishu.cn/docs/doccnIDJP4vnYZANQADawXCgaZd#F7rKpp)



## 微软的 FASTER kv

之前[整理过](https://wanghenshui.github.io/2021/03/15/fasterkv.html#compact)

大概思路，遍历整个append log文件，把不变区的有效key，捞出来，放到最新的可变区，然后把地址对应的文件全truncate，根据文件来删，如果truncate恰好在文件中间，那这个文件还是会保留的

faster的compact不够灵活，如果支持compact range，相当于还要管理一个空洞地址，又复杂化了。这里需要做一点取舍



## RAMCloud

---

### 参考

1. https://zhuanlan.zhihu.com/p/369391792
2. blobdb源码分析 https://zhuanlan.zhihu.com/p/385826245
3. https://pingcap.com/blog-cn/titan-design-and-implementation
4. https://nxwz51a5wp.feishu.cn/docs/doccnIDJP4vnYZANQADawXCgaZd#F7rKpp
5. 


---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>
