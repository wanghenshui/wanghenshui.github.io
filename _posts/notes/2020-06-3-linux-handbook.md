---
layout: post
title: Linux/Unix系统编程手册 整理笔记
category: [linux]
tags: [linux]
---
{% include JB/setup %}

---

[toc]

> 只列重点和延伸

# 基本概念

- 文件I/O模型
- 进程
  - 内存布局，文本，数据，堆，栈
  - _exit  退出 （实现是调用sys_exit退出，c标准库中的exit比这个函数多了一些清空IO 的动作，遇到过一次和log4cplus挂死的问题）
  - 进程的用户和组标识符，凭证，限定权限
  - 特权进程，用户ID为0 的进程，内核权限限制对这种进程无效
  - 不同用户的权限有不同的能力，可以赋予进程来执行或者取消特殊的能力 CAP_KILL
  - init进程 所有进程之父 创建并监控其他进程
  - 守护进程
  - 环境列表 export setenv char **environ
  - 资源限制 setrlimit()
- 内存映射 mmap
  - 共享映射
    - 同一文件
    - fork继承
      - 有标记来确认映射改动是否可见
- 进程间通信以及同步
  - 信号 ctrl c
  - 管道 |, FIFO， pipe
  - socket
  - 文件锁定 （典型使用举例？）
  - 消息队列 （典型使用举例？）
  - 信号量 
  - 共享内存

- 进程组，信号传递 （典型使用举例？）（ctrl c？）
- 会话，控制终端和控制进程 ctrl c
- 伪终端，ssh
- 日期和时间 真实事件和进程时间 time（time有两个，另一个是看更细致的内核动作的）
- /proc文件系统

---

# 系统编程概念

- 系统调用
  - 调用c wrapper函数，入参复制到寄存器，触发中断，切换到内核态，通过中断向量表找到系统调用
    - 中断改成sysenter了
  - 内核栈保存寄存器的值，校验系统编号，正式调用sysytemcall
    - 可以用strace抓
- 库函数



























##### ref

1. 

   


---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。