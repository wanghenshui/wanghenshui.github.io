---
layout: post
title: 实现一个benchmark cli应该考虑点啥
categories: [language]
tags: [c++, template, map]
---



benchmark的典型架子，网络端

- 多线程worker，worker死循环干活
- 统计信息，统计p99统计
- 后台线程实时打印qps/打印进度条
- 参数读取

一个典型的例子是memtier-benchmark，多线程worker，worker内部潜入libevent填数据，这个架构

cli典型架子

- repl 循环

- 补全

- 参数读取

典型例子redis-cli

---

### ref

- https://clig.dev/


---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>



