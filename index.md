---
layout: page
title: What's Up, Bro
tagline: bro
---
{% include JB/setup %}

## Website I usually  used:

[Compiler Explorer](https://godbolt.org/) | [C++ Insights](https://cppinsights.io/) | [Wandbox](https://wandbox.org/) | [Itanium C++ ABI](https://itanium-cxx-abi.github.io/cxx-abi/abi.html#acknowledgements) | [C++ Ref](http://zh.cppreference.com/w/%E9%A6%96%E9%A1%B5)

[Rocksdb CN Doc](https://wanghenshui.github.io/rocksdb-doc-cn/) | [Cpp Draft](https://wanghenshui.github.io/cppwp/)

[Rust Doc](https://doc.rust-lang.org/std/)

[gist viewer](https://wanghenshui.github.io/gist-viewer/) | [Readfree](https://readfree.me/)

## About Me

A humble coder, working in c++, python and rust
Current research in NoSQL database, [resume](https://wanghenshui.github.io/resume/)

Want to learn about kernel, compiler, networking, distributed server, and so on.

Not a pro, try my best.

All quarrels are but few readings.

 Quote from tk@tombkeeper
> I often advise friends who support my views not to argue with opponents in comments. 
> Because spending time sharing ideas with others is a more effective use of your time. 
> It is certainly not impossible to argue in the comments 
> if one is willing to spend one's precious time on the opponent, 
> and for a very remote purpose, which is to persuade the other party 
> that I think it is very generous, which I often fail to do.



## Contact Me

@wechat&&phone&&QQ(base64): MTg4NDQxODk1MzM= 

![Wechat code](https://wanghenshui.github.io/assets/0-1552008412820.jpg)

@email: wanghenshui@qq.com

[@telegram](http://t.me/wanghenshui) 
[@steam](https://steamcommunity.com/id/wanghenshui/) 
[@github]( https://github.com/wanghenshui/) 
[@zhihu](https://zhuanlan.zhihu.com/jieyaren) 
[@douban]( https://www.douban.com/people/61740133/) 





## Recent Posts

Here's the recent "posts list".

<ul class="posts">
  {% for post in site.posts %}
    <li><span>{{ post.date | date_to_string }}</span> &raquo; <a href="{{ BASE_PATH }}{{ post.url }}">{{ post.title }}</a></li>
  {% endfor %}
</ul>
