---
layout: post
title: 数据库的schema信息如何存储/维护？
categories: [database]
tags: [myrocks, rocksdb]
---



<!-- more -->

### myrocks

key value绑定

<img src="https://wanghenshui.github.io/assets/myrocks-key.png" alt=""  width="80%">

myrocks的方案，一张图

<img src="https://wanghenshui.github.io/assets/myrocks-cf.png" alt=""  width="100%">

schema信息存到infomation_schema表中，也就是system这个cf，保存映射关系，正常来说放在默认CF里点查也没啥问题

注意primary key和secondary key的设计差距不大，所以导致secondary key需要另外的CF来存，不然会撞

~~类似hbase这种 key-row模型不会有储存index的烦恼~~



另外，多CF比单CF多个灵活删除CF的功能，可以更快的删



#### Q：DDL改动如何处理？



### mongo-rocks

也有原数据信息，_mdb_catalog，这个更多的是映射信息

本身的原数据使用前缀作区分，0000是原数据



### 参考信息

- myrocks 图来自这里 https://github.com/wisehead/myrocks_notes/blob/master/10.CF/CF/index.md 代码分析记录的很详细，代码级别
- mongorocks整理自

---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>