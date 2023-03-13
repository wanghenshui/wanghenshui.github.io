---
layout: post
title: debug hack读书笔记
categories: review
tags: [debug,c,linux]
---
  

---

非常粗糙

---

**调试前的必知必会**

- coredump获取
  - ulimit -c确认是否开启 ulimit -c unlimited开启
  - gdb -c core_file bin_file
  - 指定目录生成core dump
  - coredump 过大导致磁盘压力 -> coredump_filter设置，排除共享内存

- 基本的gdb命令，打断点看堆栈查变量看寄存器看汇编等等
  - gdb attach/查看历史值 show value
- 初始化文件 .gdbinit 放在home下/也可以source

```gdb
define li
  x/10i $pc
end
document li
  list machine instruction
end
```

```gdb
断点
b core.h:41
b test.cpp:48 if(aiTest == 18 && biTest == 19)
条件断点，if (xxx),其中 if 与(最好有空格)
b 'helloworld::hellofunction' 对函数进行设定地址
b 0x222222243 对指令地址进行设断点

断点操作
info b
del 1/2/3

反汇编
disassemble
disassemble 'MyProcessor::ActijonHelper'
x /10i $pc 显示10条当前反汇编

变量
p infoPtr
p $rsi
p info
p &aiTest
p global::GetTest()
p /x (unsigned long long)0x7fffec8ed320 按16进制的ulong long查看0x7fffec8ed320内存里面的值

信息查看
info args
info registers
p $rsi

监视
rwatch (long long)0x7fffff22f 读
watch (long long)0x7fffff22f 写
awatch (long long)0x7fffff22f 读写
rwatch i if i == 5
watch (int)0x7fffff22f if (int)0x7fffff22f == 109999

栈帧
bt
bt full 3 全量
f 2
f 0

操作
s单指令
si 单指令入
n不进入
si 5 执行5次单指令
```


- intel架构只是
  - 字节序
  - 寄存器
- 堆栈与反汇编 disas
  - 参数传递
  - 简单看懂汇编
    - movl赋值 cmpl比较 调用call 循环 je addl 指针访问 *寄存器 水族movzbl
    - 用crash反汇编？

**内核调试的准备**

Oops

minicom ？

modprobe netconsole

diskdump？

kdump？

- makedumpfile

crash命令

- bt
- dev
- dis
- files
- irq
- kmem
- mod

特殊汇编 

- u2d 异常挂掉
- sti/cli 禁止/允许中断

**应用程序调试实践**

SIGSEGV ->core文件

- 地址重复多次，那就栈溢出
- 捕获栈溢出需要使用备用栈

堆栈无法正确显示

- 栈被破坏

  ```gdb
  info reg
  x/i $rip
  ```

  返回地址被破坏，局部变量也有可能被破坏

数组非法访问导致内存破坏

- 缓冲区溢出 Cannot access memory at address xx
- 运行地址改变
  - 怀疑地址被写入字符串
  - 怀疑索引错误

malloc /free引入的错误

- env MALLOC_CHECK_=1

无响应

- ps状态 S
- ll_lock_wait

内核停止响应

- crash 看堆栈

系统负载高

- oprofile



**进阶工具**

strace抓调用

objdump看汇编 addr2line

valgrind查泄漏

kprobes看内核 jprobes

systemtap调试 抓系统调用

/proc/meminfo

- MemFree空闲内存总量

- Buffers缓存总量

- Cached页面缓存 不在Buffer和SwapCached中

- SwapCache被换出的仍在交换区的页面大小

- Active/Inactive LRU链表中的大小

- Mapped映射到文件上的页面总大小

- Slab 分配器内存使用量

- PageTable 也秒使用内存

- Commited_As提交内存/内存泄漏的大体数值估计点

/proc/<PID\>/mem快速读取内容

OOM killer评分方法

- /proc/<PID\>/status VmSize
- swapoff系统调用的进程分数被设置为最大值
- 子进程加分
- nice值低的
- 超级进程重要，减分
- capset设置过的减分
- oom_adj调整分数

错误注入

failslab

---

