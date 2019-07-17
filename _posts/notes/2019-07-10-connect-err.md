---
layout: post
category: debug
title: No route to host vs Connection refused
tags: [linux,net]
---

{% include JB/setup %}

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

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。