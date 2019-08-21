---
layout: post
category: cpp
title: Abseil Tip of the Week
tags: [c++]
---

{% include JB/setup %}

本文是Abseil库 tip of the week的总结。不是翻译，有些点子还是不错的。

---

##### totw #1 string_view

厌烦了const char*到string之间的处理转换？你只是想用一下而已不需要构造一个拷贝？string_view就是为此而生的，它是一个视图，就是一个借用，也是类似go rust胖指针 slice之类的东西。内部有一个指针和一个长度

注意，string_view是没有\0的

##### totw #3 String Concatenation and operator+ vs. StrCat()

简单说，不要用string::operator +() 会有临时变量。absl::StrCat用来解决这个问题

##### totw #10 Splitting Strings, not Hairs

absl提供了string split相关函数

```c++
// Splits on commas. Stores in vector of string_view (no copies).
std::vector<absl::string_view> v = absl::StrSplit("a,b,c", ',');

// Splits on commas. Stores in vector of string (data copied once).
std::vector<std::string> v = absl::StrSplit("a,b,c", ',');

// Splits on literal string "=>" (not either of "=" or ">")
std::vector<absl::string_view> v = absl::StrSplit("a=>b=>c", "=>");

// Splits on any of the given characters (',' or ';')
using absl::ByAnyChar;
std::vector<std::string> v = absl::StrSplit("a,b;c", ByAnyChar(",;"));

// Stores in various containers (also works w/ absl::string_view)
std::set<std::string> s = absl::StrSplit("a,b,c", ',');
std::multiset<std::string> s = absl::StrSplit("a,b,c", ',');
std::list<std::string> li = absl::StrSplit("a,b,c", ',');

// Equiv. to the mythical SplitStringViewToDequeOfStringAllowEmpty()
std::deque<std::string> d = absl::StrSplit("a,b,c", ',');

// Yields "a"->"1", "b"->"2", "c"->"3"
std::map<std::string, std::string> m = absl::StrSplit("a,1,b,2,c,3", ',');
```

要是c++有python那种split就好了。（那种效率比较低）

##### totw #149 Object Lifetimes vs. `=delete`





----

### ref

1. https://abseil.io/tips/



Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。