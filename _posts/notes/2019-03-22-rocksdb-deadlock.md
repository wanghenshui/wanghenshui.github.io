---
layout: post
category : database
title: rocksdb delay write死锁
tags : [rocksdb, gcc]
---
{% include JB/setup %}

>场景 mongorocks配合rocksdb使用，版本5.1.2是内部分支，合入了一些改动和私有开发改动，这是前提



遇到了delaywrite hang问题，所有线程在blockawait等待主写leader，主写leader失效了或者reset了或者停了，真的需要delaywrite，比如卡在compaction或者flush，没有写入线程等等。下面分析一遍rocksdb社区中遇到的deadlock

这是rocksdb write stall列出的原因 <https://github.com/facebook/rocksdb/wiki/Write-Stalls>



这是delayWrite部分代码

```C++
  if (UNLIKELY(status.ok() && (write_controller_.IsStopped() ||
                               write_controller_.NeedsDelay()))) {
    PERF_TIMER_STOP(write_pre_and_post_process_time);
    PERF_TIMER_GUARD(write_delay_time);
    // We don't know size of curent batch so that we always use the size
    // for previous one. It might create a fairness issue that expiration
    // might happen for smaller writes but larger writes can go through.
    // Can optimize it if it is an issue.
    status = DelayWrite(last_batch_group_size_, write_options);
    PERF_TIMER_START(write_pre_and_post_process_time);
  }


...
// REQUIRES: mutex_ is held
// REQUIRES: this thread is currently at the front of the writer queue
Status DBImpl::DelayWrite(uint64_t num_bytes,
                          const WriteOptions& write_options) {
  uint64_t time_delayed = 0;
  bool delayed = false;
  {
    StopWatch sw(env_, stats_, WRITE_STALL, &time_delayed);
    uint64_t delay = write_controller_.GetDelay(env_, num_bytes);
    if (delay > 0) {
      if (write_options.no_slowdown) {
        return Status::Incomplete();
      }
      TEST_SYNC_POINT("DBImpl::DelayWrite:Sleep");

      mutex_.Unlock();
      // We will delay the write until we have slept for delay ms or
      // we don't need a delay anymore
      const uint64_t kDelayInterval = 1000;
      uint64_t stall_end = sw.start_time() + delay;
      while (write_controller_.NeedsDelay()) {
        if (env_->NowMicros() >= stall_end) {
          // We already delayed this write `delay` microseconds
          break;
        }

        delayed = true;
        // Sleep for 0.001 seconds
        env_->SleepForMicroseconds(kDelayInterval);
      }
      mutex_.Lock();
    }

    while (bg_error_.ok() && write_controller_.IsStopped()) {
      if (write_options.no_slowdown) {
        return Status::Incomplete();
      }
      delayed = true;
      TEST_SYNC_POINT("DBImpl::DelayWrite:Wait");
      bg_cv_.Wait();
    }
  }
  assert(!delayed || !write_options.no_slowdown);
  if (delayed) {
    default_cf_internal_stats_->AddDBStats(InternalStats::WRITE_STALL_MICROS,
                                           time_delayed);
    RecordTick(stats_, STALL_MICROS, time_delayed);
  }

  return bg_error_;
}
```



`分析社区的issue和合入日志`

**#pr 4475<sup>1</sup> 和主写阻塞现象有点像**

分析了这个pr，解决的问题主要是针对write option是no  slowdown的，单独设置一下，保证当前write stall不要阻塞设置no slowdown的writer（直接返回status incomplete）Fix corner case where a write group leader blocked due to write stall blocks other writers in queue with WriteOptions::no_slowdown set. 主写stall住还是无法确定

这个改动也挺好玩的，见参考链接<sup>2</sup>

**#issue 1297<sup>3</sup> delaywrite deadlock**

这个issue是cockroachdb遇到的（这个db有机会翻翻代码研究下）

具体版本是4.9之前，使用eventlisener会有死锁的问题。根本原因在于内部没解锁导致的死锁

