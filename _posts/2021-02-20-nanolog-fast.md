---
layout: post
title: 为什么nanolog这么快
categories: [language]
tags: [c++, nanolog, spdlog, binlog]

---



- 没有锁，spdlog是mpmc+锁的模式，nanolog是spsc组合模式

- 二进制日志写入，没有写放大

论文地址 https://www.usenix.org/system/files/conference/atc18/atc18-yang.pdf

这里有一篇介绍 https://zhuanlan.zhihu.com/p/136208506还有很多优化的点子，比如cache miss，比如tsc读时间


---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>