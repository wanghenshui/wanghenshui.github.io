---
layout: post
categories: language
title: Avoiding Disasters with Strongly Typed C++
tags: [cppcon, c++]
---
  

演讲主题 类型歧义以及强类型解决方案

---

典型场景

 ```c++
foo(int index,int offset);
 ```

很容易把参数记错。类似的，bool hell，一堆bool类型函数

解决办法就是使用结构体，加强类型，见参考链接1,2

具体就是在基本类型的基础上封装上各种各样的policy类，和get接口，进一步，对各种量纲做类型traits

11

然后介绍了std::chrono中的量纲 std::ratio, 类似的，利用std::ratio能实现一些其他的量纲

### reference

1. https://github.com/joboccara/NamedType

2. <https://github.com/foonathan/type_safe>

3. 这里有个std::ratio 实现量纲分析的用法，议题仍是那个TMP书里讨论的量纲问题<https://benjaminjurke.com/content/articles/2015/compile-time-numerical-unit-dimension-checking/>

   

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。

