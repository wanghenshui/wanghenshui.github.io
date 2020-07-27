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



刷新缓冲区

![](https://lihz1990.gitbooks.io/transoflptg/content/01.%E7%90%86%E8%A7%A3Linux%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F/flushing-dirty-buffers.png)





网络

![网络层级结构和网络通信过程概览](https://lihz1990.gitbooks.io/transoflptg/content/01.%E7%90%86%E8%A7%A3Linux%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F/network-layered-structure-and-overview-of-networking-operation.png)





socket buffer详情

```bash
/proc/sys/net/core/rmem_max
/proc/sys/net/core/rmem_default
/proc/sys/net/core/wmem_max
/proc/sys/net/core/wmem_default
/proc/sys/net/ipv4/tcp_mem
/proc/sys/net/ipv4/tcp_rmem
/proc/sys/net/ipv4/tcp_wmem
```

![](https://lihz1990.gitbooks.io/transoflptg/content/01.%E7%90%86%E8%A7%A3Linux%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F/socket-buffer-memory-allocation.png)





tcp链接状态图

![TCP连接状态图](https://lihz1990.gitbooks.io/transoflptg/content/01.%E7%90%86%E8%A7%A3Linux%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F/tcp-connection-state-diagram.png)









# 指标

处理器指标如下：     



- CPU利用率（CPU utilization）
    这个可能是最直接的指标，它全面展示了每个处理器的利用率。在IBM System x架构中，如果CPU利用率持续高于80%，就可能遇到了处理器瓶颈。     

- 用户时间（User time）
    表示CPU在用户进程上的时间百分比，包括nice时间。用户时间值高是一个较好的状态，在这种情况下，系统在处理真正的任务。     

- 系统时间（System time）
    表示CPU花在内核操作上的时间百分比，包括IRQ和softirq时间。持续的高系统时间可以指出网络和驱动栈的瓶颈。CPU花在内核上的时间越少越好。     

- 等待（Waiting）
    CPU花在等待I/O操作上的时间总和。类似*blocked*值，系统不应该把大量时间花在等待I/O操作上；否则，你应该调查I/O子系统的性能。     

- 空闲时间（Idle time）
    表示系统处于空闲等待任务的时间比。     

- Nice时间（Nice time）
    表示CPU花在re-nicing进程，改变进程执行顺序和优先级上的时间。     

- 平均负载（Load average）
    平均负载不是百分比，是下面的和的滚动平均值：     

  - 在队列中等待被处理的进程数     

  - 等待非中断任务完成的进程数     

    是TASK_RUNNING和TASK_UNINTERRUPTIBLE的和的平均值。如果进程请求CPU时间被阻塞（表示CPU没有时间处理它们），平均负载就会升高。另一方面，如果每个进程直接就能获得CPU时间并且没有CPU周期丢失，负载就会降下来。

- 可运行进程（Runable processes）
    表示已经准备好要执行的进程。这个值不应该持续超过CPU个数的10倍，否则就是出现了CPU瓶颈。     

- 阻塞的（Blocked）
    在等待I/O操作完成的时候，进程不能执行。阻塞进程可以指出你的I/O瓶颈。     

- 上下文切换（Context switch）
    系统上有大量的切换在线程间发生，在有大量中断和上下文切换发生时，表示驱动或应用程序出现了问题。一般来说，上下文切换不是好现象，因为CPU缓存需要刷新，但是有些上下文切换是必要的。     

- 中断（Interrupts）

    中断值包含硬中断和软中断。硬中断对系统性能有更大的影响。高中断值指示了软件瓶颈，无论是内核还是驱动程序层面的。记住中断值包含CPU时钟引起的中断。

  ### 内存指标

  如下是内存度量值：     

- 空闲内存（Free memory）
    和其它操作系统相比，不应该过分担心Linux内存的问题。在“虚拟内存管理”一节中已经说过，Linux把大部分没用到的内存作为文件系统缓存，所以计算空闲内存的时候还得加上已用内存中的缓冲（buffer）和缓存(cache)大小。     

- Swap利用率（Swap usage）
  这个数值表明已经使用的swap的空间。如“虚拟内存管理”一节中所说的那样，swap使用率只是表明Linux的内存管理有多么高效。Swap In/Out才是识别内存瓶颈的手段，长时间每秒200到300以上的swap in/out次数表明可能出现内存瓶颈。     

- 缓冲和缓存（Buffer and cache）
    cache被用作文件系统缓存和块设备缓存。     

- Slabs
    描述内核的内存使用量。注意，内核页不能page out到磁盘。     

- 活动和非活动内存
    提供关于系统中活动的内存信息。非活动内存是可能由kswapd守护进程交换到磁盘的候选。参考“页帧回收”。    



### 网络指标


以下是网络指标：     



- 接收和发送的包（Packets received and sent）
    这个指标告诉你指定网络接口的接收和发送网络包的数量。     
- 接收和发送的字节（Bytes received and sent）
    这个值是指定网卡的发送和接收的字节数。     
- 每秒碰撞（collisions per second）
    这个值提供了各个网络接口所连接网络的所发生的冲突数量。持续的冲突可能是由于网络基础设施导致的，而不是服务器。在大多数正确配置的网络中，碰撞很少发送，除非网络是由集线器组成的。     
- 丢包
    这是被内核丢弃的包的数量，可能是防火墙配置导致的，也可能是由于缺少网络缓冲。     
- 过载（Overruns）
    　过载表示网络接口用光缓冲空间的次数。这个指标应该和丢包联合起来使用，来判断瓶颈是由网络缓冲还是网络队列长度导致的。     
- 错误（Errors）
    被标识为故障的帧数目。这通常是由于网络不匹配或者部分网线损坏导致的。在铜基千兆中，部分损坏网线可能导致显著的网络性能问题。



### 块设备指标


以下是块设备的相关指标：     



- IO等待（Iowait）
    CPU花在等待I/O操作发生上的时间。该值长时间飙高预示着可能出现了I/O瓶颈。     
- 平均队列长度（Average queue length）
    未完成的I/O请求数量。通常，2到3的磁盘队列是很理想的；太高可能表示出现了I/O瓶颈。     
- 平均等待（Average wait）
    一个IO请求被服务的平均等待时间，以毫秒计算。等待时间由真实的I/O操作时间和I/O队列的等待时间组成。     
- 每秒传输（Transfers per second）
    表示每秒有多少个I/O操作被执行（读和写）。*transfers per second*和*kBytes per second*可以联合使用，来表示系统每秒的平均传输大小。平均传输大小通常应该和所使用的磁盘子系统的条带大小相匹配。     
- 每秒读写块（Blocks read/write per second）
    在内核2.6中，它表示每秒读取和写入1024字节块的数目。更早的内核，块大小可能不一样，从512字节到4K字节不等。     
- 每秒读写的千字节（Kilobytes per second read/write）
    从块设备读和写的千字节，表示从块设备中读取和写入的实际大小。     



# 工具

| 工具                 | 常用功能                 |
| -------------------- | ------------------------ |
| top                  | 所有进程情况             |
| vmstat               | 系统活动，硬件和系统信息 |
| uptime, w            | 系统平均负载             |
| ps, pstree           | 显示进程                 |
| free                 | 内存使用情况             |
| iostat               | cpu负载和磁盘活动        |
| sar                  | 收集和报告系统状态       |
| mpstat               | 多处理器使用情况         |
| numastat             | NUMA相关统计             |
| pmap                 | 进程内存情况             |
| netstat              | 网络统计                 |
| iptraf               | 实时网络统计             |
| tcpdump，ethereal    | 详细网络流量分析         |
| nmon                 | 收集和报告系统活动       |
| strace               | 系统调用                 |
| proc文件系统         | 各种内核统计信息         |
| KDE system guard     | 实时的系统图形报告       |
| Gnome System Monitor | 实时的系统图形报告       |

| 工具    | 常用功能             |
| ------- | -------------------- |
| lmbench | 微型系统功能评测工具 |
| iozone  | 文件系统压测         |
| netperf | 网络性能测试         |



##### ref

1. https://lihz1990.gitbooks.io/transoflptg/content/

   

---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。