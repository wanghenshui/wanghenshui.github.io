---
layout: post
title: 类型擦除技术 type erasure
category: [c++]
tags: [c++]
---
{% include JB/setup %}

---

说是类型擦除技术，不如说是多态技术



函数指针多态 几种做法

- void* 传统的万能参数
- 继承接口值多态，dynamic_cast
- 值语意的多态，type erasure 也就是类型擦除
  - std::function   boost::any_range boost::any 




---

### ref

- https://www.newsmth.net/nForum/#!article/Programming/3083 发现个02年的介绍boost::any的帖子卧槽，历史的痕迹
- https://akrzemi1.wordpress.com/2013/11/18/type-erasure-part-i/
- 历史的痕迹 any_iterator http://thbecker.net/free_software_utilities/type_erasure_for_cpp_iterators/any_iterator.html
- std::function实现介绍 gcc源码级https://www.cnblogs.com/jerry-fuyi/p/std_function_interface_implementation.html
- std::function实现介绍，由浅入深 https://zhuanlan.zhihu.com/p/142175297
- 这个文章写的不错。我写了一半发现有人写了。。。 直接看这个就好了https://fuzhe1989.github.io/2017/10/29/cpp-type-erasure/





---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。

