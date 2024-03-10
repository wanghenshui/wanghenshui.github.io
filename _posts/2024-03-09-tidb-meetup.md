---
layout: post
title: TiDB深圳站见闻
categories: [database]
tags: [tidb]
---

吃得很饱，那个华夫饼真好吃啊

<!-- more -->

简单过一下这几个汇报

PPT在这里 https://asktug.com/t/topic/1022494/37?replies_to_post_number=1

## 从多套Mysql到 1 套TiDB

这个玩法风险还挺大的

兼容性问题
- AUTO_ID_CACHE=1
- utf8mb4
- 排序？

同步校验/用TiCDC反向同步

- 慢查询 索引
- IO热点/ 随机自增ID

## 滔搏 ToC 系统数据库迁移 TiDB 实践

没错是那个电竞俱乐部那个滔博

主要工作是验证工作，没啥意思 https://github.com/Percona-Lab/query-playback.git


## NewSQL分布式数据库选型和实践 趣丸基于 TiDB 的实践总结

这个趣丸是做TT语音的，也有LPL俱乐部

他们公司应该是买了TiDB他们的服务了。HTAP主要选型点

数据规模 142 个节点，12 套集群。主要版本是 5.4 和 6.5，其中最大集群数据量接近 100 T

主要问题，版本不可回退 以及资源隔离问题

- GC导致突刺
- Balance 期间突刺
- 需要多租户
- 需要S3

他们用UUID的。幽默

## SHOPLINE TiDB4.0到6.5升级之路

这个talk算有意思的，遇到了bug 订阅CDC遇到盘故障，tikv OOM，导致CDC雪崩了

- 如何避免这种问题？本质还是处理订阅失败不够优雅，CDC大量重试占用内存，要及时拒绝

原来的解决方案就是揪出来表，重启节点，重试任务，后续直接更新6.5解决，并且开压缩成本降了


## 网易游戏规模化 TiDB SaaS服务建设

规模 120 集群 800T数据，最大70T 60+节点

规格
- 高性能 18C180G1T
- 高存储 9C90G2T
- 普通 9C90GT

数据同步

<img src="https://wanghenshui.github.io/assets/tidb-meetup5.png" width="100%">

问题
- 卡顿检测不到
- 热点检测不到 RANDOM
- 空间异常GC不及时 时间分区表 定期删
- leader频繁抖动，region太多了 监控region个数

<img src="https://wanghenshui.github.io/assets/tidb-meetup6.png" width="100%">

raft-engine是bitcask，可能顶不住大量热点写吧，批量写没有rocksdb好

没有提问机会没问到

## TiDB资源管控特性解读及应用探索

介绍多租户设计，都在抄CosmosDB

<img src="https://wanghenshui.github.io/assets/tidb-meetup7.png" width="100%">

<img src="https://wanghenshui.github.io/assets/tidb-meetup8.png" width="100%">

<img src="https://wanghenshui.github.io/assets/tidb-meetup9.png" width="100%">

隔离/细分，削峰填谷

这个和网易那个，这俩算有营养的


## TiDB 7.5 LTS 高性能批处理方案

介绍了个batch on insert into语法

## 彩蛋

<img src="https://wanghenshui.github.io/assets/tidb-meetup4.jpg" width="100%">

这哥们比较幽默

- 升级怕无法回滚？我直接整个服务打镜像备份
- 数据备份慢？我直接CFS文件系统级别备份
- 利用弹性网卡，什么名字服务，弹性网卡就够用

简单说就是全靠云鸡架，艺高人胆大

---

小礼品和吃的

我吃了好多华夫饼，这个真挺好吃，淘宝下单了

吃得很饱，下回还来

<img src="https://wanghenshui.github.io/assets/tidb-meetup1.jpg" width="30%"><img src="https://wanghenshui.github.io/assets/tidb-meetup2.jpg" width="30%"><img src="https://wanghenshui.github.io/assets/tidb-meetup3.jpg" width="30%">