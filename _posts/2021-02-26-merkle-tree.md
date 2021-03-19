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

<!-- more -->

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

比特币 这里直接摘抄

![](https://upload-images.jianshu.io/upload_images/1785959-b1008e063f6007dd.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)



这里比特币要求平衡树，如果不平衡会复制一个节点

所有的交易都并不存储在Merkle树中，而是将数据哈希化，然后将哈希值存储至相应的叶子节点。这些叶子节点分别是H~A~、H~B~、H~C~和H~D~

HA = SHA256(SHA256(Transaction A))

将相邻两个叶子节点的哈希值串联在一起进行哈希，这对叶子节点随后被归纳为父节点。 例如，为了创建父节点H~AB~，子节点 A和子节点B的两个32字节的哈希值将被串联成64字节的字符串。随后将字符串进行两次哈希来产生父节点的哈希值:

 HAB = SHA256(SHA256(H~A~ + H~B~))

继续类似的操作直到只剩下顶部的一个节点，即Merkle根。产生的32字节哈希值存储在区块头，同时归纳了四个交易的所有数据。图9-2展示了如何通过成对节点的哈希值计算Merkle树的根。





为了证明区块中存在某个特定的交易，一个节点只需要计算log~2~(N)个32字节的哈希值，形成一条从特定交易到树根的认证路径或者Merkle路径即可。随着交易数量的急剧增加，这样的计算量就显得异常重要，因为相对于交易数量的增长，以基底为2的交易数量的对数的增长会缓慢许多。这使得比特币节点能够高效地产生一条10或者12个哈希值（320~384字节）的路径，来证明了在一个巨量字节大小的区块中上千交易中的某笔交易的存在。

在图9-5中，一个节点能够通过生成一条仅有4个32字节哈希值长度（总128字节）的Merkle路径，来证明区块中存在一  笔交易K。该路径有4个哈希值（在图9-5中由蓝色标注）H~L~、H~IJ~、H~MNOP~和H~ABCDEFGH~。由这4个哈希值产生的认证路径，再通过计算另外四对哈希值H~KL~、H~IJKL~、H~IJKLMNOP~和Merkle树根（在图中由虚线标注），任何节点都能证明H~K~（在图中由绿色标注）包含在Merkle根中。

![](https://upload-images.jianshu.io/upload_images/1785959-ae838cf905db704d.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

为了验证黑色块需要蓝色块算出是否满足虚框中的hash

再次回顾一项使用方法

交易信息hash

hash信息构造出merkel tree，其实存储格式可以是数组（用数组存二叉树）

然后验证某个hash ，对应着找周围的点就行了。这也叫简单单点验证 SPV



---

### 参考链接

- wiki https://zh.wikipedia.org/wiki/%E5%93%88%E5%B8%8C%E6%A0%91
- 这里有个很详细的介绍 https://blog.csdn.net/Ciellee/article/details/108004428
- 比特币 https://howieliux1.gitbooks.io/mastering-bitcoin-2nd-edition/content/ch09.html
- https://github.com/bitcoin/bitcoin/blob/master/src/uint256.h
- https://www.cnblogs.com/fengzhiwu/p/5524324.html


---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>

