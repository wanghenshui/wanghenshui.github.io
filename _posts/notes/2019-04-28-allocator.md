---
layout: post
category: c++
title: c++17 std::pmr::polymorphic_allocator
tags: [cpp17, c++]
---
{% include JB/setup %}

### why 

了解学习allocator

源标题 An Allocator is a Handle to a Heap by Arthur O'Dwyer

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

还要注意，这里allocator仅能有copy语义而不能有move语义。见参考链接2

#### rebind

之前一直不理解rebind 作者列出了一个rebindable的例子 <https://wandbox.org/permlink/mHrj7Y55k3Gqu4Q5>

实际上是各种容器内部实现的区别，比如`vector<int>` 内部allocator分配的T就是int，但是 `list<T>`就不一样了，内部实际上是`Node<int>`  由于这种原因才有不同的allocator构造接口(rebind接口)

要让allocator和T无关，这就回到了 std::pmr这个上了，干掉背后的类型，虚函数来搞，T交给背后的memory_resource，看起来好像这里的allocator就起到了一个指针的作用 `allocator_traits<AllocT>::pointer`可能是T*，也可能是藏了好几层的玩意儿，fancy pointer，比如`boost::interprocess::offset_ptr<T>`



#### fancy pointer

此外，这个指针还有问题，比如他到底在堆还是在栈中？有可能都在，也就是fancy pointer场景，比如`std::list<T> ` 声明一个局部对象，考虑list的内部实现，头结点是对象本身持有的，分配在栈上，但是其他链表结点是在堆中的



### reference

1. <https://github.com/CppCon/CppCon2018/blob/master/Presentations/an_allocator_is_a_handle_to_a_heap/an_allocator_is_a_handle_to_a_heap__arthur_odwyer__cppcon_2018.pdf>

2. allocator的move问题 <https://cplusplus.github.io/LWG/issue2593>

3. 关于fancy pointer的深度讨论<http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/p0773r0.html>

4. 关于allocator的讨论<https://www.zhihu.com/question/274802525>

   1.  这个讨论里提到了cppcon2015 allocator Is to Allocation what vector Is to Vexation by Andrei Alexandrescu 有时间总结一下 

5. rebind的讨论<https://bbs.csdn.net/topics/200079053> 结论<https://www.cnblogs.com/whyandinside/archive/2011/10/23/2221675.html>

   连接中的rebind指的语义上的rebind，作者的rebind例子是是这样的 注意rebind copy ctor和move ctor

   ```c++
   #include <list>
   #include <vector>
   #include <memory>
   #include <stdio.h>
   
   namespace Stateless {
   template<class T>
   struct A {
       A() { puts("default-constructed"); }
       A(const A&) { puts("copy-constructed"); }
       A(A&&) { puts("move-constructed"); }
       void operator=(const A&) { puts("copy-assigned"); }
       void operator=(A&&) { puts("move-assigned"); }
   
       template<class U>
       A(const A<U>&) { puts("rebind-copy-constructed"); }
       template<class U>
       A(A<U>&&) { puts("rebind-move-constructed"); }
   
       using value_type = T;
       T *allocate(size_t n) { return std::allocator<T>{}.allocate(n); }
       void deallocate(T *p, size_t n) { return std::allocator<T>{}.deallocate(p, n); }
   };
   static_assert(std::allocator_traits<A<int>>::is_always_equal::value == true);
   } // namespace Stateless
   
   namespace Stateful {
   template<class T>
   struct A {
       int i = 0;
       A() { puts("default-constructed"); }
       A(const A&) { puts("copy-constructed"); }
       A(A&&) { puts("move-constructed"); }
       void operator=(const A&) { puts("copy-assigned"); }
       void operator=(A&&) { puts("move-assigned"); }
   
       template<class U>
       A(const A<U>&) { puts("rebind-copy-constructed"); }
       template<class U>
       A(A<U>&&) { puts("rebind-move-constructed"); }
       
       using value_type = T;
       T *allocate(size_t n) { return std::allocator<T>{}.allocate(n); }
       void deallocate(T *p, size_t n) { return std::allocator<T>{}.deallocate(p, n); }
   };
   static_assert(std::allocator_traits<A<int>>::is_always_equal::value == false);
   } // namespace Stateful
   
   template<template<class...> class CONTAINER>
   void test()
   {
       puts(__PRETTY_FUNCTION__);
       puts("--------Stateless:--------");
       {
           using namespace Stateless;
           puts("--- during default-construction:");
           CONTAINER<int, A<int>> a;
           puts("--- during copy-construction:");
           CONTAINER<int, A<int>> b(a);
           puts("--- during move-construction:");
           CONTAINER<int, A<int>> c(std::move(a));
           puts("--- during destructions:");
       }
       puts("--------Stateful:--------");
       {
           using namespace Stateful;
           puts("--- during default-construction:");
           CONTAINER<int, A<int>> a;
           puts("--- during copy-construction:");
           CONTAINER<int, A<int>> b(a);
           puts("--- during move-construction:");
           CONTAINER<int, A<int>> c(std::move(a));
           puts("--- during destructions:");
       }
   }
   
   int main()
   {
       test<std::list>();
       test<std::vector>();
   }
   ```

   

看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。

