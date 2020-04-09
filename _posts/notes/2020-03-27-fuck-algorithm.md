---
layout: post
title: 手撕算法整理笔记
category: [algorithm]
tags: [data structure, algorithm]
---
{% include JB/setup %}

---

> https://github.com/labuladong/fucking-algorithm

---

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