---
layout: post
title: 分布式系统中的一致性模型，以及事务
categories: [database]
tags: []

---

 经典图

<img src="https://wanghenshui.github.io/assets/c.png" alt="" width="80%">





线性一致性

我们可以利用线性一致性的原子性约束来**安全地修改状态**。我们定义一个类似`CAS（compare-and-set）`的操作，当且仅当寄存器持有某个值的时候，我们可以往它写入新值。 `CAS`操作可以作为互斥量，信号量，通道，计数器，列表，集合，映射，树等等的实现基础，使得这些共享数据结构变得可用。线性一致性保证了变更的**安全交错**。



顺序一致性，强调顺序，不是必须发生，但保持顺序发生

因果一致性，保证因果顺序，顺序一致性的子集

串行一致性，有条件必严格

最终一致性以及CRDTs数据结构



---

### ref

- https://zhuanlan.zhihu.com/p/48782892
- 时间戳相关的问题 https://zhuanlan.zhihu.com/p/333471336
- https://zhuanlan.zhihu.com/p/333471336
- https://zhuanlan.zhihu.com/p/90996685


---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>