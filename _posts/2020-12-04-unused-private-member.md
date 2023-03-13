---
layout: post
title: (译)编译器是如何处理没用到的代码的？
categories: [language, translation]
tags: [c++, compiler]
---


---

>  [原文链接](https://quuxplusone.github.io/blog/2020/12/02/unused-private-member/)

作者整理了一份测试的表格（这个大哥是真爱c++啊这种细节都要扣我感觉魔怔了有点）

| 编译器是否会对没被用到的___ 发出警告                 | Clang | GCC   | ICC  | MSVC |
| ---------------------------------------------------- | ----- | ----- | ---- | ---- |
| static function                                      | -Wall | -Wall |      | -W4  |
| static variable                                      | -Wall | -Wall |      |      |
| private data member                                  | -Wall |       |      |      |
| private static data member                           |       |       |      |      |
| private member function                              |       |       |      |      |
| private static member function                       |       |       |      |      |
| data member of private class                         |       |       |      |      |
| static data member of private class                  |       |       |      |      |
| member function of private class                     |       |       |      |      |
| static member function of private class              |       |       |      |      |
| anonymous-namespaced function                        | -Wall | -Wall |      |      |
| anonymous-namespaced variable                        | -Wall | -Wall |      |      |
| data member of anonymous-namespaced class            |       |       |      |      |
| static data member of anonymous-namespaced class     | -Wall | -Wall |      |      |
| member function of anonymous-namespaced class        |       | -Wall |      |      |
| static member function of anonymous-namespaced class |       | -Wall |      |      |
| function taking anonymous-namespaced class           | -Wall | -Wall |      |      |



| 编译器是否会优化掉未使用的________                   | Clang | GCC  | ICC  | MSVC |
| ---------------------------------------------------- | ----- | ---- | ---- | ---- |
| static function                                      | -O0   | -O1  | -O0  | -Od  |
| static variable                                      | -O0   | -O0  | -O1  | -Od  |
| private data member                                  | —     | —    | —    | —    |
| private static data member                           | —     | —    | —    | —    |
| private member function                              | —     | —    | —    | —    |
| private static member function                       | —     | —    | —    | —    |
| static data member of private class                  | —     | —    | —    | —    |
| member function of private class                     | —     | —    | —    | —    |
| static member function of private class              | —     | —    | —    | —    |
| anonymous-namespaced function                        | -O0   | -O1  | -O0  |      |
| anonymous-namespaced variable                        | -O0   | -O0  | -O1  | -Od  |
| static data member of anonymous-namespaced class     | -O0   | -O0  | -O1  |      |
| member function of anonymous-namespaced class        | -O0   | -O1  | -O1  |      |
| static member function of anonymous-namespaced class | -O0   | -O1  | -O1  |      |
| function taking anonymous-namespaced class           | -O0   | -O1  | -O1  |      |



还有很多优化空间

注意 没用到的私有函数是不回被删掉的，所以有个hack: 模版参数是私有函数指针，通过显式实例化绕开private限制，实现静态注入/调用，详情看[这篇文章](https://wanghenshui.github.io/2020/04/28/profiting-from-the-folly-of-others.html)



---



