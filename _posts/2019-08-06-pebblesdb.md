---
layout: post
categories: database
title: pebblesdb
tags: [c++,rocksdb,lsm]
---

  

---



是pebblesdb的一些资料整理~~和总结~~

参考链接1 是论文

参考链接2是提到的一点介绍

>而在 2017 年 SOSP 上发表的论文 [PebblesDB](https://link.zhihu.com/?target=http%3A//www.cs.utexas.edu/~vijay/papers/sosp17-pebblesdb.pdf) 提出了另外一种思路。在传统 LSM-Tree 中，每一层由多个 SSTable 组成，每一个 SSTable 中保存了一组排好序 Key-Value，相同层的 SSTable 之间的 Key 没有重叠。当进行 Compaction 时，上层的 SSTable 需要与下层的 SSTable 进行合并，也就是将上层的 SSTable 和下层的 SSTable 读取到内存中，进行合并排序后，组成新的 SSTable，并写回到磁盘中。由于 Compaction 的过程中需要读取和写入下层的 SSTable，所以造成了读写放大，影响应能。

> PebblesDB 将 LSM-Tree 和 Skip-List 数据结构进行结合。在 LSM-Tree 中每一层引入 Guard 概念。 每一层中包含多个 Guard，Guard 和 Guard 之间的 Key 的范围是有序的，且没有重叠，但 Guard 内部包含多个 SSTable，这些 SSTable 的 Key 的范围允许重叠。
>
> 当需要进行 Compaction 时，只需要将上层的 SSTable 读入内存，并按照下层的 Guard 将 SSTable 切分成多个新的 SSTable，并存放到下层对应的 Guard 中。在这个过程中不需要读取下层的 SSTable，也就在一定程度上避免了读写放大。作者将这种数据结构命名为 Fragemented Log-Structured Tree（FLSM）。PebblesDB 最多可以减低 6.7 倍的写放大，写入性能最多提升 105%。
>
> 和 WiscKey 类似，PebblesDB 也会多 Range Query 的性能造成影响。这是由于 Guard 内部的 SSTable 的 Key 存在重叠，所以在读取连续的 Key 时，需要同时读取 Guard 中所有的 SSTable，才能够获得正确的结果。



参考链接3pebblesdb的总结，博主写的不错

> skiplist的访问选择是一种guard，将这种guard推广到lsm上，然后通过guard组织数据，允许小范围的重复，但是这种guard是很难判定的。所以借鉴意义不大，而且读数据性能肯定也会下降，insert等操作也会加剧。

参考链接3也是pebblesdb的总结，

提到一个观点

> 弱化全局有序，切分片段，这样实际上加重了有序对系统的影响
>
> 比如scan，读性能肯定会下降。



参考链接5 6 是代码

参考链接7是个ppt介绍。值得看一看。方便理解论文

----

### ref

1. http://www.cs.utexas.edu/~vijay/papers/sosp17-pebblesdb.pdf
2. https://zhuanlan.zhihu.com/p/34455548
3. https://zhuanlan.zhihu.com/p/46069535
4. https://zhuanlan.zhihu.com/p/32225460
5. https://github.com/utsaslab/pebblesdb
6. https://github.com/xxks-kkk/HyperPebblesDB
7. http://www.cs.utexas.edu/~vijay/papers/pebblesdb-sosp17-slides.pdf



看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>