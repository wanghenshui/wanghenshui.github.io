---
layout: post
category : database
title: db_bench测试rocksdb性能
tags : [rocksdb, gcc]
---
  

场景需要，测试rocksdb事务的性能

刚巧有个测试<sup>2</sup> <https://github.com/facebook/rocksdb/issues/4402>介绍了测试结果，准备按照issue中介绍的两个脚本测试一下，gist被墙了的绕过方法见参考链接<sup>1</sup>

执行脚本命令,**注意目录rdb的设置，脚本中会有rm 目录的命令**

测试环境，四核 Intel(R) Xeon(R) Gold 6161 CPU @ 2.20GHz

```bash
bash r.sh 10000000 60 32 4 ./rdb 0 ./db_bench
```

第一个脚本结果，我个人测试的结果完全不同

这是mack的结果

```bash
test server:
* database on /dev/shm
* 2 sockets, 24 CPU cores, 48 HW threads

legend:
* #thr - number of threads
* trx=n - no transaction
* trx=p - pessimistic transaction
* trx=o - optimistic transaction
* numbers are inserts per second

--- batch_size=1

- concurrent memtable disabled
#thr    trx=n   trx=p   trx=o
1       153571  113228  101439
2       193070  182455  137708
4       167229  182313  94811
8       250508  228031  93401
12      274251  250595  92256
16      272554  266545  93403
20      281737  276026  76885
24      287475  277981  70004
28      293445  284644  48552
32      299366  288134  43672
36      303224  292887  43047
40      304027  292000  43195
44      311686  299963  44173
48      317418  308563  48482

- concurrent memtable enabled
#thr    trx=n   trx=p   trx=o
1       152156  110235  101901
2       164778  161547  130980
4       228060  193945  116742
8       335001  311307  114802
12      401206  379568  100576
16      445484  419819  72979
20      465297  435283  45554
24      472754  451805  40381
28      490107  456741  40108
32      482851  467469  40179
36      487332  473892  39866
40      485026  457858  43587
44      481420  442169  42293
48      423738  427396  40346

--- batch_size=4

- concurrent memtable disabled
#thr    trx=n   trx=p   trx=o
1       37838   28709   19807
2       62955   48829   30995
4       84903   72286   31754
8       95389   91310   25169
12      95297   97581   18739
16      92296   91696   17574
20      94451   91210   17319
24      91072   89522   16920
28      91429   91015   17170
32      92991   90158   17424
36      92823   89044   17332
40      91854   88994   17099
44      91766   88434   16909
48      91335   89298   16720

- concurrent memtable enabled
#thr    trx=n   trx=p   trx=o
1       38368   28374   19783
2       63711   48045   31141
4       99853   81364   35032
8       163958  134011  28212
12      211083  175932  18142
16      243147  207610  17281
20      254355  224073  16908
24      275674  238600  16875
28      286050  247888  17215
32      281926  252813  17657
36      274349  249263  16830
40      275749  241185  16726
44      266127  234881  16506
48      267183  235147  16760

-- test script

numk=$1
totw=$2
val=$3
batch=$4
dbdir=$5
sync=$6

# sync, dbdir, concurmt, secs, dop

function runme {
  a_concurmt=$1
  a_dop=$2
  a_extra=$3

  thrw=$(( $totw / $a_dop ))
  echo $a_dop threads, $thrw writes per thread
  rm -rf $dbdir; mkdir $dbdir
  # TODO --perf_level=0

echo ./db_bench --benchmarks=randomtransaction --use_existing_db=0 --sync=$sync --db=$dbdir --wal_dir=$dbdir --disable_data_sync=0 --num=$numk --writes=$thrw --num_levels=6 --key_size=8 --value_size=$val --block_size=4096 --cache_size=$(( 20 * 1024 * 1024 * 1024 )) --cache_numshardbits=6 --compression_type=snappy --min_level_to_compress=3 --compression_ratio=0.5 --level_compaction_dynamic_level_bytes=true --bytes_per_sync=8388608 --cache_index_and_filter_blocks=0 --benchmark_write_rate_limit=0 --hard_rate_limit=3 --rate_limit_delay_max_milliseconds=1000000 --write_buffer_size=134217728 --max_write_buffer_number=16 --target_file_size_base=33554432 --max_bytes_for_level_base=536870912 --verify_checksum=1 --delete_obsolete_files_period_micros=62914560 --max_grandparent_overlap_factor=8 --max_bytes_for_level_multiplier=8 --statistics=0 --stats_per_interval=1 --stats_interval_seconds=60 --histogram=1 --allow_concurrent_memtable_write=$a_concurmt --enable_write_thread_adaptive_yield=$a_concurmt --memtablerep=skip_list --bloom_bits=10 --open_files=-1 --level0_file_num_compaction_trigger=4 --level0_slowdown_writes_trigger=12 --level0_stop_writes_trigger=20 --max_background_compactions=16 --max_background_flushes=7 --threads=$a_dop --merge_operator="put" --seed=1454699926 --transaction_sets=$batch $a_extra


./db_bench --benchmarks=randomtransaction --use_existing_db=0 --sync=$sync --db=$dbdir --wal_dir=$dbdir --disable_data_sync=0 --num=$numk --writes=$thrw --num_levels=6 --key_size=8 --value_size=$val --block_size=4096 --cache_size=$(( 20 * 1024 * 1024 * 1024 )) --cache_numshardbits=6 --compression_type=snappy --min_level_to_compress=3 --compression_ratio=0.5 --level_compaction_dynamic_level_bytes=true --bytes_per_sync=8388608 --cache_index_and_filter_blocks=0 --benchmark_write_rate_limit=0 --hard_rate_limit=3 --rate_limit_delay_max_milliseconds=1000000 --write_buffer_size=134217728 --max_write_buffer_number=16 --target_file_size_base=33554432 --max_bytes_for_level_base=536870912 --verify_checksum=1 --delete_obsolete_files_period_micros=62914560 --max_grandparent_overlap_factor=8 --max_bytes_for_level_multiplier=8 --statistics=0 --stats_per_interval=1 --stats_interval_seconds=60 --histogram=1 --allow_concurrent_memtable_write=$a_concurmt --enable_write_thread_adaptive_yield=$a_concurmt --memtablerep=skip_list --bloom_bits=10 --open_files=-1 --level0_file_num_compaction_trigger=4 --level0_slowdown_writes_trigger=12 --level0_stop_writes_trigger=20 --max_background_compactions=16 --max_background_flushes=7 --threads=$a_dop --merge_operator="put" --seed=1454699926 --transaction_sets=$batch $a_extra
}


for dop in 1 2 4 8 12 16 20 24 28 32 36 40 44 48 ; do
# for dop in 1 24 ; do
for concurmt in 0 1 ; do

fn=o.dop${dop}.val${val}.batch${batch}.concur${concurmt}.notrx
runme $concurmt $dop "" >& $fn
q1=$( grep ^randomtransaction $fn | awk '{ print $5 }' )

t=transaction_db
fn=o.dop${dop}.val${val}.batch${batch}.concur${concurmt}.pessim
runme $concurmt $dop --${t}=1 >& $fn
q2=$( grep ^randomtransaction $fn | awk '{ print $5 }' )

t=optimistic_transaction_db
fn=o.dop${dop}.val${val}.batch${batch}.concur${concurmt}.optim
runme $concurmt $dop --${t}=1 >& $fn
q3=$( grep ^randomtransaction $fn | awk '{ print $5 }' )

echo $dop mt${concurmt} $q1 $q2 $q3 | awk '{ printf "%s\t%s\t%s\t%s\t%s\n", $1, $2, $3, $4, $5 }'

done
done
```



