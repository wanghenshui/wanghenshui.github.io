---
layout: post
title: blog review 第十四期
categories: [review]
tags: [cmu,kv,hash,redis,RavenDB,cosmosdb,rqlite,graph,TileDB,Fluree,ApertureDB]
---

看tag知内容

<!-- more -->

## [3 Innovations While Unifying Pinterest’s Key-Value Storag](https://medium.com/@Pinterest_Engineering/3-innovations-while-unifying-pinterests-key-value-storage-8cdcdf8cf6aa)

[Pinterest](https://medium.com/@Pinterest_Engineering?source=post_page-----8cdcdf8cf6aa-----------------------------------) 他们有四个kv，都是历史kv，rocksstore(rocksdb)， terrapin，基于hdfs的kv，UserMetaStore UMS，rockscassadra

历史包袱太重了，pinterest决定都归一到rockstore，首先，各个服务接口都不一样，如何归一？

首先，统一一套kvstore API，thift的接口

对于不需要写的业务，比如terrapin这种离线数据，可以直接hook terrapin的api，让terrapin的底层直接调用kvstore的api，迁移结束，hook，下线旧的服务，简单

但是有的场景只要value中的一个字段（把kv当大宽表用），需要trim掉，基于HDFS来做的，这种场景在rockstore没有，解决方案是重写key，拆成hash类似的结构

对于有读有写的业务，比如UMS，还是hook，区分读写，这里直接推进业务使用kvstore的api接口，新的写写入新机群，读，kvstore的接口调用底层的UMS的接口去读，数据迁移结束，去掉hook

另外一点：数据导入的版本问题，他们也使用双buffer切换，问题在于，就两个版本，不够用

他们引入了一个kv store manager，这个东西记录版本，然后集成到kvstore api里，这他吗不是又实现了一个etcd/zookeeper吗？

版本用时间戳记录，不同的store记录不同版本，这不也冗余了吗，意义不大啊感觉



## [Reversing an integer hash function](https://taxicat1.github.io/hash6432shift_inversion.html)



## [Five Signs You’ve Outgrown Redis](http://pages.aerospike.com/rs/229-XUE-318/images/Aerospike_Executive_Summary__Redis-5-Signs.pdf?utm_source=linkedin&utm_medium=cpc&utm_campaign=aerospike_redis_benchmark)



aerospike宣传他们的服务特点 支持持久化性能还不差，维护性还好

怎么支持持久化[Hybrid Memory Architecture](https://aerospike.com/products/features/hybrid-memory-architecture/)

有点类似hashtable，索引全内存，文件SSD，这样性能怎么会好呢？

> Disk I/O is not required to access the index, which enables predictable  performance. Such a design is possible because the read latency  characteristic of I/O in SSDs is the same, regardless of whether it is  random or sequential. For such a model, optimizations described are used to avoid the cost of a device scan to rebuild indexes.

不访问索引，读全靠运气吗，这个predictable不开就是走索引，开了，预测一波，没击中，再走索引，通过读的IO分布特征统计



## HTAP with Azure Cosmos DB: Hybrid Transaction & Analytical Processing (Hari Sudan S)


<img src="https://user-images.githubusercontent.com/8872493/155947808-6c904dbd-6188-45b4-a2ad-a8da31d6ca14.png" alt=""  width="100%">


一个root维护，可能是b树什么的，然后底层数据用parquet存

写流程

<img src="https://user-images.githubusercontent.com/8872493/155961404-bb1b52f5-15e0-460a-84c4-a56962a7f390.png" alt=""  width="100%">

具体事务怎么实现？完全没提



## RavenDB: Practical Considerations for ACID/MVCC Storage Engines (Oren Eini)


<img src="https://user-images.githubusercontent.com/8872493/156001304-9c53b92c-69a8-4de2-830d-41f0a1a37ebe.png" alt=""  width="100%">

解决方法比较简单


<img src="https://user-images.githubusercontent.com/8872493/156002007-1ac91171-3356-4cab-9d38-21be21f0f50c.png" alt=""  width="100%">


单写，实现MVCC就靠COW就可以了，不阻塞


<img src="https://user-images.githubusercontent.com/8872493/156005031-c164bda1-9d59-464b-a16f-0e0f664af80f.png" alt=""  width="100%">

不写磁盘，磁盘太慢了。写buffer往下刷


WAL设计取舍


<img src="https://user-images.githubusercontent.com/8872493/156006268-3b19fd41-f9f6-4313-902c-c49676ffbf62.png" alt=""  width="100%">



<img src="https://user-images.githubusercontent.com/8872493/156006413-7dd75bf5-aa4c-4fea-a10e-4916b6cae62d.png" alt=""  width="100%">




WAL优化点


<img src="https://user-images.githubusercontent.com/8872493/156006925-3794d1bd-8e3f-44ab-b000-f0f7c68e7848.png" alt=""  width="100%">



写优化


<img src="https://user-images.githubusercontent.com/8872493/156007759-e2cdd6c0-faf1-4289-8e23-2b666eaed930.png" alt=""  width="100%">


感觉利用c# 的协程能力，把写抽象成任务，搞成batch，而不是直接死板的lock write commit

什么时候更新文件？



<img src="https://user-images.githubusercontent.com/8872493/156010781-4a27fd96-5615-4374-a258-7def48a8c4db.png" alt=""  width="100%">



这种搞法，缓存的数据不能保证落地，丢最近的record是否可以接受？


其他场景


<img src="https://user-images.githubusercontent.com/8872493/156011175-2818bcc4-a922-479f-a29a-c175696d0058.png" alt=""  width="100%">


这个做个参考





## rqlite: The Distributed Database Built on Raft and SQLite (Philip O'Toole)



<img src="https://user-images.githubusercontent.com/8872493/156096676-f5ecef89-d6ba-4368-ab35-d311986df013.png" alt=""  width="100%">


其实主要工作就是如何把raft的接口用sqlite实现好，怎么抽象log entry



## The TileDB Universal Database (Stavros Papadopoulos)



<img src="https://user-images.githubusercontent.com/8872493/156117355-cef4fe74-f5a7-491a-986c-fa21ee7ba625.png" alt=""  width="100%">


这个想法挺有意思，但是数组怎么抽象成具体的kv呢，感觉和parquet有点像，又有点不像


<img src="https://user-images.githubusercontent.com/8872493/156118038-3ef08656-061f-4e17-82b3-c5b1bdc16127.png" alt=""  width="100%">


维度信息，快速



<img src="https://user-images.githubusercontent.com/8872493/156118498-1df1a0ef-b21e-4aa0-ab62-5d39eaebab03.png" alt=""  width="100%">


果然，两种形态
本质还是列存


<img src="https://user-images.githubusercontent.com/8872493/156119722-4ec8bc5e-0a3b-419c-a4e6-3d3ec2ca1730.png" alt=""  width="100%">


如何文件描述

<img src="https://user-images.githubusercontent.com/8872493/156120289-06b97cb5-1735-4a3b-9f98-cac791f19c85.png" alt=""  width="100%">



<img src="https://user-images.githubusercontent.com/8872493/156120098-189bb481-8045-4ed5-96be-4a8aa42d5279.png" alt=""  width="100%">



index


把一个数组的几个部分分别索引


<img src="https://user-images.githubusercontent.com/8872493/156128686-90d59e61-7304-4bc2-abab-79674cf44e29.png" alt=""  width="100%">


整体貌似是api接口形式的，也提供了各种数据库的插件

这个存储的明显受益没说。抽象能力强，面向业务场景比较集中



## Fluree - Cloud-Native Ledger Graph Database (Brian Platz)



<img src="https://user-images.githubusercontent.com/8872493/156148617-822e28cc-abe6-4e2b-815d-0bcc10334bdd.png" alt=""  width="100%">




<img src="https://user-images.githubusercontent.com/8872493/156149491-7d12fe5d-c6e6-4ca2-a103-5ec5a1f8e935.png" alt=""  width="100%">


直接把关系谓语都存了？？？？？
？？？？


<img src="https://user-images.githubusercontent.com/8872493/156149901-248270e8-580d-413a-bee7-73c3b1f5f32c.png" alt=""  width="100%">




<img src="https://user-images.githubusercontent.com/8872493/156151114-c4ca56b4-3df8-4868-9ae8-00d9792b70a5.png" alt=""  width="100%">


各种index分别存，用btree组织。最终还是回到了btree

mysql 图版？



## ApertureDB: Designing a Purpose-built System for Visual Data and Data Science (Vishakha Gupta)

用的新硬件 傲腾。没开源。部署在azure上


<img src="https://user-images.githubusercontent.com/8872493/157667915-7081be05-74f4-40d3-abe3-34b4dce35511.png" alt=""  width="100%">



<img src="https://user-images.githubusercontent.com/8872493/157668870-e2674140-d2a3-4f41-9164-c256d1561cee.png" alt=""  width="100%">


性能数据就不贴了。和neo4j比 没意思



<img src="https://user-images.githubusercontent.com/8872493/157669771-e04469ec-db5c-4ebc-b9e9-76ebc359c16c.png" alt=""  width="100%">


看着工作量挺麻烦

计划


<img src="https://user-images.githubusercontent.com/8872493/157673389-fadfea2b-21d2-4f0b-9d91-befabf61e867.png" alt=""  width="100%">


---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>
