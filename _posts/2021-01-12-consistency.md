---
layout: post
title: 分布式系统中的一致性模型，以及事务
categories: [database]
tags: [acid, consistency]

---

 经典图

<img src="https://wanghenshui.github.io/assets/c.png" alt="" width="80%">



- Unavailable: 当出现网络隔离等问题的时候，为了保证数据的一致性，不提供服务。熟悉 CAP 理论的同学应该清楚，这就是典型的 CP 系统了。
- Sticky Available: 即使一些节点出现问题，在一些还没出现故障的节点，仍然保证可用，但需要保证 client 不能更换节点。
- Highly Available: 就是网络全挂掉，在没有出现问题的节点上面，仍然可用。



## 并发事务在没有隔离性保证时会导致哪些问题：

- Dirty Write 脏写 - 一个事务覆盖了另一个事务还没提交的中间状态
- Dirty Read 脏读 - 一个事务读到了另一个事务还没提交的中间值
- Non-Repeatable Read 不可重复读 - 一个事务中连续读取同一个值时返回结果不一样（中途被其他事务更改了）
- Phantom 幻读 - 当一个事务按照条件C检索出一批数据，还未结束。另外的事务写入了一个新的满足条件C的数据，使得前一个事务检索的数据集不准确。
- Lost Update 写丢失 - 先完成提交的事务的改动被后完成提交的事务覆盖了，导致前一个事务的更新丢失了。
- Cursor Lost Update - Lost Update的变种，和Cursor操作相关。
- Read Skew 偏读 - 事务在执行a+b期间，a，b值被其他事务更改了，导致a读到旧值，b读到新值
- Write Skew 偏写 - 事务连续执行if(a) then write(b) 时， a值被其他事务改了，类似超卖。

可以看到，由于隔离型相关的问题其实都是并发竞争导致的，所以和「多线程安全」问题非常相像，思路和方案也是共通的。 现代数据库系统已经将并发竞争问题抽象为隔离级别（Isolation level）来处理 ，也就是 ACID中的I。接下来我们看一下常见的隔离级别，以及能提供的保证：

- Read Uncommitted - 能读到另外事务未提交的修改。
- Read Committed - 能读到另外事务已经提交的修改。
- Cursor Stability - 使用 cursor 在事务里面引用特定的数据，当一个事务用 cursor 来读取某个数据的时候，这个数据不可能被其他事务更改，除非 cursor 被释放，或者事务提交。
- Monotonic Atomic View - 这个级别是 read committed 的增强，提供了一个原子性的约束，当一个在 T1 里面的 write 被另外事务 T2 观察到的时候，T1 里面所有的修改都会被 T2 给观察到。
- Repeatable Read - 可重复读，也就是对于某一个数据，即使另外的事务有修改，也会读取到一样的值。
- Snapshot - 每个事务都会在各自独立，一致的 snapshot 上面对数据库进行操作。所有修改只有在提交的时候才会对外可见。如果 T1 修改了某个数据，在提交之前另外的事务 T2 修改并提交了，那么 T1 会回滚。
- Serializable - 事务完全按照顺序依次执行，相当于强锁。

这是那个经典论文描述的场景 图片介绍。另外知乎有篇验证文章

<img src="https://wanghenshui.github.io/assets/isolation.png" alt="" width="80%">



## 一致性面临的问题

<img src="https://wanghenshui.github.io/assets/consistency-view.png" alt="" width="80%">



### server端视角

- 线性一致性（Linearizability）-  最强的单对象一致性模型，要求任何写操作都能立刻同步到其他所有进程，任何读操作都能读取到最新的修改。简单说就是实现进程间的 Java  volatile 语义。这是一种对顺序和实时性都要求很高的模型。要实现这一点，要求将所有读写操作进行全局排序。
- 顺序一致性（Sequential Consistency）：在线性一致性上放松了对实时性的要求。所有的进程以相同的顺序看到所有的修改，读操作未必能及时得到此前其他进程对同一数据的写更新。
- 因果一致性（Causal Consistency）：进一步放松了顺序要求，提高了可用性。读操作有可能看到和写入不同的顺序 。只对附加了因果关系的写入操作的顺序保证顺序性。“逻辑时钟”常用来为操作附加这种因果关系。
- PRAM一致性(Pipeline Random Access Memory)  ：多进程间顺序的完全放松，只为单个进程内的写操作保证顺序，但不保证不同的写进程之间的顺序。这种放松可以大幅提高并发处理能力。例如Kafka保证在一个分区内读操作可以看到写操作的顺序 ，但是不同分区间没有任何顺序保证。

### client端视角

- 单调读一致性（Monotonic-read Consistency），如果一个客户端读到了数据的某个版本n，那么之后它读到的版本必须大于等于n。
- 单调写一致性（Monotonic-write Consistency），保证同一个客户端的两个不同写操作，在所有副本上都以他们到达存储系统的相同的顺序执行。单调写可以避免写操作被丢失。
- 写后读一致性、读己之写一致性（Read-your-writes Consistency），如果一个客户端写了某个数据的版本n，那么它之后的读操作必须读到大于等于版本n的数据。
- 读后写一致性（Writes-follow-reads Consistency）保证一个客户端读到版本n数据后（可能是其他客户端写入的），随后的写操作必须要在版本号大于等于n的副本上执行。

PRAM一致性(Pipeline Random Access Memory)完全等同于读你的写、单调写和单调读。如果要追求读后写一致性，只能选择因果一致性。如果你需要完全的可用性，可以考虑牺牲阅读你的写，选择单调读 + 单调写。





线性一致性

我们可以利用线性一致性的原子性约束来**安全地修改状态**。我们定义一个类似`CAS（compare-and-set）`的操作，当且仅当寄存器持有某个值的时候，我们可以往它写入新值。 `CAS`操作可以作为互斥量，信号量，通道，计数器，列表，集合，映射，树等等的实现基础，使得这些共享数据结构变得可用。线性一致性保证了变更的**安全交错**。



顺序一致性，强调顺序，不是必须发生，但保持顺序发生

因果一致性，保证因果顺序，顺序一致性的子集

串行一致性，有条件必严格

最终一致性以及CRDTs数据结构



---

### ref

- https://zhuanlan.zhihu.com/p/48782892
- “分布式一致性模型” 导论http://yuezhang.org/2019/05/17/consistency-model.html  解释了经典论文
- 时间戳相关的问题 https://zhuanlan.zhihu.com/p/333471336
- https://zhuanlan.zhihu.com/p/333471336
- https://zhuanlan.zhihu.com/p/90996685


---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>