这是我的结果, 很快就执行完了（我觉得有点奇怪，但没深究，好像是执行一定次数就结束）

```bash
thr     mt0/mt1 trx=n   trx=p   trx=o
1       mt0     78534   24291   43891
1       mt1     81411   38734   54249
2       mt0     104529  49916   75000
2       mt1     101522  57747   76335
4       mt0     88365   60000   49916
4       mt1     121212  72115   18850
8       mt0     77455   45714   47538
8       mt1     36577   57377   22810
12      mt0     72551   46367   47318
12      mt1     29761   14587   65359
16      mt0     64343   39376   47151
16      mt1     10551   38095   19448
20      mt0     69284   36057   45045
20      mt1     11947   45731   61037
24      mt0     63576   30573   42933
24      mt1     13655   37765   52401
28      mt0     58947   32520   43043
28      mt1     6090    8342    17598
32      mt0     50632   25827   30563
32      mt1     7158    16469   18223
36      mt0     44831   25069   33210
36      mt1     18172   10395   34090
40      mt0     43572   33613   27797
40      mt1     11500   30721   15612
44      mt0     50285   27865   26862
44      mt1     7251    10661   25821
48      mt0     43282   25668   32388
48      mt1     19223   25751   14239
```



可以看到数据完全是反常的，我反复执行多次都是这种现象，有时候还有**卡顿，hang住**

