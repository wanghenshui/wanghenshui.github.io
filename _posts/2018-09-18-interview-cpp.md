---
layout: post
title: 之前c++面试被问到过的问题
categories: c++
tags: [c++]
---
  



[简单抄袭了这篇文章，加上了自己的总结](https://blog.csdn.net/shanghairuoxiao/article/details/72876248)

[也简单抄袭了这个总结](https://github.com/arkingc/note/blob/master/interview/C%2B%2B.md)

## c/c++基础 

语义层面，参考cppreference 书籍c++ primer， 深入理解c++对象模型，Effective C++

- extern关键字，extern “C” （解决编译符号问题，C++ name mangling）

- static 生命周期引出的问题，static局部变量，static全局变量，static函数，static成员函数
  - 也有可能顺便问线程安全

- const volatile 两种限定符 
  - const 到底在不在内存中，volatile到底做什么的
  - mutable？没人问过
- malloc free new delete 
  - malloc 和new的区别，几种new的区别，delete到底做了什么
- 虚函数以及实现（虚函数表），为什么基类析构是虚函数，以及虚表指针，，以及多继承下的虚表指针是怎么排布的（深入理解c++对象模型）
- static_cast, dynamic_cast, const_cast, reinterpret_cast
- 构造函数语义学，拷贝构造函数的问题，初始化列表
  - 生命周期，RAII
  - 如何控制构造，比如禁止拷贝，禁止栈上变量，实现一个nocopyable
- 字节对齐问题（结合虚表指针一起来问）
- STL数据结构 
  - 拐弯抹角问底层，比如问map实现->红黑树，问LinuxO1公平调度器->  红黑树，问epoll->还是红黑树
  - 问hash_map  怎么实现的， 冲突的解决办法
  - vector的实现，push_back导致扩容了，底层是怎么移动的  swap clear惯用法
- 模板 （基本没人问）
- 实现简单的库函数 字符操作（strcat strlen strcmp ），memcpy，atoi等
- 智能指针 
  - 就是问引用计数，问Fork什么资源共享了 -> 也是在问引用计数
  - shared_ptr，weak_ptr unique_ptr，以及弱引用，循环引用的解决办法
  - 也有可能问线程安全的问题，shared_ptr是不是线程安全的，为了解决智能指针的线程安全问题有哪些技术

- [内存泄漏](http://www.cnblogs.com/skynet/archive/2011/02/20/1959162.html) 
  - 在windows平台下通过CRT中的库函数进行检测
  - 在可能泄漏的调用前后生成块的快照，比较前后的状态，定位泄漏的位置
  - Linux下通过工具valgrind检测
  - [一个精彩的定位内存泄漏的经验](https://zhuanlan.zhihu.com/p/40912446)

- 多线程相关，线程安全，那些函数不是线程安全
  - 也有可能问 thread使用之类的
  - 单例模式如何线程安全 也有可能顺便问如何保证唯一（私有析构

- c++11/14特性, 你用到的熟悉的有哪些 被问到过智能指针，内存模型
- 异常安全以及保证 （参考书籍 exceptional c++系列，考虑构造函数失败会怎样）
- GDB相关知识，断点，gdb线程
- 系统知识相关，堆栈空间，入栈顺序，动态库静态库，字节序转换

## 数据结构和算法

- 数据结构爱问红黑树和B树

- 算法爱问快排实现细节，堆排序，以及相关复杂度

基本就是LeetCode题目

主要考察点

- 动态规划 台阶问题 图相关算法
- 链表操作
- 树操作
- 字符操作

海量数据问题

分布式？



## TCP/IP

- l两个很远的机器到底是怎么找到对方的
- 从经典的TCP状态迁移图引出的问题
  - 三次握手与四次挥手，超时重传 以及定时器相关 顺便问探测窗口
  - TIME_WAIT 2MSL
  - 定时器的问题
  - 滑动窗口
  - RST相关问题
  - linux socket 服务端客户端都对应这状态迁移图的那些行为
    - 细节，SO_REUSEADDR， SO_LINGER
- TCP怎么保证可靠性（通过超时重传，应答保证数据不会丢失、通过校验和保证数据可靠，通过序号，ACK，滑动窗口保证数据顺序性和有效性，通过拥塞控制缓解网络压力，通过流量控制同步收发速率）
- TCP拥塞控制
- TCP窗口检测
- UDP不会直接问，会问一个心跳实现（UDP或TCP长连接）

  - 然后会引出长连接短连接区别


## Linux

- 信号，你了解的信号有哪些，如何处理信号
  - 有可能从TCP SIGPIPE就问到这里了

- 进程
  - 进程间通信手段，优劣
  - 守护进程，僵尸进程，孤儿进程
  - 进城线程区别



## 数据库


看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
![微信转账](https://wanghenshui.github.io/assets/wepay.png)
</details>


