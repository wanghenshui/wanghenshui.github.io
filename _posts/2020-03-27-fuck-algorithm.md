---
layout: post
title: 手撕算法整理笔记
categories: [algorithm]
tags: [data structure, algorithm]
---
---

> https://github.com/labuladong/fucking-algorithm
>
> https://vjudge.net/article/187
>
> https://github.com/youngyangyang04/leetcode-master
>
> https://leetcode-solution-leetcode-pp.gitbook.io/leetcode-solution
>
>
> https://github.com/SharingSource/LogicStack-LeetCode/tree/main/LeetCode

---

## [思考](https://sites.google.com/site/mostafasibrahim/programming-competitions/thinking-techniques)

### 写在纸上

- 熟悉难度就去研究更难的。suffer
- 写纸上是个大纲，是更多的点子，在电脑上写有可能局限住，边想边写很容易遗漏

### 头脑风暴，想法和实现方法

- 有些时候会卡在思考上，想了半天，一行没写，没法破解成小问题
- 有时候想法对，但是后续的算法知识你不会，卡住了，或者没有足够的信息往下走了
- 有时候你后面的解决方法没问题，但想法本身是错误的。换个角度
- 问题的解决想法很多，可能你得挨个试试，拍个优先级
  - 比如求最小值？DP，贪心？最小割？分支界限法
  - 简单分析，重新尝试
- 哪怕是最垃圾的想法，也比没有想法要强，试一试呗

### 举例/抽象/具象

先用简单例子验证，然后归纳总结通项，然后分析各个元素之间的关系

### 限制

条件能够判定规模，限制大小

| N           | 复杂度     | 可能的算法/技巧                                                  |
| ----------- | ---------- | ---------------------------------------------------------------- |
| 10^18       | O(log(N))  | 二分/快速幂/ Cycle Tricks / Big Simulation Steps / Values ReRank |
| 100 000 000 | O(N)       | 贪心？线性算法一般来说                                           |
| 40 000 000  | O(N log N) | 二分/Pre-processing & Querying/分治                              |
| 10 000      | O(N^2)     | DP/贪心/B&B(分支定界)/D&C(分治)                                  |
| 500         | O(N^3)     | DP/贪心/...                                                      |
| 90          | O(N^4)     | DP/贪心/...                                                      |
| 30-50       | O(N^5)     | Search with pruning/分支定界                                     |
| 40          | O(2^(N/2)) | Meet in Middle                                                   |
| 20          | O(2^(N))   | 回溯/ Generating 2^N Subsets                                     |
| 11          | O(N!)      | Factorial / Permutations / Combination Algorithm                 |

有些限制也可能是假的/误导人的。注意区别。限制条件是非常重要的

### 抽象题型，归纳成小问题

### 抽象题型，归纳通用场景

### 抽象题型，简化成子问题

### 一步一步来

### 抽象题型，转化成别的领域的问题

https://github.com/Strive-for-excellence/ACM-template

https://github.com/atcoder/ac-library

https://github.com/kth-competitive-programming/kactl/blob/master/content/graph/2sat.h

https://github.com/ouuan/Tree-Generator

https://github.com/BedirT/ACM-ICPC-Preparation/tree/master/Week01

https://github.com/hanzohasashi33/Competetive_programming

https://github.com/rachitiitr/DataStructures-Algorithms

https://csacademy.com/app/graph_editor/

## 经典题型


  - 龟兔赛跑
- Merge Intervals，**区间合并类型**

  - 重叠区间，判断交集
- Cyclic Sort，**循环排序**
- In-place Reversal of a LinkedList，**链表翻转**
- Tree Breadth First Search，**树上的BFS**

  - 用队列处理遍历
