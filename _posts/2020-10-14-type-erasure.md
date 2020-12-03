---
layout: post
title: 类型擦除技术 type erasure以及std::function设计实现
categories: [language]
tags: [c++, type,vtable, sbo]
---


---

> 本文是[type erased printable](https://quuxplusone.github.io/blog/2020/11/24/type-erased-printable/)和 [design space for std::function](https://quuxplusone.github.io/blog/2019/03/27/design-space-for-std-function/) 的整理总结



说是类型擦除技术，不如说是多态技术



函数指针多态 几种做法

- void* 传统的万能参数
- 继承接口值多态，dynamic_cast
- 值语意的多态，type erasure 也就是类型擦除
  - std::function   boost::any_range boost::any 



来举个例子, type erased printable 

打印托管的值 [godbolt链接](https://godbolt.org/z/rb8WTe)

```c++
#include <memory>
#include <ostream>

struct PrintableBase {
    virtual void print(std::ostream& os) const = 0;
    virtual ~PrintableBase() = default;
};

template<class T>
struct PrintableImpl : PrintableBase {
    T t_;
    explicit PrintableImpl(T t) : t_(std::move(t)) {}
    void print(std::ostream& os) const override { os << t_; }
};

class UniquePrintable {
    std::unique_ptr<PrintableBase> p_;
public:
    template<class T>
    UniquePrintable(T t) : p_(std::make_unique<PrintableImpl<T>>(std::move(t))) { }

    friend std::ostream& operator<<(std::ostream& os, const UniquePrintable& self) {
        self.p_->print(os);
        return os;
    }
};

#include <iostream>

void printit(UniquePrintable p) {
    std::cout << "The printable thing was: " << p << "." << std::endl;
}

int main() {
    printit(42);
    printit("hello world");
}
```

直接打印值（传引用） [Godbolt.](https://godbolt.org/z/GTsK5c)

```c++
#include <ostream>

class PrintableRef {
    const void *data_;
    void (*print_)(std::ostream&, const void *);
public:
    template<class T>
    PrintableRef(const T& t) : data_(&t), print_([](std::ostream& os, const void *data) {
        os << *(const T*)data;
    }) { }

    friend std::ostream& operator<<(std::ostream& os, const PrintableRef& self) {
        self.print_(os, self.data_);
        return os;
    }
};

#include <iostream>

void printit(PrintableRef p) {
    std::cout << "The printable thing was: " << p << "." << std::endl;
}

int main() {
    printit(42);
    printit("hello world");
}
```



这两种类型擦除，一个是统一接口，记住值类型，然后打印方法和类型绑定

一个是干脆在一开始就吧打印方法实例化，值类型 void* 存地址 

也就是上面说到的两种技术的展开

第一种虚函数的方法是有开销的

说到std::function和std::any，标准库为这种虚函数做了优化，也叫SBO

首先从std::function的设计谈起

- 函数要不要保存？保存就是std::function,不保存就是[`function_ref`](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p0792r3.html). (一种view，提案中)

  - 需求，需不需要管理这个函数，生命周期等，function_ref只用不管

- 需不需要拷贝？需要就是std::function，不需要拷贝就是[`std::unique_function`](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p0228r3.html). (一种unique guard，提案中) 也就是move-only

- 需不需要共享？共享带来函数副作用了

  ```c++
  uto f = [i=0]() mutable { return ++i; };
  F<int()> alpha = f;
  F<int()> beta = alpha;
  F<int()> gamma = f;
  assert(alpha() == 1);
  assert(beta() == 2);  // beta shares alpha's heap-managed state
  assert(gamma() == 1);  
  ```

  可能会有个shared_function的东西（我感觉多余）

- SBO相关设计 类似SSO 就是在栈上开个buffer存，不分配堆资源

  - buffer大小？要不要可定制？ 当前不同的标准库用的buffer不一样，clang libc++ 是24 gcc libstdc++是16

  自己设计，可能会定制化

  ```c++
  template<class Signature, size_t Capacity = 24, size_t Align = alignof(std::max_align_t)>
  class F;
  
  using SSECallback = F<int(), 32, 32>;  // suitable for lambdas that capture MMX vector type
  ```

  这点子没人想过？不可能，已经有人实现了 [`inplace_function`](https://github.com/WG21-SG14/SG14/blob/master/SG14/inplace_function.h).

- 如果SBO优化不了怎么办？是不是需要支持alloctor接口？

- 强制SBO，不能SBO的直接编译爆错，[`inplace_function`](https://github.com/WG21-SG14/SG14/blob/master/SG14/inplace_function.h).做了

- SBO优化，要保证对象nothrow 

  - `static_assert(std::is_nothrow_move_constructible_v<T>)` inside the constructor of `F`.

- SBO优化针对not trivially copyable如何处理

  - libc++ 保证可以SBO，但是libstdc++没有 
  - 通过static_assert(is_trivially_relocatable_v<T> && sizeof(T) <= Capacity && alignof(T) <= Align) inside the constructor of F控制

- function能不能empty，能不能从nullptr构造

- function之间能不能转换类型？

还有很多角落，不想看了，这也是有各种function提案补充的原因


---

### ref

- https://www.newsmth.net/nForum/#!article/Programming/3083 发现个02年的介绍boost::any的帖子卧槽，历史的痕迹
- https://akrzemi1.wordpress.com/2013/11/18/type-erasure-part-i/
- 历史的痕迹 any_iterator http://thbecker.net/free_software_utilities/type_erasure_for_cpp_iterators/any_iterator.html
- std::function实现介绍 gcc源码级https://www.cnblogs.com/jerry-fuyi/p/std_function_interface_implementation.html
- std::function实现介绍，由浅入深 https://zhuanlan.zhihu.com/p/142175297
- 这个文章写的不错。我写了一半发现有人写了。。。 直接看这个就好了https://fuzhe1989.github.io/2017/10/29/cpp-type-erasure/





---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>

