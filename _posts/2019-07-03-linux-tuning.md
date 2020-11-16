---
layout: post
title: Linux调优指南
categories: [linux]
tags: [linux]
---
  

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





# 分析性能瓶颈



### 分析服务器性能

> 重要： 在做排错之前，备份所有数据和配置信息，以免丢失。

你应该要监控服务器，最简单的办法是在被监控服务器上运行监控工具。

应该在操作高峰记录服务器的性能日志，例如早9点到晚上5点，这取决于服务器提供的是什么服务，和谁在使用这些服务。在创建日志的时候，应该尽力把如下的数据记录在里面：

- 处理器
- 系统
- 服务器工作队列
- 内存
- 页文件
- 物理磁盘
- 重定向器
- 网卡

在开始之前，请注意性能调优的办法很重要。我们推荐的服务器性能调优过程如下：

- 1 理解影响服务器性能的因素
- 2 根据当前服务器性能表现，设立基准线，用来和未来的测试数据做比较，找出性能瓶颈。
- 3 使用监控工具来找出性能瓶颈。通过接下来的章节中的方法，你就可以把瓶颈范围缩小到部分子系统上。
- 4 通过对造成瓶颈的组件执行某些操作，提升服务器性能。

> 注意：很重要的是，在其它组件具有足够能力维持高性能的时候，通过升级造成瓶颈的组件，可以获得极大的性能提升。

- 1. 衡量新的性能。这一步可以帮助你比较调优前和调优后的性能差别。

在尝试修复性能问题的时候，注意：

- 应用程序应该用适当的方法来编译，减少路径长度。
- 在做任何升级和修改之前做性能衡量，这样就可以知道修改是否有用。
- 除了检查新添加的硬件，还要检查重新配置过的旧硬件。



对于应用或数据库服务器来说，CPU是十分关键的资源，也常常是性能瓶颈的源头。需要明白的是，高的CPU利用率并不总是意味着CPU正在繁忙的工作；也可能是正在等着其它子系统完成工作。正确的判断，需要把整个系统作为一个整体，并且观察到每一个子系统，因为子系统可能存在关联的反应。

> 在普遍的认知中，总是误以为CPU是服务器最重要的部件。但情况并不总是这样，在服务器上配置的CPU总是好于磁盘、内存、网络等子系统组件。只有特定的CPU密集型程序才能正真利用到今天的高端处理器。

### 找出CPU瓶颈

有好几种办法可以确认瓶颈出现在CPU上。已经在第二章"监控和测试工具"中讨论过了，Linux有各类工具来帮助我们。关键是选择什么工具。

可以使用uptime。通过分析uptime的输出，可以粗略知道在过去15分钟里，服务器上发生了什么

使用top工具，你可以看到CPU利用率和哪个进程是消耗CPU的大户。如果设置了sar，你会收集到很多信息，比如一段时间内的CPU利用率。分析这些信息的办法可能不同，使用isag，可以对sar的输出画出图形。你还可以通过脚本和表格来分析信息，看看CPU利用率的走向。你也可以在命令行使用sar -u或者sar -U processornumber。要想获得系统更全面情况，而不只是CPU子系统，vmstat是个好帮手



**有个流程图最好**



### SMP

基于SMP的系统呈现出来的问题可能是很难检测到的。在SMP环境中，有一个CPU affinity的概念,表示绑定进程到CPU上。 这么做的主要好处是CPU缓存优化，可以让同样的进程运行在一个CPU上，而不是在多个CPU上切换。当进程在CPU间切换的时候，要刷新新的CPU的缓存。进程在处理器间切换的时候会导致很多缓存刷新，那样，一个独立的进程要花费更多的时间才能处理完。而探测器很难检测到，在监控中，CPU负载会十分均衡，不会在任何一个上出现高峰。在基于NUMA的系统上，比如IBM System x3950上，CPU affinity也很有用，重要的是保持内存、缓存和CPU访问都是本地的。

### 性能优化选项

