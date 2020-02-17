---
layout: page
title: What's Up, Bro
tagline: bro
---
{% include JB/setup %}

## Website I usually  used

[CppCoreGuidelines](https://isocpp.github.io/CppCoreGuidelines/)\| [Compiler Explorer](https://godbolt.org/) \| [C++ Insights](https://cppinsights.io/) \| [Wandbox](https://wandbox.org/) \| [Itanium C++ ABI](https://itanium-cxx-abi.github.io/cxx-abi/abi.html#acknowledgements) \| [C++ Ref](http://zh.cppreference.com/w/%E9%A6%96%E9%A1%B5) \| [Rust Doc](https://doc.rust-lang.org/std/) \| [demangle online](http://demangler.com/) \| [c++filtjs](https://d.fuqu.jp/c++filtjs/) \| [ascii table](http://www.asciitable.com/)

[rocksdb blog](https://rocksdb.org/blog/) \| [Rocksdb CN Doc](https://wanghenshui.github.io/rocksdb-doc-cn/) (tks [johnzeng](https://github.com/johnzeng)) \| [MyRocks CN Doc](https://wanghenshui.github.io/MyRocks_zh_doc/) (tks [zhangshuao](https://github.com/zhangshuao/MyRocks_zh_doc)) \|

[Cpp Draft](https://wanghenshui.github.io/cppwp/) \| [Gist Viewer](https://wanghenshui.github.io/gist-viewer/) \| [ReadFree](https://readfree.me/) \| [Book Review](https://wanghenshui.github.io/book_review/) not finish yet \|

[Vim CheatSheet](https://vim.rtorr.com/lang/zh_cn)  \| [ISOCPP Blog](https://isocpp.org/blog) \| [Fluent C++](https://www.fluentcpp.com/) \| [Bartek's Awesome c++  blog](https://www.bfilipek.com/)\| [Simon Brand's c++ blog](https://blog.tartanllama.xyz/)

[python anti-pattern](https://docs.quantifiedcode.com/python-anti-patterns/index.html) \|

[highscalability](http://highscalability.com/) \|

[programming in the twenty-first century](https://prog21.dadgum.com/23.html) \|

[Building a Data Pipeline - Languages and Stack](https://blog.subnetzero.io/post/2018/11/grimwhisker-language-and-stack/) \|

[leveldb](https://dirtysalt.github.io/html/leveldb.html) \| [Crafting Interpreters](http://craftinginterpreters.com/contents.html) \| [redbase](https://cs.stanford.edu/people/widom/cs346/) \| [TDOP](https://tdop.github.io/) \|

[Awesome Distribute systems](https://github.com/zhenlohuang/awesome-distributed-systems)\| [ds](https://github.com/ty4z2008/Qix/blob/master/ds.md) \| [Christopher Meiklejohn's cool blog, about distribute system](http://christophermeiklejohn.com/) \| [baptiste-wicht's cool blog, about c++](https://baptiste-wicht.com/) \|

[Rust Macro cn](http://blog.luxko.site/tlborm-chinese/book/) \|

[bash cheat sheet](https://devhints.io/bash) \|

[YAML lint](http://www.yamllint.com/) \|

[oi wiki](https://oi-wiki.org/)  \|

[random string](https://www.random.org/strings/) \| [random password](https://passwordsgenerator.net/) \|

[current time] (https://currentmillis.com/) \|


some cool chinese's blog

[loopjump](http://loopjump.com/)

[dirtysalt](https://dirtysalt.github.io/html/blogs.html) 

[zenlife.tk](http://zenlife.tk/)

[andremouche, cool girl](http://andremouche.github.io/)

[xargin](https://www.xargin.com/)

[meituan tech blog](https://tech.meituan.com/)

[Linux Kernel Exploration](http://ilinuxkernel.com/)

[nosuchfield](https://www.nosuchfield.com/)

[kkfnui's blog](http://blog.makerome.com/)



## About Me

A humble coder, working in c++, python and rust

Current research in NoSQL database

Want to learn about kernel, compiler, networking, distributed server, and so on.

[Resume](https://wanghenshui.github.io/resume/)

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
