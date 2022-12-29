---
layout: post
title: 软件调试的艺术读书笔记
categories: [debug, review]
tags: [gdb]
---
gdb汇总

<!-- more -->

---

| 命令名称    | 命令缩写 | 命令说明                                               |
| ----------- | -------- | ------------------------------------------------------ |
| run         | r        | 运行                                                   |
| continue    | c        | 让暂停的程序继续运行                                   |
| next        | n        | 运行到下一行                                           |
| step        | s        | 如果有调用函数，进入调用的函数内部，相当于 step into   |
| until       | u        | 运行到指定行停下来                                     |
| finish      | fi       | 结束当前调用函数，到上一层函数调用处                   |
| return      | return   | 结束当前调用函数并返回指定值，到上一层函数调用处       |
| jump        | j        | 将当前程序执行流跳转到指定行或地址                     |
| print       | p        | 打印变量或寄存器值                                     |
| backtrace   | bt       | 查看当前线程的调用堆栈                                 |
| frame       | f        | 切换到当前调用线程的指定堆栈，具体堆栈通过堆栈序号指定 |
| thread      | thread   | 切换到指定线程                                         |
| break       | b        | 添加断点                                               |
| tbreak      | tb       | 添加临时断点                                           |
| delete      | del      | 删除断点                                               |
| enable      | enable   | 启用某个断点                                           |
| disable     | disabl   | 禁用某个断点                                           |
| watch       | watch    | 监视某一个变量或内存地址的值是否发生变化               |
| list        | l        | 显示源码                                               |
| ptype       | ptype    | 查看变量类型                                           |
| set args    |          | 设置程序启动命令行参数                                 |
| disassemble | disas    | 查看汇编代码                                           |
| show args   |          | 查看设置的命令行参数                                   |



|格式 |含义|
|--|--|
|x |按十六进制格式显示变量|
|d |按十进制格式显示变量|
|u |按十六进制格式显示无符号整型|
|o |按八进制格式显示变量|
|t |按二进制格式显示变量|
|a |按十六进制格式显示变量|
|c |按字符格式显示变量|
|f |按浮点数格式显示变量|



### 预备知识

- gdbinit启动文件
- gdb -command=z x 在x上运行gdb，从z文件中读命令
- 原理 ptrace
- set disassembly-flavor intel intel格式汇编
### 停下来看一看

- 断点
  - 创建
    - break _function_
    - break _line_number_
    - break _filename:line_number_   注意相对路径
    - break _filename:line_number_
    - break _filename:function_
  - 删除 delete clear
  - 禁用disable
  - 继续执行
    - 下一行，next 执行函数不会暂停 step进入函数停在第一行
    - continue  c继续执行到下一个断点，continue n 跳过n个断点
    - finish fin当前函数执行结束
    - util u 快速执行完循环
      - 可能违反直觉，但是实际上是跳到比当前地址更高的位置上去
      - 看汇编直观一些
      - todo：需要分析一波
  - 属性
    - info breakpoints
- 条件断点
  - break _break-args_ if (condition)
    - 注意优先级
    - 注意表达式的返回值默认是int，需要定义指针强转函数符号
- 断点命令列表
  - commands 1 xx end
- 监视点
  - watch
- 捕获点

> 其实早期gdb对于断点没有明确区分。delete可以同时删除这三种点，注意

### 检查和设置变量

- print p p可以打印字段，也可以打印结构体
- display disp 每次断点击中都会打印上次display的内容， p升级版
- commands组合
  - commands + call
  - commands组合命令也可以录入命令来做复现
- 数组
  - p *x@25  *pointer@number_of_elements
  - 支持强制类型转换 p (int [25]) *x
- c++
  - 需要带上命名空间/类空间
  - ptype打印结构
- 局部变量 info locals
- x 查看内存地址 x/10wx addr
  - x/10i addr
- p disp 高进选项
  - p/x y 十六进制查看
  - dis disp 1临时禁止display 1
- gdb 变量
  - 值历史 p *$1 p *$也可以
  - convenience variable  set $q = p

### 程序崩溃处理

- 崩溃相关的基本内存布局以及页的概念
  - 页表，页表项，以及为什么会有段错误 -> 数据段 栈区，堆区的权限校验
    - 轻微的内存访问程序错误可能不会导致段错误，比如越界
    - 段错误也可以捕获，故意触发段错误来执行一些动作（todo想不到这么做为了啥）
  - 其他信号可能造成的崩溃，比如fpe ，buserr
- core文件
  - 注意某些shell禁止coredump ，`ulimit -c unlimited`
- 建议，调试重编期间不要退出gdb。多shell管理

### 多活动上下文中的调试

- 网络编程 gdb 系统函数+ strace系统函数
- 信号 handle
- 多线程,切换线程看函数调用栈
  - info threads thread n bt f n
  - break _cond_ thread n（当线程3到达源代码行时停止执行）
  - thread apply bt all
    - 打印过长导致进程复位，或者连接断开，使用不阻塞方式
      - 查线程id `find / proc/pid/task -name "sched" |xargs grep threads`
      - pstack
  - 转到线程t
  - `set scheduler-locking off|on|step`控制当前线程调度
- 多进程MPI
  - attach到进程上看调用栈以及对应栈帧上的信息
- 不阻塞 gdb -batch -ex “cmd” -p pid

### 特殊主题

不说了。编译连接错误之类的

### 其他工具

- 充分利用编译警告 ide等等工具
- 检查系统错误码之类的
- strace ltrace
- lint
- 内存问题，MALLOC_宏(valgrind没介绍)

### 其他语言调试

基本大同小异

最好要了解一点汇编

<img src="https://wanghenshui.github.io/assets/gdb.png" alt="" width="80%">

没有符号信息，自己编译一套-g的o文件，反汇编 有-g `obj -d -S -l xx.o`, 没-g `objdump -dr xx.o`

如果没有o文件，反汇编看call调用自己推到调用栈

    找特殊调用 寻址偏移 特殊值

## 内存错误

```gdb
disas
i r
i proc m
```

---

### ref

- https://github.com/hellogcc/100-gdb-tips/

---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>