- Tree Depth First Search，**树上的DFS**
- 模拟堆栈
- Two Heaps，**双堆类型** 最大最小堆求中位数
- 优先队列
- 找一组数中的最大最小中位数
- Subsets，**子集类型，一般都是使用多重DFS**
- Modified Binary Search，**改造过的二分**
- Top ‘K’ Elements，**前K个系列** 堆
- K-way merge，**多路归并**
- DP

  - **0/1背包类型**
  - Unbounded Knapsack，无限背包
  - 斐波那契数列
  - Palindromic Subsequence回文子系列
  - Longest Common Substring最长子字符串系列
- Topological Sort (Graph)，**拓扑排序类型**

  - hashmap邻接表

博弈问题 https://zhuanlan.zhihu.com/p/50787280

https://www.lintcode.com/ladder/47/

https://www.lintcode.com/ladder/2/

https://hrbust-acm-team.gitbooks.io/acm-book/content/chang_jian_ji_chu_cuo_wu.html

https://github.com/lightyears1998/polymorphism

https://github.com/menyf/acm-icpc-template

https://github.com/nataliekung/leetcode/tree/master/amazon

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

**初级排序**

- 选择排序
  - 运行时间和输入无关，并不能保留信息，有记忆信息更高效
- 插入排序

```cpp
void insertion_sort(vector<int> &nums, int n) {
    for (int i = 0; i < n; ++i) {
        for (int j = i; j > 0 && nums[j] < nums[j-1]; --j) {
            swap(nums[j], nums[j-1]);
        } 
    }
}
```
  - 如果有序，更友好
  - 进阶，希尔排序，分组插入排序
    - 分组怎么确定？

**归并排序**

左闭右闭 `[l,r]`
```cpp
void merge_sort(vector<int> &nums, int l, int r, vector<int> &temp) {
    if (l + 1>= r) return;
    // divide
    int m = l + (r - l) / 2;
    merge_sort(nums, l, m, temp);
    merge_sort(nums, m, r, temp);
    // conquer
    int p = l, q = m, i = l;
    while (p < m || q < r) {
       if (q >= r || (p < m && nums[p] <= nums[q])) {
           temp[i++] = nums[p++];
       } else {
           temp[i++] = nums[q++];
       }
    }
    for (i = l; i < r; ++i) {
       nums[i] = temp[i];
    }
}
```
- 难在原地归并
- 递归归并

**快速排序**

左闭右开 `[l,r)`
```cpp
void quick_sort(int q[], int l, int r){
    if (l >= r) return;
    int i = l - 1, j = r + 1, x = q[l + r >> 1];
    while (i < j) {
        do i ++ ; while (q[i] < x);
        do j -- ; while (q[j] > x);
        if (i < j) swap(q[i], q[j]);
    }
    quick_sort(q, l, j), quick_sort(q, j + 1, r);
}
```

yxc这个模版还是比较干净利落的  https://www.acwing.com/blog/content/277/

- 如何选位置？
- 改进方案
  - 小数组用插入排序
  - 三取样切分，中位数的选取

**优先队列**

二叉堆维护

- 插入
  - 加到数组末尾，上浮
- 删除最大元素
  - 最后一个元素放到顶端，下沉

多叉堆

堆排序

---

## 查找

基本抽象 符号表（dict） put/get/delete/contains

- 是否需要有序 min/max/range-find
- 插入和查找能不能都快
  - 插入块不考虑查找，链表，插入慢查找快，哈希表？
  - 二叉查找树，插入对数查找对数（二分）

**二叉查找树**

左边小右边大

删除节点

- 右边大，但是右边的左节点小，要找到右边没有左子节点的左节点，作为被删节点的交换节点
- 左边一定是小于右边的，所以要确定右边最小的，抬到被删节点的位置就行了
- 如果删除的是最小节点，那一定是左边的没有左子节点的节点，右子节点直接抬上来就行了，因为左边没了

最坏情况，数不平衡，退化成链表

范围查找 也就是中序遍历

**平衡查找树**

在插入场景下保证二叉查找树的完美平衡难度过大

