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
    - 后面的章节会讲这个
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
  - 版本号
  - errno perror 封装一些错误处理和解析函数
- 可移植性问题，指的是一些宏开关，BSD POSIX GNU_SOURCE之类的 



# 文件IO: 通用的IO模型



- open
  - flag 只列有意思的，后面还会讲
    - O_CLOEXEC fcntl
    - O_NONBLOCK 非阻塞io
    - O_ASYNC 信号驱动io， fcntl(file control)
  - err
    - 无法访问，目录问题，文件描述符上限，文件打开数目上限，文件只读，文件为exe
- read 返回值，错误-1没了0读到多少返回多少
  - 内核维护读到那里，aka偏移量 lseek
- write 返回值，写入了多少。可能和指定的count不一致（磁盘满/RLIMIT_FSIZE）
  - 偏移量超过文件结尾继续写入 aka文件空洞 eg: coredump
    - 文件空洞占不占用？严格说占用，看空洞边界落在哪里，落在文件块内还是会分配空间的 用0填充
- ioctl (io control)

- 原子操作和竞争条件
- fcntl更改文件状态位
- 文件描述符与打开文件的关系
  - 内核维护的数据结构
    - 进程及文件描述符表
      - fd
      - flag
    - 系统级打开文件表
      - 文件句柄
      - 文件偏移量，状态，访问模式，inode引用
    - 文件系统inode表
      - 文件类型，访问权限，锁指针，文件属性
    - 多个文件描述符可以对应同一个句柄，共用同一个偏移量
      - 复制文件描述符 dup/dup2 2>&1
    - O_CLOSEXEC 描述符私有
- 特定偏移 pread pwrite
- 分散输入和集中输出scatter-gather readv writev
- 阶段文件truncate ftruncate
- 大文件IO
- /dev/fd ?



















ps -o majflt,minflt -p pid

minor fault 在内核中，缺页中断导致的异常叫做page fault。其中，因为filemap映射导致的缺页，或者swap导致的缺页，叫做major fault；匿名映射导致的page fault叫做minor fault。 作者一般这么区分：需要IO加载的是major fault；minor fault则不需要IO加载

























##### ref

1. 

   

---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。