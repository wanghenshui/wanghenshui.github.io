---
layout: post
title: (译)Handles are the better pointers
category: [cpp]
tags: [c++, yaml]
---
{% include JB/setup %}

---

[toc]

作者的一个经验，把指针转换成index-handles，也就是如何写不涉及分配和指针的程序



背景

- 0.5到1百万行代码，智能指针管理内存
- 万到十万以上的小对象，堆分配，智能指针管理

这种管理方式基本不会有segfault，有问题的代码也都能抓到问题根源

但是存在问题

- dog-slow？遍地都是cache-miss
- 内存碎片问题
- fake memory leaks 内存指针占用的内存没有及时回收，看上去像是内存泄漏了，而这种问题通过内存检测工具也检查不出来

作者给的方法有一定借鉴意义（甚至对于那些GC语言，因为会面临同样的场景，大量小对象）

但是可能要要求创建销毁对象尽可能的集中，某些场景可能不可行，也就是面向数据

这里的使用场景是游戏场景，有大量小对象频繁创建删除

简要概括

- 所有的内存管理集中成一个模块，用这个模块来管理分配
- 把小对象分类，每个小对象有自己的数组指针-索引来管理
- 创建对象，返回index-handle就可以了
- 需要的话，就把handle强转指针来用，并且任何地方都不要保存指针

感觉这是个很常见的CRTP分配器套路，尽可能的复用内存，对于代理型应用，都会这么设计，作者是游戏型应用，也是有大量小对象大量的创建删除的。一个好的分配器能降低系统碎片且让cpu利用率高，不轻易cache miss --这些都影响延迟

下面作者说了针对他们这个场景的几点优势

- 管理高效
- cache friendly
  - 内存数据尽可能的热
- 不会有很多的内存碎片

全面用这个index-handle替换指针的优势

- 避免直接访问内存，安全
- 只有分配器组件知道这个内存分配的细节和指针信息，别人只能通过index拿到 （其实index也可以隐藏起来）
- 内存增长更安全，会尽可能复用，不会激增

但是这要求应用本身不能乱用指针，因为引用的对象随时会变



这个东西和普通的CRTP 内存池还不太一样。代码我还没有读。有些作者的设计点我没有领会完整。后面有时间会看看



### ref

- https://floooh.github.io/2018/06/17/handles-vs-pointers.html
- 作者的封装库 https://github.com/floooh/sokol#sokol_gfxh
- 背景文档 https://floooh.github.io/2018/06/02/one-year-of-c.html 也值得一看
- 我是看lobste上的推荐看的这篇文章，还有https://ourmachinery.com/post/data-structures-part-1-bulk-data/ 后面也要看看



---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。