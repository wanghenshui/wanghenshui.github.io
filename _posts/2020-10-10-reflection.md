---
layout: post
title: c++反射的几种实现以及介绍几个库
categories: [language]
tags: [c++, reflect, boost]
---

人需求真是复杂。又想要名字信息，又想要泛化的访问接口

反射实现的几种方案

- 预处理一层
  - 代表 QT Unreal 先用宏声明好需要处理的字段，然后让编译框架中的预-预编译处理器先处理一遍，展开对应的标记
  - 用libclang来做，[metareflect](https://github.com/Leandros/metareflect)  [cpp-reflection](https://github.com/AustinBrunkhorst/CPP-Reflection) 还有个原理[介绍](https://austinbrunkhorst.com/cpp-reflection-part-1/)
- 注册，有几种方案
  - 用宏拼方法+注册 [Rttr](https://github.com/rttrorg/rttr) 
  - 手写注册 [meta](https://github.com/skypjack/meta)
  - 编译器推导(功能有限) magic_get




---

### ref

-  复述了这篇博客的内容 https://blog.csdn.net/D_Guco/article/details/106744416
-  [Rttr](https://github.com/rttrorg/rttr) 这个手法就是宏注册 
-  [ponder](https://billyquith.github.io/ponder/) 也是有一个注册中心的，把字符串和函数指针绑起来
-  [cista](https://github.com/felixguendling/cista) [官网介绍](https://cista.rocks/) 这个库的思路和之前提到的magic_get差不多，也提供宏注入的手段，他说灵感来自这个[帖子](https://playfulprogramming.blogspot.com/2016/12/serializing-structs-with-c17-structured.html)


---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>