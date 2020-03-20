---
layout: post
title: (译)代码审核：关于信号
category: linux
tags : [linux, signal, gcc]
---
{% include JB/setup %}


//翻译的十分糟糕，就当做自己的阅读笔记了[原文点击](http://delyan.me/code-review-signals/)



POSIX信号是个挺让人畏惧的话题，在这个帖子中，我会用几个真实环境中的例子来消除这些疑惑，看这些例子是如何通过信号来解决问题的



### 第一部分 POSIX 信号（Linux）

POSIX 信号有很复杂的规则，伴随而来的是一些bug（”段错误“带来的恐惧），基本上在核心代码中很少出现

本帖希望列举一些有用的依赖信号的设计模式并且解释内部信号的传递过程。我会主要在Linux环境上阐述，我以前的工作也基于Linux，大家对Linux或Unix-like系统也熟悉

这个帖子不会包含所有信号的整体介绍，这已经有很多不错的帖子列举了

- [“Signal Concepts” from the POSIX.1-2018 specification](http://pubs.opengroup.org/onlinepubs/9699919799/functions/V2_chap02.html#tag_15_04)
- [“All about Linux signals” on Linux Programming Blog](http://www.linuxprogrammingblog.com/all-about-linux-signals?page=show)

我只会指出大家在使用信号时的错误观念



#### thread-local signal masks 和全局handler回调函数

我工作用的系统上有很多bug，和开源代码中一样，这些bug的根源在于对下列基本概念的误解

​	信号处理（是否注册回调函数，回调函数做什么）是全局函数

​	信号掩码（是否一个线程可以收到信号）是thread-local类型

这个现象一部分原因在于 线程工作之前信号就已经处理好了，所以就没必要为线程写特定的信号回调handler了，

另一部分原因在于POSIX sigprocmask(3) 文档包含了下面这行吓人的话

​	sigprocmask函数在多线程进程中是未明确的（unspecified	）

##### 这技术上是正确的，POSIX值明确表示pthread_sigmosk在多线程环境中是安全的

pthread_sigmask和sigprocmask在linux上的区别是pthread_sigmask（libc）是sigprocmask（syscall）实现的



#### 信号到任意一个线程

POSIX标准明确区分了两种信号的产生

Thread-targeted 信号，标准明确了在线程中任何动作触发的信号会在这个线程收到

即信号从哪个线程生成就会给哪个线程



Process-targeted 信号，任何不是线程产生的信号就是Process-targeted信号

那些和进程ID或进程组ID或异步事件相关的生成的信号，会给进程本身，比如终端活动



如果你关心的信号时thread-targeted，其他线程是收不到的，如果你阻塞他（sigmask是thread-local对象），你就是在用默认的处理方式

如果这个信号是进程相关的，任何进程都能收到，然而，这不是什么魔法，内核中的代码能自圆其说，主线程（tid==pid）会尝试收到该信号，其他的线程会循环获取来平衡信号传递



人们想到许多可以知道 方法去处理这些乱七八糟的东西-从信号管道 到一个信号处理线程，总有一些你可以放到你应用中的点子，或许，你可以通过kill和tgkill发送信号



#### 你不可以处理“致命”错误

POSIX标准对信号处理回调说过

> 对于 SIGBUS, SIGFPE, SIGILL, SIGSEGV这些不是由kill(), sigqueue(), raise(),生成的信号，假如用回调函数捕获处理了这些信号，之后程序的行为将是未定义的

在Linux上，内核会重新发陷阱指令并重新发信号，这个行为是ABI的一部分，不会改变

这也说明，程序返回并不是跳出信号处理回调函数的唯一办法，也可以调用setjmp/longjmp 或者make/set/getcontext （不反回），可以在程序处理期间做一些有意思的事。实际上POSIX在一开始就考虑到了，这也是为什么信号掩码，sigsetjmp siglongjmp还保留至今。

```
    thread_local jmp_context;
    thread_local in_dangerous_work;
    handler() {
      if (in_dangerous_work) {
        in_dangerous_work = false;
        siglongjmp(&jmp_context, 0);
      }
      // call previous handler here
    }
    work() {
      register_handler_for_dangerous_work(&handler);
      // calls sigaction for the signals we care about
      // the second argument means that the return
      // value from the sigsetjmp will be 1 if we
      // jumped to it
      if (sigsetjmp(&jmp_context, 1) == 0) {
        in_dangerous_work = true;
        do_dangerous_work();
        in_dangerous_work = false;
      } else {
        // we crashed while doing the dangerous work,
        // do something else.
      }
    }
```

通过使用thread-local变量和longjump 我们可以安全的识别有风险的部分并且挽救回来，且不影响整体的正确性



例子中的可能需要放到沙盒中搞危险工作包括

- 与不能保证安全的库（ABI）进行交互
- 在没有简单的方法查询每条指令的详细存在情况下，检测平台对CPU扩展指令的支持情况（咳咳，arm）
- 全地与程序的其他部分进行竞争（当所做的工作不是和竞争相关的，例如，收集特定于线程的诊断数据)

#### 信号处理回调函数不能做什么有用的事儿

信号处理回调函数不过是个小函数去打断内核信号动作，函数可以操作一个人一多 上下文，可以访问当前被打断状态下的任何东西的任何状态（SA_SIGINFO flag中给了ucontext访问券，包含了在信号传递过程中所有线程寄存器的状态），并且有足够清晰的语义来分析这些状态是怎么被传递和处理的

然而这需要谨慎的设计出正确的同步原语，不是不可能，我也希望下面这个项目能演示出来



### 第二部分 一些信号的有趣用法

下面是一些我在工作中和google中而然发现的关于信号的有趣用法

#### 虚拟机内部实现（JavaScriptCore）

当实现一个虚拟机，一个需要你实现的机制是在一个设定的时间点挂住一个线程的能力，有时，你需要实现这个机制去遍历这个线程的所有堆栈来进行垃圾回收（GC），或者你需要这个功能区实现调试器断点功能。

javascriptCore，webkit‘s javascript 内核使用信号来实现Linux上的悬停/恢复原语，它也是用信号来实现所谓的“VM陷阱” -就是线程运行时附到调试器断点，结束线程等等操作

- [悬停/恢复](https://github.com/WebKit/webkit/blob/fe9e4ea7777da0afeef0ed1f4a2cf658aa234226/Source/WTF/wtf/ThreadingPthreads.cpp#L363)
- [VM陷阱](https://github.com/WebKit/webkit/blob/d9cd5e31e4ebd912fee7e53295d847d16e1b229b/Source/JavaScriptCore/runtime/VMTraps.cpp#L310)



#### 在虚拟机中的异常处理 （JavaScriptCore，ART，HotSpot）

继续虚拟机中使用信号的话题，另一个有趣的用法是允许内存踩踏发生，检测出来，抛出异常

举个例子，在java中，当程序引用一个无效的引用，虚拟机会抛出NullPointerException异常

当虚拟机编译程序（比如JIT编译，或ART的例子，AOT ），NullPointerException不是个主要路径，虚拟机可以省略所有的null检查代码。然而，为了保证运行时正确，当编译过的代码抛出了异常，虚拟机会使用一个信号回调函数来处理

- [JavaScriptCore](https://github.com/WebKit/webkit/blob/4b7982931186cc895f71d461ce03860007cc80c1/Source/JavaScriptCore/wasm/WasmFaultSignalHandler.cpp#L59)
- [ART](https://android.googlesource.com/platform/art/+/android-9.0.0_r10/runtime/fault_handler.cc#220)
- [HotSpot](https://github.com/ramonza/jdk8-hotspot/blob/d317105aec55e94e92ca51921cc6a63cfce9d229/src/os_cpu/linux_x86/vm/os_linux_x86.cpp#L401)

实际上，如果你读一下链接里的Hotspot虚拟机代码，虚拟机很多功能都通过信号来实现，除零错误和堆栈溢出就在那里



#### 用户态页错误（libsigsegv）

在GNU libsigsegv项目中有一个SIGSEGV信号处理的有趣的应用，[主页地址](https://www.gnu.org/software/libsigsegv/)

- 持久化数据库内存映射访问
- 通用的垃圾收集器
- 堆栈溢出处理函数
- 分布式共享内存

当处理内存映射文件，一大堆控制动作藏在用户态程序和内核中，当预取页文件，不管我们正在连续读还是随机读，读硬盘上的数据，什么时候把数据从脏页刷到硬盘，这些决定都是内核代表用户态程序去做的

通过处理SIGSEGV信号，（无论是否是libsigsegv还是标准POSIX调用），我们就获得了执行的控制权，可以自由获取地址空间，自己做决定。

这个需求普遍通用，linux内核实现了userfaultfd，更简单的实现用户态页错误



#### 性能分析（gperftools）

一些POSIX性能分析API是基于信号的，比如POSIX测量CPU时间的方法，使用setitimer 和ITIMER_PROF，这个定时器发送一个线程检测信号SIGPROF到线程移动指定的CPU频率（？）

比如，[gperftools项目用setitimer和栈回溯来实现CPU-time堆栈跟踪](https://github.com/gperftools/gperftools/blob/c41688bf20186723367b560ceb539b2330951ddb/src/profiler.cc#L336)



#### 崩溃分析（breakpad）

最近我们接触到信号处理的最平常用法 - 崩溃报告，实际上并没有实际处理信号，只是记录发生

breakpad实现了崩溃手机系统，通过处理SIGSEGV，SIGSBRT和其他终端信号和通过信号处理函数尽可能的收紧更多的信息，它记录了寄存器的状态，不活了所有线程的堆栈信息，并且尽可能的展开崩溃线程的对竹山，这些动作是的信号处理函数中预分配的内存在不安全的上下文下来获得的



####  结论

希望这篇文章能让我们了解这个常常令人恐惧的POSIX信号世界。我希望它能启发你或至少能驱散你的恐惧。我知道我很喜欢读这样的东西。





---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。