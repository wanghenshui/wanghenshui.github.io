---
layout: post
title: (译)Consistent Hashing: Algorithmic Tradeoffs
categories: [database]
tags: [hash]
---

> 原文链接 https://medium.com/@dgryski/consistent-hashing-algorithmic-tradeoffs-ef6b8e2fcae8
>
> 加了很多自己的理解

## 概念 一个好的分布式hash算法

>  [引自这里](https://gardiant.github.io/2019/03/14/%E4%B8%80%E8%87%B4%E6%80%A7hash%E4%B8%8E%E8%B4%9F%E8%BD%BD%E5%9D%87%E8%A1%A1/)

> **平衡性(Balance)**
> 平衡性是指哈希的结果能够尽可能分布到所有的缓冲中去，这样可以使得所有的缓冲空间都得到利用。很多哈希算法都能够满足这一条件。
>
> **单调性(Monotonicity)**
> 单调性是指如果已经有一些内容通过哈希分派到了相应的缓冲中，又有新的缓冲区加入到系统中，那么哈希的结果应能够保证原有已分配的内容可以被映射到新的缓冲区中去，而不会被映射到旧的缓冲集合中的其他缓冲区。简单的哈希算法往往不能满足单调性的要求，如最简单的线性哈希：x = (ax + b) mod  (P)，在上式中，P表示全部缓冲的大小。不难看出，当缓冲大小发生变化时(从P1到P2)，原来所有的哈希结果均会发生变化，从而不满足单调性的要求。哈希结果的变化意味着当缓冲空间发生变化时，所有的映射关系需要在系统内全部更新。而在P2P系统内，缓冲的变化等价于Peer加入或退出系统，这一情况在P2P系统中会频繁发生，因此会带来极大计算和传输负荷。单调性就是要求哈希算法能够应对这种情况。
>
> **分散性(Spread)**
> 在分布式环境中，终端有可能看不到所有的缓冲，而是只能看到其中的一部分。当终端希望通过哈希过程将内容映射到缓冲上时，由于不同终端所见的缓冲范围有可能不同，从而导致哈希的结果不一致，最终的结果是相同的内容被不同的终端映射到不同的缓冲区中。这种情况显然是应该避免的，因为它导致相同内容被存储到不同缓冲中去，降低了系统存储的效率。分散性的定义就是上述情况发生的严重程度。好的哈希算法应能够尽量避免不一致的情况发生，也就是尽量降低分散性。
>
> **负载(Load)**
> 负载问题实际上是从另一个角度看待分散性问题。既然不同的终端可能将相同的内容映射到不同的缓冲区中，那么对于一个特定的缓冲区而言，也可能被不同的用户映射为不同的内容。与分散性一样，这种情况也是应当避免的，因此好的哈希算法应能够尽量降低缓冲的负荷。
>
> **平滑性(Smoothness)**
> 平滑性是指缓存服务器的数目平滑改变和缓存对象的平滑改变是一致的。



几种方案

### 直接求余数

这里要直接对key取hash，然后在取余数，落到具体的server上  `server := serverList[hash(key) % N]`

这里的hash要快，还要有好的碰撞率，不能单纯的只追求速度不考虑碰撞率。xxhash在性能和碰撞率上都做的很好。实际性能和std::hash差不多 https://github.com/Cyan4973/xxHash/issues/236#issuecomment-522051621 这里有个快的但是根本没法用的hash https://github.com/jandrewrogers/AquaHash/issues/7 hash算法用aes指令实现不行。这里就不展开了

 问题在于可用性，如果一个节点坏了，如何搬迁保证搬迁数据最小，增删节点，如何搬迁数据？要么抽象一层，底层FS做好分布式，支持文件路径，节点坏了直接路径被其他节点接管。如果不能提供这种支持，那就只能考虑搬迁数据的最小化，以及搬迁的维护问题



## hash ring

如果hash映射成一组范围，针对范围进行分裂/搬迁，就可以了，cassandra dynamo都是这么做的，最小节点就是vnode

还是存在问题，增加节点个数导致的分配不均匀，对于这种场景，xxhash之类的hash只是工具，没有针对个数。新加入的节点并没有很好的分配请求，新家的节点被匀了后面的节点，请求更多分配在前面的节点。当然。分配也可以通过程序的额外代码来调整，使之均匀。多做一些工作

- 引入新方案，[jumphash](https://arxiv.org/abs/1406.2294) 这里设计了一个和bucket相关的hash。

```c++
int32_t JumpConsistentHash(uint64_t key, int32_t num_buckets) {
  int64_t b = -1, j = 0;
  while (j < num_buckets) {
    b = j;
    key = key * 2862933555777941757ULL + 1;
    j = (b + 1) * (double(1LL << 31) / double((key >> 33) + 1));
  }
  return b;
}
```

这里有一个jumphash的[解释](https://zhuanlan.zhihu.com/p/104124045) 更直观一些，这里不展开讲了

这有个issue jump hash方案迁移还挺快？定位快的功劳吗https://github.com/gluster/glusterfs/issues/1706

- 其他方案 [Rendezvous hashing](https://colobu.com/2016/03/22/jump-consistent-hash/)，计算一个key应该放入到哪个bucket时，它使用哈希函数h(key,bucket)计算每个候选bucket的值，然后返回值最大的bucket。buckets比较多的时候耗时也较长，有人也提出了一些改进的方法，比如将bucket组织成tree的结构，但是在reblance的时候花费时间又长了 放在客户端比较合适
- [Multi-probe consistent hashing](https://arxiv.org/pdf/1505.00062.pdf) 估算？
- [Maglev Hashing](https://static.googleusercontent.com/media/research.google.com/zh-CN//pubs/archive/44824.pdf)多层查找表

感觉也就粗暴分slot比较省事儿。jump hash也可以接受，其他的算法就比较少见了。了解即可



## 参考

我搜了半天发现这里有个整理的非常细的

https://blog.laisky.com/p/consistent-hashing/ 直接看这个也挺好


---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>