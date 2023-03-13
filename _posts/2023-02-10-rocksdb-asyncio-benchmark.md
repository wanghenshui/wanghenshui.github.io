---
layout: post
title: rocksdb asyncio benchmark
categories: [database]
tags: [rocksdb,asyncio,folly]
---

TL;DR

本来想测测asyncio能带来多大提升，结果没啥提升，我都有点怀疑是不是我理解错了

<!-- more -->

## 准备

folly 集成在这里 https://github.com/facebook/rocksdb/wiki/RocksDB-Contribution-Guide#folly-integration

```bash
make checkout_folly
make build_folly
cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo -DWITH_LIBURING=1 -DFAIL_ON_WARNINGS=0 -DWITH_SNAPPY=1 -DWITH_LZ4=1 -DWITH_ZSTD=1 -DUSE_COROUTINES=1 -DWITH_GFLAGS=1 -DROCKSDB_BUILD_SHARED=0 .. && make -j16  db_bench
make -j32

```
缺少什么依赖自己补充，有一点坑爹的地方就是这个folly生成的库的位置在/tmp ，所以说机器重启就没啦，还得重编，编译完记得保留一份文件

```bash
cp -r  /tmp/fbcode_builder_getdeps-ZhomeZwZcodeZrocksdbZthird-partyZfollyZbuildZfbcode_builder folly_build_tmp
```

目录名字不一样自己改改

或者把依赖的库全复制到db_bench同级目录然后preload一下，总之得留一份

另外 我用的7.9版本，http://rocksdb.org/blog/2022/10/07/asynchronous-io-in-rocksdb.html

这个博客说的压测我自己运行会直接coredump。我就只能自己db_bench来玩了。。

摸索的数据贴在 https://github.com/wanghenshui/wanghenshui.github.io/issues/83

## 磁盘

之前也说过我用的固态是凯侠 RC20，我又跑了dd/fio，这里贴一下参数

### dd

<img src="https://user-images.githubusercontent.com/8872493/218255155-2e3f7b45-9933-457b-8e11-490aab39e0ca.png" width="80%">

```bash
dd if=/data/tmp/test of=/data/tmp/test2 bs=64k
记录了1250000+0 的读入
记录了1250000+0 的写出
81920000000字节（82 GB，76 GiB）已复制，112.668 s，727 MB/s
```

我觉得效果还可以

### fio  fsync

```bash
 fio --randrepeat=1 --ioengine=sync --direct=1 --gtod_reduce=1 --name=test --filename=/data/tmp/fio_test_file --bs=4k --iodepth=64 --size=4G --readwrite=randread --numjobs=32 --group_reporting

fio-3.30
Starting 32 processes
Jobs: 32 (f=32): [r(32)][100.0%][r=962MiB/s][r=246k IOPS][eta 00m:00s]
test: (groupid=0, jobs=32): err= 0: pid=11567: Sat Feb 11 19:17:06 2023
read: IOPS=244k, BW=953MiB/s (999MB/s)(128GiB/137532msec)
bw ( KiB/s): min=22408, max=1006104, per=100.00%, avg=976605.28, stdev=2430.25, samples=8768
iops : min= 5602, max=251526, avg=244151.32, stdev=607.56, samples=8768
cpu : usr=0.26%, sys=1.54%, ctx=33554635, majf=5, minf=346
IO depths : 1=100.0%, 2=0.0%, 4=0.0%, 8=0.0%, 16=0.0%, 32=0.0%, >=64=0.0%
submit : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
complete : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
issued rwts: total=33554432,0,0,0 short=0,0,0,0 dropped=0,0,0,0
latency : target=0, window=0, percentile=100.00%, depth=64

Run status group 0 (all jobs):
READ: bw=953MiB/s (999MB/s), 953MiB/s-953MiB/s (999MB/s-999MB/s), io=128GiB (137GB), run=137532-137532msec

Disk stats (read/write):
nvme1n1: ios=33537154/0, merge=0/0, ticks=4317401/0, in_queue=4317401, util=99.94%
```

### fio aio