第一步是要确保，系统性能问题是由CPU引起的，而不是其它子系统。如果处理器是服务器瓶颈，可以采取如下的办法来增强性能：

- 使用ps -ef来确保没有不必要的进程程序在后台运行，如果找到了这样的程序，关掉它，或者使用cron让它在非高峰的时候运行。
- 通过top找到非关键的、CPU密集型进程，然后用renice修改它的优先级。
- 在基于SMP的机器上，尝试使用taskset命令绑定进程到CPU上，避免进程在多个处理器之间切换，引起cache刷新。
- 基于运行的应用，确认你的应用是否能高效的利用多处理器。来决定是否应该使用更强劲的CPU而不是更多的CPU。例如，单线程应用，会从更快的CPU中受益，增加值CPU个数也没用。
- 还有其它办法，比如，确保你使用的是最新的驱动和固件，这能影响到他们在系统上的负载。





# 内存瓶颈



 页错误（Page faults） | 有两类页错误：软页错误，在内存中发现页；硬页错误，在内存中没有发现页，而必须从磁盘中获取。访问磁盘会显著的使应用变慢。sar -B命令可以提供观察页错误的信息。，尤其是pgpgin/s和pgpgout/s两列。

分页可能是严重的性能问题，当空闲内存量小于预设的值时，因为分页机制不能处理对物理内存页的请求，于是调用swap机制释放更多的页，把内存数据放入到swap中。这会导致增加I/O，并且明显的性能降低。 如果服务器总是分页到磁盘（page-out很高）上，应该考虑增加更多的内存。然而，如果系统的page-out很低，可能是性能利用不充分



### 性能调优选项

如果确定是内存瓶颈，可以执行下面的操作：

- 使用bigpages、hugetlb和共享内存调优swap空间。
- 增加或者减少页大小。
- 改善活动和非活动的内存处理
- 调整page-out率
- 限制服务器上每个用户可使用的资源
- 关掉用不到的服务
- 增加内存

没有严肃的判定标准





### 找到磁盘瓶颈

服务器表现出如下的症状，可能是磁盘出现了瓶颈：

- 磁盘慢的表现：
  - 内存缓冲中填满了写数据（或者在等待读数据），因为没有可用的空闲内存缓冲供写（或者是在等待磁盘队列中的读数据响应），拖慢了所有请求。
  - 内存不足，在没有可以为网络请求分配足够内存缓冲的时候，会产生同步磁盘I/O。
- 磁盘或者控制器使用率变高。
- 大多数网络传输都是在磁盘I/O完成之后。表现形式为极长的响应时间和非常低的网络利用率。
- 磁盘I/O花费相当长的时间，并且磁盘队列变满，因为处理请求时间变长，所以CPU利用率变得很低。

磁盘子系统可能是最难配置的子系统。除了查看磁盘接口速度和磁盘容量，还要理解磁盘负载。访问磁盘是随机的还是顺序的？I/O是大还是小？为了充分利用磁盘，需要回答上面的这些问题。

厂商会一般会给你展示它们设备的吞吐量上限。但是，花时间来了解你的工作负载吞吐量将会帮你找到你所需要的磁盘子系统。

下表展示不同驱动在8KB I/Os下的真实吞吐。

| 磁盘速度  | 延时   | 寻道时间 | 完全随机访问时间 | 单盘每秒I/O | 8 KB I/O的吞吐 |
| --------- | ------ | -------- | ---------------- | ----------- | -------------- |
| 15000 RPM | 2.0 ms | 3.8 ms   | 6.8 ms           | 147         | 1.15 Mbps      |
| 10000 RPM | 3.0 ms | 4.9 ms   | 8.9 ms           | 112         | 900 KBps       |
| 7200 RPM  | 4.2 ms | 9 ms     | 13.2 ms          | 75          | 600 KBps       |

- a. 如果处理命令 + 传输数据 < 1ms，完全随机访问 = 延时 + 寻道时间 + 1ms
- b. 以1/随机访问时间为吞吐量。

