---
layout: post
title: (译)unordered set 背后的堆分配行为
category: [translation,c++]
tags : [c++, algorithm]
---
{% include JB/setup %}

> 翻译整理自 https://bduvenhage.me/performance/2019/04/22/size-of-hash-table.html
>
> 其实文章写得通俗易懂没必要翻译。感谢原作者的分享

[TOC]



## 1.  std::unoredered_set的实现

std::unorederd_set 是hash set实现的，这个容器通过桶 bucket来维护元素，当插入一个元素，先计算hash计算出桶索引bucket index，然后元素加入到桶中。桶典型由链表来维护

unoredered_set会记录每个桶的负载因子(load factor) 也就是平均每个桶放几个元素，默认是1，如果负载因子超过了默认值，那就需要扩容2倍，即让负载因子降低成原来的一半。负载因子低，每个桶的元素少，这样桶的链表就短，维护链表的开销旧地。



## 2. 堆分配表现

测试数据条件

32位无符号整形，插入2000万数据，代码见参考链接，编译使用clang10 O3 (xcode release)



![容器堆占用 vs 插入个数](https://bduvenhage.me/assets/images/unordered_set_heap_size.png)

上图，每次大幅度跳跃都是 调整负载因子的场景。作者想用valgrind massif工具来分析 std::unordered_set的内存占用，但是valgrind不支持macos，所以作者写了个alloctor来调用默认的alloctor，只是记录次数





![负载因子 vs 插入个数](https://bduvenhage.me/assets/images/unordered_set_load_factor.png)



![桶个数 vs 插入个数](https://bduvenhage.me/assets/images/unordered_set_buckets.png)



上图，随机插入数据，每次负载因子达到上限，都会重新调整桶数量，使负载因子降低到上限的一半





![执行时间 vs 插入个数](https://bduvenhage.me/assets/images/unordered_set_running_time.png)



增加桶的个数需要重新分配内存，调整元素的位置，上图展示了每次重整耗费的时间



保存两千万个32位无符号数据需要657M内存，细节如下

| 元素大小  | 已经分配的元素总数 | 在堆上的元素总数 |
| --------- | ------------------ | ---------------- |
| size=8    | 52679739           | 26339969         |
| size = 24 | 19953544           | 19953544         |

每个桶的元素结构基本上是这样的

```c++
struct BucketItem
{
    size_t hash_;
    uint32_t item_; 
    //4 bytes of padding lay here.
    BucketItem *next_;
};
```

数据size=24为什么两个数据是相等的？

## 3. 总结 && 参考链接



 博客地址 https://bduvenhage.me/performance/2019/04/22/size-of-hash-table.html

作者的代码 https://github.com/bduvenhage/Bits-O-Cpp/blob/master/containers/main_hash_table.cpp

---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。