```bash
w@w-msi:~$ fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 --name=test --filename=/data/tmp/fio_test_file2 --bs=4k --iodepth=64 --size=4G --readwrite=randread
test: (g=0): rw=randread, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=64
fio-3.30
Starting 1 process

Jobs: 1 (f=1): [r(1)][100.0%][r=971MiB/s][r=248k IOPS][eta 00m:00s]
test: (groupid=0, jobs=1): err= 0: pid=11667: Sat Feb 11 19:19:47 2023
read: IOPS=247k, BW=965MiB/s (1012MB/s)(4096MiB/4246msec)
bw ( KiB/s): min=981088, max=996264, per=100.00%, avg=990337.00, stdev=5501.80, samples=8
iops : min=245272, max=249066, avg=247584.25, stdev=1375.45, samples=8
cpu : usr=12.82%, sys=43.18%, ctx=338888, majf=0, minf=71
IO depths : 1=0.1%, 2=0.1%, 4=0.1%, 8=0.1%, 16=0.1%, 32=0.1%, >=64=100.0%
submit : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
complete : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.1%, >=64=0.0%
issued rwts: total=1048576,0,0,0 short=0,0,0,0 dropped=0,0,0,0
latency : target=0, window=0, percentile=100.00%, depth=64

Run status group 0 (all jobs):
READ: bw=965MiB/s (1012MB/s), 965MiB/s-965MiB/s (1012MB/s-1012MB/s), io=4096MiB (4295MB), run=4246-4246msec

Disk stats (read/write):
```

这个读写还可以把，但是我db bench 单线程读，磁盘就40M，给我测的失去信心了。连续读写可以，但是小文件读垃圾



## 压测数据以及结论

命令

```bash
NUM_THREADS=32 NUM_KEYS=100000000 DB_DIR=/data/tmp/ben WAL_DIR=/data/tmp/wal ./benchmark.sh bulkload,readrandom
NUM_THREADS=32 NUM_KEYS=1000000000 DB_DIR=/data/tmp/ben WAL_DIR=/data/tmp/wal ./benchmark.sh bulkload
NUM_THREADS=32 NUM_KEYS=100000000 DB_DIR=/data/tmp/ben WAL_DIR=/data/tmp/wal ./benchmark.sh readrandom
ASYNC_IO=1 NUM_THREADS=32 NUM_KEYS=100000000 DB_DIR=/data/tmp/ben WAL_DIR=/data/tmp/wal ./benchmark.sh readrandom
ASYNC_IO=1 NUM_THREADS=32 NUM_KEYS=100000000 DB_DIR=/data/tmp/ben WAL_DIR=/data/tmp/wal ./benchmark.sh multireadrandom
NUM_THREADS=32 NUM_KEYS=100000000 DB_DIR=/data/tmp/ben WAL_DIR=/data/tmp/wal ./benchmark.sh multireadrandom
```

一开始是10G的数据，然后重新生成了100G的数据

ASYNC_IO是我加的

diff

```bash
diff --git a/tools/benchmark.sh b/tools/benchmark.sh
index b41d25c78..df3f6e52e 100755
--- a/tools/benchmark.sh
+++ b/tools/benchmark.sh
@@ -170,7 +170,7 @@ compression_max_dict_bytes=${COMPRESSION_MAX_DICT_BYTES:-0}
 compression_type=${COMPRESSION_TYPE:-zstd}
 min_level_to_compress=${MIN_LEVEL_TO_COMPRESS:-"-1"}
 compression_size_percent=${COMPRESSION_SIZE_PERCENT:-"-1"}
-
+async_io=${ASYNC_IO:-0}
 duration=${DURATION:-0}
 writes=${WRITES:-0}
 
@@ -291,6 +291,7 @@ const_params_base="
   --memtablerep=skip_list \
   --bloom_bits=10 \
   --open_files=-1 \
+  -async_io=$async_io \
   --subcompactions=$subcompactions \
   \
   $bench_args"

```

就加了个async_io

结果

