---
layout: post
title: Writing Bug Free C code chapter 1 Understand Why Bugs Exist
category: translation
keywords: [c,bug]
---



\######本翻译仅供参考/博客凑数/多数翻译是意译,拿不准的部分会加英语原文

## Chapter 1: Understand Why Bugs Exist/理解为什么有bug

在软件开发迭代中为啥老是有bug悄悄溜进来？花费时间来理解为什么bug存在是写出bug-free代码的第一步。第二步则是采取行动制定策略去减少问题/检测问题。更重要的是要让整个团队明白这些新的策略。

笔者的一个好朋友工作在一个特别的公司，会对他写的代码和模块使用运行时参数校验（run-time parameter  validation）。这是一个好主意，但这种强制的做法可能会使其他程序员不太情愿。有一天朋友修改了一点旧代码，然后他加上了参数校验。他测试了他的代码然后就传到代码库了，几周之后这个代码调用老代码（一年前的）就会显示参数错误了。但是有些程序员想把这个参数校验去掉。他们认为有错误日志打印，不可能是老代码有问题，肯定是新加的参数校验错了。

这就是个极端的例子，但也足够说明在一个编程项目中必须让团队中每个人理解这种策略施行。

\####1.1 小项目 vs. 大项目

如果你需要写一个hex dump工具 （就叫它DUMP）,这个程序需要接收命令行上一个你想显示的文件名字作为参数，能写出一个没有bug的代码吗？或许是的，因为这个项目很小，定义良好且隔离没有什么交互

因此如果你被要求写一个项目（叫ALPHA),一个你们公司集中为其他公司携的项目。这个项目需要几百上千行代码而且已经有十个程序员已经在这个项目上工作了。交付日期马上就到了，公司需要你的聪明才智，你认为可以马上跳进这个团队并且写出新的代码并且不引入bug？我不能，要是没有方法策略来捕捉错误的话任何新手都会引入bug。

思考一下你现在处理的最大的项目，有多少头文件，并且头文件里都有什么？有多少源代码文件，并且里面都有什么？你处理DUMP这种小工具毫无问题，那为啥你处理这个大项目就这么难呢？为啥大项目不像十个一百个小项目那样简单？

```
编程原则必须新手友好，新手进入项目不至于引入新bug
```

咱们研究研究你的小项目。由几个头文件和实现文件组成，头文件有函数原型，数据结构声明，宏定义，typedef定义等，你啥都知道，因为文件足够少，你能处理掉，现在，把它乘十乘百，突然这个项目就变得不可管理了。

你的头文件里有太多东西要管理，这个项目需要支持，你增加人数处理这个项目让它更快完成，但是这只会加重问题，因为现在有更多的人向头文件中加入信息且其他人需要了解，这就是所有大项目都会陷入的一个恶性循环。

\####1.2 头文件里太多数据结构

大项目有一个明显的问题信息太多是需要花一段时间来熟悉数据结构。如果能减少这些信息，这个过程可能会简单，因为你需要了解的数据结构少了。

根本问题是头文件里面放了太多的信息，主要贡献者就是数据结构声明。当你开始一个项目，你在头文件里放几个声明，项目进行中，你就越放越多。等你反应过来已经是一团乱麻了。你的实现文件里面有数据结构的
全部（The majority of your source files have knowledge of the data structures and directly reference elements from the structures.）

```
需要减少数据结构的方法
```

考虑如果你改动多个数据结构。就得把所有用到的地方都得重新编译一边。（Making changes in an  environment where many data structures directly refer to other data  structures becomes, at best, a headache. Consider what happens when you  change a data structure. This change forces you to recompile every  source file that directly, or more importantly indirectly, refers to the  changed data structure. This happens when a source file refers to a  data structure that refers to a data structure that refers to the  changed data structure. A change to the data structure may force you to  modify some code, possibly in multiple source files. ）

在第四节用类来解决这个问题

\####1.3 技巧与规模无关

```
你的方法应该是融洽的，项目规模无关
```

