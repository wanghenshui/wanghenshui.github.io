---
layout: post
categories: debug
title: No route to host vs Connection refused
tags: [linux,net]
---

  

---

遇到个问题

用的某弹性云服务器，两台机器，内网ip却连不上，跑不了benchmark，提示是No route to host

而不是connnect err timeout之类的。两侧关掉iptables解决。route被iptables限制了。



另外，之前在安全组上分了神，安全组vpc和iptables是两套体系。安全组一般同一个vpc就没问题了。



----

### ref

1. https://yq.aliyun.com/articles/174058
2. https://blog.csdn.net/bisal/article/details/44731431

### contact

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
![微信转账](https://wanghenshui.github.io/assets/wepay.png)
</details>