第二个脚本

 ```bash
numk=$1
secs=$2
val=$3
batch=$4
dbdir=$5
sync=$6
dbb=$7

# sync, dbdir, concurmt, secs, dop

function runme {
  a_concurmt=$1
  a_dop=$2
  a_extra=$3

  rm -rf $dbdir; mkdir $dbdir
  # TODO --perf_level=0

$dbb --benchmarks=randomtransaction --use_existing_db=0 --sync=$sync --db=$dbdir --wal_dir=$dbdir --num=$numk --duration=$secs --num_levels=6 --key_size=8 --value_size=$val --block_size=4096 --cache_size=$(( 20 * 1024 * 1024 * 1024 )) --cache_numshardbits=6 --compression_type=none --compression_ratio=0.5 --level_compaction_dynamic_level_bytes=true --bytes_per_sync=8388608 --cache_index_and_filter_blocks=0 --benchmark_write_rate_limit=0 --write_buffer_size=$(( 64 * 1024 * 1024 )) --max_write_buffer_number=4 --target_file_size_base=$(( 32 * 1024 * 1024 )) --max_bytes_for_level_base=$(( 512 * 1024 * 1024 )) --verify_checksum=1 --delete_obsolete_files_period_micros=62914560 --max_bytes_for_level_multiplier=8 --statistics=0 --stats_per_interval=1 --stats_interval_seconds=60 --histogram=1 --allow_concurrent_memtable_write=$a_concurmt --enable_write_thread_adaptive_yield=$a_concurmt --memtablerep=skip_list --bloom_bits=10 --open_files=-1 --level0_file_num_compaction_trigger=4 --level0_slowdown_writes_trigger=20 --level0_stop_writes_trigger=30 --max_background_jobs=8 --max_background_flushes=2 --threads=$a_dop --merge_operator="put" --seed=1454699926 --transaction_sets=$batch --compaction_pri=3 $a_extra
}

for dop in 1 2 4 8 16 24 32 40 48 ; do
for concurmt in 0 1 ; do

fn=o.dop${dop}.val${val}.batch${batch}.concur${concurmt}.notrx
runme $concurmt $dop "" >& $fn
q1=$( grep ^randomtransaction $fn | awk '{ print $5 }' )

t=transaction_db
fn=o.dop${dop}.val${val}.batch${batch}.concur${concurmt}.pessim
runme $concurmt $dop --${t}=1 >& $fn
q2=$( grep ^randomtransaction $fn | awk '{ print $5 }' )

t=optimistic_transaction_db
fn=o.dop${dop}.val${val}.batch${batch}.concur${concurmt}.optim
runme $concurmt $dop --${t}=1 >& $fn
q3=$( grep ^randomtransaction $fn | awk '{ print $5 }' )

echo $dop mt${concurmt} $q1 $q2 $q3 | awk '{ printf "%s\t%s\t%s\t%s\t%s\n", $1, $2, $3, $4, $5 }'

done
done
 ```

 执行到transaction-db ，线程数大于4就会卡死，前几个数据

```
1       mt0     61676   35118   43794
1       mt1     60019   35307   44344
2       mt0     98688   55459   70069
2       mt1     103991  59430   75082
```

执行命令<sup>4</sup> 查看堆栈信息

