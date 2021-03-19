---
layout: post
title: blog review #1
categories: [review]
tags: [mysql]
---

准备把blog阅读和paper阅读都归一，而不是看一篇翻译一篇，效率太低了

后面写博客按照 paper review，blog review，cppcon review之类的集合形式来写，不一篇一片写了。太水了

<!-- more -->

### [Memory saturated MySQL](https://blog.koehntopp.info/2021/02/28/memory-saturated-mysql.html)

- cache都是ns级，磁盘是ms级别,尽可能的把working set都放到内存里
- memory就是buffer pool，算下需要多少

```sql
 SELECT sum(data_length+index_length)/1024/1024 AS total_mb FROM information_schema.tables WHERE table_type = “base table” AND table_schema IN (<list of schema names>)
```



### [如何设计安全的用户登录功能](https://my.oschina.net/u/1269381/blog/852679)

在cookie中，保存三个东西——用户名，登录序列，登录token。
 用户名：明文存放。
 登录序列：一个被MD5散列过的随机数，仅当强制用户输入口令时更新（如：用户修改了口令）。
 登录token：一个被MD5散列过的随机数，仅一个登录session内有效，新的登录session会更新它。

登陆id密码 盐，随机盐。定期更新

后段存密码加盐hash，存盐

经典方案，做个备忘




---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>