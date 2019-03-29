---
layout: post
category : database
title: 分布式事务，xa，2pc，以及rocksdb xa测试
tags : [rocksdb, gcc]
---
{% include JB/setup %}

### why

科普概念

---

`背景知识`: 分布式事务和2pc在参考链接<sup>1</sup>中有介绍，2pc协议是分布式事务的一个解决方案，2pc主要缺陷

> 1. **同步阻塞问题**。执行过程中，所有参与节点都是事务阻塞型的。当参与者占有公共资源时，其他第三方节点访问公共资源不得不处于阻塞状态。
> 2. **单点故障**。由于协调者的重要性，一旦协调者发生故障。参与者会一直阻塞下去。尤其在第二阶段，协调者发生故障，那么所有的参与者还都处于锁定事务资源的状态中，而无法继续完成事务操作。（如果是协调者挂掉，可以重新选举一个协调者，但是无法解决因为协调者宕机导致的参与者处于阻塞状态的问题）
> 3. **数据不一致**。在二阶段提交的阶段二中，当协调者向参与者发送commit请求之后，发生了局部网络异常或者在发送commit请求过程中协调者发生了故障，这回导致只有一部分参与者接受到了commit请求。而在这部分参与者接到commit请求之后就会执行commit操作。但是其他部分未接到commit请求的机器则无法执行事务提交。于是整个分布式系统便出现了数据部一致性的现象。
> 4. 二阶段无法解决的问题：协调者再发出commit消息之后宕机，而唯一接收到这条消息的参与者同时也宕机了。那么即使协调者通过选举协议产生了新的协调者，这条事务的状态也是不确定的，没人知道事务是否被已经提交。

`rocksdb 2pc实现` 见参考链接<sup>2, 3</sup> 主要多了prepare操作。这个需求来自myrocks，作为mysql引擎需要xa事务机制myrocks学习可以见参考链接<sup>4</sup>

2pc实现简单说

```c++
txn->Put(...);
txn->Prepare();
txn->Commit();
```



我一开始是找myrocksxa事务是咋实现的，myrocks引擎在代码storage/myrocks里，但是翻了半天没找到。

找手册，这<sup>5</sup>有个myrocks配置选项

