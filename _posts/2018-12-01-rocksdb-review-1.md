---
layout: post
categories : database
title: rocksdb 初探
tags : [rocksdb,c++]
---
  

### why

不整理就忘了

---



rocksdb的整体框架和数据模型，leveldb的整体框架，网上文章遍地都是了。细分到组件，又一大堆分析。看的头都大了。事实上我现在还是分不清的。术语看了一遍又一遍，还是卡壳，看代码，还是会忘记。感觉不用硬看不行啊。还是上图吧。

dbimpl 属性图

![img](https://wipple.devnull.network/research/rippled/api.docs/classrocksdb_1_1DBImpl__coll__graph.png)







column family 属性图

![img](https://wipple.devnull.network/research/rippled/api.docs/classrocksdb_1_1ColumnFamilyData__coll__graph.png)





supervision属性图

![img](https://wipple.devnull.network/research/rippled/api.docs/structrocksdb_1_1SuperVersion__coll__graph.png)

version 属性图

![img](https://wipple.devnull.network/research/rippled/api.docs/classrocksdb_1_1Version__coll__graph.png)



version set 属性图

![img](https://wipple.devnull.network/research/rippled/api.docs/classrocksdb_1_1VersionSet__coll__graph.png)

### reference

- 官方文档 https://github.com/facebook/rocksdb/wiki
- 一个Rocksdb简要分析 http://alexstocks.github.io/html/rocksdb.html
- rocksdb 各种图，点击即可 https://wipple.devnull.network/research/rippled/api.docs/structrocksdb_1_1SuperVersion.html
- 翻译的中文文档 https://rocksdb.org.cn/doc.html
- dbio 这个分类很有意思。https://dbdb.io/db/rocksdb
- leveldb 介绍，感觉skiplist要被说烂了  http://taobaofed.org/blog/2017/07/05/leveldb-analysis/



### to do list

- arangodb 用的rocksdb ，怎么做的？ https://dzone.com/articles/rocksdb-integration-in-arangodb
- cockroachdb 用的rocksdb， 怎么做的？ https://www.cockroachlabs.com/blog/cockroachdb-on-rocksd/
- myrocks 分析，参数很有参考价值。https://www.percona.com/blog/2018/04/30/a-look-at-myrocks-performance/
  - 一个cpu指标数据分析，http://www.cs.unca.edu/brock/classes/Spring2013/csci331/notes/paper-1130.pdf
  
  
 看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
![微信转账](https://wanghenshui.github.io/assets/wepay.png)
</details>或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。

