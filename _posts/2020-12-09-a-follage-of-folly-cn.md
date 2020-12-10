---
layout: post
title: (译)还是讨论folly的静态注入技术:合法访问私有成员函数
categories: [language, translation]
tags: [c++, folly]
---


---

>  [原文链接](https://dfrib.github.io/a-foliage-of-folly/)



需求，不改动Foo类的前提下访问bar和x，即使他们是private

```c++
// foo.h
#pragma once
#include <iostream>

class Foo {
    int bar() const {
        std::cout << __PRETTY_FUNCTION__;
        return x;
    }

    int x{42};
};
```



先是总结了一遍folly的技术

```c++
// access_private_of_foo.h
#pragma once
#include "foo.h"

// Unique namespace in each TU.
namespace {
// Unique type in each TU (internal linkage).
struct TranslationUnitTag {};
}  // namespace

// 'Foo::bar()' invoker.
template <typename UniqueTag,
          auto mem_fn_ptr>
struct InvokePrivateFooBar {
    // (Injected) friend definition.
    friend int invoke_private_Foo_bar(Foo const& foo) {
        return (foo.*mem_fn_ptr)();
    }
};
// Friend (re-)declaration.
int invoke_private_Foo_bar(Foo const& foo);

// Single explicit instantiation definition.
template struct InvokePrivateFooBar<TranslationUnitTag, &Foo::bar>;

// 'Foo::x' accessor.
template <typename UniqueTag,
          auto mem_ptr>
struct AccessPrivateMemFooX {
    // (Injected) friend definition.
    friend int& access_private_Foo_x(Foo& foo) {
        return foo.*mem_ptr;
    }
};
// Friend (re-)declaration.
int& access_private_Foo_x(Foo& foo);

// Single explicit instantiation definition.
template struct AccessPrivateMemFooX<TranslationUnitTag, &Foo::x>;
```

这个代码更清晰一点，之前也谈到过，见[这篇文章](https://wanghenshui.github.io/2020/04/28/profiting-from-the-folly-of-others.html)

现在是2020年了，考虑c++20的做法

> C++20 implemented [P0692R1](http://open-std.org/JTC1/SC22/WG21/docs/papers/2017/p0692r1.html) (*Access Checking on Specializations*), summarized in [P2131R0](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2131r0.html) (*Changes between C++17 and C++20 DIS*) as



> This change fixes a long-standing, somewhat obscure situation, where it  was not possible to declare a template specialization for a template  argument that is a private (or protected) member type. For example,  given `class Foo { class Bar {}; };`, the access `Foo::Bar` is now allowed in `template<class> struct X; template<> struct X<Foo::Bar>;`.



特化模版，模版参数可以填private/protected成员函数, 也就规避了显式实例化，保留原来的特化即可

回到这个函数接口，原来的友元技术不变，只是去掉显式实例化

```c++
// accessprivate.h
#pragma once
template <auto mem_ptr>
struct AccessPrivate
{
    // kMemPtr is intended to be either a pointer to a private
    // member function or pointer to a private data member.
    static constexpr auto kMemPtr = mem_ptr;
    struct Delegate;  // Define only in explicit specializations.
};
```

```c++
// access_private_of_foo_cpp20.h
#pragma once
#include "accessprivate.h"
#include "foo.h"

// Specialize the nested Delegate class for each private
// member function or data member of Foo that we'd like to access.

template <>
struct AccessPrivate<&Foo::bar>::Delegate {
    // (Injected) friend definition.
    friend int invoke_private_Foo_bar(Foo const& foo) {
        return (foo.*kMemPtr)();
    }
};
// Friend (re-)declaration.
int invoke_private_Foo_bar(Foo const& foo);

template <>
struct AccessPrivate<&Foo::x>::Delegate {
    // (Injected) friend definition.
    friend int& access_private_Foo_x(Foo& foo) {
        return foo.*kMemPtr;
    }
};
// Friend (re-)declaration.
int& access_private_Foo_x(Foo& foo);
```



注意这里，声明了Delegate，只特化需要的注入访问接口，之前的显式实例化，以及匿名空间Tag(TU唯一)都去掉了。加了一层Delegate



用宏整理一下



```c++
// accessprivate/accessprivate.h
#pragma once

namespace accessprivate {
template <auto mem_ptr>
struct AccessPrivate
{
    // kMemPtr is intended to be either a pointer to a private
    // member function or pointer to a private data member.
    static constexpr auto kMemPtr = mem_ptr;
    struct Delegate;  // Define only in explicit specializations.
};

}  // namespace accessprivate

// DEFINE_ACCESSOR(<qualified class name>, <class data member>)
//
// Example usage:
//   DEFINE_ACCESSOR(foo::Foo, x)
//
// Defines:
//   auto& accessprivate::get_x(foo::Foo&)
#define DEFINE_ACCESSOR(qualified_class_name, class_data_member)\
namespace accessprivate {\
template <>\
struct AccessPrivate<&qualified_class_name::class_data_member>::Delegate {\
    friend auto& get_##class_data_member(\
        qualified_class_name& obj) { return obj.*kMemPtr; }\
};\
auto& get_##class_data_member(qualified_class_name& obj);\
}
```



这样写getter setter更简单

```c++
#include <iostream>
#include "accessprivate/accessprivate.h"

namespace bar {

struct Bar {
    int getX() const { return x; }
    int getY() const { return y; }
private:
    int x{42};
    int y{88};
};

}  // namespace bar

DEFINE_ACCESSOR(bar::Bar, x)
// -> accessprivate::get_x(Bar&)
DEFINE_ACCESSOR(bar::Bar, y)
// -> accessprivate::get_y(Bar&)

void demo() {
    bar::Bar b{};
    accessprivate::get_x(b) = 13;
    accessprivate::get_y(b) = 33;
    std::cout << b.getX() << " " << b.getY();  // 13 33
}
```



作者已经写了[仓库](https://github.com/dfrib/accessprivate) c++17可用

---

### ref

- 原文中列出了一些c++的标准中对应的描述，这里不列举了，不仔细追究什么符号查找之类的限定了
- 作者的博客很值得一读，老语言律师了
- 还有一个讨论，技巧和folly一样，不多说了 https://quuxplusone.github.io/blog/2020/12/03/steal-a-private-member/


---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>