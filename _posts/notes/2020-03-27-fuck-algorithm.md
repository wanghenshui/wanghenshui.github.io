---
layout: post
title: 算法4/手撕算法整理笔记
category: [algorithm]
tags: [data structure, algorithm]
---
{% include JB/setup %}

---

> https://github.com/labuladong/fucking-algorithm

---

## 基础

- 完整详细的定义问题，找出解决问题所必须的基本抽象操作并定义一份API
- 间接地实现一种础计算法，给出一个开发用例并使用实际数据作为输入
- 当实现所能解决的问题的最大规模达不到期望时决定改进还是放弃
- 逐步改进，通过经验性分析和数学分析验证改进后的结果
- 用更高层侧的抽象表示数据接口活算法来设计更高级的改进版本
- 如果可能尽量为最坏情况下的性能提供保证，在处理普通数据时也要有良好的性能
- 在适当的时候讲更细致的深入援救留给有经验的研究之并继续解决下一个问题

---

## 排序

### 初级排序

- 选择排序 
  - 运行时间和输入无关，并不能保留信息，有记忆信息更高效
- 插入排序
  - 如果有序，更友好
  - 进阶，希尔排序，分组插入排序
    - 分组怎么确定？

### 归并排序

- 难在原地归并
- 递归归并

### 快速排序

- 如何选位置？
- 改进方案
  - 小数组用插入排序
  - 三取样切分，中位数的选取

### 优先队列

### 应用



## 动态规划

- 求最值的，通常要穷举，聪明的穷举(dp table)
- 重叠子问题以及最优子结构
  - 如果没有最优子结构，改造转换
- 正确的状态转移方程
  - 数学归纳
  - dp[i]代表了什么？
    - 最长上升子序列问题，**dp[i] 表示以 nums[i] 这个数结尾的最长递增子序列的长度**
  - 公式条件？
  - dp的遍历方向问题
    - **遍历的过程中，所需的状态必须是已经计算出来的**。
    - **遍历的终点必须是存储结果的那个位置**。

 



---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。