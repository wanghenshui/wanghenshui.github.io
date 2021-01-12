---
layout: post
title: C++ STL best and worst performance features and how to learn from them
categories: [language]
tags: [c++, C++onSea]

---

<img src="https://wanghenshui.github.io/assets/quadraddnt.png" alt="" width="60%">

##  C++ STL best and worst performance features and how to learn from them - Danila Kutenin

> 视频地址 https://www.youtube.com/watch?v=GRuX31P4Ric



介绍stl好用和不好用的组件

- 好用，简单
  - std::array std::is_trivial_copyable memcopy memmove

    - Trick #1 如果可以，尽量让你的类是`trivial`

      - trivial destructible 能让优化器`复用`

      <img src="https://wanghenshui.github.io/assets/image-20210112135044934.png" alt="" width="70%">

      对比看出，多用一个寄存器.  ~~代码复制点[这里](https://github.com/wanghenshui/hello-world/blob/master/blog/trivial.cpp)~~

      - trivial copyable 有mem*加速

  -  std::optional 析构函数也根据T特化了，如果trivial，就省事儿了

  <img src="https://wanghenshui.github.io/assets/image-20210112135716724.png" alt="" width="70%">

  有个bug std::optional\<int>构造比std::pair<bool, int>重，move copy语义补全

  - std::variant
  - std::atomic Trick #8 有需求就用，别用volatile 
  - std::span std::string_view
    - ·Trick #3 尽可能使用std::string_view和std::span 避免SSO SOO
  -  \<algorithm> 没有ABI问题，某些可能有点问题，比如std::sort std::nth_element但是继续用也没什么问题 Trick #7 尽可能用，免费的午餐
    - Std::sort竞品 pdqsort introsort countsort 根据自己需求抉择 比如clickhouse自由定制的select
      - libc++用了qsort改良，选了四个点sort 并发，这个技巧jvm也用了好像
    - minmax_element不如min_element+max_element

- 可能有替代品
  - std::vector std::map std::set  对于性能取舍等方面还有很多讨论

  -  std::string SSO

    - `const std::string &`应该被淘汰，用std::string_view更省 传值就行了

    <img src="https://wanghenshui.github.io/assets/image-20210112143058129.png" alt="" width="70%">

    这里和gcc表现不同，llvm/clang/libc++的实现和fbstring实现类似，是有短串校验的，为了让短串更长，复用了几个字段

    如果用gcc/gnu libstdc++是这样的

    <img src="https://wanghenshui.github.io/assets/image-20210112144719455.png" alt="" width="70%">

    关于libc++的string 的实现，见https://joellaity.com/2020/01/31/string.html，讨论见https://news.ycombinator.com/item?id=22198158 也有讨论到folly fbstring和这个实现很类似

    fbstring更激进

      - 很短的用SSO(0-22), 23字节表示字符串(包括’\0′), 1字节表示长度.
      - 中等长度的(23-255)用eager copy, 8字节字符串指针, 8字节size, 8字节capacity.
      - 很长的(>255)用COW. 8字节指针(指向的内存包括字符串和引用计数), 8字节size, 8字节capacit
  
  - Trick #4 但是要明白可能潜在的SOO，所以捕获引用要小心
  
  - std::string拼接问题 absl::StrJoin, folly::join 一开始就分配好内存，然后做拼接
  
- 不建议用

  - std::pair std::tuple 信息丢失，赋值场景性能损失
    - why？没有default用了reference需要额外的寄存器？
    - Trick #2 如果可以，尽可能使用 `= default`
- std::unordered_* 数据规模大，性能糟糕
    - 性能糟糕，替代品absl::flat_hash_* #Trick #6 如果hashtable需求强烈，那就用外部的
      - Why?
  - std::regex 性能糟糕 Trick #9 永远别用 std::regex 
    - CTRE吊打 boost::regex也比他强
    - 而且是ABI一部分了，天呐

回到现实世界

- ClickHouse切换到libc++ 某些查询意外快了很多，整体快了%2，离谱 见https://github.com/ClickHouse/ClickHouse/pull/8311
- 还是ClickHouse，切换标准到c++17 char8_t也快了很多

Trick #10 经常benchmark 慢了就找原因



对于ABI问题，也有breakage的提案，建议能改动，但别太多

这个视频就是再复习复习一些c++ 一些点子还是很有意思的，重点关注了clickhouse，很多案例，要关注一下


---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>