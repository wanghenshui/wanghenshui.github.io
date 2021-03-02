---
layout: post
title: merkle tree aka hash tree
categories: [algorithm]
tags: [tree]
---



顾名思义，就是记录key和对应value hash的一棵二叉树。

树的形态

通过每层hash来校验数据块

如果要求严苛，hash函数需要用安全的xxhash之类的。如果要求仅仅是校验 crc即可

<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/95/Hash_Tree.svg/2880px-Hash_Tree.svg.png" alt="" width="80%">

特点

1. Merkle Tree是一种树，大多数是二叉树，也可以多叉树，无论是几叉树，它都具有树结构的所有特点；
2. Merkle Tree的叶子节点的value是数据集合的单元数据或者单元数据HASH。
3. 非叶子节点的value是根据它下面所有的叶子节点值，然后按照Hash算法计算而得出的。



一种攻击方式 Second Preimage Attack:
 Merkle tree的树根并不表示树的深度，这可能会导致second-preimage attack，即攻击者创建一个具有相同Merkle树根的虚假文档。

一个简单的解决方法在Certificate Transparency中定义：
 当计算叶节点的hash时，在hash数据前加0x00。当计算内部节点是，在前面加0x01。
 另外一些实现限制hash tree的根，通过在hash值前面加深度前缀。
 因此，前缀每一步会减少，只有当到达叶子时前缀依然为正，提取的hash链才被定义为有效

## 实际应用

比特币



---

### 参考链接

- wiki https://zh.wikipedia.org/wiki/%E5%93%88%E5%B8%8C%E6%A0%91
- 这里有个很详细的介绍 https://blog.csdn.net/Ciellee/article/details/108004428


---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>

