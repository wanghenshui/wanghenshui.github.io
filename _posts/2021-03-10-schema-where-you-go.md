---
layout: post
title: 数据库的schema信息如何存储/维护？
categories: [database]
tags: [myrocks, rocksdb]
---


---



### myrocks

key value绑定

<img src="https://wanghenshui.github.io/assets/myrocks-key.png" alt="">

myrocks的方案，一张图

<img src="https://wanghenshui.github.io/assets/myrocks-cf.png" alt="">

有secondary key的场景，要多用一个cf来存secondary



schema信息存到infomation_schema表中，也就是system这个cf，保存映射关系

---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>