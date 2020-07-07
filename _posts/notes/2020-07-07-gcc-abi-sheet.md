---
layout: post
title: gcc libstd 版本对应关系表格
category: [c++]
tags: [debug]
---
{% include JB/setup %}

---

[toc]

> 屡次被stdc++ glibc 符号困扰。
>
> 从4.9开始记录。这个版本算是真正支持c++11的



| gcc版本 | libstdc++版本号     | glibc版本号    | cxxabi版本号  |
| ------- | ------------------- | -------------- | ------------- |
| 4.9     | libstdc++.so.6.0.20 | GLIBCXX_3.4.20 | CXXABI_1.3.8  |
| 5.1     | libstdc++.so.6.0.21 | GLIBCXX_3.4.21 | CXXABI_1.3.9  |
| 6.1     | libstdc++.so.6.0.22 | GLIBCXX_3.4.22 | CXXABI_1.3.10 |
| 7.1     | libstdc++.so.6.0.23 | GLIBCXX_3.4.23 | CXXABI_1.3.11 |
| 7.2     | libstdc++.so.6.0.24 | GLIBCXX_3.4.24 | CXXABI_1.3.11 |
| 8.1     | libstdc++.so.6.0.25 | GLIBCXX_3.4.25 | CXXABI_1.3.11 |
| 9.1     | libstdc++.so.6.0.26 | GLIBCXX_3.4.26 | CXXABI_1.3.12 |
| 9.2     | libstdc++.so.6.0.27 | GLIBCXX_3.4.27 | CXXABI_1.3.12 |
| 9.3     | libstdc++.so.6.0.28 | GLIBCXX_3.4.28 | CXXABI_1.3.12 |
| 10.1    | libstdc++.so.6.0.28 | GLIBCXX_3.4.28 | CXXABI_1.3.12 |



## ref

1. https://gcc.gnu.org/onlinedocs/libstdc++/manual/abi.html

   

---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。