随机读写负载通常需要多个磁盘决定。SCSI或者光纤的带宽不太要关注。大量随机访问负载的数据库最好有多块磁盘。大的SMP服务器最好配置多块磁盘。通常磁盘可以简单的平均划分为70%的读和30%的写，RAID10的性能比RAID5要高出50%到60%。

顺序读写需要看重磁盘子系统的总线带宽。需要最大吞吐量的时候，需要特别关注SCSI总线或者光纤控制器的数量。在阵列中，为每个盘指定相同的数量，RAID-10、RAID-0和RAID-5的读写吞吐流很相似。

分析磁盘瓶颈的办法：实时监控和跟踪.

- 在问题发生的时候一定要做实时监控。在动态系统负载和问题不可重现的情况下，这可能是不实际的。然而，如果问题是可重现的，通过这个办法就可以增加对象和计数器使问题更清晰。
- 跟踪是通过收集一段时间的性能数据来诊断问题。这是远程性能分析的好办法。缺点是在问题不可重现的时候，需要分析大量的文件，如果没有跟踪到所有的关键对象和参数，必须等待下一次问题出现来获取额外的数据。

使用vmstat工具。vmstat中关于I/O最重要的列是bi和bo。



**iostat命令**

 在反复同时打开、读、写、关闭太多文件的时候可能遇到性能问题。这可能会以寻道时间（把磁头移动到数据存储位置的时间）变长的现象表现出来。使用iostat工具，可以监控I/O设备的实时负载。不同的选项可以帮你挖掘到更深更多有用的数据。输出显示平均等待时间(await)，服务时间(svctm) util看负载繁忙度



### 性能调优选项

在确定磁盘子系统瓶颈之后，有如下可能的解决方法：

- 如果负载是顺序的，压力在控制器带宽上，办法就是添加更快的磁盘控制器。然而，如果负载是随机的，瓶颈可能在磁盘上，增加更多多的磁盘可以帮助增加性能。
- 在RAID中添加更多的磁盘，把数据分散到多块物理磁盘，可以同时增强读和写的性能。增加磁盘会提升每秒的读写I/O数。另外，请使用硬件RAID而不是Linux提供的RAID软件。如果是硬件RAID，RAID级别对操作系统是不可见的。
- 考虑使用Linux逻辑卷分区，而不是没有分区的单块大磁盘或者逻辑卷。
- 把处理负载转移到网络中的其它系统（用户，应用程序或者服务）。
- 添加RAM。添加内存会提升系统磁盘缓冲，增强磁盘响应速度



### 内核参数存储路径

内核参数存储在/proc（一般来说是/proc/sys）目录下。

通过/proc目录树下的文件，可以简单的了解与内核、进程、内存、网络以及其它组件相关的参数配置。每一个进程在/proc目录下都有一个以它的PID命令的目录。下表是部分文件所包含内核信息说明。