```
# ops_sec - operations per second
# mb_sec - ops_sec * size-of-operation-in-MB
# lsm_sz - size of LSM tree
# blob_sz - size of BlobDB logs
# c_wgb - GB written by compaction
# w_amp - Write-amplification as (bytes written by compaction / bytes written by memtable flush)
# c_mbps - Average write rate for compaction
# c_wsecs - Wall clock seconds doing compaction
# c_csecs - CPU seconds doing compaction
# b_rgb - Blob compaction read GB
# b_wgb - Blob compaction write GB
# usec_op - Microseconds per operation
# p50, p99, p99.9, p99.99 - 50th, 99th, 99.9th, 99.99th percentile response time in usecs
# pmax - max response time in usecs
# uptime - RocksDB uptime in seconds
# stall% - Percentage of time writes are stalled
# Nstall - Number of stalls
# u_cpu - #seconds/1000 of user CPU
# s_cpu - #seconds/1000 of system CPU
# rss - max RSS in GB for db_bench process
# test - Name of test
# date - Date/time of test
# version - RocksDB version
# job_id - User-provided job ID
# githash - git hash at which db_bench was compiled
ops_sec	mb_sec	lsm_sz	blob_sz	c_wgb	w_amp	c_mbps	c_wsecs	c_csecs	b_rgb	b_wgb	usec_op	p50	p99	p99.9	p99.99	pmax	uptime	stall%	Nstall	u_cpu	s_cpu	rss	test	date	version	job_id	githash
1536598	615.5	18GB	0GB	17.6	0.9	276.0	203	199	0	0	0.7	0.5	1	1	1139	41244	65	43.2	64	0.2	0.0	NA	bulkload	2023-02-11T21:58:57	8.0.0		a72f591825
1480156	374.8	11GB	0GB	0.0	NA	0.0	0	0	0	0	21.6	2.6	327	696	1563	414661	2162	0.0	0	12.4	2.6	16.4	readrandom.t32	2023-02-11T22:02:17	8.0.0		a72f591825
1546717	619.5	177GB	0GB	177.2	0.9	280.7	2028	1964	0	0	0.6	0.5	1	1	1151	35774	646	46.8	651	2.2	0.1	NA	bulkload	2023-02-11T22:55:03	8.0.0		a72f591825
867544	219.7	107GB	0GB	0.0	NA	0.0	0	0	0	0	36.9	2.6	408	960	3881	333915	3689:q	0.0	0	12.5	4.7	17.6	readrandom.t32	2023-02-12T14:15:06	8.0.0		a72f591825
810797	205.3	107GB	0GB	0.0	NA	0.0	0	0	0	0	39.4	2.6	440	1046	3490	18445	3947	0.0	0	12.3	4.8	18.5	readrandom.t32	2023-02-12T19:48:38	8.0.0		a72f591825
817781	207.1	107GB	0GB	0.0	NA	0.0	0	0	0	0	39.1	329.7	1559	3949	11708	19654	3914	0.0	0	12.1	4.8	17.6	multireadrandom.t32	2023-02-12T21:15:11	8.0.0		a72f591825
800529	202.7	107GB	0GB	0.0	NA	0.0	0	0	0	0	40.0	336.0	1615	4130	11987	23272	3998	0.0	0	12.1	4.9	18.3	multireadrandom.t32	2023-02-12T22:30:05	8.0.0		a72f591825
```

简单来说，开了AIO和没开AIO，没啥区别? 我没办法解释

没有使用folly的db_bench我还没测。有空我再补充

---

2023-02-20

重新测了一组数据

```bash
ASYNC_IO=1 NUM_THREADS=32 NUM_KEYS=100000000 DB_DIR=/data/tmp/ben WAL_DIR=/data/tmp/wal ./benchmark.sh multireadrandom
NUM_THREADS=32 NUM_KEYS=100000000 DB_DIR=/data/tmp/ben WAL_DIR=/data/tmp/wal ./benchmark.sh multireadrandom


ASYNC_IO=1 NUM_THREADS=32 NUM_KEYS=100000000 DB_DIR=/data/tmp/ben WAL_DIR=/data/tmp/wal ./benchmark.sh readrandom
NUM_THREADS=32 NUM_KEYS=100000000 DB_DIR=/data/tmp/ben WAL_DIR=/data/tmp/wal ./benchmark.sh readrandom


ASYNC_IO=1 NUM_THREADS=32 NUM_KEYS=100000000 DB_DIR=/data/tmp/ben WAL_DIR=/data/tmp/wal ./benchmark.sh multireadrandom
NUM_THREADS=32 NUM_KEYS=100000000 DB_DIR=/data/tmp/ben WAL_DIR=/data/tmp/wal ./benchmark.sh multireadrandom


ASYNC_IO=1 NUM_THREADS=32 NUM_KEYS=100000000 DB_DIR=/data/tmp/ben WAL_DIR=/data/tmp/wal ./benchmark.sh readrandom
NUM_THREADS=32 NUM_KEYS=100000000 DB_DIR=/data/tmp/ben WAL_DIR=/data/tmp/wal ./benchmark.sh readrandom
```

