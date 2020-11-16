---
layout: post
title: (转)(译)Redis响应延迟问题排查
categories: [database, translation, debug]
tags: [redis,translation]
---
  

---



 

---



转载自https://nullcc.github.io/2018/02/15/(%E8%AF%91)Redis%E5%93%8D%E5%BA%94%E5%BB%B6%E8%BF%9F%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5/

非常感谢！ 博客不错，比我的好看多了

---

本文翻译自[Redis latency problems troubleshooting](https://redis.io/topics/latency)。



本文将帮助你了解当你遇到了Redis延迟问题时究竟发生了什么。

在这里延迟指的是客户端从发送命令到接收命令回复这段时间的最大值。一般情况下Redis处理命令的时间非常短，基本上在微秒级别，但是这里有几种情况会导致高延迟。

## 我很忙，把清单给我

下面的文档对于想要以低延迟运行Redis来说非常重要。然而我知道大家都很忙，所以我们先来看一个快速清单。如果你没有遵守这些步骤，请回到这里阅读整个文档。

1. 确保服务器没有被慢查询阻塞。使用Redis的慢日志功能来检查是否有慢查询。
2. 对于EC2的用户，确保你基于现代的EC2实例使用HVM，比如m3.medium。否则fock()操作会很慢。
3. 必须禁用内核的Transparent huge pages特性。使用`echo never > /sys/kernel/mm/transparent_hugepage/enabled`来禁用它，然后重启你的Redis进程。
4. 如果你在使用虚拟机，很可能存在一种和Redis无关的内在延迟。检查机器的最小延迟，你可以在你的运行环境中使用`./redis-cli --intrinsic-latency 100`。注意：你需要在服务器上运行这个命令而不是在客户端上。
5. 打开并使用Redis的延迟监控特性来获取你机器上的人类可读的延迟事件描述。

一般来说，使用下表进行持久化和延迟/性能的权衡，顺序从最高安全性/最高延迟到最低安全性/最低延迟。

1. AOF + fsync always: 非常慢，只有当你确实需要时才使用该配置。
2. AOF + fsync every second: 一个比较均衡的选择。
3. AOF + fsync every second + no-appendfsync-on-rewrite选项为yes: 也是一个比较均衡的选择，但是要避免重写期间执行fsync，这可以降低磁盘压力。
4. AOF + fsync never: 将fsync操作交给内核，减少了对磁盘的压力和延迟。
5. RDB: 这里你可以配置触发生成RDB文件的条件。

以下我们花费15分钟时间来看看细节。

## 测量延迟

如果你对处理延迟问题很有经验，可能你知道在你的应用程序中如何测量延迟，也许你的延迟问题是非常明显的，甚至是肉眼可见的。然而redis-cli可以在毫秒级别测量一个Redis服务器的延迟，只需要运行：

```
redis-cli --latency -h `host` -p `port`
```

## 使用Redis内置的延迟监控子系统

从Redis 2.8.13开始，Redis提供了延迟监控功能，能够取样检测出是哪里导致了服务器阻塞。这使得本文档所列举的问题的调试更加简单，所以我们建议尽量开启延迟监控。有关这方面更详细的说明请查阅[延迟监控的文档](https://redis.io/topics/latency-monitor)。

虽然延迟监控的采样和报告能力可以使我们更容易地了解造成Redis延迟的原因，但还是建议你阅读本文档更广泛地了解Redis的延迟尖峰。

## 延迟的基线

在你运行Redis的环境中有一种固有的延迟，这种延迟来自操作系统内核，如果你正在使用虚拟化，这种延迟来自于你使用的虚拟机管理程序。

虽然这个延迟无法被抹去，但这是我们学习的重要对象，因为它是基线，或者换句话说，由于内核和虚拟机管理程序的存在，你无法将Redis的延迟优化得比你系统中正在运行的进程的延迟还要低。

我们称这种延迟为内在延迟，redis-cli从Redis 2.8.7版本之后就可以测量内在延迟了。下面是一个运行在Linux 3.11.0入门级服务器上的实例。

注意：参数100表示测试执行的时间的秒数。我们运行测试的时间越久，就越有可能发现延迟尖峰。100秒通常是合适的，不过你可能希望在测试过程中不同的时间执行一些其他的操作。请注意，测试是CPU密集型的，这可能会使系统中的单个内核跑满。

```
$ ./redis-cli --intrinsic-latency 100
Max latency so far: 1 microseconds.
Max latency so far: 16 microseconds.
Max latency so far: 50 microseconds.
Max latency so far: 53 microseconds.
Max latency so far: 83 microseconds.
Max latency so far: 115 microseconds.
```

注意：在这个特殊情况下，redis-cli需要在服务器端运行，而不是在客户端。这种特殊模式下，redis-cli根本不需要连接到一台Redis服务器：它只是试图测量内核不提供CPU时间给redis-cli进程本身的最大时间。

上面的例子中，系统固有延迟只有0.115毫秒（或115微秒），这是个好消息，但是请记住，系统内在延迟可能随着系统负载而随时间变化。

虚拟化环境的情况会差一些，特别是在共享虚拟环境中有高负载的其他应用在运行时。下面是一个在Linode 4096实例上运行Redis和Apache的例子：

```
$ ./redis-cli --intrinsic-latency 100
Max latency so far: 573 microseconds.
Max latency so far: 695 microseconds.
Max latency so far: 919 microseconds.
Max latency so far: 1606 microseconds.
Max latency so far: 3191 microseconds.
Max latency so far: 9243 microseconds.
Max latency so far: 9671 microseconds. 
```

这里我们测量出有9.7毫秒的内在延迟：这意味着Redis的延迟不可能比这个数字更低了。然而，在不同的虚拟化环境中，如果有高负载的其他应用程序在运行时，很容易出现更高的内在延迟。除非我们能够在系统中测量出40毫秒的内在延迟，否则显然Redis运行正常。

## 网络通信引起的延迟

客户端使用一条TCP/IP连接或一条UNIX域连接来连接Redis。一个带宽为1  Gbit/s的网络典型的延迟为200μs，然而一个UNIX域套接字的延迟可以低至30μs。这具体依赖你的网络和系统硬件情况。高层的通信增加了更多的延迟（由于线程调度、CPU缓存、NUMA配置等等）。系统内部引起的延迟在虚拟化环境中要比在物理机上高得多。

其结果是尽管Redis处理大部分命令的时间都在亚微秒级别，但一个客户端和服务器之间的多次往返会增加网络和系统的延迟。

一个高效的客户端将会通过使用流水线来限制执行多个命令时的通信往返次数。流水线特性被服务器和绝大多数客户端所支持。批量操作命令如MSET/MGET也是为了这个目的。从Redis 2.4起，一些命令还支持所有数据类型的可变参数。

下面是一些准则：

- 如果经济上允许，优先选择使用物理机而不是虚拟机来承载Redis服务端。
- 不要随意连接/断开到服务器（尤其是web应用程序）。尽量保持连接长时间可用。
- 如果Redis的服务端和客户端部署在同一台机器上，请使用UNIX域套接字。
- 相比起流水线，尽量使用批量操作命令（MSET/MGET），或可变参数命令（如果可能的话）。
- 相比起发送多个单独命令，尽量使用流水线（如果可能的话）。
- 在不适合使用原生流水线功能的场景，Redis支持服务端Lua脚本（针对一个命令的输出是另一个命令的输入的情况）。

在Linux中，你可以通过process placement (taskset)、 cgroups、 real-time  priorities (chrt)、 NUMA configuration  (numactl)或使用一个低延迟内核来获得更低的延迟。请注意Redis并不适合被绑定在一个CPU内核上运行。Redis会fork出一些后台任务比如bgsave或AOF重写这些非常消耗CPU的任务。这些任务禁止和Redis的主事件循环运行在同一个CPU上。

大部分情况下，我们不需要这种类型的系统级优化。只有当你确实需要或者对它们很熟悉的情况下再去使用它们。

## Redis的单线程属性

Redis被设计成大部分情况下是单线程的。这意味着使用一个线程处理所有的客户端请求，其中使用了多路复用技术。这意味着Redis在一个时刻只能处理一个命令，所以所有命令都是串行执行的。这和Node.js的工作机制很类似。然而，Redis和Node.js通常都被认为是非常高性能的。这有部分原因是因为它们处理每个请求的时间都很短，但是主要原因是因为它们都被设计成不会被系统调用锁阻塞，比如从套接字中读取或写入数据。

之所以说Redis大部分情况下是单线程的，是因为从Redis 2.4版本起，为了在后台执行一些慢速的I/O操作，一般是磁盘I/O，Redis使用了其他线程来执行。但这也不能改变Redis使用单线程处理所有请求这个事实。

## 慢查询命令引起的响应延迟

使用单线程的一个结果是，当一个请求的处理很慢时，所有其他客户端将等待该请求被处理完毕。当执行普通命令时，比如GET或SET或LPUSH时这完全不是问题，因为这几个命令的执行时间是常数（非常短）。然而，有些命令会操作多个元素，比如SORT、LREM、SUNION等。例如，计算两个大集合的交集需要花费很长的时间。

所有命令的算法复杂度都有文档记录。一个好的实践是当你使用你不熟悉的命令之前先检查该命令的算法复杂度。

如果你关注Redis的响应延迟问题，你就不应该对有多个元素的值使用慢查询命令，你应该在Redis复制节点上运行你所有的慢查询。

可以使用Redis的[Slow Log功能](https://redis.io/commands/slowlog)来监控慢查询命令。

而且，你可以使用你最喜欢的进程级监控程序（top, htop, prstat等）来快速检查Redis主进程的CPU消耗。如果并发量并不是很高，很可能是因为你使用了慢查询命令。

重要提示：一个非常常见的造成Redis响应延迟的情况是在生产环境中使用KEYS命令。Redis文档中指出KEYS命令只能用于调试目的。从Redis 2.8之后，为了在键空间或大集合中增量地迭代键而引入了一些命令，请查阅SCAN, SSCAN, HSCAN and  ZSCAN的文档来获取更多信息。

## fork引起的响应延迟

为了在后台生成RDB文件，或者当AOF持久化开启时重写AOF文件，Redis需要执行fork。fork操作（在主线程中执行）会引发响应延迟。

在大多数类UNIX系统中fork是一个开销很昂贵的操作，因为它涉及复制与进程相关联的大量对象。对于和虚拟内存相关联的页表尤其如此。

例如在一个Linux/AMD64系统上，内存被划分为一个个个4KB大小的页面。为了将逻辑地址转换成物理地址，每个进程都维护一个页表（在内部用一棵树表示），每个页面包含进程地址空间中的至少一个指针。所以一个拥有24GB内存的Redis实例需要的页表大小为24 GB / 4 kB * 8 = 48 MB。

当执行一个后台持久化任务时，该Redis实例需要执行fork，这将涉及分配和复制48MB的内存。这需要消耗时间和CPU资源，特别是在虚拟机上执行分配和初始化大内存时开销尤其昂贵。

## 不同系统中fork操作的耗时

现代硬件在复制页表这个操作上非常快，但Xen却不是这样。Xen的问题不在于虚拟化，而在于Xen本身。一个例子是使用VMware或Virtual Box不会导致fork变慢。下面比较了不同Redis实例执行fork操作的耗时。数据来自于执行BGSAVE，并观察INFO命令输出的`latest_fork_usec`信息。

然而，好消息是基于EC2 HVM的实例执行fork操作的表现很好，几乎和在物理机上执行差不多，所以使用m3.medium（或高性能）的实例将会得到更好的结果。

- 运行于VMware的Linux对一个6.0GB的Redis实例执行fork操作耗时77ms（12.8ms/GB）。
- 运行于物理机（硬件未知）上的Linux对一个6.1GB的Redis实例执行fork操作耗时80ms（13.1ms/GB）。
- 运行于物理机（Xeon @ 2.27Ghz）对一个6.9GB的Redis实例执行fork操作耗时62ms（9ms/GB）。
- 运行于6sync（KVM）虚拟机的Linux对360MB的Redis实例执行fork操作耗时8.2ms（23.3ms/GB）。
- 运行于EC2，旧实例类型（Xen）的Linux对6.1GB的Redis实例执行fork操作耗时1460ms（239.3ms/GB）。
- 运行于EC2，新实例类型（Xen）的Linux对1GB的Redis实例执行fork操作耗时10ms（10ms/GB）。
- 运行于Linode（Xen）虚拟机的Linux对0.9GB的Redis实例执行fork操作耗时382ms（424ms/GB）。

你可以看到运行在Xen上的虚拟机会有一到两个数量级的性能损失。对于EC2的用户有个很简单的建议：使用现代的基于HVM的实例。

## transparent huge pages引起的响应延迟

遗憾的是如果一个Linux内核启用了transparent huge pages，Redis为了将数据持久化到磁盘时调用fork将会引起很大的响应延迟。大内存页导致了以下问题：

1. 当调用fork时，共享大内存页的两个进程将被创建。
2. 在一个高负载的实例上，一些事件循环就将导致访问上千个内存页，导致几乎整个进程执行写时复制。
3. 这将导致高响应延迟和大内存的使用。

请确保使用下面的命令关闭transparent huge pages：

```
echo never > /sys/kernel/mm/transparent_hugepage/enabled
```

## 页交换引起的响应延迟（操作系统分页）

为了更高效地利用系统内存，Linux（以及很多其他的现代操作系统）能够将内存页迁移到磁盘，反之亦然。

如果内核将一个Redis的内存页从内存交换到磁盘文件，当Redis要访问该内存页中的数据时（比如访问该内存页中的一个键），内核为了将内存页从磁盘文件迁移回内存将会暂停Redis进程。这是一个涉及随机I/O的慢速操作（和访问一个已经在内存中的页面相比是非常慢的），这将导致导致Redis客户端感觉到异常的响应延迟。

内核将Redis内存页从内存交换到磁盘主要有三个原因：

- 系统有内存压力，比如正在运行的进程需要比当前可用物理内存更多的内存。最简单的例子就是Redis使用了比可用内存更多的内存。
- Redis实例中的数据集，或数据集中的一部分几乎是闲置状态（从未被客户端访问过），此时内核将把这部分内存页交换到磁盘上。这种情况非常罕见，因为即使是一个中等速度的Redis实例也经常会访问所有内存页，迫使内核将所有内存页保留在内存中。
- 系统中的一些进程引发了大量读或者写这种I/O操作。因为一般文件都会被缓存，这将导致内核需要增加文件系统缓存，这会导致内存页交换。请注意这包括生成Redis RDB和/或AOF这些会生成大文件的后台线程。

幸运的是Linux提供了很不错的工具来检查这些问题，所以当由于内存页交换导致的响应延迟发生时我们应该怀疑是否是上面三个原因导致的。

首先要做的是检查有多少Redis内存页被交换到了磁盘。为了达到这个目的我们需要获得Redis实例的pid：

```
$ redis-cli info | grep process_id
process_id:5454
```

现在进入这个进程的文件系统目录：

```
$ cd /proc/5454
```

你可以在这里找到一个名为`smaps`的文件，这个文件描述了Redis进程的内存布局（假设你正在使用Linux 2.6.16或更高版本的内核）。这个文件包含了进程非常详细的内存布局信息，其中有一个名为`Swap`字段对我们很重要。然而，这里面不仅仅只有一个swap字段，因为smaps文件还包含了Redis进程的其他内存映射（进程的内存布局比一个内存页的线性数组要复杂得多）。

由于我们对进程的所有内存交换情况感兴趣，因此首先要做的就是找出该文件中的所有Swap字段：

```
$ cat smaps | grep 'Swap:'
Swap:                  0 kB
Swap:                  0 kB
Swap:                  0 kB
Swap:                  0 kB
Swap:                  0 kB
Swap:                 12 kB
Swap:                156 kB
Swap:                  8 kB
Swap:                  0 kB
Swap:                  0 kB
Swap:                  0 kB
Swap:                  0 kB
Swap:                  0 kB
Swap:                  0 kB
Swap:                  0 kB
Swap:                  0 kB
Swap:                  0 kB
Swap:                  4 kB
Swap:                  0 kB
Swap:                  0 kB
Swap:                  4 kB
Swap:                  0 kB
Swap:                  0 kB
Swap:                  4 kB
Swap:                  4 kB
Swap:                  0 kB
Swap:                  0 kB
Swap:                  0 kB
Swap:                  0 kB
Swap:                  0 kB
```

如果所有Swap低端都是0 Kb，或者只有零星的字段是4k，那么一切正常。实际上在我们这个例子中（线上真实的每秒处理上千请求的Redis实例）有一些条目表示存在更多的内存页交换问题。为了调查这是否是一个严重的问题，我们使用其他命令以便打印出内存映射的大小：

```
$ cat smaps | egrep '^(Swap|Size)'
Size:                316 kB
Swap:                  0 kB
Size:                  4 kB
Swap:                  0 kB
Size:                  8 kB
Swap:                  0 kB
Size:                 40 kB
Swap:                  0 kB
Size:                132 kB
Swap:                  0 kB
Size:             720896 kB
Swap:                 12 kB
Size:               4096 kB
Swap:                156 kB
Size:               4096 kB
Swap:                  8 kB
Size:               4096 kB
Swap:                  0 kB
Size:                  4 kB
Swap:                  0 kB
Size:               1272 kB
Swap:                  0 kB
Size:                  8 kB
Swap:                  0 kB
Size:                  4 kB
Swap:                  0 kB
Size:                 16 kB
Swap:                  0 kB
Size:                 84 kB
Swap:                  0 kB
Size:                  4 kB
Swap:                  0 kB
Size:                  4 kB
Swap:                  0 kB
Size:                  8 kB
Swap:                  4 kB
Size:                  8 kB
Swap:                  0 kB
Size:                  4 kB
Swap:                  0 kB
Size:                  4 kB
Swap:                  4 kB
Size:                144 kB
Swap:                  0 kB
Size:                  4 kB
Swap:                  0 kB
Size:                  4 kB
Swap:                  4 kB
Size:                 12 kB
Swap:                  4 kB
Size:                108 kB
Swap:                  0 kB
Size:                  4 kB
Swap:                  0 kB
Size:                  4 kB
Swap:                  0 kB
Size:                272 kB
Swap:                  0 kB
Size:                  4 kB
Swap:                  0 kB
```

正如你在上面输出中所看到的，有一个720896 kB（其中只有12 kB的内存页交换）的内存映射，在另一个内存映射中交换了156 kB：只有很少一部分内存页被交换到磁盘，这没什么问题。

相反，如果有大量进程内存页被交换到磁盘，那么你的响应延迟问题可能和内存页交换有关。如果是这样的话，你可以使用`vmstat`命令来进一步检查你的Redis实例：

```
$ vmstat 1
procs -----------memory---------- ---swap-- -----io---- -system-- ----cpu----
r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa
0  0   3980 697932 147180 1406456    0    0     2     2    2    0  4  4 91  0
0  0   3980 697428 147180 1406580    0    0     0     0 19088 16104  9  6 84  0
0  0   3980 697296 147180 1406616    0    0     0    28 18936 16193  7  6 87  0
0  0   3980 697048 147180 1406640    0    0     0     0 18613 15987  6  6 88  0
2  0   3980 696924 147180 1406656    0    0     0     0 18744 16299  6  5 88  0
0  0   3980 697048 147180 1406688    0    0     0     4 18520 15974  6  6 88  0
^C
```

你需要注意查看`si`和`so`两列，这两列统计了内存页从内存交换到磁盘和从磁盘交换到内存的次数。如果在这两列中你看到非零值，就说明你的系统中存在内存页交换。

最后，可以使用`iostat`命令来检查系统的全局I/O活动。

```
$ iostat -xk 1
avg-cpu:  %user   %nice %system %iowait  %steal   %idle
        13.55    0.04    2.92    0.53    0.00   82.95

Device:         rrqm/s   wrqm/s     r/s     w/s    rkB/s    wkB/s avgrq-sz avgqu-sz   await  svctm  %util
sda               0.77     0.00    0.01    0.00     0.40     0.00    73.65     0.00    3.62   2.58   0.00
sdb               1.27     4.75    0.82    3.54    38.00    32.32    32.19     0.11   24.80   4.24   1.85
```

如果你的响应延迟问题是由Redis内存页交换导致的，你就需要降低系统中的内存压力，如果Redis使用了比可用内存更多内存的话你就增加更多内存，或者避免在同一个系统中运行其他需要大量内存的进程。

## AOF和磁盘I/O引起的响应延迟

另一个响应延迟的原因是Redis的AOF。Redis使用了两个系统调用来完成AOF功能。一个是使用write(2)来将数据写入到只追加的文件中，另一个是使用fdatasync(2)来刷新内核文件缓冲区到磁盘以满足用户指定的持久化级别。

write(2)和fdatasync(2)都会造成响应延迟。例如当系统进程同步时write(2)会造成阻塞，或者当输出缓冲区满时内核需要将数据刷到磁盘上以便能接受新的写入。

fdatasync(2)会导致更严重的响应延迟，许多内核和文件系统对它的结合使用会导致数毫秒到数秒的延迟。当特别是在有其他进程正在执行I/O时。出于这些原因，从Redis 2.4开始fdatasync(2)会在另一个线程中执行。

我们将看到在使用AOF功能时，不同配置如何影响Redis的响应延迟。

AOF的配置项appendfsync可以有三种不同的方式来执行磁盘的fsync（这些配置可以在运行时使用`CONFIG SET`命令动态修改）。

- 当appendfsync被设置为no时，Redis不执行fsync。这种配置下响应延迟的唯一原因就是write(2)了。这种情况下发生响应延迟一般没有解决方案，因为磁盘的处理速度跟不上Redis接收数据的速度，然而，如果当磁盘没有被其他进程的I/O拖慢时，这是很少见的。
- 当appendfsync被设置成everysec时，Redis每秒执行一次fsync。Redis使用另外的线程执行fsync，如果此时fsync正在执行，Redis使用缓冲区来延迟2秒执行write(2)（因为在Linux中对一个正在执行fsync的文件执行write将被阻塞）。然而，如果fsync执行时间太长，即使fsync正在执行，Redis也将执行write(2)，这会引起响应延迟。
- 当appendfsync被设置成always时，Redis将在每次写操作发生时，返回OK给客户端之前执行fsync（实际上Redis会尝试将同一时间的多个命令的执行使用fsync一次性进行写入）。这种模式下Redis性能很低，此时一般建议使用高速硬盘和文件系统的实现以便能更快地完成fsync。

大多数Redis用户将appendfsync配置项设置为no或everysec。将响应延迟降低到最小的建议是避免在同一个系统中有其他进程执行I/O。使用固态硬盘也能降低I/O造成的的响应延迟，但一般来说当Redis写AOF时，如果此时硬盘上没有其他查找操作，非固态硬盘的性能也还不错。

如果你想调查AOF引起的响应延迟问题，你可以使用strace命令：

```
sudo strace -p $(pidof redis-server) -T -e trace=fdatasync
```

上面的命令将显示Redis在主线程中执行的所有fdatasync(2)系统调用情况。当appendfsync配置项被设置为everysec时，使用上面的命令无法查看到后台进程执行fdatasync系统调用情况，如果需要查看后台进程的情况，在strace命令上加上-f选项即可。

如果你同事想查看fdatasync和write两个系统调用的情况，使用下面的命令：

```
sudo strace -p $(pidof redis-server) -T -e trace=fdatasync,write
```

然而因为write(2)也被用来向客户端套接字写入数据，所有可能会显示很多与磁盘I/O无关的信息。显然strace命令无法只显示慢系统调用的信息，所以我们使用下面的命令：

```
sudo strace -f -p $(pidof redis-server) -T -e trace=fdatasync,write 2>&1 | grep -v '0.0' | grep -v unfinished
```

## 过期数据引起的响应延迟

Redis有两种方式淘汰过期键：

- 一个被动删除过期键的方式是当一个键被一个命令访问时，如果发现它已经过期就删除之。
- 一个主动删除过期键的方式是每隔100毫秒删除掉一些过期键。

主动删除过期键这种方式被设计成自适应的。每隔100毫秒（即一秒执行10次）执行一次过期键删除，方式如下：

- 根据ACTIVE_EXPIRE_CYCLE_LOOKUPS_PER_LOOP的值采样键，删除所有已经过期的键。
- 如果采样出的键有超过25%的键过期了，重复这个采样过程。

ACTIVE_EXPIRE_CYCLE_LOOKUPS_PER_LOOP的默认值是20，采样删除过期键这个过程一秒执行10次，一般来说每秒最多有200个过期键被删除。那些已经过期很久的键也可以通过这种主动淘汰的方式被清除出数据库，所以被动删除方式意义不大。同时每秒钟删除200个键也不会引起Redis实例的响应延迟。

然而，主动淘汰算法是自适应的，如果在采样删除时有25%以上的键过期，将直接执行下一次循环。但考虑到我们每秒运行该算法10次，这意味着可能发生在同一秒内被采样的键25%以上都过期的情况。

基本上就是说，如果数据库在同一秒中有非常多键过期，而这些键至少占当前已经过期键的25%时，Redis为了让过期键占所有键的比例下降到25%以下将会阻塞。

这种做法是必要的，这可以避免已经过期的键占用太多内存。而且这种方式通常来说是绝对无害的，因为在同一秒有大量键过期的情况非常奇怪，但这种情况也不是完全不可能发生，因为用户可以使用EXPIREAT命令为键设置相同的过期时间。

简而言之：注意大量键同时过期引起的响应延迟。

## Redis软件监控

Redis 2.6引入了Redis软件监控的调试工具，用来跟踪那些无法用常规工具分析出的响应延迟问题。

Redis的软件监控是一个实验性地功能。虽然它被设计用于生产环境，由于在使用时它可能会与Redis服务器的正常运行产生意外的交互，所以使用前应该先备份数据库。

需要特别说明的是只有在万不得已的情况下再使用这种方式跟踪响应延迟问题。

下面是这个功能的工作细节：

- 用户使用`CONFIG SET`命令开启软件监控功能。
- Redis不断地监控自己。
- 如果Redis检测到服务器被一些操作阻塞导致无法快速响应，则可能是响应延迟的问题所在，将会生成一份服务器在何处被阻塞的底层日志报告。
- 用户在Redis的Google Group中联系开发者，并展示监控报告的内容。

注意该功能无法在redis.conf文件中开启，因为这个功能被设计用于调试正在运行的实例。

使用下面的命令开启次功能：

```
CONFIG SET watchdog-period 500
```

命令中的时间单位是毫秒。上面的示例中制定了尽在检测到服务器有超过500毫秒的延迟时才记录问题。最小的克配置时间是200毫秒。

当你不需要软件监控功能时，可以通过将watchdog-period参数设置为0来关闭它。
非常重要：请记得在不需要软件监控时关闭它，因为一般来说长时间在实例上运行软件监控不是个好主意。

下面的例子展示了软件监控检测到了响应延迟超过配置时间的情况，在日志文件中输出的信息：

```
[8547 | signal handler] (1333114359)
--- WATCHDOG TIMER EXPIRED ---
/lib/libc.so.6(nanosleep+0x2d) [0x7f16b5c2d39d]
/lib/libpthread.so.0(+0xf8f0) [0x7f16b5f158f0]
/lib/libc.so.6(nanosleep+0x2d) [0x7f16b5c2d39d]
/lib/libc.so.6(usleep+0x34) [0x7f16b5c62844]
./redis-server(debugCommand+0x3e1) [0x43ab41]
./redis-server(call+0x5d) [0x415a9d]
./redis-server(processCommand+0x375) [0x415fc5]
./redis-server(processInputBuffer+0x4f) [0x4203cf]
./redis-server(readQueryFromClient+0xa0) [0x4204e0]
./redis-server(aeProcessEvents+0x128) [0x411b48]
./redis-server(aeMain+0x2b) [0x411dbb]
./redis-server(main+0x2b6) [0x418556]
/lib/libc.so.6(__libc_start_main+0xfd) [0x7f16b5ba1c4d]
./redis-server() [0x411099]
------
```

注意：在这个例子中`DEBUG SLEEP`命令用来使服务器阻塞。这个服务器阻塞的栈跟踪信息会随服务器上下文而异。

我们鼓励你将所搜集到的监控栈跟踪信息发送至Redis Google Group：获得的信息越多，就越能轻松了解你的Redis实例的问题所在。





---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>