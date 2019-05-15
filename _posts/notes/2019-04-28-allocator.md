---
layout: post
category: c++
title: c++17 std::pmr::polymorphic_allocator
tags: [cpp17, c++]
---
{% include JB/setup %}

### why 

了解学习allocator

---

#### object和value语义

object有地址，value无地址。

#### allocator是否需要状态？

c++14 以前：stateless allocator

想要个statefull allocator怎么办 以前的方法是实现一个allocator

```c++
template <class T>
struct Bad{
    alignas(16)  char data[1024];
    size_t used = 0;
    T* allocate(size_t){
        auto k = n*sizeof(T);
        used+=k;
        return(T*)(data+used-k);
    }
};
```

现在的方法是->std::pmr::polymorphic_allocator + memory_resource

可以继承memory_resource 来实现statefull, 从allocator中拆分出来

```c++
template <class T>
struct trivial_res : std::pmr::memory_resource {
    alignas(16)  char data[1024];
    size_t used = 0;
    T* allocate(size_t){
        auto k = n*sizeof(T);
        used+=k;
        return(T*)(data+used-k);
    }
};
trivial_res<int> mr;
std::vector<int, polymorphic_allocator<int>> vec(&mr);
```

allocator本身还是值语义的，不需要考虑拷贝移动背后的危险（statefull allocator就会有这种问题）



#### 重新实现allocator

语义上只负责分配，（调用全局new delete）就是个singleton

std::pmr::memory_resource就是为了提供存储空间，剩下的由allocator调用

std::pmr::new_delete_resource 实际上就是个singleton::get

std::pmr::polymorphic_allocator只要持有memory_resource的指针就行了



### reference

1.  提案<http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/p0532r0.pdf>
2.  <https://zh.cppreference.com/w/cpp/utility/launder> 翻译的偏学术，结合例子看更佳
3.  这个博客讲的很好<https://miyuki.github.io/2016/10/21/std-launder.html>
    1.  其中涉猎的很多链接我都是先看了一遍，才搜到这个博客。。走了点弯路
    2.  我也搜了launder的实现，结果发现这个博客已经列举了。
4.  上面的博客援引的链接 ，也是用的同样的实例<https://stackoverflow.com/questions/39382501/what-is-the-purpose-of-stdlaunder>
5.  folly的实现 <https://github.com/facebook/folly/blob/master/folly/lang/Launder.h>
6.  llvm的实现<https://reviews.llvm.org/D40218>

看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。

