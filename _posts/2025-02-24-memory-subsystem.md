---
layout: post
title: Memory Subsystem Optimizations
categories: [system]
tags: [language]
---

<!-- more -->



## 减少内存访问次数
- Loop Fusion循环融合，如果是操作同一块内存的循环，合并到一起
- 编译器可能自动执行，也可能没有效果
- 和循环分段优化互补，有时候为了局部向量化可能牺牲掉合并循环，主动拆分
- c++ range操作等于循环融合的优化，所以尽可能range
- Kernel Fusion 子计算流水线化
- 循环内的循环融合 降低内存访问
- 为了降低内存访问，可以增加计算，CPU换内存 https://johnnysswlab.com/horrible-code-clean-performance/
- 小数组放寄存器里

## 编译器影响

- 指针别名 Pointer Aliasing
- Register Spills导致的寄存器压力问题
- 调查https://johnnysswlab.com/loop-optimizations-interpreting-the-compiler-optimization-report/ 
- 减少寄存器使用数量 参数降低/合并，缩短生命周期

Rematerialization 降低加载开销，合并
PGO likely
尾调用 clang::musttail /__attribute((preserve_most))


改变内存布局

- Loop Interchange 循环交换，强制顺序访问
- Loop Tiling  循环平铺 大循环分成L1大小的块进行处理 
- Loop Sectioning循环分段 可能会下降

类型布局
- 大类型字段尽可能相邻，提高局部性
- 不同类有字段引用？拆，合并到一起，提高局部性
- 优化掉指针
- Denormalization 多副本，避免指针问题
- SOA
- padding
- 尽可能在小数据集上操作

数据结构重新设计
- 链表 尽可能group，提高cache利用率
- 二叉树 ->四叉树 -> BTree
- hashmap node节点记录更多信息方便probe

内存消耗与数据集 降低数据集利于TLB cache
- 小类型 float
- 指针优化/tagpointter
- bool/位域/padding
- SBO
- jemalloc/tcmalloc
- 更细的分配器

指令并行ILP
- 打破依赖链
- 使用数组映射/index映射/sparsearraymap
- 缩短依赖链，BTree
- 交织，interleave

In-Order CPU Cores 强制顺序如何优化
- 循环展开/交织
- pipeline 加速，循环计算不同步骤

preefetch
TLB and Huge Pages 配置大页加速tlb

节省内存带宽
避免预测，fence

无分支cmov，避免分支预测失败，汇编inline

多线程影响，numa影响

延迟敏感？
- 预热
- 分配后立即初始化，避免page faull
- mmap
- 容器，resize代替reserve
- TLB，hugepage，以及不要用五级页表
- swap关闭
- TLB shootdowns规避

内存吞吐计算模型
屋顶模型和工具分析 https://johnnysswlab.com/measuring-memory-subsystem-performance/

设计数据结构加速内存顺序访问

skip
数组拍扁，之前见过folly就有类似的玩意
矩阵转置
查找逆序，降低循环规模
部分有序查找更快 分支预测