结果

```txt
# ops_sec - operations per second
# mb_sec - ops_sec * size-of-operation-in-MB
# lsm_sz - size of LSM tree
# blob_sz - size of BlobDB logs
# c_wgb - GB written by compaction
# w_amp - Write-amplification as (bytes written by compaction / bytes written by memtable flush)
# c_mbps - Average write rate for compaction
# c_wsecs - Wall clock seconds doing compaction
# c_csecs - CPU seconds doing compaction
# b_rgb - Blob compaction read GB
# b_wgb - Blob compaction write GB
# usec_op - Microseconds per operation
# p50, p99, p99.9, p99.99 - 50th, 99th, 99.9th, 99.99th percentile response time in usecs
# pmax - max response time in usecs
# uptime - RocksDB uptime in seconds
# stall% - Percentage of time writes are stalled
# Nstall - Number of stalls
# u_cpu - #seconds/1000 of user CPU
# s_cpu - #seconds/1000 of system CPU
# rss - max RSS in GB for db_bench process
# test - Name of test
# date - Date/time of test
# version - RocksDB version
# job_id - User-provided job ID
# githash - git hash at which db_bench was compiled
ops_sec	mb_sec	lsm_sz	blob_sz	c_wgb	w_amp	c_mbps	c_wsecs	c_csecs	b_rgb	b_wgb	usec_op	p50	p99	p99.9	p99.99	pmax	uptime	stall%	Nstall	u_cpu	s_cpu	rss	test	date	version	job_id	githash
4325990	1095.4	107GB	0GB	0.0	NA	0.0	0	0	0	0	7.2	62.5	253	613	1257	337223	740	0.0	0	17.3	2.3	23.6	multireadrandom.t32	2023-02-19T21:15:01	8.0.0		a72f591825
4309570	1091.2	107GB	0GB	0.0	NA	0.0	0	0	0	0	7.3	62.3	263	536	1133	46141	743	0.0	0	17.2	2.3	24.2	multireadrandom.t32	2023-02-19T20:35:12	8.0.0		a72f591825


4425381	1120.5	107GB	0GB	0.0	NA	0.0	0	0	0	0	7.1	4.4	28	170	453	427580	724	0.0	0	17.3	2.3	24.1	readrandom.t32	2023-02-19T21:29:13	8.0.0		a72f591825
4391332	1111.9	107GB	0GB	0.0	NA	0.0	0	0	0	0	7.1	4.4	29	169	368	431012	729	0.0	0	17.3	2.3	24.4	readrandom.t32	2023-02-19T22:04:38	8.0.0		a72f591825

4103189	1039.0	107GB	0GB	0.0	NA	0.0	0	0	0	0	7.7	59.1	342	776	3829	418001	780	0.0	0	16.4	2.1	17.9	multireadrandom.t32	2023-02-19T23:03:14	8.0.0		a72f591825
4143277	1049.1	107GB	0GB	0.0	NA	0.0	0	0	0	0	7.7	59.0	322	564	4243	19460	773	0.0	0	16.3	2.2	21.4	multireadrandom.t32	2023-02-19T23:30:45	8.0.0		a72f591825


4291820	1086.7	107GB	0GB	0.0	NA	0.0	0	0	0	0	7.4	4.1	112	198	368	25312	746	0.0	0	16.7	2.0	21.9	readrandom.t32	2023-02-19T22:48:11	8.0.0		a72f591825
4004245	1013.9	107GB	0GB	0.0	NA	0.0	0	0	0	0	8.0	3.9	130	235	581	248845	800	0.0	0	16.3	2.3	17.8	readrandom.t32	2023-02-19T22:32:36	8.0.0		a72f591825
```


不用folly的 db_bench 开asyncio要比不开快一丢丢

folly 版本开asyncio也要比不开快一丢丢

用folly反而比不用folly更慢了

感觉是folly用的不对

---


