---
layout: post
title:  (cppcon)c++11 几个生产中常用的小工具
categories: language
tags: [c++, cppcon]
---
  

这个讲的是scope_exit, std::range, make_range , operator <=> ，后面这两个已经进入c++标准了，前面这个有很多案例

先说scope_exit

作者写了个宏，显得scope_exit更好用一些，实际上没啥必要

他的实现类似这个

```c++
 template <typename Callable> class scope_exit {
   Callable ExitFunction;
   bool Engaged = true; // False once moved-from or release()d.
 
 public:
   template <typename Fp>
   explicit scope_exit(Fp &&F) : ExitFunction(std::forward<Fp>(F)) {}
 
   scope_exit(scope_exit &&Rhs)
       : ExitFunction(std::move(Rhs.ExitFunction)), Engaged(Rhs.Engaged) {
     Rhs.release();
   }
   scope_exit(const scope_exit &) = delete;
   scope_exit &operator=(scope_exit &&) = delete;
   scope_exit &operator=(const scope_exit &) = delete;
 
   void release() { Engaged = false; }
 
   ~scope_exit() {
     if (Engaged)
       ExitFunction();
   }
 };
 
```

几个疑问

- 为什么直接保存Callable，而不是用 std::function来保存
  - 太重，引入类型擦除，效率不行，生成的汇编很差
  - 作者还稍稍科普了下类型擦除的技术，怎么做到的
- 为什么不用AA的scopeguard或者boost::scope_exit
  - 不好用，还需要传参数，scope_exit好就好在可以传lambda



第二个是make_iterable，对应标准库应该是std::range 本质上还是视图一类的东西。因为自定义类型，不想写一套iterator接口，给个view就行。没啥说的

第三个是operator<=> 实际上是解决comparator这种语义实现的问题

就比如rocksdb，bytewisecomparator

```c++
  int r = memcmp(data_, b.data_, min_len);
  if (r == 0) {
    if (size_ < b.size_) r = -1;
    else if (size_ > b.size_) r = +1;
  }
  return r;
```

内部肯定有三个分支，这是影响效率的，怎么搞？

再比如std::tuple 他是怎么比较的？

然后推导出一个适当的operator<=>来解决上述问题





### ref

- [https://github.com/CppCon/CppCon2014/blob/master/Presentations/C%2B%2B11%20in%20the%20Wild%20-%20Techniques%20from%20a%20Real%20Codebase/C%2B%2B11%20in%20the%20Wild%20-%20Techniques%20from%20a%20Real%20Codebase%20-%20Arthur%20O'Dwyer%20-%20CppCon%202014.pdf](https://github.com/CppCon/CppCon2014/blob/master/Presentations/C%2B%2B11 in the Wild - Techniques from a Real Codebase/C%2B%2B11 in the Wild - Techniques from a Real Codebase - Arthur O'Dwyer - CppCon 2014.pdf)
- 上面那段exit抄自<http://llvm.org/docs/doxygen/ScopeExit_8h_source.html> 作者的实现是不支持move的，没有release


