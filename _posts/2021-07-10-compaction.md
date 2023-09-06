---
layout: post
title: KV分离 compaction GC 到底怎么做？
categories: [database]
tags: [lsm,hashtable,blobdb, titandb, fasterkv, rocksdb, terarkdb, wisckey, Bourbon, badger, ramcloud]
---

[toc]

<!-- more -->

## wisckey<sup>1</sup>原理

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



## blobdb

6.22之后的rocksdb重新实现了blobdb，很有意思

这里看代码，简单过一下读写/垃圾回收流程, 没有delete

注意这是6.22版本，新版本应该实现了根据空洞率重写log

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



能看到这个GC仅仅是判断是否关联，有关联才会去真正的删除，也不会重写blob file



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
        - BlobGCJob::DoRunGC()
      - blob_gc->trigger_next()...   -> AddToGCQueue(blob_gc->column_family_handle()->GetID());
    - log_buffer.FlushBufferToLog();
    - LogFlush
  - MaybeScheduleGC



> - GC 选择了一些 candidates，当 discardable size 达到一定比例之后再 GC。使用 Sample 算法，随机取  BlobFile 中的一段数据 A，计其大小为 a，然后遍历 A 中的 key，累加过期的 key 所在的 blob record 的 size 计为 d，最后计算得出 d 占 a 比值 为 r，如果 r >= discardable_ratio 则对该 BlobFile 进行  GC，否则不对其进行 GC。如果 discardable size 占整个 BlobFile 数据大小的比值已经大于或等于  discardable_ratio 则不需要对其进行 Sample

也是评估空洞率，和badger一个思路

但是sample算法我没有看到，这个点子可以参考一下

这里是否可以引入learned index来学习一下方便gc？

## [Badger](https://github.com/dgraph-io/badger)

