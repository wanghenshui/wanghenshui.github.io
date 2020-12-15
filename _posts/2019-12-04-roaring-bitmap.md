---
layout: post
title: roaring bitmap aka RBM
categories: [algorithm]
tags: [bitmap]
---



首先，redis的bitmap占用空间是很恐怖的，512M，就算用的很少也是512M

但是使用概率型数据结构，比如hyperloglog，省空间，但是有误差，且只能增不能删

又想要大量标记，又不想有误差，又不想占用大空间，解决方案 roaring bitmap

对稀疏位图进行压缩，减少内存占用并提高效率。比较有代表性的有WAH、EWAH、Concise，以及RoaringBitmap。前三种算法都是基于[行程长度编码](https://links.jianshu.com/go?to=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FRun-length_encoding)（Run-length encoding, RLE）做压缩的，而RoaringBitmap算是它们的改进

1. 支持动态修改位图（静态的位图有其它压缩方式）
2. 利用SIMD加速位图操作

![image-20201214204833017](https://wanghenshui.github.io/assets/image-20201214204833017.png)





32位无符号整数按照高16位分桶，即最多可能有216=65536个桶，论文内称为container。存储数据时，按照数据的高16位找到container（找不到就会新建一个），再将低16位放入container中。也就是说，一个RBM就是很多container的集合

- 第一层称之为Chunk，每个Chunk表示该区间取值范围的base(n**2^16, 0<= n < 2^16)**，如果该取值范围内没有数据则Chunk不会创建
- 第二层称之为Container，会依据数据分布进行创建（Container内的值实际是区间内的offset）

#### ArrayContainer

当桶内数据的基数不大于4096时，会采用它来存储，其本质上是一个unsigned short类型的有序数组。数组初始长度为4，随着数据的增多会自动扩容（但最大长度就是4096）。另外还维护有一个计数器，用来实时记录基数。

- 当区间内数量少于4096时，数组占用更紧凑；多于4096，则使用位图更经济

#### BitmapContainer

当桶内数据的基数大于4096时，会采用它来存储，其本质就是上一节讲过的普通位图，用长度固定为1024的unsigned long型数组表示，亦即位图的大小固定为216位（8KB）。它同样有一个计数器。

上图中的第三个container基数远远大于4096，所以要用BitmapContainer存储。

#### RunContainer

RunContainer在图中并未示出，初始的RBM实现中也没有它，而是在本节开头的第二篇论文中新加入的。它使用可变长度的unsigned short数组存储用行程长度编码（RLE）压缩后的数据。

```vash
AAAAAAbbbXXXXXt
6A3b5X1t
```

由此可见，RunContainer的压缩效果可好可坏。考虑极端情况：如果所有数据都是连续的，那么最终只需要4字节；如果所有数据都不连续（比如全是奇数或全是偶数），那么不仅不会压缩，还会膨胀成原来的两倍大。所以，RBM引入RunContainer是作为其他两种container的折衷方案。

O(logn)的查找性能：

- 首先二分查找key值的高16位是否在分片（chunk）中

- 如果分片存在，则查找分片对应的Container是否存

- - 如果Bitmap Container，查找性能是O(1)
  - 其它两种Container，需要进行二分查找



### 参考链接

- 论文地址 https://arxiv.org/pdf/1603.06549.pdf
- 官网 http://roaringbitmap.org/，有各种实现 c实现 https://github.com/RoaringBitmap/CRoaring
- redis的bitmap不是这个方案，社区实现了一个module https://github.com/aviggiano/redis-roaring，直接搬croaring
- 图来自 https://blog.bcmeng.com/post/doris-bitmap.html 这篇介绍，doris了解一下，doris和clickhouse啥区别？
  - https://github.com/apache/incubator-doris
  - 他这篇hbase rowkey设计也不错，基本覆盖了书里介绍的内容 https://blog.bcmeng.com/post/hbase-rowkey.html
- 本文内容整理自 https://zhuanlan.zhihu.com/p/39828878和https://www.jianshu.com/p/818ac4e90daf


---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>