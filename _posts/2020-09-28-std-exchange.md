---
layout: post
title: std::exchange用法
categories: [c++]
tags: [type, c++14, cppcon, cppcon17]
---

这个函数没啥好说的，主要是为了`偷东西` 诞生的,实现非常简单

```c++
template<class T, class U = T>
constexpr // since C++20
T exchange(T& obj, U&& new_value)
{
    T old_value = std::move(obj);
    obj = std::forward<U>(new_value);
    return old_value;
}
```



比如参考链接1里面 move constructor的实现

```c++
struct S
{
  int n;
 
  S(S&& other) noexcept : n{std::exchange(other.n, 0)}
  {}
 
  S& operator=(S&& other) noexcept 
  {
    if(this != &other)
        n = std::exchange(other.n, 0); // 移动 n ，并于 other.n 留下零
    return *this;
  }
};
```



我看到的用法

```c++
template <promise_base::urgent Urgent>
void promise_base::make_ready() noexcept {
    if (_task) {
        if (Urgent == urgent::yes) {
            ::seastar::schedule_urgent(std::exchange(_task, nullptr));
        } else {
            ::seastar::schedule(std::exchange(_task, nullptr));
        }
    }
}
```





可能就要比较`std::swap`和他的区别了，直接上结论吧，上限是std::swap的性能，要不是为了偷东西这个特性，不要用

SO有个链接做了简单验证，见参考链接2

然后***Ben Deane*** 有个案例 std::exchange 惯用法，在参考链接3 4 里。简单概括下

就是用std:exchange 来省掉没必要的临时变量，链接3 的ppt可以看下，写的很漂亮，作者叫他 **The “swap-and-iterate” pattern**

 我把参考链接四的代码贴一下

以前用swap

```c++
class Dispatcher {
    // We hold some vector of callables that represents
    // events to dispatch or actions to take
    using Callback = /* some callable */;
    std::vector<Callback> callbacks_;
 
    // Anyone can register an event to be dispatched later
    void defer_event(const Callback& cb) {
        callbacks_.push_back(cb);
    }
 
    // All events are dispatched when we call process
    void process() {
        std::vector<Callback> tmp{};
        using std::swap; // the "std::swap" two-step
        swap(tmp, callbacks_);
        for (const auto& callback : tmp) {
            std::invoke(callback);
        }
    }
  
    void post_event(Callback& cb) {
        Callback tmp{};
        using std::swap;
        swap(cb, tmp);
        PostToMainThread([this, cb_ = std::move(tmp)] {
            callbacks_.push_back(cb_);
        });
    }
};
```



改成exchange

```c++
class Dispatcher {
    // ...
 
    // All events are dispatched when we call process
    void process() {
        for (const auto& callback : std::exchange(callbacks_, {}) {
            std::invoke(callback);
        }
    }
    
    void post_event(Callback& cb) {
        PostToMainThread([this, cb_ = std::exchange(cb, {})] {
            callbacks_.push_back(cb_);
        });
    }
};
```



可能你会问，直接std::move不就完事儿，这里作者强调接口的灵活性？

强调move并不会empty,并不会clear，可能还有值，比如std::optional 



结合lock

原本std::swap 是这样的

```c++
class Dispatcher {
    // ...
 
    // All events are dispatched when we call process
    void process() {
        std::vector<Callback> tmp{};
        {
            using std::swap;
            std::scoped_lock lock{mutex_};
            swap(tmp, callbacks_);
        }
        for (const auto& callback : tmp) {
            std::invoke(callback);
        }
    }
};
```

改成exchange 省掉一个数组

```c++
class Dispatcher {
    // ...
 
    // All events are dispatched when we call process
    void process() {
        std::scoped_lock lock{mutex_};
        for (const auto& callback : std::exchange(callbacks_, {})) {
            std::invoke(callback);
        }
    }
};
```

能不能吧lock也省掉？临时变量声明周期是一行，一行就够了

```c++
class Dispatcher {
    // ...
 
    // All events are dispatched when we call process
    void process() {
        const auto tmp = (std::scoped_lock{mutex_}, std::exchange(callbacks_, {}));
        for (const auto& callback : tmp) {
            std::invoke(callback);
        }
    }
};
```






---

### ref

- https://zh.cppreference.com/w/cpp/utility/exchange
- https://stackoverflow.com/questions/20807938/stdswap-vs-stdexchange-vs-swap-operator
- https://github.com/CppCon/CppCon2017/blob/master/Lightning%20Talks%20and%20Lunch%20Sessions/std%20exchange%20idioms/std%20exchange%20idioms%20-%20Ben%20Deane%20-%20CppCon%202017.pdf
- https://www.fluentcpp.com/2020/09/25/stdexchange-patterns-fast-safe-expressive-and-probably-underused/



---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>