---
layout: post
title: 重载返回值
category: [c++]
tags: [c++]
---
{% include JB/setup %}

---

[toc]

> 本文是参考链接的翻译整理



主要是这个场景

```c++
// this is OK
std::string to_string(int i);
std::string to_string(bool b);

std::string si = to_string(0);
std::string sb = to_string(true);

// this is not OK
int from_string(std::string_view s);
bool from_string(std::string_view s);

int i = from_string("7");
bool b = from_string("false");

```



想让返回值更统一

做法是做一个统一的返回类型，然后重载 类型操作符



```c++
struct to_string_t
{
    std::string_view s;

    operator int() const;  // int  from_string(std::string_view s);
    operator bool() const; // bool from_string(std::string_view s);
};

int i = to_string_t{"7"};
bool b = to_string_t{"true"};

```



每个类型都要写？模版话，给内建类型定义好，自己的类型，自己用sfinae拼



```c++
// base template, specialize and provide a static from_string method
template <class T, class = void>
struct to_string_impl 
{
};

namespace detail // hide impl detail
{
template <class T>
auto has_from_string(int) -> decltype(
    to_string_impl<T>::from_string(std::declval<std::string_view>()), 
    std::true_type{});

template <class T>
std::false_type has_from_string(char);
}

// check if T has a from_string
template <class T>
constexpr bool has_from_string = decltype(detail::has_from_string<T>(0))::value;

// return-type overload mechanism
struct to_string_t
{
    std::string_view s;

    template <class T>
    operator T() const 
    {
        static_assert(has_from_string<T>, "conversion to T not supported");
        return to_string_impl<T>::from_string(s); 
    }
};

// convenience wrapper to provide a "return-type overloaded function"
to_string_t from_string(std::string_view s) { return to_string_t{s}; }



//各种类型的实现自己拼好就可以了
template <>
struct to_string_impl<int>
{
    static int from_string(std::string_view s);
};

template <>
struct to_string_impl<bool>
{
    static bool from_string(std::string_view s);
};

//自定义实现
template <class T>
struct my_range { /* ... */ };

template <class T>
struct to_string_impl<my_range<T>, std::enable_if_t<has_from_string<T>>>
{
    static my_range<T> from_string(std::string_view s);
};

```



就是偏特化+sfinae套路







---

### ref

- https://artificial-mind.net/blog/2020/10/10/return-type-overloading


---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。