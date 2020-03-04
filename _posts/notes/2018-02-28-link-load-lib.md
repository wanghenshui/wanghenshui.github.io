---
layout: post
title: 程序员自我修养链接加载库 读书笔记
category: tools
tags: []
---
{% include JB/setup %}

---



[toc]

---

### 静态链接

- 预处理 编译 汇编 链接
  - 预处理，展开# 
    - #define替换
    - #if #endif替换
    - 处理#include 递归替换
    - 删除注释
    - 添加行号和文件名标识
- 词法分析，语法分析，语义分析，中间语言生成
- 链接
  - 地址空间分配
  - 符号决议
  - 重定位



### 目标文件

- relocatable executable shared object

- 格式都一样，布局也一样，代码段数据段

  - .text  代码.data已经初始化的全局变量静态变量 .bss未初始化的全局变量静态变量
    -  ->二进制文件也可以强转成relocatable文件 objcopy
  - .plt .got跳转表/全局入口
  - strtab .debug .rodata .hash .line .dynamic
  - .init .fini 
  - 自定义段 `__attribute__((section("FOO")))`

  elf结构

  | ELF头                                                |
  | ---------------------------------------------------- |
  | .text                                                |
  | .data                                                |
  | .bss                                                 |
  | 其他段                                               |
  | section header table,段表 readelf查看 elf 头串起段表 |
  | string table <br>symbol table...                     |

  特殊符号`__executable_start` `__etext` `__edata`

  符号，name mangleing，extern “C”

  强符号，弱符号，默认强符号 `__attribute__((week))`

  强引用，弱引用，默认强引用 `__attribute__((weakref))` void foo 用来被覆盖

### 静态链接

- 相似段合并
  - 空间地址分配
    - elf专属地址，其他给个偏移
  - 符号解析重定位
    - 重定位表 object -r a.o
    - 链接需要符号表 readelf -s a.o



---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。