| 文件/目录          | 作用                                                         |
| ------------------ | ------------------------------------------------------------ |
| /proc/sys/abi/*    | 用于提供对外部二进制的支持，比如在类UNIX系统，SCO UnixWare 7、SCO  OpenServer和SUN Solaris 2上编译的软件。默认情况下是安装的，也可以在安装过程中移除。 |
| /proc/sys/fs/*     | 设置系统允许的打开文件数和配额等。                           |
| /proc/sys/kernel/* | 可以启用热插拔、操作共享内存、设置最大的PID文件数和syslog中的debug级别。 |
| /proc/sys/net/*    | 优化网络，IPV4和IPV6                                         |
| /proc/sys/vm/*     | 管理缓存和缓冲                                               |

### 使用sysctl命令

sysctl使用/proc/sys目录树中的文件名作为参数。例如，shmmax内核参数保存在/proc/sys/kernel/shmmax中，你可以使用cat来读取、echo来修改：

```
#cat /proc/sys/kernel/shmmax
33554432
#echo 33554430 > /proc/sys/kernel/shmmax
#cat /proc/sys/kernel/shmmax
33554430
```

然而，使用echo很容易弄错，所以我们推荐使用sysctl命令，因为它会修改前检查数据一致性，如下：

```
#sysctl kernel.shmmax
kernel.shmmax = 33554432
#sysctl -w kernel.shmmax=33554430
kernel.shmmax = 33554430
#sysctl kernel.shmmax
kernel.shmmax = 33554430
```

上面的修改会在下次重启之后消失。如果你想做永久修改，你应该编辑/etc/sysctl.conf文件，添加参数如下：

```
kernel.shmmax = 33554439
```

下次重启系统的时候会读取/etc/sysctl.conf文件，你也可以通过如下的命令，不用重启就让配置生效：

```
# sysctl -p
```



### 进程优先级

前面已经说过，我们不可能修改某个进程的优先级。唯一的办法是间接的通过调整进程nice级别，但这也并非总是可行。如果某个进程运行太慢，你就可以调低它的nice级别，给它更过的CPU时间。当然，这就意味着其它进程拥有更低的处理器时间，将会变得更慢。

Linux支持的nice级别从19（最低级别）到-20（最高级别）。默认值是0。需要使用root权限，才能把进程的nice级别设置为负数（更高的优先级）。

以nice级别-5启动xyz程序，使用如下命令：

```
nice -n -5 xyz
```

修改运行中的程序优先级，使用如下命令：

```
renice level pid
```

把PID为2500的进程优先级设置为10：

```
renice 10 2500
```

### CPU中断处理

在中断处理中，如下两个原则是十分有效的：

- 把产生大量中断的进程绑定到一个CPU上。

CPU亲和力使得管理员可以把中断绑定到某个或者某组物理处理器上（当然，这对单CPU系统无效）。要更改某个IRQ的亲和力，进入到/proc/irq/%{irq号码}/目录，修改smp_affinity文件的CPU mask值。把19号IRQ的亲和力设置到第三个CPU的命令如下（不适用SMT）：

```
echo 03 > /proc/irq/19/smp_affinity
```

- 让物理处理器处理中断

在对称多线程（SMT，symmetric multi-threadind）系统中，例如IBM POWER  5+处理器支持多线程，它就推荐将中断处理绑定到物理处理器上，而不是SMT实例。在双路多线程系统中，物理处理器通常都是较低的CPU数，CPU 编号 0和2通常是物理CUP，而1和3通常是指多线程实例。

如果你不使用smp_affnity标志，你就没必要担心这个了！

### 考虑NUMA系统

非统一内存架构（NUMA，Non-Uniform Memory  Architecture）系统正在获取市场份额，被看做是传统统一多处理系统的自然演化。尽管当前Linux发行版的CPU调度也同样适用于NUMA系统，但是应用程序可能就不一定了。由non-NUMA导致的性能降低是很难识别的。可以使用numactl包中的numastat工具找到在NUMA架构上有问题进程。

numastat统计数据保存在/sys/devices/system/node/%{node  number}%/numastat文件中，可以用来帮助找到瓶颈。numa_miss和other_node字段偏高可能是MUMA引起的。如果你发现给进程分配的内存不是在进程的本地节点上（运行程序的处理器节点），尝试对这个进程renice或者采用NUMA。



# 网络调优

在相同的配置的情况下，即使细微的流量行为差别也能导致巨大的性能差别。请熟悉下面的网络流量行为和要求：

- 事务吞吐需求（峰值和平均值）
- 数据传输的吞吐需求（峰值和平均值）
- 延时需求
- 传输数据大小
- 接收和发送的比例 
- 连接建立和关闭的频率，还有连接并发数
- 协议（TCP，UDP，应用协议，比如HTTP，SMTP，LDAP等等）

使用netstat，tcpdump，ethereal等工具可以获得准确的行为。



### MTU大小

在Gb网络中，最大传输单元（maximum transmission  units，MTU）越大，网络性能越好。问题是，太大的MTU可能不受大多数网络的支持，大量的网卡不支持大MTU。如果要在Gb速度上传输大量数据（例如HPC环境），增加默认MTU可以导致明显的性能提升。使用/sbin/ifconfig修改MTU大小





### 增加网络缓冲

Linux网络栈在分配内存资源给网络缓冲时十分谨慎！在服务器所连接的现代高速网络中，如下的参数应该增大，使得系统能够处理更多网络包。

- TCP的初始内存大小是根据系统内存自动计算出来的；可以在如下文件中找到这个值：

```
/proc/sys/net/ipv4/tcp_mem
```

- 调高默认以及最大接收Socket的内存值：

```
/proc/sys/net/core/rmem_default
/proc/sys/net/core/rmem_max
```

- 调高默认和最大发送Socket的内存值：

```
/proc/sys/net/core/wmem_default
/proc/sys/net/core/wmem_max
```

- 调高最大缓存值：

```
/proc/sys/net/core/optmem_max
```

**调整窗口大小**

可以通过上面的网络缓冲值参数来优化最大窗口大小。可以通过BDP（时延带宽积，bandwidth delay product）来获得理论上的最优窗口大小。BDP是导线中的传输的数据量。BDP可以使用如下的公式计算得出：

```
BDP = Bandwidth (bytes/sec) * Delay (or round trip time) (sec)
```

要使网络管道塞满，达到最大利用率，网络节点必须有和BDP相同大小的缓冲区。另一方面，发送方还必须等待接收方的确认，才能继续发送数据。

例如，在1ms时延的GB级以太网中，BDP等于：

```
125Mbytes/sec (1Gbit/sec) * 1msec = 125Kbytes
```

在大多数发行版中，rmem_max和wmem_max的默认值都是128KB，对一般用途的低时延网络环境已经足够。然而，如果时延很大，这个默认值可能就太小了！

再看看另外一个例子，假如一个samba文件服务器要支持来自不同地区的16个同时在线的文件传输会话，在默认配置下，平均每个会话的缓冲大小就降低为8KB。如果数据传输量很大，这个值就会显得很低了！

- 把所有协议的系统最大发送缓冲（wmem）和接收缓冲（rmem）设置为8MB。

```
sysctl -w net.core.wmem_max=8388608
sysctl -w net.core.rmem_max=838860
```

指定的这个内存值会在TCP socket创建的时候分配给每个TCP socket。

- 此外，还得使用如下的命令设置发送和接收缓冲。分别指定最小、初始和最大值。

```
sysctl -w net.ipv4.tcp_rmem="4096 87380 8388608"
sysctl -w net.ipv4.tcp_wmem="4096 87380 8388608"
```

第3个值必须小于或等于wmem_max和rmem_max。在高速和高质量网络上，建议调大第一个值，这样，TCP窗口在一个较高的起点开始。

- 调高/proc/sys/net/ipv4/tcp_mem大小。这个值的含义分别是最小、压力和最大情况下分配的TCP缓冲。

可以使用tcpdump查看哪些值在socket缓冲优化中被修改了。如下图所示，把socket缓冲限制在较小的值，导致窗口变小，引起频繁的确认包，会使网络效率低下。相反，增加套接字缓冲会增加窗口大小。





**socket缓冲大小**

在服务器处理许多大文件并发传输的时候，小socket缓冲可能引起性能降低。如下图所示，在小socket缓冲的情况下，导致明显的性能下降。在rmem_max和wmem_max很小的情况下，即使对方拥有充足的socket缓冲可用，还是会影响可用缓冲大小。这使得窗口变小，成为大数据传输时候的瓶颈。下图中没有包含小数据（小于4KB）传输的情况，实际中，小数据传输不会受到明显的影响。





### 额外的TCP/IP调整

还有很多其它增加或降低网络性能的配置。如下的参数可能会帮助提升网络性能。

**优化IP和ICMP**

如下的sysctl命令可以优化IP和ICMP：

- 禁用如下的参数可以阻止骇客进行针对服务器IP的地址欺骗攻击。

```
sysctl -w net.ipv4.conf.eth0.accept_source_route=0
sysctl -w net.ipv4.conf.lo.accept_source_route=0
sysctl -w net.ipv4.conf.default.accept_source_route=0
sysctl -w net.ipv4.conf.all.accept_source_route=0
```

- 如下的服务器配置用来忽略来自网关机器的重定向。重定向可能是攻击，所以我们值允许来自可信来源的重定向。

```
sysctl -w net.ipv4.conf.eth0.secure_redirects=1
sysctl -w net.ipv4.conf.lo.secure_redirects=1
sysctl -w net.ipv4.conf.default.secure_redirects=1
sysctl -w net.ipv4.conf.all.secure_redirects=1
```

- 你可以设置网卡是否接收ICMP重定向。ICMP重定向是路由器向主机传达路由信息的一种机制。例如，当路由器从某个接口收到发往远程网络的数据时，发现源ip地址与下一跳属于同一网段，这是路由器会发送ICMP重定向报文。网关检查路由表获取下一跳地址，下一个网关把网络包发给目标网络。使用如下的命令静止重定向：

```
sysctl -w net.ipv4.conf.eth0.accept_redirects=0
sysctl -w net.ipv4.conf.lo.accept_redirects=0
sysctl -w net.ipv4.conf.default.accept_redirects=0
sysctl -w net.ipv4.conf.all.accept_redirects=0
```

- 如果服务器不是网关，它就没必要发送重定向包，可以禁用如下的参数

```
sysctl -w net.ipv4.conf.eth0.send_redirects=0
sysctl -w net.ipv4.conf.lo.send_redirects=0
sysctl -w net.ipv4.conf.default.send_redirects=0
sysctl -w net.ipv4.conf.all.send_redirects=0
```

- 配置服务器忽略广播ping和smurf攻击：

```
sysctl -w net.ipv4.icmp_echo_ignore_broadcasts=1
```

- 忽略所有类型的icmp包和ping：

```
sysctl -w net.ipv4.icmp_echo_ignore_all=1
```

- 有些路由器会发送错误的广播响应包，内核会对每一个包都会生成日志，这个响应包可以忽略：

```
sysctl -w net.ipv4.icmp_ignore_bogus_error_responses=1
```

- 还应该设置ip碎片参数，尤其是NFS和Samba服务器来说。可以设置用来做IP碎片整理的最大和最小缓冲。当以bytes为单位设置ipfrag_high_thresh的值之后，分配处理器会丢掉报文，直到达到ipfrag_low_thresh的值。

当TCP包传输中发生错误时，就会产生碎片。有效的数据包会放在缓冲中，而错误的包会重传。

例如，设置可用内存范围为256M到384M，使用：

```
sysctl -w net.ipv4.ipfrag_low_thresh=262144
sysctl -w net.ipv4.ipfrag_high_thresh=393216
```

**优化TCP**

这里讨论通过调整参数，修改TCP的行为。

如下的命令可以用来调整服务器支持巨大的连接数。

- 对于并发连接很高的服务器，TIME-WAIT套接字可以重复利用。这对web服务器很有用：

```
sysctl -w net.ipv4.tcp_tw_reuse=1
```

如果使用了上面的参数，还应该开启TIME-WAIT的套接字快速回收参数：

```
sysctl -w net.ipv4.tcp_tw_recycle=1
```



- tcp_fin_timeout是socket在服务器上关闭后，socket保持在FIN-WAIT-2状态的时间。

TCP连接以三次握手同步syn开始，以3次FIN结束，过程中都不会传递数据。通过修改tcp_fin_timeout值，定义何时FIN队列可以释放内存给新的连接，由此提升性能。因为死掉的socket有内存溢出的风险，这个值必须在仔细的观察之后才能修改：

```
sysctl -w net.ipv4.tcp_fin_timeout=30
```

- 服务器可能会遇到大量的TCP连接打开着，却没有使用的问题。TCP有keepalive功能，探测这些连接，默认情况下，在7200秒（2小时）后释放。这个时间对服务器来说可能太长了，还可能导致超出内存量，降低服务器性能。

把这个值设置为1800秒（30分钟）：

```
sysctl -w net.ipv4.tcp_keepalive_time=1800
```

- 当服务器负载很高，拥有很多坏的高时延客户端连接，会导致半开连接的增长。在web服务器中，这个现象很常见，尤其是在许多拨号用户的情况下。这些半开连接保存在backlog connections队列中。你应该该值最小为4096（默认是1024）。

即使服务器不会收到这类连接，也应该设置这个参数，他可以保护免受DoS（syn-flood）攻击。

```
sysctl -w net.ipv4.tcp_max_syn_backlog=4096
```

- TCP SYN  cookies可以帮助保护服务器免受syn-flood攻击，无论是DoS（拒绝服务攻击，denial-of-service）还是DDoS（分布式拒绝服务攻击，distributed denial-of-service），都会对系统性能产生不利影响。建议只有在明确需要TCP SYN cookies的时候才开启。

```
sysctl -w net.ipv4.tcp_syncookies=1
```

> 注意，只有在内核编译了CONFIG_SYNCOOKIES选项的时候，上面的命令才是正确的

**优化TCP选项**

如下的TCP选项可以进一步优化Linux的TCP协议栈。

- 选择性确认可以在相当大的成都上优化TCP流量。然而，SACK和DSACK可能对Gb网络产生不良影响。tcp_sack和tcp_dsack默认情况下是启用的，但是和优化TCP/IP性能向背，在高速网络上应该禁用这两个参数。

```
sysctl -w net.ipv4.tcp_sack=0
sysctl -w net.ipv4.tcp_dsack=0
```

- 每个发往Linux网络栈的以太帧都会收到一个时间戳。这对于防火墙、Web服务器这类系统是很有用且必要的，但是后端服务器可能会从禁用TCP时间戳，减少负载中获益。可以使用如下的命令禁用TCP时间戳：

```
sysctl -w net.ipv4.tcp_timestamps=0
```

- 我们已经知道缩放窗口可以增大传输窗口。然而，测试表明，窗口缩放对高网络负载的环境不合适。另外，某些网络设备不遵守RFC指导，可能导致窗口缩放故障。建议禁用窗口缩放，并且手动设置窗口大小。

```
sysctl -w net.ipv4.tcp_window_scaling=0
```



### 增加包队列

在增加各种网络缓冲大小之后，建议增加未处理包的数量，那么，花更长的时间，内核才会丢弃包。可以通过修改/proc/sys/net/core/netdev_max_backlog来实现。

### 增加发送队列长度

把每个接口的txqueuelength参数值增加到1000至20000。这对数据均匀且量大的高速网络连接十分有用。可以使用ifconfig命令调整传输队列长度。

```
[root@linux ipv4]# ifconfig eth1 txqueuelen 2000
```

### 减少中断

除非使用NAPI，处理网络包的时候需要Linux内核处理大量的中断和上下文切换。对Intel  e1000–based网卡来说，要确保网卡驱动编译了CFLAGS_EXTRA  -DCONFIG_E1000_NAP 标志。Broadcom  tg3模块的最新版本内建了NAPI支持。

如果你需要重新编译e1000驱动支持NAPI，你可以通过在你的系统做如下操作;

```
make CFLAGS_EXTRA -DCONFIG_E1000_NAPI
```

此外，在多处理器系统中，把网卡中断绑定到物理CPU可能带来额外的性能提升。为实现这个目标，首先要识别特定网卡的IRQ。可以通过ifconfig命令获得中断号。

获取中断号之后，你可以使用在/proc/irq/%{irq number}中mp_affinity参数把中断和CPU绑定在一起。如下图示范了如何把之前获取的eth1网卡的169号中断，绑定到系统的第二个处理器。



##### ref

1. https://lihz1990.gitbooks.io/transoflptg/content/

   

---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。