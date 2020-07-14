---
layout: post
title: Linux调优指南
category: [linux]
tags: [linux]
---
{% include JB/setup %}

---

[toc]

> 只列重点和延伸

# linux内存


![](https://lihz1990.gitbooks.io/transoflptg/content/01.%E7%90%86%E8%A7%A3Linux%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F/linux-virtual-memory-manager.png)

**页帧分配(Page frame allocation)**  

页是物理内存或虚拟内存中一组连续的线性地址，Linux内核以页为单位处理内存，页的大小通常是4KB。当一个进程请求一定量的页面时，如果有可用的页面，内核会直接把这些页面分配给这个进程，否则，内核会从其它进程或者页缓存中拿来一部分给这个进程用。内核知道有多少页可用，也知道它们的位置。  

**伙伴系统（Buddy system）**  

Linux内核使用名为伙伴系统（Buddy  system）的机制维护空闲页，伙伴系统维护空闲页面，并且尝试给发来页面申请的进程分配页面，它还努力保持内存区域是连续的。如果不考虑到零散的小页面可能会导致内存碎片，而且在要分配一个连续的大内存页时将变得很困难，这就可能导致内存使用效率降低和性能下降。下图说明了伙伴系统如何分配内存页。
![buddy-system](https://lihz1990.gitbooks.io/transoflptg/content/01.%E7%90%86%E8%A7%A3Linux%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F/buddy-system.png)

如果尝试分配内存页失败，就启动回收机制。参考"内存页回收(Page fram reclaiming)"     

可以在/proc/buddyinfo文件看到伙伴系统的信息。详细内容参考"zone中使用的内存(Memory used in a zone)" 

**页帧回收**     

如果在进程请求指定数量的内存页时没有可用的内存页，内核就会尝试释放特定的内存页（以前使用过，现在没有使用，并且基于某些原则仍然被标记为活动状态）给新的请求使用。这个过程叫做*内存回收*。*kswapd*内核线程和*try_to_free_page()*内核函数负责页面回收。

kswapd通常在task  interruptible状态下休眠，当一个区域中的空闲页低于阈值的时候，它就会被伙伴系统唤醒。它基于最近最少使用原则（LRU，Least  Recently  Used）在活动页中寻找可回收的页面。最近最少使用的页面被首先释放。它使用活动列表和非活动列表来维护候选页面。kswapd扫描活动列表，检查页面的近期使用情况，近期没有使用的页面被放入非活动列表中。使用vmstat -a命令可以查看有分别有多少内存被认为是活动和非活动状态。详细内容可以参考"vmstat"一节。    

kswapd还要遵循另外一个原则。页面主要有两种用途：*页面缓存(page cahe)*和*进程地址空间(process address space)*。页面缓存是指映射到磁盘文件的页面；进程地址空间的页面（又叫做匿名内存，因为不是任何文件的映射，也没有名字）使用来做堆栈使用的，参考1.1.8 “进程内存段”。在回收内存时，kswapd更偏向于回收页面缓存。     

>  Page out和swap out：“page out”和“swap out”很容易混淆。“page out”意思是把一些页面（整个地址空间的一部分）交换到swap；"swap out"意味着把所有的地址空间交换到swap。     

如果大部分的页面缓存和进程地址空间来自于内存回收，在某些情况下，可能会影响性能。我们可以通过/proc/sys/vm/swappiness文件来控制这个行为

**swap**

在发生页面回收时，属于进程地址空间的处于非活动列表的候选页面会发生page  out。拥有交换空间本身是很正常的事情。在其它操作系统中，swap无非是保证操作系统可以分配超出物理内存大小的空间，但是Linux使用swap的空间的办法更加高效。如图1-12所示，虚拟内存由物理内存和磁盘子系统或者swap分区组成。在Linux中，如果虚拟内存管理器意识到内存页已经分配了，但是已经很久没有使用，它就把内存页移动到swap空间。     

像getty这类守护进程随着开机启动，可是却很少使用到，此时，让它腾出宝贵的物理内存，把内存页移动到swap似乎是很有益的，Linux正是这么做的。所以，即使swap空间使用率到了50%也没必要惊慌。因为swap空间不是用来说明内存出现瓶颈，而是体现了Linux的高效性。



ps -o majflt,minflt -p pid

minor fault 在内核中，缺页中断导致的异常叫做page fault。其中，因为filemap映射导致的缺页，或者swap导致的缺页，叫做major fault；匿名映射导致的page fault叫做minor fault。 作者一般这么区分：需要IO加载的是major fault；minor fault则不需要IO加载



# I/O子系统结构

![](https://lihz1990.gitbooks.io/transoflptg/content/01.%E7%90%86%E8%A7%A3Linux%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F/io-subsystem-architecture.png)



一图胜千言





##### ref

1. https://lihz1990.gitbooks.io/transoflptg/content/

   

---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。