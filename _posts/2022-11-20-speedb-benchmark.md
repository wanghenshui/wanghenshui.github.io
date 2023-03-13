---
layout: post
title: speedb benchmark
categories: [database]
tags: [rocksdb,speedb,bloom filter,paired bloom filter]
---
speedb是fork rocksdb 也是apache，那拿他的代码patch到rocksdb上是合规的行为么？

<!-- more -->

我的机器是双十一新拼的7950x 5G PBO开了

测试使用的固态是凯侠 RC20 1T 拼多多 400到手。配置的xfs

磁盘性能，使用diskexploer跑了个图, 这个是我的魔改版，https://github.com/wanghenshui/diskplorer 原来的版本有问题，可能会导致磁盘被抹

```bash
sudo ./diskplorer.py /dev/nvme1n1 --filename=/data/tmp/tempfile --result-file koxia.json --size-limit=1G
```

<img src="https://user-images.githubusercontent.com/8872493/202881466-94430102-44c9-4140-9822-c3dbf7bc76f7.png" alt="" width="80%">

压测命令

```bash
#rocksdb
TEST_TMPDIR=/data/tmp/dbbench ./db_bench --benchmarks=fillrandom,readrandom -max_background_jobs=12 -num=400000000 -target_file_size_base=33554432

#speedb
TEST_TMPDIR=/data/tmp ./db_bench  --benchmarks=fillrandom,readrandom -max_background_jobs=12 -num=400000000 -target_file_size_base=33554432
TEST_TMPDIR=/data/tmp ./db_bench  --memtablerep=speedb.HashSpdRepFactory --benchmarks=fillrandom,readrandom -max_background_jobs=12 -num=400000000 -target_file_size_base=33554432
TEST_TMPDIR=/data/tmp ./db_bench  -filter_uri=speedb.PairedBloomFilter:23.4   --benchmarks=fillrandom,readrandom -max_background_jobs=12 -num=400000000 -target_file_size_base=33554432
TEST_TMPDIR=/data/tmp ./db_bench  -filter_uri=speedb.PairedBloomFilter:23.4  --memtablerep=speedb.HashSpdRepFactory --benchmarks=fillrandom,readrandom -max_background_jobs=12 -num=400000000 -target_file_size_base=33554432
```


结果



| 命令                              | fillrandom | readrandom |
| --------------------------------- | ---------- | ---------- |
| rocksdb 7.9                       | 74.5 MB/s  | 9.6 MB/s   |
| speedb rocks版本                  | 51.0 MB/s  | 7.2 MB/s   |
| speedb 使用 paired bloom filter   | 66.3 MB/s  | 24.2 MB/s  |
| speedb 使用 sorted hash  memtable | 53.2 MB/s  | 4.9 MB/s   |
| speedb 上面两个都用               | 66.0 MB/s  | 24.8 MB/s  |


具体结果可以看 https://github.com/wanghenshui/wanghenshui.github.io/issues/67

这个speedb的paiared bloom filter确实值得研究一下

---


