---
layout: post
category: c++
title: 检测函数重载
tags: [c++, template, sfinae]
---

  

本文是参考链接1 的翻译，感谢原作者。

---

#### Why

考虑一个简单的需求，Compute函数接口，有这么两个接口

```c++
// lib V1:
void Compute(int in, int& out) { }
// lib V2:
void Compute(double in, double& out) { }
```

假如我想用v2的接口但是用不到，可能就需要自己适配，如何灵活的检查这个接口呢？

首先想到的就是宏，判断接口使用的版本，区分出，然后自己适配接口。但是问题在于接口宏混乱以后无法灵活的适配

这时候就需要第三种方法，就是模板探测惯用法了



```c++
template <typename T, typename = void>
struct is_compute_available : std::false_type {};

template <typename T>
struct is_compute_available<T, 
           std::void_t<decltype(Compute(std::declval<T>(), 
                       std::declval<T&>())) >> : std::true_type {};
```

其中std::void_t吃掉decltye的类型。如果Compute对于指定的T没有匹配，整体就会退化到第一个匹配

关于std::void_t 参考链接2 3也可以看一下。有很多类似的用法。新时代的std::enable_if

上面的整体封装一下

```c++
// helper variable template
template< class T> inline constexpr bool is_compute_available_v = 
          is_compute_available<T>::value;

template <typename T>
void ComputeTest(T val)
{
    if constexpr (is_compute_available_v<T>)
    {
        T out { };
        Compute(val, out);
    }
    else
    {
        std::cout << "fallback...\n";
    }
}
```



回到这篇文章想要讨论的函数，std::from_chars.鉴于这些功能实现的还不完整，msvc全实现了，gcc和clang只实现了T=int

所以套用上面的解决方案，如果用宏，能区分gcc clang和msvc，但是具体到gcc和clang呢？

考虑feature test macros，但是这个只能确定有没有这个功能，不能确定这个功能支持啥类型



最终，使用模板探测惯用法

```c++
template <typename T, typename = void>
struct is_from_chars_convertible : false_type {};
template <typename T>
struct is_from_chars_convertible<T, 
                 void_t<decltype(from_chars(declval<const char*>(), declval<const char*>(), declval<T&>()))>> 
                 : true_type {};


template <typename T>
[[nodiscard]] std::optional<T> TryConvert(std::string_view sv) noexcept {
    T value{ };
    if constexpr (is_from_chars_convertible<T>::value) {
        const auto last = sv.data() + sv.size();
    const auto res = std::from_chars(sv.data(), last, value);
    if (res.ec == std::errc{} && res.ptr == last)
            return value;
    }
    else  {
        try {
            std::string str{ sv };
            size_t read = 0;
            if constexpr (std::is_same_v<T, double>)
                value = std::stod(str, &read);
            else if constexpr (std::is_same_v<T, float>)
                value = std::stof(str, &read);

            if (str.size() == read)
                return value;
        }
        catch (...) {  }
    }
}
```

不支持的类型放到try里用以前的api来搞。全文完。参考6中提到了作者提到的几个参考链接。非常棒。



----

### ref

1. https://www.bfilipek.com/2019/07/detect-overload-from-chars.html
2. std::void_t https://zh.cppreference.com/w/cpp/types/void_t
3. 这里有个介绍detection idiom的 写的不错。https://zhuanlan.zhihu.com/p/26155469
4. std::from_charshttps://zh.cppreference.com/w/cpp/utility/from_chars
5. std::is_detected 上面这套东西的封装 https://en.cppreference.com/w/cpp/experimental/is_detected
6. 几个作者提到的网址
   1. https://stackoverflow.com/questions/51404763/c-compile-time-check-that-an-overloaded-function-can-be-called-with-a-certain
   2. https://stackoverflow.com/questions/257288/is-it-possible-to-write-a-template-to-check-for-a-functions-existence
   3. 又讲了遍函数探测方法，https://akrzemi1.wordpress.com/2014/06/26/clever-overloading/
   4. std::from_chars详细介绍，有了这套工具，可以放弃sprintf https://www.bfilipek.com/2018/12/fromchars.html
   5. 这里提到了expression SFINAE ，其实手法差不多，也是decltype和void_t std::declval  https://blog.tartanllama.xyz/detection-idiom/ 里面的链接内容不错。有时间可以看看。



Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。