> #### `rocksdb_enable_2pc`
>
> - **Description:** Enable two phase commit for MyRocks. When set, MyRocks will keep its data consistent with the [binary log](https://mariadb.com/kb/en/binary-log/) (in other words, the server will be a crash-safe master). The consistency is achieved by doing two-phase XA commit with the binary log.
> - **Commandline:** `--rocksdb-enable-2pc={0|1}`
> - **Scope:** Global
> - **Dynamic:** Yes
> - **Data Type:** `boolean`
> - **Default Value:** `ON`

`全程配置allow_2pc就能模拟xa事务吗?` 我针对这个改了一版db_bench 

dbbench改动，增加allow_2pc配置，如果有这个配置，就true， 调用定义DEFINE_bool就好了（gflags这个库也很好玩，之前吐槽没有命令行的库，孤陋寡闻）

机器32核，脚本参考mark改的，执行脚本

> bash r.sh  10000000 60 32 4 /home/vdb/rocksdb-5.14.3/rdb 0 /home/vdb/rocksdb-5.14.3/db_bench

核心代码

```bash
#set -x
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
  a_2pc=$4

  rm -rf $dbdir; mkdir $dbdir
  # TODO --perf_level=0

$dbb --benchmarks=randomtransaction --use_existing_db=0 --sync=$sync --db=$dbdir --wal_dir=$dbdir --num=$numk --duration=$secs --num_levels=6 --key_size=8 --value_size=$val --block_size=4096 --cache_size=$(( 20 * 1024 * 1024 * 1024 )) --cache_numshardbits=6 --compression_type=none --compression_ratio=0.5 --level_compaction_dynamic_level_bytes=true --bytes_per_sync=8388608 --cache_index_and_filter_blocks=0 --benchmark_write_rate_limit=0 --write_buffer_size=$(( 64 * 1024 * 1024 )) --max_write_buffer_number=4 --target_file_size_base=$(( 32 * 1024 * 1024 )) --max_bytes_for_level_base=$(( 512 * 1024 * 1024 )) --verify_checksum=1 --delete_obsolete_files_period_micros=62914560 --max_bytes_for_level_multiplier=8 --statistics=0 --stats_per_interval=1 --stats_interval_seconds=60 --histogram=1 --allow_concurrent_memtable_write=$a_concurmt --enable_write_thread_adaptive_yield=$a_concurmt --memtablerep=skip_list --bloom_bits=10 --open_files=-1 --level0_file_num_compaction_trigger=4 --level0_slowdown_writes_trigger=20 --level0_stop_writes_trigger=30 --max_background_jobs=8 --max_background_flushes=2 --threads=$a_dop --merge_operator="put" --seed=1454699926 --transaction_sets=$batch --compaction_pri=3 $a_extra -enable_pipelined_write=false -allow_2pc=$a_2pc
}

for dop in 1 2 4 8 16 24 32 40 48 ; do
for concurmt in 0 1 ; do
for pc in 0 1; do

fn=o.dop${dop}.val${val}.batch${batch}.concur${concurmt}.notrx
runme $concurmt $dop "" $pc >& $fn
q1=$( grep ^randomtransaction $fn | awk '{ print $5 }' )

t=transaction_db
fn=o.dop${dop}.val${val}.batch${batch}.concur${concurmt}.pessim
runme $concurmt $dop --${t}=1 $pc >& $fn
q2=$( grep ^randomtransaction $fn | awk '{ print $5 }' )

t=optimistic_transaction_db
fn=o.dop${dop}.val${val}.batch${batch}.concur${concurmt}.optim
runme $concurmt $dop --${t}=1 $pc >& $fn
q3=$( grep ^randomtransaction $fn | awk '{ print $5 }' )

echo $dop mt${concurmt} allow2pc${pc} $q1 $q2 $q3 | awk '{ printf "%s\t%s\t%s\t%s\t%s\t%s\n", $1, $2, $3, $4, $5, $6 }'

done
done
done
```

能看到是allow_2pc和和其他项组合的。

测试结果发现数据没有不同 

线程数， 是否并发写， 是否开启2pc， 无事务，悲观事务，乐观事务
```bash
1       mt0     allow2pc0       39512   22830   21238
1       mt0     allow2pc1       40720   23014   22767
1       mt1     allow2pc0       40539   22683   22131
1       mt1     allow2pc1       36361   21680   23592
2       mt0     allow2pc0       62337   33972   27747
2       mt0     allow2pc1       62725   33941   27553
2       mt1     allow2pc0       62535   33640   31501
2       mt1     allow2pc1       62127   34320   30636
4       mt0     allow2pc0       64864   41878   25235
4       mt0     allow2pc1       65517   41184   26055
4       mt1     allow2pc0       93863   49895   28183
4       mt1     allow2pc1       89718   48726   29027
8       mt0     allow2pc0       79444   52166   26142
8       mt0     allow2pc1       80186   51643   26254
8       mt1     allow2pc0       139753  72598   24661
8       mt1     allow2pc1       136604  73382   25482
16      mt0     allow2pc0       87555   61620   22809
16      mt0     allow2pc1       88055   61812   21631
16      mt1     allow2pc0       193535  98820   21272
16      mt1     allow2pc1       190517  98582   21007
24      mt0     allow2pc0       91718   65400   20736
24      mt0     allow2pc1       92319   64477   20505
24      mt1     allow2pc0       226268  111956  20453
24      mt1     allow2pc1       224815  111901  21005
32      mt0     allow2pc0       88233   65121   20683
32      mt0     allow2pc1       89150   65643   20127
32      mt1     allow2pc0       111623  120843  20626
32      mt1     allow2pc1       230557  120421  20124
40      mt0     allow2pc0       87062   66972   20093
40      mt0     allow2pc1       86632   66814   20590
40      mt1     allow2pc0       113856  60101   20280
40      mt1     allow2pc1       115139  58768   20264
48      mt0     allow2pc0       87093   68637   20153
48      mt0     allow2pc1       87283   68382   19537
48      mt1     allow2pc0       122819  64030   19796
48      mt1     allow2pc1       126721  64090   19907
```
同事zcw指出这种测试可能不对，我的测试 2pc和悲观乐观事务是组合的形式，这可能并不合理,乐观事务这个参数没意义，allow_2pc只是一个配置，表示rocksdb支持而已，还是要调用prepare才能实现应用的xa，我之前错误的理解allow_2pc配置后会在rocksdb内部有prepare过程（我之前好像看到了）

还是回头看db_bench，看db_bench到底怎么测试的 所有randomtransaction会调用doinsert来真正的执行

定义在transaction_test_util.cc中，果不其然 找到txn->prepare调用

```C++
bool RandomTransactionInserter::DoInsert(DB* db, Transaction* txn,
                                         bool is_optimistic) {
	...
  // pick a random number to use to increment a key in each set
    ...
  // For each set, pick a key at random and increment it
    ...
	
  if (s.ok()) {
    if (txn != nullptr) {
      bool with_prepare = !is_optimistic && !rand_->OneIn(10);
      if (with_prepare) {
        // Also try commit without prepare
        s = txn->Prepare();
        assert(s.ok());
        ROCKS_LOG_DEBUG(db->GetDBOptions().info_log,
                        "Prepare of %" PRIu64 " %s (%s)", txn->GetId(),
                        s.ToString().c_str(), txn->GetName().c_str());
        db->GetDBOptions().env->SleepForMicroseconds(
            static_cast<int>(cmt_delay_ms_ * 1000));
      }
      if (!rand_->OneIn(20)) {
        s = txn->Commit();
```



注意with_prepare这句，这句表明，不是乐观事务，悲观事务，会注意这个取反，会90%调用prepare，调用prepare的事务可以确定肯定是xa事务。所以我需要加个配置项，改成100%的，也应该加个完全不调用prepare的做对照

另外，这个rand_->OneIn(10)实现的很好玩。看测试代码总能发现这些犄角旮旯的需求以及好玩的实现



改动点<sup>6</sup>

- 加上transaction_db_xa
- 所有 FLAGS_transaction_db都得或上FLAGS_transaction_db_xa，避免遗漏，或者不复用，单独再写
- randomTransaction入口

```c++

void RandomTransaction(ThreadState* thread) {
while (!duration.Done(1)) {
  bool success;

  // RandomTransactionInserter will attempt to insert a key for each
  // # of FLAGS_transaction_sets
  if (FLAGS_optimistic_transaction_db) {
    success = inserter.OptimisticTransactionDBInsert(db_.opt_txn_db);
  } else if (FLAGS_transaction_db) {
    TransactionDB* txn_db = reinterpret_cast<TransactionDB*>(db_.db);
    success = inserter.TransactionDBInsert(txn_db, txn_options);
  } else if (FLAGS_transaction_db_xa) {
    TransactionDB* txn_db = reinterpret_cast<TransactionDB*>(db_.db);
    success = inserter.TransactionDBXAInsert(txn_db, txn_options);
  } else {
    success = inserter.DBInsert(db_.db);
  }
```
加上个flags_transaction_db_xa 对应的option也得注意，要enable allow_2pc

没enable allow_2pc做了个测试，结果真的就是降低了10%，没啥参考价值的感觉。 最后一列是100% prepare

```bash
1       mt0     37353   21628   22018   21845
1       mt1     38089   21171   22606   21688
2       mt0     62627   31901   27003   32895
2       mt1     62029   33865   31083   33691
4       mt0     64915   41651   26226   40853
4       mt1     88089   51123   29066   48673
8       mt0     79742   51276   25154   49865
8       mt1     134687  72683   25000   71469
16      mt0     88103   61816   21568   60656
16      mt1     192417  98546   21265   97890
24      mt0     91989   64858   20592   63141
24      mt1     232313  111736  20706   110083
32      mt0     91073   65840   20399   64103
32      mt1     221337  61289   20164   118167
40      mt0     85909   66244   20144   64709
40      mt1     116536  59155   20119   55437
48      mt0     86006   68390   19828   66910
48      mt1     125246  63577   19700   61621
```



我enable allow2pc 100%prepare 测了一组数据，作为对照，测了一个0%prepare 



```shell
#set -x
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

$dbb --benchmarks=randomtransaction --use_existing_db=0 --sync=$sync --db=$dbdir --wal_dir=$dbdir --num=$numk --duration=$secs --num_levels=6 --key_size=8 --value_size=$val --block_size=4096 --cache_size=$(( 20 * 1024 * 1024 * 1024 )) --cache_numshardbits=6 --compression_type=none --compression_ratio=0.5 --level_compaction_dynamic_level_bytes=true --bytes_per_sync=8388608 --cache_index_and_filter_blocks=0 --benchmark_write_rate_limit=0 --write_buffer_size=$(( 64 * 1024 * 1024 )) --max_write_buffer_number=4 --target_file_size_base=$(( 32 * 1024 * 1024 )) --max_bytes_for_level_base=$(( 512 * 1024 * 1024 )) --verify_checksum=1 --delete_obsolete_files_period_micros=62914560 --max_bytes_for_level_multiplier=8 --statistics=0 --stats_per_interval=1 --stats_interval_seconds=60 --histogram=1 --allow_concurrent_memtable_write=$a_concurmt --enable_write_thread_adaptive_yield=$a_concurmt --memtablerep=skip_list --bloom_bits=10 --open_files=-1 --level0_file_num_compaction_trigger=4 --level0_slowdown_writes_trigger=20 --level0_stop_writes_trigger=30 --max_background_jobs=8 --max_background_flushes=2 --threads=$a_dop --merge_operator="put" --seed=1454699926 --transaction_sets=$batch --compaction_pri=3 $a_extra -enable_pipelined_write=false
}

for dop in 1 2 4 8 16 24 32 40 48 ; do
for concurmt in 0 1 ; do

fn=o.dop${dop}.val${val}.batch${batch}.concur${concurmt}.notrx
runme $concurmt $dop ""  >& $fn
q1=$( grep ^randomtransaction $fn | awk '{ print $5 }' )

t=transaction_db
fn=o.dop${dop}.val${val}.batch${batch}.concur${concurmt}.pessim
runme $concurmt $dop --${t}=1  >& $fn
q2=$( grep ^randomtransaction $fn | awk '{ print $5 }' )

t=optimistic_transaction_db
fn=o.dop${dop}.val${val}.batch${batch}.concur${concurmt}.optim
runme $concurmt $dop --${t}=1  >& $fn
q3=$( grep ^randomtransaction $fn | awk '{ print $5 }' )

t=transaction_db_xa
fn=o.dop${dop}.val${val}.batch${batch}.concur${concurmt}.pessimxa
runme $concurmt $dop --${t}=1  >& $fn
q4=$( grep ^randomtransaction $fn | awk '{ print $5 }' )


fn=o.dop${dop}.val${val}.batch${batch}.concur${concurmt}.pessimnopre
runme $concurmt $dop --${t}=-1  >& $fn #-1 for no prepare
q5=$( grep ^randomtransaction $fn | awk '{ print $5 }' )
echo $dop mt${concurmt} $q1 $q2 $q3 $q4 $q5 | awk '{ printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\n", $1, $2, $3, $4, $5, $6, $7 }'

done
done
```



| 线程数 | 是否并发写 | 无事务 | 悲观事务 默认90%prepare      allwo_2pc=0 | 乐观事务 | 悲观事务  prepare 100% allwo_2pc=1 | 悲观事务      prepare 0% |
| ------ | ---------- | ------ | ---------------------------------------- | -------- | ---------------------------------- | ------------------------ |
| 1      | mt0        | 40631  | 22399                                    | 23447    | 22085                              | 23957                    |
| 1      | mt1        | 40744  | 21680                                    | 23316    | 21896                              | 24040                    |
| 2      | mt0        | 59313  | 33031                                    | 27751    | 32342                              | 36653                    |
| 2      | mt1        | 60690  | 33169                                    | 30819    | 33349                              | 34445                    |
| 4      | mt0        | 54808  | 41715                                    | 25583    | 37383                              | 46622                    |
| 4      | mt1        | 74016  | 50699                                    | 29411    | 48445                              | 52160                    |
| 8      | mt0        | 68584  | 48591                                    | 25009    | 45397                              | 59238                    |
| 8      | mt1        | 94581  | 64892                                    | 24612    | 70616                              | 83271                    |
| 16     | mt0        | 86554  | 60897                                    | 22602    | 58607                              | 74842                    |
| 16     | mt1        | 186053 | 96305                                    | 21548    | 93654                              | 121303                   |
| 24     | mt0        | 91051  | 63187                                    | 20792    | 61605                              | 79021                    |
| 24     | mt1        | 209827 | 111059                                   | 20735    | 106036                             | 144641                   |
| 32     | mt0        | 90318  | 64180                                    | 20839    | 62339                              | 77219                    |
| 32     | mt1        | 185310 | 113754                                   | 20439    | 108233                             | 84580                    |
| 40     | mt0        | 87769  | 65888                                    | 20449    | 63999                              | 80699                    |
| 40     | mt1        | 119916 | 60919                                    | 19891    | 56265                              | 88792                    |
| 48     | mt0        | 86097  | 67501                                    | 19838    | 66396                              | 81704                    |
| 48     | mt1        | 119423 | 61086                                    | 19217    | 59750                              | 86127                    |



markdown 不能调格间距，真破

这个数据作为参考。

另外，有个2pc的bug 值得关注一下 pr <https://github.com/facebook/rocksdb/pull/1768>

看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。
### reference

1. 分布式事务，2pc 3pc <https://www.hollischuang.com/archives/681>
2. rocksdb 2pc实现 <https://github.com/facebook/rocksdb/wiki/Two-Phase-Commit-Implementation>
3. rocksdb 事务，其中有2pc事务讲解<https://zhuanlan.zhihu.com/p/31255678>
4. myrocks deep dive，不错，关于rocksdb的部分提纲摰领<https://www.percona.com/live/plam16/sites/default/files/slides/myrocksdeepdive201604-160419162421.pdf>
5. <https://mariadb.com/kb/en/library/myrocks-system-variables/>
6. 我的测试改动 <https://github.com/wanghenshui/rocksdb/tree/14.3-modified-db-bench>
7. 一个excel小知识，生成的数据如何整理成excel格式，选择这列 ->{数据}菜单 ->分列->按照空格分列，<https://zhidao.baidu.com/question/351335222>