```bash
gdb -ex "set pagination 0" -ex "thread apply all bt" \
  --batch -p $(pidof db_bench)
```



```bash
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib64/libthread_db.so.1".
0x00007fa47568d6d5 in pthread_cond_wait@@GLIBC_2.3.2 () from /lib64/libpthread.so.0

Thread 5 (Thread 0x7fa46b5c3700 (LWP 14215)):
#0  0x00007fa47568d6d5 in pthread_cond_wait@@GLIBC_2.3.2 () from /lib64/libpthread.so.0
#1  0x00007fa47475f9ac in std::condition_variable::wait(std::unique_lock<std::mutex>&) () from /lib64/libstdc++.so.6
#2  0x000000000067e47c in std::condition_variable::wait<rocksdb::WriteThread::BlockingAwaitState(rocksdb::WriteThread::Writer*, uint8_t)::__lambda4> (__p=..., __lock=..., this=0x7fa46b5c1e90) at /usr/include/c++/4.8.2/condition_variable:93
#3  rocksdb::WriteThread::BlockingAwaitState (this=this@entry=0x2b5cf30, w=w@entry=0x7fa46b5c1df0, goal_mask=goal_mask@entry=30 '\036') at db/write_thread.cc:45
#4  0x000000000067e590 in rocksdb::WriteThread::AwaitState (this=this@entry=0x2b5cf30, w=w@entry=0x7fa46b5c1df0, goal_mask=goal_mask@entry=30 '\036', ctx=ctx@entry=0xae62b0 <rocksdb::jbg_ctx>) at db/write_thread.cc:181
#5  0x000000000067ea23 in rocksdb::WriteThread::JoinBatchGroup (this=this@entry=0x2b5cf30, w=w@entry=0x7fa46b5c1df0) at db/write_thread.cc:323
#6  0x00000000005fba9b in rocksdb::DBImpl::PipelinedWriteImpl (this=this@entry=0x2b5c800, write_options=..., my_batch=my_batch@entry=0x7fa46b5c2630, callback=callback@entry=0x0, log_used=log_used@entry=0x0, log_ref=log_ref@entry=0, disable_memtable=disable_memtable@entry=false, seq_used=seq_used@entry=0x0) at db/db_impl_write.cc:418
#7  0x00000000005fe092 in rocksdb::DBImpl::WriteImpl (this=0x2b5c800, write_options=..., my_batch=my_batch@entry=0x7fa46b5c2630, callback=callback@entry=0x0, log_used=log_used@entry=0x0, log_ref=log_ref@entry=0, disable_memtable=disable_memtable@entry=false, seq_used=seq_used@entry=0x0, batch_cnt=batch_cnt@entry=0, pre_release_callback=pre_release_callback@entry=0x0) at db/db_impl_write.cc:109
#8  0x00000000007d82fb in rocksdb::WriteCommittedTxn::RollbackInternal (this=0x2b6b9f0) at utilities/transactions/pessimistic_transaction.cc:367
#9  0x00000000007d568a in rocksdb::PessimisticTransaction::Rollback (this=0x2b6b9f0) at utilities/transactions/pessimistic_transaction.cc:341
#10 0x00000000007449ca in rocksdb::RandomTransactionInserter::DoInsert (this=this@entry=0x7fa46b5c2ad0, db=db@entry=0x0, txn=<optimized out>, is_optimistic=is_optimistic@entry=false) at util/transaction_test_util.cc:191
#11 0x0000000000744fd9 in rocksdb::RandomTransactionInserter::TransactionDBInsert (this=this@entry=0x7fa46b5c2ad0, db=<optimized out>, txn_options=...) at util/transaction_test_util.cc:55
#12 0x0000000000561c5a in rocksdb::Benchmark::RandomTransaction (this=0x7ffd2127ed30, thread=0x2b95680) at tools/db_bench_tool.cc:5058
#13 0x0000000000559b59 in rocksdb::Benchmark::ThreadBody (v=0x2b5dba8) at tools/db_bench_tool.cc:2687
#14 0x00000000006914c2 in rocksdb::(anonymous namespace)::StartThreadWrapper (arg=0x2b85350) at env/env_posix.cc:994
#15 0x00007fa475689dc5 in start_thread () from /lib64/libpthread.so.0
#16 0x00007fa473ecb73d in clone () from /lib64/libc.so.6

Thread 4 (Thread 0x7fa472dd2700 (LWP 14197)):
#0  0x00007fa47568d6d5 in pthread_cond_wait@@GLIBC_2.3.2 () from /lib64/libpthread.so.0
#1  0x00007fa47475f9ac in std::condition_variable::wait(std::unique_lock<std::mutex>&) () from /lib64/libstdc++.so.6
#2  0x000000000073ffd4 in rocksdb::ThreadPoolImpl::Impl::BGThread (this=this@entry=0x2890760, thread_id=thread_id@entry=1) at util/threadpool_imp.cc:196
#3  0x000000000074038f in rocksdb::ThreadPoolImpl::Impl::BGThreadWrapper (arg=0x2b603f0) at util/threadpool_imp.cc:303
#4  0x00007fa4747631e0 in ?? () from /lib64/libstdc++.so.6
#5  0x00007fa475689dc5 in start_thread () from /lib64/libpthread.so.0
#6  0x00007fa473ecb73d in clone () from /lib64/libc.so.6

Thread 3 (Thread 0x7fa4735d3700 (LWP 14196)):
#0  0x00007fa47568d6d5 in pthread_cond_wait@@GLIBC_2.3.2 () from /lib64/libpthread.so.0
#1  0x00007fa47475f9ac in std::condition_variable::wait(std::unique_lock<std::mutex>&) () from /lib64/libstdc++.so.6
#2  0x000000000073ffd4 in rocksdb::ThreadPoolImpl::Impl::BGThread (this=this@entry=0x2890760, thread_id=thread_id@entry=0) at util/threadpool_imp.cc:196
#3  0x000000000074038f in rocksdb::ThreadPoolImpl::Impl::BGThreadWrapper (arg=0x2b603d0) at util/threadpool_imp.cc:303
#4  0x00007fa4747631e0 in ?? () from /lib64/libstdc++.so.6
#5  0x00007fa475689dc5 in start_thread () from /lib64/libpthread.so.0
#6  0x00007fa473ecb73d in clone () from /lib64/libc.so.6

Thread 2 (Thread 0x7fa473dd4700 (LWP 14195)):
#0  0x00007fa47568d6d5 in pthread_cond_wait@@GLIBC_2.3.2 () from /lib64/libpthread.so.0
#1  0x00007fa47475f9ac in std::condition_variable::wait(std::unique_lock<std::mutex>&) () from /lib64/libstdc++.so.6
#2  0x000000000073ffd4 in rocksdb::ThreadPoolImpl::Impl::BGThread (this=this@entry=0x2890420, thread_id=thread_id@entry=0) at util/threadpool_imp.cc:196
#3  0x000000000074038f in rocksdb::ThreadPoolImpl::Impl::BGThreadWrapper (arg=0x2b600c0) at util/threadpool_imp.cc:303
#4  0x00007fa4747631e0 in ?? () from /lib64/libstdc++.so.6
#5  0x00007fa475689dc5 in start_thread () from /lib64/libpthread.so.0
#6  0x00007fa473ecb73d in clone () from /lib64/libc.so.6

Thread 1 (Thread 0x7fa475a9fa40 (LWP 14194)):
#0  0x00007fa47568d6d5 in pthread_cond_wait@@GLIBC_2.3.2 () from /lib64/libpthread.so.0
#1  0x00000000006d870d in rocksdb::port::CondVar::Wait (this=this@entry=0x7ffd2127e578) at port/port_posix.cc:91
#2  0x000000000055c969 in rocksdb::Benchmark::RunBenchmark (this=this@entry=0x7ffd2127ed30, n=n@entry=4, name=..., method=(void (rocksdb::Benchmark::*)(rocksdb::Benchmark * const, rocksdb::ThreadState *)) 0x561ab0 <rocksdb::Benchmark::RandomTransaction(rocksdb::ThreadState*)>) at tools/db_bench_tool.cc:2759
#3  0x000000000056d9d7 in rocksdb::Benchmark::Run (this=this@entry=0x7ffd2127ed30) at tools/db_bench_tool.cc:2638
#4  0x000000000054d481 in rocksdb::db_bench_tool (argc=1, argv=0x7ffd2127f4c8) at tools/db_bench_tool.cc:5472
#5  0x00007fa473df6bb5 in __libc_start_main () from /lib64/libc.so.6
#6  0x000000000054c201 in _start ()
```



