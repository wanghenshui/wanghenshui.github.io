---
layout: post
categories: c++
title: SO_REUSEPORT与惊群问题
tags: [c++,linux,epoll]
---

  

---

#### why

和同事聊天提到SO_REUSEPORT是解决惊群问题而引入的，我有点不服，决定顺一顺这个问题

---

参考链接<sup>1</sup>中说的比较详尽，我之前以为惊群就是accept本身的问题，在linux2.6就被解决掉了，实际上不是

accept惊群问题

多进程模式，父进程监听，子进程继承监听并accept，每次accept都会导致所有子进程响应，nginx解决方案，加个大锁。导致效率低下

epoll惊群问题

nginx解决的方案



---

### ref

1. https://simpleyyt.com/2017/06/25/how-ngnix-solve-thundering-herd/



### contact

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。