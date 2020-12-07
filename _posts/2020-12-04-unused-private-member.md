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





---



看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>