- 2-3查找树，插入能尽可能的保持平衡

  - 如果插入终点是2节点，就转换成3节点
  - 如果终点是3节点
    - 只有一个3节点，该节点编程4节点，4节点可以轻松抽出二叉树子树
      - 父2节点，子3节点，同理，抽出子树，把子树父节点塞到父节点
      - 父3节点，子3节点，同理，抽出子树，把子树父节点塞到父节点，父节点再抽出子树，重复
      - 全是3节点 树高 +1
- 红黑二叉查找树描述2-3树？？

  - 替换3节点 抽出子树 左连接子树要标红 有图
  - 红连接放平，就是2-3树了

    ![image-20200827165325062](https://wanghenshui.github.io/assets/image-20200827165325062.png)

  一种等价定义

  - 红连接均为左连接
  - 没有任何一个节点同时和两条红连接相连
  - 完美黑色平衡，任意空连接到根节点的路径上的黑连接相同
- 旋转 就是单纯的改变方向
- 插入

  - 2节点插入
    - 单个2节点插入 一个元素就是单个2节点，左边就变红，如果右边 变红+旋转 最终都是3节点
    - 树底2节点插入，右边，那就旋转（交换位置）
  - 双键树插入，3节点插入 三种情况，小于/之间/大于
    - 大于，直接放到右边，平衡了，变黑
    - 小于，放到左边，两连红，旋转 变黑
    - 之间，放左边右子节点，旋转，在旋转，变黑
- 删除
- 红黑树性质

  - 高度
  - 到任意节点的路径平均长度

**散列表**

- 拉链法，也就是每个表项对应一个链表，有冲突就放到链表里
- 线性探测，放在下一个？？？长键簇会很多很难受

**应用**

- 查找表
- 索引，反向索引
- 稀疏矩阵 哈希表表达

---

## 图

`无向图` `边(edge)` `顶点(vertex) `

顶点名字不重要，用数字描述方便数组描述

特殊的图 `自环` /`平行边` 含有平行边的叫 `多重图` 没有平行边/自环的是 `简单图`

两个顶点通过一条边相连 `相邻` 这条边 `依附于`这两个顶点

`依附于`顶点的边的总数称为顶点的 `度数`

`子图` 一幅图的所有变的一个子集以及所依附的顶点构成的图 许多问题要识别各种类型的子图

`路径` 由边顺序链接一系列顶点 u-v-w-x

`简单路径` 没有重复顶点的路径

`环` 至少包含一条边，起点终点相同的路径 u-v-w-x-u

`简单环` 不包含重复顶点和重复边的 `环`

如果从任意一个顶点都存在一条路径到达另一个顶点，我们称这幅图是 `连通图`

一幅非连通的图由若干连通部分组成，它们都是极大连通子图

` 无环图` 不包含环的图

`树` 无环连通图

`生成树` 连通图的子图，包含所有顶点，且是一棵树

`森林` 树的集合 `生成树森林` 生成树的集合

树的定义非常通用便于程序描述

图G 顶点V个

- G有V-1条边且不含环
- G有V-1条边且连通
- G连通，但删除任意一条编都会是它不在联通
- G是无环图，添加任意一条边会产生一条换
- G中任意一对顶点之间仅存在一条简单路径

图的 `密度` 已经连接的顶点对栈所有可能被连接的顶点对的比例 `稀疏图` 被连接的顶点对很少，`稠密图` 只有很少的抵抗点对之间没有边连接 如果一幅图中不同的边的数量在顶点总数的一个很小的常数倍之内就是稀疏的

`二分图` 能够将所所有节点分成两部分的图

图的表达方式

- 要求，空间，快
  - 邻接矩阵 V*V矩阵 空间太大
    - 平行边无法描述
  - 边的数组 查相邻不够快
  - 邻接表数组 顶点为索引的数组，数组内是和该顶点相邻的列表
    - 空间 V+E
- 遍历
  - DFS 其实也是dp数组方法的一种 递归要用堆栈
  - 连通性判定
- 寻找路径，路径最短判定？
  - BFS
- 连通分量？
- 间隔的度数？

`有向图`

有向图取反

有向图的可达性

- mark-sweep gc
- 有向图寻路
  - 单点有向路径
  - 单点最短有向路径

环/有向无环图(DAG)/有向图中的环

- 有向环检测,有向无环图就是不含有有向环的有向图
  - dfs
- 有向图中的强连通性
  - 构成有向环
  - 自反/对称/传递

**最小生成树 MST**

加权图 权值最小的生成树

- Prim/Kruskal
  - Prim 贪心 + 优先队列
- 几个简化
  - 权重不同，路径唯一
  - 只考虑连通
  - 权重可以是负数，意义不一定是距离
- 树的特点
  - 任意两个顶点都会产生一个新的环
  - 树删掉一条边就会得到两个独立的树
- 切分定理
  - 给定任意的切分，它的横切边中权重最小的必然是图的最小生成树 ？？
  - 这些算法都是一种贪心算法
    - V个顶点的任意加权连通图中属于最小生成树的边标记成黑色，初始为灰色，找到一种切分，横切边均不为黑色，将它权重最小的横切边标记为黑色，反复，直到标记了V-1条黑色边为止 ？？

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

https://github.com/xtaci/algorithms


## 贪心

策略，局部最优解是什么，扩大化

说实话，很少有应用，更像智力题

## 双指针

- Sliding window，**滑动窗口类型**
- two points, **双指针类型**
- Fast & Slow pointers, **快慢指针类型**

可以快慢，也可以左右，也可以滑动，总之是一次遍历收集两种信息
   - (1) 对于一个序列，用两个指针维护一段区间
   - (2) 对于两个序列，维护某种次序，比如归并排序中合并两个有序序列的操

合并数组，判断链表是否有环(Floyd判定)，链表第K个，链表中间，给你两个字符串，判断包含的最短字符串

双指针有时候只是算法题的一小步，相当于数学压轴提的第一小题，铺垫用，他妈的，算法题为啥这么难


```cpp
for (int i = 0, j = 0; i < n; i ++ ) {
    while (j < i && check(i, j)) j ++ ;

    // 具体问题的逻辑
}

```
## 二分

yxc的模版

```cpp
bool check(int x) {/* ... */} // 检查x是否满足某种性质

// 区间[l, r]被划分成[l, mid]和[mid + 1, r]时使用：
int bsearch_1(int l, int r) {
    while (l < r)
    {
        int mid = l + r >> 1;
        if (check(mid)) r = mid;    // check()判断mid是否满足性质
        else l = mid + 1;
    }
    return l;
}
// 区间[l, r]被划分成[l, mid - 1]和[mid, r]时使用：
int bsearch_2(int l, int r) {
    while (l < r)
    {
        int mid = l + r + 1 >> 1;
        if (check(mid)) l = mid;
        else r = mid - 1;
    }
    return l;
}

bool check(double x) {/* ... */} // 检查x是否满足某种性质

double bsearch_3(double l, double r) {
    const double eps = 1e-6;   // eps 表示精度，取决于题目对精度的要求
    while (r - l > eps)
    {
        double mid = (l + r) / 2;
        if (check(mid)) r = mid;
        else l = mid;
    }
    return l;
}
```

实现lower_bound/upper_bound, 求平方根

```cpp
int lower_bound(vector<int> &nums, int target) {
    int l = 0, r = nums.size(), mid;
    while (l < r) {
        mid = l + (r - l) / 2;
        if (nums[mid] >= target) { // upper_bound，改下这个条件就行
            r = mid;
        } else {
            l = mid + 1;
        }
    }
    return l; 
}
```

旋转数组找数组，局部二分
---