能看到卡在wait上了，应该是死锁了，其他写线程await主写线程。

我当时没怀疑是db_bench的问题，就是单纯的认为卡住了，毕竟第一个脚本测试好用，怀疑是机器不行，issue中mack用32核机器测试。我于是找了个32核的机器Intel(R) Xeon(R) Gold 6161 CPU @ 2.20GHz重新测试第二个脚本

重新测试，还是会卡死。抓pstack

```bash
pstack 14194
Thread 5 (Thread 0x7fa46b5c3700 (LWP 14215)):
#0  0x00007fa47568d6d5 in pthread_cond_wait@@GLIBC_2.3.2 () from /lib64/libpthread.so.0
#1  0x00007fa47475f9ac in std::condition_variable::wait(std::unique_lock<std::mutex>&) () from /lib64/libstdc++.so.6
#2  0x000000000067e47c in std::condition_variable::wait<rocksdb::WriteThread::BlockingAwaitState(rocksdb::WriteThread::Writer*, uint8_t)::__lambda4> (__p=..., __lock=..., this=0x7fa46b5c1e90) at /usr/include/c++/4.8.2/condition_variable:93
#3  rocksdb::WriteThread::BlockingAwaitState (this=this@entry=0x2b5cf30, w=w@entry=0x7fa46b5c1df0, goal_mask=goal_mask@entry=30 '\036') at db/write_thread.cc:45
#4  0x000000000067e590 in rocksdb::WriteThread::AwaitState (this=this@entry=0x2b5cf30, w=w@entry=0x7fa46b5c1df0, goal_mask=goal_mask@entry=30 '\036', ctx=ctx@entry=0xae62b0 <rocksdb::jbg_ctx>) at db/write_thread.cc:181
#5  0x000000000067ea23 in rocksdb::WriteThread::JoinBatchGroup (this=this@entry=0x2b5cf30, w=w@entry=0x7fa46b5c1df0) at db/write_thread.cc:323
#6  0x00000000005fba9b in rocksdb::DBImpl::PipelinedWriteImpl (this=this@entry=0x2b5c800, write_options=..., my_batch=my_batch@entry=0x7fa46b5c2630, callback=callback@entry=0x0, log_used=log_used@entry=0x0, log_ref=log_ref@entry=0, disable_memtable=disable_memtable@entry=false, seq_used=seq_used@entry=0x0) at db/db_impl_write.cc:418
#7  0x00000000005fe092 in rocksdb::DBImpl::WriteImpl (this=0x2b5c800, write_options=..., my_batch=my_batch@entry=0x7fa46b5c2630, callback=callback@entry=0x0, log_used=log_used@entry=0x0, log_ref=log_ref@entry=0, disable_memtable=disable_memtable@entry=false, seq_used=seq_used@entry=0x0, batch_cnt=batch_cnt@entry=0, pre_release_callback=pre_release_callback@entry=0x0) at db/db_impl_write.cc:109
#8  0x00000000007d82fb in rocksdb::WriteCommittedTxn::RollbackInternal (this=0x2b6b9f0) at utilities/transactions/pessimistic_transaction.cc:367
#9  0x00000000007d568a in rocksdb::PessimisticTransaction::Rollback (this=0x2b6b9f0) at utilities/transactions/pessimistic_transaction.cc:341
#10 0x00000000007449ca in rocksdb::RandomTransactionInserter::DoInsert (this=this@entry=0x7fa46b5c2ad0, db=db@entry=0x0, txn=<optimized out>, is_optimistic=is_optimistic@entry=false) at util/transaction_test_util.cc:191
#11 0x0000000000744fd9 in rocksdb::RandomTransactionInserter::TransactionDBInsert (this=this@entry=0x7fa46b5c2ad0, db=<optimized out>, txn_options=...) at util/transaction_test_util.cc:55
#12 0x0000000000561c5a in rocksdb::Benchmark::RandomTransaction (this=0x7ffd2127ed30, thread=0x2b95680) at tools/db_bench_tool.cc:5058
#13 0x0000000000559b59 in rocksdb::Benchmark::ThreadBody (v=0x2b5dba8) at tools/db_bench_tool.cc:2687
#14 0x00000000006914c2 in rocksdb::(anonymous namespace)::StartThreadWrapper (arg=0x2b85350) at env/env_posix.cc:994
#15 0x00007fa475689dc5 in start_thread () from /lib64/libpthread.so.0
#16 0x00007fa473ecb73d in clone () from /lib64/libc.so.6
Thread 4 (Thread 0x7fa472dd2700 (LWP 14197)):
#0  0x00007fa47568d6d5 in pthread_cond_wait@@GLIBC_2.3.2 () from /lib64/libpthread.so.0
#1  0x00007fa47475f9ac in std::condition_variable::wait(std::unique_lock<std::mutex>&) () from /lib64/libstdc++.so.6
#2  0x000000000073ffd4 in rocksdb::ThreadPoolImpl::Impl::BGThread (this=this@entry=0x2890760, thread_id=thread_id@entry=1) at util/threadpool_imp.cc:196
#3  0x000000000074038f in rocksdb::ThreadPoolImpl::Impl::BGThreadWrapper (arg=0x2b603f0) at util/threadpool_imp.cc:303
#4  0x00007fa4747631e0 in ?? () from /lib64/libstdc++.so.6
#5  0x00007fa475689dc5 in start_thread () from /lib64/libpthread.so.0
#6  0x00007fa473ecb73d in clone () from /lib64/libc.so.6
Thread 3 (Thread 0x7fa4735d3700 (LWP 14196)):
#0  0x00007fa47568d6d5 in pthread_cond_wait@@GLIBC_2.3.2 () from /lib64/libpthread.so.0
#1  0x00007fa47475f9ac in std::condition_variable::wait(std::unique_lock<std::mutex>&) () from /lib64/libstdc++.so.6
#2  0x000000000073ffd4 in rocksdb::ThreadPoolImpl::Impl::BGThread (this=this@entry=0x2890760, thread_id=thread_id@entry=0) at util/threadpool_imp.cc:196
#3  0x000000000074038f in rocksdb::ThreadPoolImpl::Impl::BGThreadWrapper (arg=0x2b603d0) at util/threadpool_imp.cc:303
#4  0x00007fa4747631e0 in ?? () from /lib64/libstdc++.so.6
#5  0x00007fa475689dc5 in start_thread () from /lib64/libpthread.so.0
#6  0x00007fa473ecb73d in clone () from /lib64/libc.so.6
Thread 2 (Thread 0x7fa473dd4700 (LWP 14195)):
#0  0x00007fa47568d6d5 in pthread_cond_wait@@GLIBC_2.3.2 () from /lib64/libpthread.so.0
#1  0x00007fa47475f9ac in std::condition_variable::wait(std::unique_lock<std::mutex>&) () from /lib64/libstdc++.so.6
#2  0x000000000073ffd4 in rocksdb::ThreadPoolImpl::Impl::BGThread (this=this@entry=0x2890420, thread_id=thread_id@entry=0) at util/threadpool_imp.cc:196
#3  0x000000000074038f in rocksdb::ThreadPoolImpl::Impl::BGThreadWrapper (arg=0x2b600c0) at util/threadpool_imp.cc:303
#4  0x00007fa4747631e0 in ?? () from /lib64/libstdc++.so.6
#5  0x00007fa475689dc5 in start_thread () from /lib64/libpthread.so.0
#6  0x00007fa473ecb73d in clone () from /lib64/libc.so.6
Thread 1 (Thread 0x7fa475a9fa40 (LWP 14194)):
#0  0x00007fa47568d6d5 in pthread_cond_wait@@GLIBC_2.3.2 () from /lib64/libpthread.so.0
#1  0x00000000006d870d in rocksdb::port::CondVar::Wait (this=this@entry=0x7ffd2127e578) at port/port_posix.cc:91
#2  0x000000000055c969 in rocksdb::Benchmark::RunBenchmark (this=this@entry=0x7ffd2127ed30, n=n@entry=4, name=..., method=(void (rocksdb::Benchmark::*)(rocksdb::Benchmark * const, rocksdb::ThreadState *)) 0x561ab0 <rocksdb::Benchmark::RandomTransaction(rocksdb::ThreadState*)>) at tools/db_bench_tool.cc:2759
#3  0x000000000056d9d7 in rocksdb::Benchmark::Run (this=this@entry=0x7ffd2127ed30) at tools/db_bench_tool.cc:2638
#4  0x000000000054d481 in rocksdb::db_bench_tool (argc=1, argv=0x7ffd2127f4c8) at tools/db_bench_tool.cc:5472
#5  0x00007fa473df6bb5 in __libc_start_main () from /lib64/libc.so.6
#6  0x000000000054c201 in _start ()
```

