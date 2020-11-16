---
layout: post
title: MongoRocks优化与实践
categories: [database, rocksdb]
tags: [rocksdb, mongodb]
---
  

---

 

腾讯云mongorocks做的工作，作者kdy是个大神。

mongorocsk编码原理不说了。只说他们做的改进点

分ColumnFamily存储

- 多ColumnFamily
  - kv业务索引少
  - 每个索引单独CF/数据单独CF

- 索引/表快速删除
  - dropColumnFamily 物理删除CF数据
  - 便于Oplog按sst文件删除 
    - 计算出需要删除的oplog所在的sstfiles
    - RocksDB::DeleteFilesInRange
  - 方便按CF为粒度对Cache大小调参

针对KV业务的缓存优化

- 开启RowCache，减小BlockCache
  - 对于KV业务,点查询优先于区间查询
- 对于存数据的CF，开启optimize_filters_for_hits
  - 索引CF中存在，数据CF中一定存在
  - 数据CF无bloomFilter的必要性
  - 该参数减小CF的bloomFilter大小

##### ref

1. https://mongoing.com/wp-content/uploads/2017/04/mongoRocks.pdf

   

---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
![微信转账](https://wanghenshui.github.io/assets/wepay.png)
</details>