---
layout: post
title: (译)对于模版类，尽可能的使用Hidden Friend函数定义operator，而不是放在外侧当成模版方法
categories: [language, translation]
tags: [c++, friend, template]
---


---

> 原文[链接](https://quuxplusone.github.io/blog/2020/12/09/barton-nackman-in-practice/)



两种比较实现

一种是通用的模版方法

```c++
template<class V>
struct Cat {
    V value_;
};

template<class V>
bool operator<(const Cat<V>& a, const Cat<V>& b) {
    return a.value_ < b.value_;
}
```



另一种是友元函数

```c++
template<class V>
struct Dog {
    V value_;

    friend bool operator<(const Dog& a, const Dog& b) {
        return a.value_ < b.value_;
    }
};
```



这也叫Hidden Friend 惯用法，更推荐这种写法，比如这种场景



```c++
template<class T>
void sort_in_place(const std::vector<T>& vt) {
    std::vector<std::reference_wrapper<const T>> vr(vt.begin(), vt.end());
    std::sort(vr.begin(), vr.end());
    std::transform(vr.begin(), vr.end(),
        std::ostream_iterator<int>(std::cout), std::mem_fn(&T::value_));
}
```

使用reference_wrapper，增加一层，对于sort比较，通过ADL找对应的operator < , 推导失败，([Godbolt.](https://godbolt.org/z/PscoPz))



```c++
opt/compiler-explorer/gcc-snapshot/lib/gcc/x86_64-linux-gnu/11.0.0/../../../../include/c++/11.0.0/bits/predefined_ops.h:43:23: error: invalid operands to binary expression ('std::reference_wrapper<const Cat<int>>' and 'std::reference_wrapper<const Cat<int>>')
      { return *__it1 < *__it2; }
               ~~~~~~ ^ ~~~~~~
```

对于Dog类，用到friend方法，能隐式把 const Dog\<int>& 转换reference_wrapper<Dog\<int>> 

对于Cat类，operator < 需要具体的类型来推导，否则直接报错





这个技巧也叫Barton–Nackman trick

标准库的写法通常都是Cat，reference_wrapper	也是后加的，大部分没有sort_in_place这种需求




---

