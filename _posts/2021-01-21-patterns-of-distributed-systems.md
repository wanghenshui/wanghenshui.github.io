---
layout: post
title: (译)分布式系统的模式
categories: [database, system]
tags: [kafka, etcd,cassandra, zookeeper, distributed-systems]

---

> 看到网友推荐这篇博客，整理归纳一下 https://martinfowler.com/articles/patterns-of-distributed-systems/
>
> 我发现有人翻译了，但是翻译的不全。 https://xie.infoq.cn/article/f4d27dd3aa85803841d050825

这里的分布式系统是指所有的系统，共性问题

| Type of platform/framework       | Example                                    |
| -------------------------------- | ------------------------------------------ |
| Databases数据库                  | Cassandra, HBase, Riak                     |
| Message Brokers消息队列          | Kafka, Pulsar                              |
| Infrastructure基础架构元信息管理 | Kubernetes, Mesos, Zookeeper, etcd, Consul |
| In Memory Data/Compute Grids网格 | Hazelcast, Pivotal Gemfire                 |
| Stateful Microservices微服务     | Akka Actors, Axon                          |
| File Systems文件系统             | HDFS, Ceph                                 |

## 面临的共性问题

- 进程崩溃
  - 配置文件修改导致的暂时下线（大公司已经出过很多起了）
  - 异常场景没处理，比如磁盘满
  - 云场景下的其他影响的场景

这些场景下如何处理数据丢失？解决方案：WAL

- 网络延迟问题
  - 不知道其他进程的状态是否正常 解决方案： 心跳
  - 脑裂导致的数据冲突 解决方案 Quorum



- 另一种异常，进程暂停，可能是内部在忙，没有及时响应，可能是gc引起的延迟等等
  -  Generation Clock 我的理解就是term 推进，老master检测自己不是最新的index，就自动降低身份 也就是Lamport’s timestamp

- 时间同步问题，ntp是不准的甚至是会出错的，有原子钟方案，也有lamport逻辑时钟方案 

  ~~（其实原子钟方案比较简单，一个gps原子钟七八万，我之前的老项目用过，这个成本对于互联网公司还好吧，为啥都不用呢，不方便部署么）~~



## 一个整合方案，以及涉及到具体的设计细节

<img src="https://wanghenshui.github.io/assets/paterns.png" alt="" width="80%">



### WAL

首先是WAL 也就是commit log commit log要保证持久性

每个日志要有独立的标记，依此来分段整理，方便写，但是不能无限长，所以要有个Low-Water-Mark标记，其实就是后台线程定期删日志

日志更新就相当于队列追加写了，为了吞吐可能要异步一些

![img](https://martinfowler.com/articles/patterns-of-distributed-systems/wal.png)



考虑如何实现这样一个kv；

首先kv得能序列化成log，并且能从log恢复

需要支持指定snapshot/timestap恢复，这两种是淘汰判定的标准，也就是一个unit



#### Low-Water-Mark实现方案

- 基于快照snapshot，每次成功的写入index都是一次快照，快照落盘就过期，可以删掉	有点像生产消费

zookeeper etcd都是这个方案，代码类似下面

```java
public SnapShot takeSnapshot() {
    Long snapShotTakenAtLogIndex = wal.getLastLogEntryId();
    return new SnapShot(serializeState(kv), snapShotTakenAtLogIndex);
}

//Once a snapshot is successfully persisted on the disk, the log manager is given the low water mark to discard the older logs.

List<WALSegment> getSegmentsBefore(Long snapshotIndex) {
    List<WALSegment> markedForDeletion = new ArrayList<>();
    List<WALSegment> sortedSavedSegments = wal.sortedSavedSegments;
    for (WALSegment sortedSavedSegment : sortedSavedSegments) {
        if (sortedSavedSegment.getLastLogEntryId() < snapshotIndex) {
            markedForDeletion.add(sortedSavedSegment);
        }
    }
    return markedForDeletion;
}
```

- 基于时间，有点像日志轮转

kafka就是这种方案

```java
private List<WALSegment> getSegmentsPast(Long logMaxDurationMs) {
    long now = System.currentTimeMillis();
    List<WALSegment> markedForDeletion = new ArrayList<>();
    List<WALSegment> sortedSavedSegments = wal.sortedSavedSegments;
    for (WALSegment sortedSavedSegment : sortedSavedSegments) {
        if (timeElaspedSince(now, sortedSavedSegment.getLastLogEntryTimestamp()) > logMaxDurationMs) {
            markedForDeletion.add(sortedSavedSegment);
        }
    }
    return markedForDeletion;
}

private long timeElaspedSince(long now, long lastLogEntryTimestamp) {
    return now - lastLogEntryTimestamp;
}
```




---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>

