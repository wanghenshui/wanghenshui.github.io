---
layout: post
title: Map Reduce整理
categories: [database]
tags: [mapreduce, mit6824]
---
> 参考资料
>
> https://lvsizhe.github.io/course/2020/03/mapreduce.html
>
> https://zhuanlan.zhihu.com/p/34849261

<img src="https://wanghenshui.github.io/assets/mr-overview.png" alt=""  width="100%">

<!-- more -->

基本逻辑

1. 作为输入的文件会被分为 ![[公式]](https://www.zhihu.com/equation?tex=M) 个 Split，每个 Split 的大小通常在 16~64 MB 之间
2. 如此，整个 MapReduce 计算包含 ![[公式]](https://www.zhihu.com/equation?tex=M) 个Map 任务和 ![[公式]](https://www.zhihu.com/equation?tex=R) 个 Reduce 任务。Master 结点会从空闲的 Worker 结点中进行选取并为其分配 Map 任务和 Reduce 任务
3. 收到 Map 任务的 Worker 们（又称 Mapper）开始读入自己对应的 Split，将读入的内容解析为输入键值对并调用由用户定义的 Map 函数。由 Map 函数产生的中间结果键值对会被暂时存放在缓冲内存区中
4. 在 Map 阶段进行的同时，Mapper 们周期性地将放置在缓冲区中的中间结果存入到自己的本地磁盘中，同时根据用户指定的 Partition 函数（默认为 ![[公式]](https://www.zhihu.com/equation?tex=hash%28%5Ctextrm%7Bkey%7D%29%5C%3A+%5Ctextbf%7Bmod%7D%5C%3A+R)）将产生的中间结果分为 ![[公式]](https://www.zhihu.com/equation?tex=R) 个部分。任务完成时，Mapper 便会将中间结果在其本地磁盘上的存放位置报告给 Master
5. Mapper 上报的中间结果存放位置会被 Master 转发给 Reducer。当 Reducer 接收到这些信息后便会通过 RPC 读取存储在  Mapper 本地磁盘上属于对应 Partition 的中间结果。在读取完毕后，Reducer  会对读取到的数据进行排序以令拥有相同键的键值对能够连续分布
6. 之后，Reducer 会为每个键收集与其关联的值的集合，并以之调用用户定义的 Reduce 函数。Reduce 函数的结果会被放入到对应的 Reduce Partition 结果文件

优化考虑 **减少磁盘或者网络的IO**

- **数据的局部性**: MR框架会通过查询分布式文件系统(DFS)，尽可能的将task调度到数据所的物理机、或者接近的网段上；这个能够有效减少需要传输的数据量。
- **任务的粒度**:  一般而言，需要让M和R远远大于worker机器的数量，即让任务粒度足够小。这样一来可以实现更好的负载均衡。性能强的机器处理更多的task、性能差的处理得少一些；二来task重做的时候，发生重做的部分会更少些。经验上，最好将任务分割成处理64MB/128MB粒度的task为佳[4](https://lvsizhe.github.io/course/2020/03/mapreduce.html#fn:4)
- **Backup-task**:  在现实中，可能出现一些任务执行不正常(比如调度到故障机器)上，执行极慢导致整个job都在等待这几个任务结束。因此解决的手段是对于一些任务(一般选择最后调度上去的那批、或者执行时间超出大多数其他任务平均时长许多的)，重复的提交一个，然后master先收取第一个执行完成的结果。这能够有效的消除长尾问题。
- **分区hash可定制**: MR框架提供了可定制的分区计算方法，使得业务可以根据需要，引入自身场景以方便编写任务。比如在建库的时候，可以以hostname来作为hash的key，让同hostname的网页都落入同一个reduce进行处理。
- **顺序保证**: 在框架中，确保了每个分区内部，都是按照key的顺序进行处理的，这样就给全局排序这样的任务提供了实现的基础。
- **Combiner**: 在许多场景下(比如WordCount)，可以在map端作一轮的合并，然后让reduce在map已经合并过的基础上进一步合并结果。因此，引入了Map端的Combiner的概念，以显著减少map-reduce之间需要走网络传输的数据量。
- **信息披露**: 为方便用户，MR框架可以查看所有task的执行状态，并提供了Counter功能进行一些用户层面的统计计数。这样用户就能够从这些基础信息中，了解自己任务的执行情况，在外围做一些诸如监控、管理类的行为。

可用性保证

- Worker挂掉/慢 直接杀掉重做
- Reducer丢失数据 FS系统保证

---

说了半天都是别人的用法，现在流行的做法是用spark了，而且上面没有考虑的点很多。这里罗列一下

- 任务的粒度 引申出来的问题
    - 任务的优先级？谁先谁后，机器的上传下载带宽有限，执行快慢也不同
    - 任务的取消？任务执行的时间长度不同，但一批任务作为一个整体，有一个任务失败，整体就必然失败，所以取消要有。而且如果任务之间有传递链接关系，那取消任务能节省非常多的时间
    - 任务的排队？作为一个系统，影响的环节非常的多。而这个系统又是多租户使用，比如一个导入系统，处理完数据要导入到不同的机器中，但机器的带宽有限，这又引入了排队的问题
- 状态。上面的或者说spark，都是无状态。无状态当然很简单。引入状态，痛苦的东西就来了。
    - 比如增量的map reduce，如何维护管理全量/增量数据？
        - 引入对象存储又会引入新的问题。直接用分布式文件系统？这里的抉择可能影响整个map reduce系统的性能
    - 状态的引入，MP期间发生了状态的变更，数据上线存在问题。旧的元数据和新的元数据要做好映射逻辑。不然对不上。这里不能细想，细想一堆问题
- 调度器以及元数据管理，维护，可用性保证。这些都是小事

---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>