比如说一个程序员joe制定了一个规则，所有的数据声明都得放在头文件里，这样所有的实现文件都能直接访问，这佯为他赢得了速度优势，他的产品也更高级一些。

这样可能在他产品的第一版有用，当他的产品的规模越来越大，达到临界点，大量的公共公共数据声明导致无法管理。他的工作有麻烦了。这个策略在小规模的项目上工作的很好，但是在大规模的项目中遗憾的失败。优秀的小项目早晚会变成大项目。

要明白你的编程方法应该是融洽的，在大小项目上都行得通的。

\####1.4 太多全局变量

全局变量应该尽量避免。这种用法在大的应用上有局限。当一个较大的应用变的越来越大，全局变量的数目变的越来越多。等你反应过来，你的全局变量已经多到你管不过来了。

当你用到全局变量的时候，想想为什么你需要直接访问全局变量。把一个模块函数调用放在变量那里效果不是一样（Would a function  call to the module where the variable is defined work just as well?  ）大多数情况都可以替代。如果一个全局变量被修改了，你需要问你自己这个全局变量的影响，如果被一个函数调用代替，那就把问题交给函数处理

```
暴漏给多个文件的变量应该避免
```

有些全局变量影响不大，无论项目多大，全局变量都不应该过多。

\####1.5 依靠debugger

```
在减少bug的技巧中debugger最有效,但是这通常是你的最后手段，出现了这种问题，你前面的bug-free技巧方法已经出现问题了。
```

不要过分依赖debugger来捕捉bug，要用你自己之前设定的规则与技巧。

\####1.6 解决现象，而不是问题

比如你在你的代码里遇到了个bug，//这段没什么意思不翻译了

```
改bug时要改掉隐藏在bug背后的原因不要仅仅改掉bug本身，
```

一个高级点的例子就是内存泄露，大多数情况内存泄露不会直接造成问题，直到内存耗尽为止，内存耗尽就是结果，你最终找到了导致内存耗尽的那一行代码并且回收了这块内存，看上去bug已经fixed了，但是并没有。

隐藏的内存泄露问题仍然在你的代码里。你需要一个堆管理模块来告诉你哪里内存泄露了，而不是自己花费时间来追踪内存泄露。彻底额的解决这个问题，堆管理模块会告诉你具体到细节，哪里出现了泄露。第五节会仔细讨论这个问题

\####1.7 不可维护的代码

通常遇到维护他人写好的代码，修改bug或者添加新功能，我不知道你怎么想，对我来说这不是什么愉悦的体验，通常代码不好理解需要花费时间来琢磨代码流程究竟是什么。

```
坚持写别人能理解的代码
    //正在翻译的我不是这么认为的，我感觉需要有恰当的注释
```

总之明白最后有人会看你的代码，所以尽量写的不要太模糊。除非注释清晰文档明确
//果然作者也是这么想的。

\####1.8 别用微软的内置调试器

不细说

\####1.9 总结

1. The first step in writing bug-free code is to understand why bugs  exist. The second step is to take action. That is what this book is all  about.
2. Programming methodologies that are developed to prevent and detect  bugs must work equally well for both small and large programming  projects.
3. A technique that helps eliminate data structure declarations from  include files needs to be found. Doing so will allow programmers to come  up to speed on an existing project much quicker.
4. Global variables that are known to more than one source file should  be avoided. Global variables make it hard to maintain a project.
5. Debuggers should be used only as a last resort. Having to resort to a  debugger means that your programming methodologies used to detect bugs  have failed.
6. When you fix a bug, make sure you are really fixing the underlying  cause of the bug and not just the symptom of the bug. Ask yourself how  many times you have fixed the same type of bug.
7. Strive to write code that is straightforward and easily understandable by others. Avoid writing code that pulls a lot of tricks.
8. Finally, make sure that you use the Windows debug kernel all the  time. It contains extra error checking that can automatically detect  certain types of bugs that go undetected in the retail release of  Windows