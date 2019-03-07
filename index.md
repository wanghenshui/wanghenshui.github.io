---
layout: page
title: Welcome
#tagline: Supporting tagline
---
{% include JB/setup %}

常用的网站导航

[Compiler Explorer](https://godbolt.org/) [c++ Insights](https://cppinsights.io/) [Wandbox](https://wandbox.org/) [Itanium C++ ABI](https://itanium-cxx-abi.github.io/cxx-abi/abi.html#acknowledgements) [cpp ref](http://zh.cppreference.com/w/%E9%A6%96%E9%A1%B5)


## About me

补习中的程序员，努力学习c++，python，rust中
目前研究NoSQL数据库内核方向，门外汉，[简历](https://github.com/wanghenshui/resume/blob/master/wqw.pdf)

想研究分布式服务端，分布式数据库 ~~，高并发服务端，网络编程，编译器等等~~ 
非计算机科班出身，还是要不断练习啊。

一切争吵无非读书太少。引自大神tk@tombkeeper

> 我常建议支持我观点的朋友不要在评论里和反对者辩论。因为把时间用来和众人分享想法是更有效的利用方式。在评论中辩论当然不是不可以，如果有人愿意将宝贵的时间花在反对者身上，并且是为了一个可能性极其渺茫的目标，即：说服对方，我认为这是非常慷慨的，我常常做不到如此慷慨。

@微信&&电话&&QQ(base64): MTg4NDQxODk1MzM= 
@email: wanghenshui@qq.com

[@telegram](t.me/wanghenshui) 
[@steam](https://steamcommunity.com/id/wanghenshui/) 
[@github]( https://github.com/wanghenshui/) 
[@知乎专栏(看缘分更新)](https://zhuanlan.zhihu.com/jieyaren) 
[@豆瓣]( https://www.douban.com/people/61740133/) 
[@读书笔记]( https://www.douban.com/people/jieyaren/reviews) 
[读书摘要](https://github.com/wanghenshui/book_review)
## Recent Posts

Here's the recent "posts list".

<ul class="posts">
  {% for post in site.posts %}
    <li><span>{{ post.date | date_to_string }}</span> &raquo; <a href="{{ BASE_PATH }}{{ post.url }}">{{ post.title }}</a></li>
  {% endfor %}
</ul>