多了点信息，比如pipeline write<sup> 5</sup>。wolfkdy确定是db_bench的bug(感谢。我都没有这么自信)。然后找到了rocksdb 的fix

```markdown
5.15.0 (7/17/2018)
......
Bug Fixes
Fix deadlock with **enable_pipelined_write=true** and max_successive_merges > 0
Check conflict at output level in CompactFiles.
Fix corruption in non-iterator reads when mmap is used for file reads
Fix bug with prefix search in partition filters where a shared prefix would be ignored from the later partitions. The bug could report an eixstent key as missing. The bug could be triggered if prefix_extractor is set and partition filters is enabled.
Change default value of bytes_max_delete_chunk to 0 in NewSstFileManager() as it doesn't work well with checkpoints.
Fix a bug caused by not copying the block trailer with compressed SST file, direct IO, prefetcher and no compressed block cache.
Fix write can stuck indefinitely if enable_pipelined_write=true. The issue exists since pipelined write was introduced in 5.5.0.
```



这个参数我在db_bench页面搜了，没搜到（应该是很久没更新了。我给加上了），在pipeline write页面中列出了。

db_bench help页面也列出了这个参数。我没想到。下次记得先看软件自带的man page

加上enable_pipelined_write=false后，新测了一组数据，符合预期
```bash
1       mt0     39070   22716   23107
1       mt1     39419   22649   23345
2       mt0     60962   33602   27778
2       mt1     66347   35297   31959
4       mt0     63993   42740   26964
4       mt1     91138   50720   28831
8       mt0     81788   52713   25167
8       mt1     141298  72900   25832
16      mt0     90463   62032   21954
16      mt1     194290  100470  21581
24      mt0     87967   64610   20957
24      mt1     226909  111770  20506
32      mt0     88986   65632   20474
32      mt1     110627  123805  20040
40      mt0     86774   66612   19835
40      mt1     113140  58720   19886
48      mt0     86848   68086   19611
```

看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。
### 参考

1. gist被屏蔽的一个解决办法 <https://blog.jiayu.co/2018/06/an-alternative-github-gist-viewer/> 这个帮助很大
2. 一个测试参考<https://github.com/facebook/rocksdb/issues/4402>
3. db_bench介绍，注意，没有写隐藏参数enable_pipelined_write=true默认<https://github.com/facebook/rocksdb/wiki/Benchmarking-tools>
4. poor man‘s profiler <https://poormansprofiler.org/> 感谢mack
5. pipeline 提升性能 <https://github.com/facebook/rocksdb/wiki/Pipelined-Write> 测试结果 <https://gist.githubusercontent.com/yiwu-arbug/3b5a5727e52f1e58d1c10f2b80cec05d/raw/fc1df48c4fff561da0780d83cd8aba2721cdf7ac/gistfile1.txt>
6. 这个滴滴的大神fix的这个bug，链接里有分析过程<https://bravoboy.github.io/2018/09/11/rocksdb-deadlock/>

看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。