这里有个[文档可以参考](https://nxwz51a5wp.feishu.cn/docs/doccnIDJP4vnYZANQADawXCgaZd#F7rKpp)

大部分资料都是介绍kv分离降低写放大 以及value压缩delta encoding之类的优点，没说过具体是怎么管理GC的。还是得自己看代码

### update

- `func (db *DB) Update(fn func(txn *Txn) error) ` 这个update是入口，但具体的set要塞到txn里
  - `txn.Set` `txn.SetEntry` 构造NewEntry，然后`func (txn *Txn) modify(e *Entry)` 塞到pendingWrites里
  - func (txn *Txn) Commit()
    - `func (txn *Txn) commitAndSend()`
    - `func (db *DB) sendToWriteCh(entries []*Entry) (*request, error)`  发给db.writeCh
    - `func (db *DB) doWrites(lc *z.Closer)`
    - `func (db *DB) writeRequests(reqs []*request)`
      - `db.vlog.write(reqs)`，这里已经把reqs的指针更新好，传给writeLSM
        - curlf.doneWriting
      - `func (db *DB) writeToLSM(b *request) `
        - 根据valueThreshold来判定是否写value还是写value指针，走db.mt.Put

### RunValueLogGC

单独提供了ValueLogGC的API

Size API会返回lsm的大小和Vlog的大小，可以根据这个数据比例来调用ValueLogGC(ratio)

简单流程

- func (vlog *valueLog) runGC(discardRatio float64)
  - lf := vlog.pickLog(discardRatio) 这个会根据discardStatus信息来选一个文件做compact，discardstatus信息如何更新？doCompact
    -  discardRatio * float64(fi.Size()) 和 discardStatus记录的discard 比较
  - vlog.doRunGC(lf)
    - func (vlog *valueLog) rewrite(f *logFile)
      - 逻辑就是反查 lsm，根据valuepointer来判定这个value在不在这个vlog上，然后重写
      - vlog.filesToBeDeleted或者 vlog.deleteLogFile(f)
    - 更新discardStatus

discardStatus更新

- doCompact
  - runCompactDef
    - compactBuildTables
      - func (s *levelsController) subcompact
        - s.kv.vlog.updateDiscardStats(discardStats)



badger的GC是根据空洞率来决定的，外部指定淘汰比例，然后算该空洞率是否满足，然后进行重写文件

我在[这里看到一个分析](https://shimingyah.github.io/2019/08/BadgerDB%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90%E4%B9%8Bvlog%E8%AF%A6%E8%A7%A3/) 已经比较老了，思路是random pick，有几个判定标准

> - 遍历时间超过10S。
> - 遍历entry数超过`ValueLogMaxEntries * 1%`。
> - 遍历entry总大小超过vlog文件大小的`10%`。
>
> GC阈值：
>
> - 遍历entry数大于`ValueLogMaxEntries * 1%`。
> - 遍历entry总大小超过vlog文件大小的`0.075`
> - 删除比例超过设置的`discardRatio`。

这里的遍历时长限制和遍历entry限制感觉算是个好点子。可以留作优化项。可能random还是过于玄乎了吧，不如实打实计算metric收益稳定

我看commit消息 

> Value log would now no longer grow indefinitely, because of the shift to MemTable WAL.

貌似已经改回rocksdb那套方案了，而不是靠vlog保持崩溃一致性(猜的，没验证)

### discard信息持久化

承上，更新逻辑

```go
func (vlog *valueLog) updateDiscardStats(stats map[uint32]int64) {
	if vlog.opt.InMemory {
		return
	}
	for fid, discard := range stats {
		vlog.discardStats.Update(fid, discard)
	}
}
```

这个更新，全局共用一个mmap文件，文件名就叫DISCARD 这是用mmap当成map/数组来用了，（数组也是一种map）



```go
func InitDiscardStats(opt Options) (*discardStats, error) {
	fname := filepath.Join(opt.ValueDir, discardFname)

	// 1GB file can store 67M discard entries. Each entry is 16 bytes. fid 8 + discard 8
	mf, err := z.OpenMmapFile(fname, os.O_CREATE|os.O_RDWR, 1<<20)
	lf := &discardStats{
		MmapFile: mf,
		opt:      opt,
	}
	if err == z.NewFile {
		// We don't need to zero out the entire 1GB. 就前面两个entry清空了
		lf.zeroOut()
	} else if err != nil {
		return nil, y.Wrapf(err, "while opening file: %s\n", discardFname)
	}

	for slot := 0; slot < lf.maxSlot(); slot++ {
		if lf.get(16*slot) == 0 {
			lf.nextEmptySlot = slot
			break
		}
	}
	sort.Sort(lf)
	return lf, nil
}
```

更新和查找就简单了

```go
// Update would update the discard stats for the given file id. If discard is
// 0, it would return the current value of discard for the file. If discard is
// < 0, it would set the current value of discard to zero for the file.
func (lf *discardStats) Update(fidu uint32, discard int64) int64 {
	fid := uint64(fidu)
	lf.Lock()
	defer lf.Unlock()

	idx := sort.Search(lf.nextEmptySlot, func(slot int) bool {
		return lf.get(slot*16) >= fid
	})
	if idx < lf.nextEmptySlot && lf.get(idx*16) == fid {
		off := idx*16 + 8
		curDisc := lf.get(off)
		if discard == 0 {
			return int64(curDisc)
		}
		if discard < 0 {
			lf.set(off, 0)
			return 0
		}
		lf.set(off, curDisc+uint64(discard))
		return int64(curDisc + uint64(discard))
	}
	if discard <= 0 {
		// No need to add a new entry.
		return 0
	}

	// Could not find the fid. Add the entry.
	idx = lf.nextEmptySlot
	lf.set(idx*16, uint64(fid))
	lf.set(idx*16+8, uint64(discard))

	// Move to next slot.
	lf.nextEmptySlot++
	for lf.nextEmptySlot >= lf.maxSlot() {
		y.Check(lf.Truncate(2 * int64(len(lf.Data))))
	}
	lf.zeroOut()

	sort.Sort(lf)
	return int64(discard)
}

func (lf *discardStats) Iterate(f func(fid, stats uint64)) {
	for slot := 0; slot < lf.nextEmptySlot; slot++ {
		idx := 16 * slot
		f(lf.get(idx), lf.get(idx+8))
	}
}

// MaxDiscard returns the file id with maximum discard bytes.
func (lf *discardStats) MaxDiscard() (uint32, int64) {
	lf.Lock()
	defer lf.Unlock()

	var maxFid, maxVal uint64
	lf.Iterate(func(fid, val uint64) {
		if maxVal < val {
			maxVal = val
			maxFid = fid
		}
	})
	return uint32(maxFid), int64(maxVal)
}
```

两个问题

1. 大锁
2. 全局一个对象



## [TerarkDB](https://github.com/bytedance/terarkdb)

其实也是wisckey的一个实现，但是做了很多魔改，比如调优compaction，给sst文件加了个额外的信息，叫amap

然后针对amap以及其他数据增加了新的数据结构以及对应这个数据结构的快速压缩方法。加速了lz4?

[这里有片博客介绍的不错，简单搬过来](https://cloud.tencent.com/developer/news/603133)

compaction优化

Adaptive Map，虚拟sst，评估compact程度

- 大的 Compaction 策略上，继承了 RocksDB 的 Level Compaction（Universal Compaction 也可以支持，看场景需要，默认是 Level Compaction）
- 当需要进行 Compaction 的时候，会首选构建 Adaptive Map，将候选的几个 SST 构成一个逻辑上的新 SST（如上图所示）
- Amap 中会切分出多个不同的重叠段，R1、R2、R3、R4、R5，这些重叠段的重叠度会被追踪记录
- 后台的 GC 线程会优先选择那些重叠度更好的层进行 GC，通过这种手段，我们可以让 GC 更有效率，即写放大远低于默认的情况

这等于让sst多了一些信息，对于l0的compact来说，这个信息比较重要。其他层基本没有重叠信息，只有tombstone, 也有收益么？另外，这个想法好像有点类似FAST21-REMIX，那个是scan加速保存sst范围信息，这个信息，也可以用在compaction上

对于wisckey实现程度，做了个简单对比，这个表[搬运自这里](https://bytedance.feishu.cn/docs/doccnZmYFqHBm06BbvYgjsHHcKc#)

|                    | **WiscKey**                                                  | **TitanDB**                                                  | **TerarkDB **                                                |
| ------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 分离策略 | Always Seprate                                               | Value Size Ratio                                             | Value Size Ratio                                             |
| value存储      | vLOG (rotation log)                                          | Blob File和vlog差不多                                        | Original SST Format                                          |
| Get                | 1) Key → VLOG Position 2) VLOG Position → Value              | 1) Key → FileNumber + Handle  2) FileNumber → Blob  3) Blob + Handle → Value | 1) Key → FileNumber 2) FileNumber → SST 3) SST + Key → Value |
| Scan 代价         | Slower than LevelDB Support Prefetch                         | prefetch支持     | 不确定 |
| GC                 | 1) Pop out vLOG's oldest values and check if its valid 2) Re-write all valid data into LSM again | 1) Pick a blob and check if its kv pairs are valid. 2) Re-write all valid keys into LSM and generate a new blob. | 1) Pick Value SSTs and check its KV validation 2) Generate new KV SST, do not need to re-write old keys into LSM |
| GC 效率      | Rotation could be very slow and WA is not so good.           | Always pick the most urgent blob, better but slow need to re-write LSM | Comparing with TItanDB, do not need to re-write LSM          |

