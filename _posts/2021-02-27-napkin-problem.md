---
layout: post
title: Napkin Problem
categories: [database, translation]
tags: [redis]
---

现在是20年代了，计算机领域所有的指标都在变快。如何才能快速估算？

这里有一个估算系列的问题https://sirupsen.com/napkin/，以及需要的参数 https://github.com/sirupsen/napkin-math

<!-- more -->
作者在macbook2017拿到了一组数据

| Operation                           | Latency                                  | Throughput | 1 MiB  | 1 GiB  |
| ----------------------------------- | ---------------------------------------- | ---------- | ------ | ------ |
| Sequential Memory R/W (64 bytes)    | 5 ns                                     | 10 GiB/s   | 100 μs | 100 ms |
| Hashing, not crypto-safe (64 bytes) | 25 ns                                    | 2 GiB/s    | 500 μs | 500 ms |
| Random Memory R/W (64 bytes)        | 50 ns                                    | 1 GiB/s    | 1 ms   | 1 s    |
| Fast Serialization `[8]` `[9]` †    | N/A                                      | 1 GiB/s    | 1 ms   | 1s     |
| Fast Deserialization `[8]` `[9]` †  | N/A                                      | 1 GiB/s    | 1 ms   | 1s     |
| System Call                         | 500 ns                                   | N/A        | N/A    | N/A    |
| Hashing, crypto-safe (64 bytes)     | 500 ns                                   | 200 MiB/s  | 10 ms  | 10s    |
| Sequential SSD read (8 KiB)         | 1 μs                                     | 4 GiB/s    | 200 μs | 200 ms |
| Context Switch `[1] [2]`            | 10 μs                                    | N/A        | N/A    | N/A    |
| Sequential SSD write, -fsync (8KiB) | 10 μs                                    | 1 GiB/s    | 1 ms   | 1 s    |
| TCP Echo Server (32 KiB)            | 10 μs                                    | 4 GiB/s    | 200 μs | 200 ms |
| Sequential SSD write, +fsync (8KiB) | 1 ms                                     | 10 MiB/s   | 100 ms | 2 min  |
| Sorting (64-bit integers)           | N/A                                      | 200 MiB/s  | 5 ms   | 5 s    |
| Random SSD Seek (8 KiB)             | 100 μs                                   | 70 MiB/s   | 15 ms  | 15 s   |
| Compression `[3]`                   | N/A                                      | 100 MiB/s  | 10 ms  | 10s    |
| Decompression `[3]`                 | N/A                                      | 200 MiB/s  | 5 ms   | 5s     |
| Serialization `[8]` `[9]` †         | N/A                                      | 100 MiB/s  | 10 ms  | 10s    |
| Deserialization `[8]` `[9]` †       | N/A                                      | 100 MiB/s  | 10 ms  | 10s    |
| Proxy: Envoy/ProxySQL/Nginx/HAProxy | 50 μs                                    | ?          | ?      | ?      |
| Network within same region `[6]`    | 250 μs                                   | 100 MiB/s  | 10 ms  | 10s    |
| {MySQL, Memcached, Redis, ..} Query | 500 μs                                   | ?          | ?      | ?      |
| Random HDD Seek (8 KiB)             | 10 ms                                    | 70 MiB/s   | 15 ms  | 15 s   |
| Network between regions `[6]`       | [Varies](https://www.cloudping.co/grid#) | 25 MiB/s   | 40 ms  | 40s    |
| Network NA East <-> West            | 60 ms                                    | 25 MiB/s   | 40 ms  | 40s    |
| Network EU West <-> NA East         | 80 ms                                    | 25 MiB/s   | 40 ms  | 40s    |
| Network NA West <-> Singapore       | 180 ms                                   | 25 MiB/s   | 40 ms  | 40s    |
| Network EU West <-> Singapore       | 160 ms                                   | 25 MiB/s   | 40 ms  | 40s    |



本篇文章长期翻译对应的议题文档。




---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>

