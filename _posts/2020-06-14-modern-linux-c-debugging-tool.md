---
layout: post
title: (cppcon)linux下c++现代调试工具手段
categories: [c++, cppcon, cppcon2019]
tags: [c++]
---
  

---

> 这第三页ppt介绍的也不能说modern吧。rr确实没用过

# gdb
gdb -> ptrace ->signal

strace 也是用的ptrace

通过 ptrace(PTRACE_CONT) 传出去
断点和单步，传的信号是SIGTRAP，退出是SIGINT

debug register??头一回知道

DWARF info细节
- PC信息
- 堆栈信息
- 类型信心，函数原型，。。。。

readelf --debug-dump

info signals能看到所有信号的触发


调试 符号优化没了，用-g3 （有没有性能影响？）

堆栈，堆栈指针的优化，CFA，注意，可以利用来导出堆栈 （好像安全不让用？）

libthreaddb 库，用来调试

# rr

没细说


# valgrind, sanitizers

malloc free的实现是有隐藏细节的。导致意外的越界会有问题，这两个工具都是用来抓类似问题的

#cppcheck, coverity

一个coverity公司来做介绍。。这个ppt我见过，以前也有来我们公司的
检查dead code 死循环，越界还算挺有效果的

简单介绍了一下原理？
所有的checker都所定义好的，用调用图来算异常节点？ 


## ref

1. https://www.bilibili.com/video/BV1pJ411w7kh?p=15
2. ppt https://github.com/CppCon/CppCon2019/tree/master/Presentations/modern_linux_cpp_debugging_tools__under_the_covers

   

---
Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。