实现思路和titan基本一致，也是利用事件监听器

这里有一点，提到了scan的效率问题，没有用到prefetch, 我看最新的rocksdb是用上了prefetch的

另外，由于amap带来的收益，可以对真正的 GC 操作进行延迟到负载较低的时候进行，how？rocksdb的WriteController

其他基本上和titan没差，这里不看了

## 微软的 FASTER kv

之前[整理过](https://wanghenshui.github.io/2021/03/15/fasterkv.html#compact)

大概思路，遍历整个append log文件，把不变区的有效key，捞出来，放到最新的可变区，然后把地址对应的文件全truncate，根据文件来删，如果truncate恰好在文件中间，那这个文件还是会保留的

faster的compact不够灵活，如果支持compact range，相当于还要管理一个空洞地址，且删掉文件。如果不删文件的话倒是比较简单，但是违背了compact的初衷



## RAMCloud

之前[整理过](https://wanghenshui.github.io/2021/06/30/ramcloud.html#compact)

思路是总结访问记录，segmentManager记录访问，根据metric来做compact，支持内存/磁盘使用固定比率和删除key的比率两种方案

其实compact文件的过程也是把key捞出来重新放到hastable里，主要是有个挑选文件的过程，且，文件不是整体的，空洞也没关系，删掉就完了。针对挑选有很多种策略



## Scan相关

几个问题

1. 上面提到了scan的优化策略，prefetch，如何做prefetch？

简单列一下titan的prefetch，就是确定是否加载value，给个option指引，在scan的时候同时把value加载到缓存里，这样才比得过rocksdb

- GetBlobValueImpl
  -  storage_->NewPrefetcher
    -  file_cache_->NewPrefetcher
      - new BlobFilePrefetcher
    - prefetcher->Get
      - reader_->file_->Prefetch
        - readahead

2. FAST21-REMIX提到的scan优化方案，就是存sst的范围信息，能结合到wisckey上吗？把blob file的信息也索引上。感觉收益不大

3. 根据[VLDB'17: Fast Scans on Key-Value Stores](https://zhuanlan.zhihu.com/p/393773578)的思路，在scan阶段可以做GC，考虑收益
4. 根据[OSDI20 - Bourbon: Learned Index for LSM](https://zhuanlan.zhihu.com/p/277979207)learned index是否有助于GC？

## 空洞信息持久化？

bagder有discard信息

terarkdb有amap来存

其他的没有

如果想要更灵活的compact，这个参数是要导出来的

## 总结

总的compact思路

- 如果可以，多线程加快读取速度
- 有信息metric，可以是文件访问次数指标get/delete，可以是记录的活key/死key数据，可以是内存key/磁盘key比率 通过指标来决定该文件做不做compact
- 每个文件都compact还是compact一个，也有个指标，compact key总数，可以对文件选择来逼近这个数字，也可以文件排序一个一个加，两种算法
- 文件的引用判定，比如和checkpoint有关系不能删之类的。(blobdb是最笨拙的有关联就不删，空洞就空洞，也不重写)

---

## 参考

1. https://zhuanlan.zhihu.com/p/369391792
2. blobdb源码分析 https://zhuanlan.zhihu.com/p/385826245
3. https://pingcap.com/blog-cn/titan-design-and-implementation
4. https://nxwz51a5wp.feishu.cn/docs/doccnIDJP4vnYZANQADawXCgaZd#F7rKpp
5.  一文带你看透基于LSM-tree的NoSQL系统优化方向 https://zhuanlan.zhihu.com/p/351241814 写的非常完善
6. https://zhuanlan.zhihu.com/p/381997271 这个有点乱单写的和5是差不多的


---