```c++
+	c->ReleaseCompactionFiles(status);
+	*made_progress = true;
	NotifyOnCompactionCompleted(
        c->column_family_data(), c.get(), status, 
        compaction_job_stats, job_context->job_id);        
-	c->ReleaseCompactionFiles(status);	
-	*made_progress = true;
```



后面还有不恰当配置 `max_background_compactions=0`导致的wait, 不再赘述

**#pr 1884<sup>4</sup> 如果没有bg work 优化sleep时间**

这个改动是优化delaywrite逻辑。当没有bg work的时候，也就是bg_compaction_scheduled_ bg_flush_scheduled_等为0就会sleep一段时间，然后进入wait，假如这段时间write_controller可以工作了，还在sleep就不太应该，改成sleep单位时间，每次重新判断条件。这个改动和deadlock无关。

注意，这里测量 write_stall_rate的方法。是个好手段

```bash
# fillrandom
# memtable size = 10MB
# value size = 1 MB
# num = 1000
# use /dev/shm
./db_bench --benchmarks="fillrandom,stats" --value_size=1048576 --write_buffer_size=10485760 --num=1000 --delayed_write_rate=XXXXX  --db="/dev/shm/new_stall" | grep "Cumulative stall"
```



**#issue 1235 hit write stall<sup> 5</sup>**  

这个issue提到的现象和遇到的完全一致。但是无法定位。

**#pr 4615<sup>6</sup> 避免manual flush意外错误造成的wait hang**

这个优化是在WaitUntilFlushWouldNotStallWrites基础上的，如果bgworkstopped，有错误的话（比如db只读，肯定会错误），这次处理就返回，不stall wait。否则后台由于错误永远不触发，就会永远hang在这里。由于项目用的代码没有这个优化，理论上不会有这个问题

**#pr 4611<sup>7</sup> 避免manual compaction在只读模式下造成的hang**

这个错误没看懂怎么就hang了，貌似是shared_ptr没释放导致的？这里以后记得研究一下

**#pr 3923<sup>8</sup> enable_pipelined_write=true可能死锁 15.0修复**

这个也是锁两次了，在外部解锁就可以。这个问题db_bench也会遇到

**#pr 4751<sup>9</sup> file-ingest-trgger flush导致deadlock 17.2修复**

这个也是WaitUntilFlushWouldNotStallWrites引入的deadlock，进入了writestall WaitForIngestFile 有个**#issue 5007<sup>10</sup>** 解决方法就是让ingestfile跳过writestall

**#pr 1480<sup>11</sup> IngestExternalFile 导致deadlock**

这个原理没有看懂，以后有时间分析一下测试的代码<https://github.com/facebook/rocksdb/pull/1480/files>

**#commit 6ea41f852708cf09d861894d33e1b65cd1d81c45 Fix deadlock when trying update options when write stalls<sup>12</sup>**

这个就是防止write stall期间改动option造成triger混乱 加了个NeedFlushOrCompaction



遇到的问题还在分析中，也有可能不是rocksdb的原因。

看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。

### 参考

1. https://github.com/facebook/rocksdb/pull/4475
2. <https://github.com/facebook/rocksdb/blob/master/db/db_impl_write.cc#L1242>
3. <https://github.com/facebook/rocksdb/issues/1297>
4. <https://github.com/facebook/rocksdb/pull/1884>
5. https://github.com/facebook/rocksdb/issues/1235
6. <https://github.com/facebook/rocksdb/pull/4615>
7. <https://github.com/facebook/rocksdb/pull/4611/>
8. <https://github.com/facebook/rocksdb/pull/3923>
9. <https://github.com/facebook/rocksdb/pull/4751>
10. <https://github.com/facebook/rocksdb/issues/5007>
11. <https://github.com/facebook/rocksdb/pull/1480>
12. <https://github.com/facebook/rocksdb/commit/6ea41f852708cf09d861894d33e1b65cd1d81c45>



