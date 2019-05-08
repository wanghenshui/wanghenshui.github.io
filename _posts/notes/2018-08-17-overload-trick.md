---
layout: post
category : c++
title: overloaded trick
tags : [c++,gcc]
---
{% include JB/setup %}

### why

这篇就是参考链接2的总结，还是从参考链接1中单独拎出来说一下

---



之前学std::variant 和 std::visit   学到了overloaded这个模板，

```c++
#include <variant>
#include <cstdio>
#include <vector>

template<class... Ts> struct overloaded : Ts... { using Ts::operator()...; }; // (1)
template<class... Ts> overloaded(Ts...) -> overloaded<Ts...>;  // (2)

using var_t = std::variant<int, const char*>;

int main() {
    std::vector<var_t> vars = {1, 2, "Hello, World!"};

    for (auto& v : vars) {
        std::visit(overloaded {  // (3)
            [](int i) { printf("%d\n", i); },
            [](const char* str) { puts(str); }
        }, v);
    }

    return 0;
}
```

(2)是c++17引入的新特性，乍一看看不懂，咱们一点一点顺一下



首先，这个overloaded模板就是一个转发继承而来的operator (),  一个粗暴的版本，需要基类实现operator()

```c++
struct PrintInt { //(1)
    void operator() (int i) {
        printf("%d\n", i);
    }
};

struct PrintCString { // (2)
    void operator () (const char* str) {
        puts(str);
    }
};

struct Print : PrintInt, PrintCString { // (3)
    using PrintInt::operator();
    using PrintCString::operator();
};
```



如果写成模板形式，那就是

```c++
template <class... Ts> // (1)
struct Print : Ts... {
    using Ts::operator()...;
};

int main() {
    std::vector<var_t> vars = {1, 2, "Hello, World!"};

    for (auto& v : vars) {
        std::visit(Print<PrintCString, PrintInt>{}, v); // (2)
    }

    return 0;
}
```



注意到这个写法特别重，考虑到开头这个优雅的用法，使用lambda，代码写起来就更难看了

```c++
int main() {
    std::vector<var_t> vars = {1, 2, "Hello, World!"};
    auto PrintInt = [](int i) { printf("%d\n", i); }; // (1)
    auto PrintCString = [](const char* str) { puts(str); };

    for (auto& v : vars) {
        std::visit(
            Print<decltype(PrintCString), decltype(PrintInt)>{PrintCString, PrintInt}, // (2)
            v);
    }

    return 0;
}
```

所以理所当然，推导动作应该放在一个helper函数里,    上面这个调用模式还是很容写出一个推导helper的

```c++
template <class... Ts> // (1)
auto MakePrint(Ts... ts) {
    return Print<Ts...>{ts...};
}

int main() {
    std::vector<var_t> vars = {1, 2, "Hello, World!"};

    for (auto& v : vars) {
        std::visit(
            MakePrint( // (2)
                [](const char* str) { puts(str); },
                [](int i) { printf("%d\n", i); }
                ),
            v);
    }

    return 0;
}
```

这已经和overload非常接近了，回到一开始我们提到的，如何写成开头那个样子呢，这就需要c++

17 的新特性，类模板实参推导,   自定义推导指引，User-defined deduction guides，简单说，就是构造函数能做helper的活(make_tuple, make_pair)，只要定义好规则就可以

在c++17中，可以干净的写出

```c++
std::tuple t(4, 3, 2.5); // same as auto t = std::make_tuple(4, 3, 2.5);
```

 在tuple中，写好了推导规则

```c++
#ifndef _LIBCPP_HAS_NO_DEDUCTION_GUIDES
// NOTE: These are not yet standardized, but are required to simulate the
// implicit deduction guide that should be generated had libc++ declared the
// tuple-like constructors "correctly"
template <class _Alloc, class ..._Args>
tuple(allocator_arg_t, const _Alloc&, tuple<_Args...> const&) -> tuple<_Args...>;
template <class _Alloc, class ..._Args>
tuple(allocator_arg_t, const _Alloc&, tuple<_Args...>&&) -> tuple<_Args...>;
#endif
```

make_tuple就下岗了

类似的，只要为Print写好推导，就可以省掉MakePrint

```c++
#include <variant>
#include <cstdio>
#include <vector>

using var_t = std::variant<int, const char*>;

template <class... Ts>
struct Print : Ts... {
    using Ts::operator()...;
};

template <class...Ts> Print(Ts...) -> Print<Ts...>; // (1)

int main() {
    std::vector<var_t> vars = {1, 2, "Hello, World!"};
    for (auto& v : vars) {
        std::visit(
            Print{ // (2)
                [](const char* str) { puts(str); },
                [](int i) { printf("%d\n", i); }
            },
            v);
    }
    return 0;
}
```



  到此，overloaded trick就解释完了




### reference
- 上一篇文章<https://wanghenshui.github.io/2018/08/15/variant-visit>

- 对overload的解释 https://dev.to/tmr232/that-overloaded-trick-overloading-lambdas-in-c17

- 对overload的解释和加强，并且有提案。https://arne-mertz.de/2018/05/overload-build-a-variant-visitor-on-the-fly/

- 类模板实参推导 <https://zh.cppreference.com/w/cpp/language/class_template_argument_deduction> 注意后面的User-defined deduction guides 用户定义推导指引

- 这篇文章更好的写了个match，我没写成。。这个写的还挺好玩的<https://zhuanlan.zhihu.com/p/52519126>

  

看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。