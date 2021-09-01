---
layout: post
title: 常用快捷键/命令行/系统设定
categories: tools
tags: [linux, macos, windows, vscode, vim, shell, docker]
---



[toc]

<!-- more -->

---

## 遇到故障速查十个命令

---


```
uptime
dmesg | tail
vmstat 1
mpstat -P ALL 1
pidstat 1
iostat -xz 1
free -m
sar -n DEV 1
sar -n TCP,ETCP 1
top
```

其中的一些命令需要安装sysstat软件包。这些命令暴露出的指标将帮助您完成一些USE方法：一种查找性能瓶颈的方法。它们涉及检查所有资源（CPU、内存、磁盘等）的利用率，饱和度和错误指标。在诊断过程中还应该注意检查和排除某些资源的问题。因为通过排除某些资源的问题，可以缩小诊断的范围，并指民后续的诊断。

以下各节通过生产系统中的示例总结了这些命令。有关这些工具更多的信息，请参见其手册页。

### uptime

```bash
$ uptime 
23:51:26 up 21:31, 1 user, load average: 30.02, 26.43, 19.02
```

这是快速查看平均负载的方法，该平均负载指标了要运行的任务（进程）的数量。在Linux系统上，这些数字包括要在CPU上运行的进程以及在不中断IO（通常是磁盘IO）中阻塞的进程。这里给出了资源负载高层次的概览，但是没有其它工具就很难正确理解，值得快速看一眼。

这三个数字是指数衰减移动平均值，分别代表了1分钟、5分钟、15分钟的平均值。这三个数字使我们对负载如何随时间变化有了一定的了解。例如，如果您去诊断一个有问题的服务器，发现1分钟的值比15分钟的值低很多，那么您可能已经登录得太晚了，错过了问题。

在上面的例子中，平均负载有所增加，因为1分钟的值30相对15分钟的值19来说大了一些。数字变大意味着很多种可能：有可能是CPU的需求变多了，使用3和4中提到的vmstat或mpstat命令将可以进一步确认问题。

### dmesg | tail

```bash
$ dmesg | tail
[1880957.563150] perl invoked oom-killer: gfp_mask=0x280da, order=0, oom_score_adj=0
[...]
[1880957.563400] Out of memory: Kill process 18694 (perl) score 246 or sacrifice child
[1880957.563408] Killed process 18694 (perl) total-vm:1972392kB, anon-rss:1953348kB, file-rss:0kB
[2320864.954447] TCP: Possible SYN flooding on port 7001. Dropping request.  Check SNMP counters.
```

该命令展示最近 10条系统消息。在这些系统消息中查找有可能引起性能问题的报错。上面的例子包括`oom-killer`和TCP丢弃了一个请求。

不能忘记这个步骤，`dmesg`通常对诊断问题很有价值。

###  vmstat  1

```bash
$ vmstat 1
procs ---------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
34  0    0 200889792  73708 591828    0    0     0     5    6   10 96  1  3  0  0
32  0    0 200889920  73708 591860    0    0     0   592 13284 4282 98  1  1  0  0
32  0    0 200890112  73708 591860    0    0     0     0 9501 2154 99  1  0  0  0
32  0    0 200889568  73712 591856    0    0     0    48 11900 2459 99  0  0  0  0
32  0    0 200890208  73712 591860    0    0     0     0 15898 4840 98  1  1  0  0
^C
```

vmstat是虚拟内存统计(Virtual Memory Stat)的缩写，vmstat(8)是一个通常可用的工具(最初是在之前的BSD时代创建的)，它每行打印一行服务器关键统计的概览。

vmstat使用参数1运行，意味着每1秒打印打印一次概览。命令输出的第一行展示的是从启动开始的平均值，而不是最近一秒的平均值。因此跳过第一行，除非您想学习并记住哪一列是哪一列。

要检查的列：

- `r`：在CPU上运行并等待回合的进程数。由于它不包含IO，因此它比指示CPU饱和的平均负载提供了更多的信息。一个大于CPU核数的`r`值就是饱和的。
- `free`：空闲的内存（单位的KB）。如果计数很大，说明服务器有足够的内存，`free -m`命令将对空闲内存的状态有更好的说明。
- `si`、`so`：交换置入和交换置出。如果这两个值是非空，说明物理内存用完了，现在在使用交换内存了。
- `us`、`sy`、`id`、`wa`、`st`：这些是CPU时间的分类，其是所有CPU的平均值。它们是用户时间、系统时间(内核)、空闲时间、等待IO和被偷窃时间（被其它宾客系统进行使用，或宾客系统隔离的驱动程序域Xen）

通过将用户时间和系统时间这两个分类相加，即可判断CPU是否繁忙。一定的等待IO时间说明磁盘有可能是性能瓶颈。你可以认为等待IO时间是另一种形式的空闲时间，它提供了它是如何空闲的线索。

IO处理需要占用CPU系统时间。一个较高的CPU系统时间（超过20%）可能会很有趣，有必要进一步研究：也许内核在很低效地处理IO。

在上面的示例中，CPU时间基本全在用户时间，这说明应用程序本身在大量占用CPU时间。CPU的平均利用率也远远超过90%。这不一定是问题，可以使用`r`列来检查饱和度。

###  mpstat -P ALL  1

```bash
$ mpstat -P ALL 1
Linux 3.13.0-49-generic (titanclusters-xxxxx)  07/14/2015  _x86_64_ (32 CPU)

07:38:49 PM  CPU   %usr  %nice   %sys %iowait   %irq  %soft  %steal  %guest  %gnice  %idle
07:38:50 PM  all  98.47   0.00   0.75    0.00   0.00   0.00    0.00    0.00    0.00   0.78
07:38:50 PM    0  96.04   0.00   2.97    0.00   0.00   0.00    0.00    0.00    0.00   0.99
07:38:50 PM    1  97.00   0.00   1.00    0.00   0.00   0.00    0.00    0.00    0.00   2.00
07:38:50 PM    2  98.00   0.00   1.00    0.00   0.00   0.00    0.00    0.00    0.00   1.00
07:38:50 PM    3  96.97   0.00   0.00    0.00   0.00   0.00    0.00    0.00    0.00   3.03
[...]
```

此命令显示每个CPU的CPU时间明细，可用于检查不平衡的情况。单个热CPU说明是单线程应用程序在大量占用CPU时间。

###  pidstat 1

```bash
$ pidstat 1
Linux 3.13.0-49-generic (titanclusters-xxxxx)  07/14/2015    _x86_64_    (32 CPU)

07:41:02 PM   UID       PID    %usr %system  %guest    %CPU   CPU  Command
07:41:03 PM     0         9    0.00    0.94    0.00    0.94     1  rcuos/0
07:41:03 PM     0      4214    5.66    5.66    0.00   11.32    15  mesos-slave
07:41:03 PM     0      4354    0.94    0.94    0.00    1.89     8  java
07:41:03 PM     0      6521 1596.23    1.89    0.00 1598.11    27  java
07:41:03 PM     0      6564 1571.70    7.55    0.00 1579.25    28  java
07:41:03 PM 60004     60154    0.94    4.72    0.00    5.66     9  pidstat

07:41:03 PM   UID       PID    %usr %system  %guest    %CPU   CPU  Command
07:41:04 PM     0      4214    6.00    2.00    0.00    8.00    15  mesos-slave
07:41:04 PM     0      6521 1590.00    1.00    0.00 1591.00    27  java
07:41:04 PM     0      6564 1573.00   10.00    0.00 1583.00    28  java
07:41:04 PM   108      6718    1.00    0.00    0.00    1.00     0  snmp-pass
07:41:04 PM 60004     60154    1.00    4.00    0.00    5.00     9  pidstat
^C
```

`pidstat`有点像top的每个进程摘要，但是会滚动打印，而不是清屏再打印。这对于观察一段时间内的模式以及将所看到的内容（复制&粘贴）记录到调查记录中很有用。

上面的示例显示两个Java进程要为消耗大量CPU负责。`%CPU`这一列是所有CPU核的总和，`1591%`说明Java进程差不多消耗了16个核的CPU。

### iostat -xz 1

```bash
$ iostat -xz 1
Linux 3.13.0-49-generic (titanclusters-xxxxx)  07/14/2015  _x86_64_ (32 CPU)

avg-cpu:  %user   %nice %system %iowait  %steal   %idle
          73.96    0.00    3.73    0.03    0.06   22.21

Device:   rrqm/s   wrqm/s     r/s     w/s    rkB/s    wkB/s avgrq-sz avgqu-sz   await r_await w_await  svctm  %util
xvda        0.00     0.23    0.21    0.18     4.52     2.08    34.37     0.00    9.98   13.80    5.42   2.44   0.09
xvdb        0.01     0.00    1.02    8.94   127.97   598.53   145.79     0.00    0.43    1.78    0.28   0.25   0.25
xvdc        0.01     0.00    1.02    8.86   127.79   595.94   146.50     0.00    0.45    1.82    0.30   0.27   0.26
dm-0        0.00     0.00    0.69    2.32    10.47    31.69    28.01     0.01    3.23    0.71    3.98   0.13   0.04
dm-1        0.00     0.00    0.00    0.94     0.01     3.78     8.00     0.33  345.84    0.04  346.81   0.01   0.00
dm-2        0.00     0.00    0.09    0.07     1.35     0.36    22.50     0.00    2.55    0.23    5.62   1.78   0.03
[...]
^C
```

这是了解块设备（磁盘），应用的工作负载和产生的性能影响的绝佳工具。重点关注下面的指标：

- `r/s`、`w/s`、 `rkB/s`、 `wkB/s`：这些是设备每秒交付的读取、写入、读取千字节和写入千字节。使用这些来表征块设备的工作负载。性能问题可能是由于向块设备施加了过多的工作负载。
- `await`：IO的平均时间，以毫秒为单位。这是应用程序所感受到的时间，它包括IO排队时间和IO服务时间。大于预期的平均时间可能表示块设备饱和或设备出现问题了。
- `avgqu-sz`：发给设备的平均请求数。值大于1可以表明已达到饱和状态（尽管设备通常可以并行处理请求，尤其是在多个后端磁盘所组成的前端虚拟设备的情况下）。
- `%util`：设备利用率。这是一个表征繁忙度的百分比，它表示设备每秒工作的时间。尽管它的值取决于设备，但值大于60%通常会导致性能不佳（也会通过await的值观察到）。接近100%的值通常表示饱和。

如果存储设备是有许多后端磁盘组成的前端逻辑磁盘设备，则100%的利用率可能仅意味着100%的时间正在处理某些IO，但是后端磁盘可能远远没有饱和，并且可能还可以处理更多的工作。

请记住，性能不佳的磁盘IO不一定是应用问题，通常可以使用许多技术以执行异步IO，以便使应用程序不会被阻塞住而产生直接产生IO延迟（例如，预读和缓冲写入技术）

###  free -m

```bash
$ free -m
             total       used       free     shared    buffers     cached
Mem:        245998      24545     221453         83         59        541
-/+ buffers/cache:      23944     222053
Swap:            0          0          0
```

右边两列：

- `buffers`：缓冲区高速缓存，用于块设备I / O
- `cached`：页面缓存，由文件系统使用

我们只需要检查下它们的大小是否接近零。如果接近零的话，这可能导致较高的磁盘IO（可以使用iostat进行确认）和较差的性能。上面的示例看起来不错，每列都有较大的数据。

`-/+ buffers/cache`为已用和空闲内存提供较少让人产生混乱的值。Linux将可用内存用于高速缓存，但是如果应用程序需要，它们可以快速被回收。因此应以某种方式将缓存的内存包括在`free`列中，这也就是这一行的所做的。甚至还有一个[网站](http://www.linuxatemyram.com/)专门讨论了这种混乱。

如果在Linux上使用ZFS，就像我们对某些服务所做的那么，因为ZFS具有自己的文件系统缓存，它们并不会反映在`free -m`的列中，因此这种场景下这种混乱还将存在。所以会看到似乎系统的可用内存不足，而实际上可根据需要从ZFS缓存中申请到内存。

###  sar -n DEV 1

```bash
$ sar -n DEV 1
Linux 3.13.0-49-generic (titanclusters-xxxxx)  07/14/2015     _x86_64_    (32 CPU)

12:16:48 AM     IFACE   rxpck/s   txpck/s    rxkB/s    txkB/s   rxcmp/s   txcmp/s  rxmcst/s   %ifutil
12:16:49 AM      eth0  18763.00   5032.00  20686.42    478.30      0.00      0.00      0.00      0.00
12:16:49 AM        lo     14.00     14.00      1.36      1.36      0.00      0.00      0.00      0.00
12:16:49 AM   docker0      0.00      0.00      0.00      0.00      0.00      0.00      0.00      0.00

12:16:49 AM     IFACE   rxpck/s   txpck/s    rxkB/s    txkB/s   rxcmp/s   txcmp/s  rxmcst/s   %ifutil
12:16:50 AM      eth0  19763.00   5101.00  21999.10    482.56      0.00      0.00      0.00      0.00
12:16:50 AM        lo     20.00     20.00      3.25      3.25      0.00      0.00      0.00      0.00
12:16:50 AM   docker0      0.00      0.00      0.00      0.00      0.00      0.00      0.00      0.00
^C
```

此工具可以检查网络接口的吞吐量：`rxkB/s`和`txkB/s`，作为工作负载的度量，还可以检查是否已达到网络接口的限制。在上面的示例中，eth0接收速率达到22MB/s，即176Mbit/s（远低于1Gbit/s的网络接口限制，假设是千兆网卡）。

此版本还具有`%ifutil`用来指示设备利用率（全双工双向），这也是我们使用的Brendan的[nicstat工具](https://github.com/scotte/nicstat)测量出来的。就像nicstat一样，这个指标很难计算正确，而且在本例中好像不起作用（数据是0.00）。

###  sar -n TCP,ETCP 1

```bash
$ sar -n TCP,ETCP 1
Linux 3.13.0-49-generic (titanclusters-xxxxx)  07/14/2015    _x86_64_    (32 CPU)

12:17:19 AM  active/s passive/s    iseg/s    oseg/s
12:17:20 AM      1.00      0.00  10233.00  18846.00

12:17:19 AM  atmptf/s  estres/s retrans/s isegerr/s   orsts/s
12:17:20 AM      0.00      0.00      0.00      0.00      0.00

12:17:20 AM  active/s passive/s    iseg/s    oseg/s
12:17:21 AM      1.00      0.00   8359.00   6039.00

12:17:20 AM  atmptf/s  estres/s retrans/s isegerr/s   orsts/s
12:17:21 AM      0.00      0.00      0.00      0.00      0.00
^C
```

这是一些关键的TCP指标的摘要，包括：

- `active / s`：每秒本地启动的TCP连接数（例如，通过connect（））。
- `passive/s`：每秒远程启动的TCP连接数（例如，通过accept（））。
- `retrans / s`：每秒TCP重传的次数。

主动和被动计数通常作为服务器TCP负载的粗略度量：新接受的连接数（被动）和新出站的连接数（主动）。将主动视为出站，将被动视为入站可能对理解这两个指标有些帮助，但这并不是严格意义上的（例如，考虑从localhost到localhost的连接）。

重新传输是网络或服务器问题的迹象；它可能是不可靠的网络（例如，公共Internet），也可能是由于服务器过载并丢弃了数据包。上面的示例仅显示每秒一个新的TCP连接。

###  top

```bash
$ top
top - 00:15:40 up 21:56,  1 user,  load average: 31.09, 29.87, 29.92
Tasks: 871 total,   1 running, 868 sleeping,   0 stopped,   2 zombie
%Cpu(s): 96.8 us,  0.4 sy,  0.0 ni,  2.7 id,  0.1 wa,  0.0 hi,  0.0 si,  0.0 st
KiB Mem:  25190241+total, 24921688 used, 22698073+free,    60448 buffers
KiB Swap:        0 total,        0 used,        0 free.   554208 cached Mem

   PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND
 20248 root      20   0  0.227t 0.012t  18748 S  3090  5.2  29812:58 java
  4213 root      20   0 2722544  64640  44232 S  23.5  0.0 233:35.37 mesos-slave
 66128 titancl+  20   0   24344   2332   1172 R   1.0  0.0   0:00.07 top
  5235 root      20   0 38.227g 547004  49996 S   0.7  0.2   2:02.74 java
  4299 root      20   0 20.015g 2.682g  16836 S   0.3  1.1  33:14.42 java
     1 root      20   0   33620   2920   1496 S   0.0  0.0   0:03.82 init
     2 root      20   0       0      0      0 S   0.0  0.0   0:00.02 kthreadd
     3 root      20   0       0      0      0 S   0.0  0.0   0:05.35 ksoftirqd/0
     5 root       0 -20       0      0      0 S   0.0  0.0   0:00.00 kworker/0:0H
     6 root      20   0       0      0      0 S   0.0  0.0   0:06.94 kworker/u256:0
     8 root      20   0       0      0      0 S   0.0  0.0   2:38.05 rcu_sched
```

`top`命令包括我们之前检查的许多指标。运行它可以很方便地查看是否有任何东西与以前的命令有很大不同，这表明负载是可变的。

`top`命令不太好的地方是，随着时间的推移很难看到指标变化的模式，这在提供滚动输出的`vmstat`和`pidstat`之类的工具中可能更清楚一点。如果您没有足够快地暂停输出（Ctrl-S暂停，Ctrl-Q继续），在屏幕输出被`top`命令清除后，间歇性问题的证据也可能被丢失了。

一图流

<p><img src="https://wanghenshui.github.io/assets/top.png" alt="" width="100%"></p>

## Vim

- G 跳到最后
- set foldmethod=indent "set default foldmethod
- zi 打开关闭折叠 "zv 查看此行 zm 关闭折叠 zM 关闭所有 zr 打开 zR 打开所有 zc 折叠当前行 zo 打开当前折叠 zd 删除折叠 zD 删除所有折叠
- / 查找 n下一个
  - 正则表达式，例如/vim$匹配行尾的"vim"
  - \c表示大小写不敏感查找，\C表示大小写敏感查找。/foo\c
  - set ignorecase  ~/.vimrc
- 替换 :{作用范围}s/{目标}/{替换}/{替换标志} %s/foo/bar/g会在全局范围(%)查找foo并替换为bar，所有出现都会被替换（g）
  - 作用范围
    - :s/foo/bar/g
    - :%s/foo/bar/g
    - :5,12s/foo/bar/g :.,+2s/foo/bar/g
  - 替换标志
    - 目标的第一次出现：:%s/foo/bar
    - i表示大小写不敏感查找，I表示大小写敏感 :%s/foo/bar/i
    - \#等效于模式中的\c（不敏感）或\C（敏感）:%s/foo\c/bar
    - c表示需要确认，例如全局查找"foo"替换为"bar"并且需要确 :%s/foo/bar/gc
    - 参考： [Vim中如何快速进行光标移](http://harttle.com/2015/11/07/vim-cursor.html)
- 1y lh 粘贴
- v模式 e选中 
- b w 前后走动
- 命令行 补全 ctrl l
- 插入模式补全 ctrl p
- 在vim里执行命令 加感叹号就可以 !ls



## linux常用

- Ctrl a 到命令行开头 ctrl e到命令行结尾

- grep取反 grep -v ”ect“”

- Linux 

  - Ctrl + L清屏
  - mv filename(/*) -t directory 也有重命名功能
  
- du -a du -h
    - du -h --max-depth=1 常用，看一个目录
  - file libvswrtp.so 查询文件信息（查链接库版本一个小经验）ldd
  
- gdb

    - thread apply all bt
    - pstack
      - pstack在chroot下执行的进程，可能找不到符号，要到chroot下面的目录去执行pstack
        - https://nanxiao.me/linux-pstack/

- tar 

    - 对于xz文件 **tar xvJf  \**\*.tar.xz**
    - 流  tar cf - xxfile | lz4  > xxfile2
      - 也可以用snzip

- mount

    - mount /dev/vdb target_dir

- scp 

    - scp local_file root@xx.xx.xx.xx:/root

- rpm -ivh xx.rpm

- 特殊场景

    - 查找体积较大的十个文件
      - du -hsx * | sort -rh | head -10
    - 端口占用 netstat|grep 11221
      - lsof -i :11221抓到对应的进程

- putty

    - alt enter退出全屏 在window behaviour里，勾选最后一个
      - [x] full screen on alt-enter
    - 小键盘设置，在terminal features 勾选 
      - [x] disable application keypad mode
    - 记得保存设置

- telnet 

    - 退出 ctrl  ]

- iptables

    - 查看端口 **cat  /etc/sysconfig/iptables**

- jq 格式化json文档 `jq . xx.json > xx.json.new` 注意不能原地覆盖，这里有bug直接文件就空了

- 查看磁盘是否是ssd `cat /sys/block/vdb/queue/rotational` 1是sata 0是ssd

- `echo 1 > /proc/sys/vm/drop_caches ` 清除缓存

    
## win

  - wslconfig /l  wslconfig /s ubuntu-18.04
  - win shirl S win10 截图
  - compmgmt.msc 计算机 管理
  - devmgmt.msc 设备管理器
  - win + break 直接调出系统设置
  - eventvwr
  - ie 卸载程序
  - Ctrl + Shift + Esc 任务管理器
  - alt space n
  - alt f4/alt space c
  - snipingtool
  - mspaint
  - ctrl + win +d /F4 虚拟桌面
  - ctrl + win + →
  - win + L 锁屏
  - 磁盘格式转换 convert h: /fs:ntfs
  - windows查看端口占用 `netstat -aon|findstr 25340` 最后一行就是进程id
  - windows 杀死进程，在任务管理找不到的前提下 taskkill /f /pid 13656


## bazel


- 编译 bazel build //redis:* --copt="-g" --strip="never"
```bash
## 参数项一次只能指定一个
bazel build --copt="-O3" --copt="-fpic" --cxxopt="-std=c++11"
```

- http://zhulao.gitee.io/blog/2019/04/05/%E7%BC%96%E8%AF%91%E6%9E%84%E5%BB%BA%E5%B7%A5%E5%85%B7-bazel/index.html 这个文档不错 什么时候用什么时候再看

- 换编译器 --repo_env=CC=clang

- 编译所有 bazel build ...

- 测试 bazel test ...

* `--nocache_test_results` may be required if you are trying to re-run a test without changing
anything.
* `--test_filter=<TestName>` to run a specific test (when test splits are not already in use)

- 遇到bazel错误先看看路径是不是错了，或者文件名是不是错了

- bazel设置cache目录，修改.bazelrc `build --disk_cache=/my/tmp/cache` 不过.cache的缓存不能通过这个改，只能通过命令行改`--output_user_root`，我没有实验过



## MacOS

- 截图 command shift 4

- 截图且复制到剪贴板 Shift+Control+Command+4

- 截屏command shift 3

- 截屏且复制到剪贴板 Shift+Control+Command+3

- 打开新终端 command + T

- 回到桌面 fn + f11 或者五个手指缩放(比较反人类，算了)

- 设置触发角，我设置到了右下角，这样和windows行为一致

- 终端分屏 cmd + d 取消 cmd + shift + d

- 终端切换标签页 command + shift  + 左右箭头

- 设置 /使用习惯

- 鼠标 滚轮 去掉自然

- sudo spctl --master-disable 设置信任

- 邮件要按住ctrl

- 解压zip 7z e xx.7z 

    

    
## 其他软件

- VS
  - Ctrl+k Ctrl+f 对齐(format)
  - Ctrl+k Ctrl+c注释
  - Ctrl+k Ctrl+U 取消注释
  - F5 F9断点 F10 F11
- vscode 

  - 格式化代码 shift + alt + f 
  - 配置clang-format
- cmder

  - cmder /register all
- tex 

```tex
\tiny
\scriptsize
\footnotesize
\small
\normalsize
\large
\Large
\LARGE
\huge
\Huge
```



## git

- git统计提交行数

```bash
git log --author="name"  --since=2019–01-01 --until=2020-01-01  --pretty=tformat: --numstat | awk '{ add += $1; subs += $2; loc += $1 -  $2 } END { printf "added lines: %s, removed lines: %s, total lines:  %s\n", add, subs, loc }'
```

-  整理commit` git rebase -i HEAD~3`
-  修改上次提交`git reset HEAD^` 
-  提错分支，搬过来

```bash
git reset HEAD~ --soft
git stash
#切分支
git checkout branchxx
git stash pop
#后续add操作，不举例了
```

- 查看被修改的文件

```bash
git diff --name-only
git diff --name-only HEAD~ HEAD
git diff --name-only <commit-id1> <commit-id2>
```



- 修改提交人 git commit --amend --author="NewAuthor <NewEmail@address.com>"

```shell
  git push <远程主机名> <本地分支名>:<远程分支名>
  git pull <远程主机名> <远程分支名>:<本地分支名> 
```
  分支丢了或者head detached了或者错误覆盖了，不要慌，`git reflog`能找回来

  mac要装lfs brew install git-lfs

  设置拉取为变基 git config pull.rebase true

  git推送分支一定要设定 git config --global push.default current

  git设置保存密码 git config credential.helper store

  建议写个init脚本 https://github.com/wanghenshui/lazy-scripts/blob/master/scripts/git_config.sh

  比较两个文件夹

```bash
 diff -Nrq a b
```



列出目录几层的文件

```bash
tree -L 1
```

拆分 合并文件

```shell
split -b 10M data
cat x* > data & #加个&是因为输出可能把tmux标签污染，干脆就后台运行
```



## k8s

scg0-1-6是容器名字

拷贝

kubectl cp scg0-1-6:/data/  /disk0/temp/

进入容器

kubectl exec scg0-1-6 -it -- bash

查看容器

kubectl get pods -o wide

## docker

官网做好了图，挺好

https://www.docker.com/sites/default/files/d8/2019-09/docker-cheat-sheet.pdf



我经常用的就几个

`清理`

```bash
docker system prune
# -a 能把所有的都删掉，包括overlay里头的。太大了
```

设置存储目录，docker默认放在/var/lib/docker，比较傻逼

```bash
ln -s /data/docker_root  /var/lib/docker
```



`pull`

```shell
docker pull _linkxx_
```

`run`

```shell
docker run -it --privileged -d  _linkxx_
docker run -it --privileged -d  _linkxx_ /bin/bash #run + exec 
```

有的镜像会在run的时候做一些动作，这个镜像不能通过run+exec分开使用，会报错

> docker: Error response from daemon: OCI runtime create failed: container_linux.go:345: starting container process caused "exec: \"nginx\": executable file not found in $PATH": unknown.

如果不能使用gdb,  命令行要加上`--cap-add=SYS_PTRACE --security-opt seccomp=unconfined` 

`exec`

```shell
docker exec -it commitid/_container_name_ bash
```

`stop`

```shell
docker container stop _container_name_
```

 `commit`

```bash
docker commit _container_name_ linkxx
```

拷贝文件

```shell
docker cp /root/xx _container_name_:/root/
```

hardcore_varahamihira是docker名字

`登陆`

```bash
docker login -u username -p password registry.xx.com
```

-v指定共享目录

```bash
docker run -it -v abs_dir_shared:abs_docker_work_dir centos /bin/bash
#例子
docker run -it --privileged -v /root/nosql/DTS:/dts -d  mirrors.dockerhub.com/xx/xximage:0.0.1
```

`删除`

```bash
docker ps -a #查看所有镜像，包括退出的，深坑，不清理会一直占用着
docker rm container_id 
```



## 小工具 推荐

- 同步github gitee仓库 https://github.com/ShixiangWang/sync2gitee
- git diff工具，delta https://github.com/dandavison/delta 非常好用！为啥没有rust的时候没人做这个工具呢，是因为用c++写太麻烦吗？我要写一个！

- 图片压缩需求，网络限制，超过50k不让上传

  - jpg by `jpegtran`
  - png by  `optipng`

```bash
apt install libjpeg-progs
jpegtran -optimize image-20200402171439048.jpg
apt install optipng
optipng -o3 image-20200402172644242.png #o1 ~ o7 七个等级压缩
```





## 软件安装清单

|                | windows     | MacOS              | Ubuntu   |
| -------------- | ----------- | ------------------ | -------- |
| markdown       | typora      | typora             | typora   |
| sftp可视化工具 | winscp      | transmit           |          |
| git管理工具    | tortoisegit | sourcetree         |          |
| 终端           | putty       |                    |          |
| 画图           | drawio      | OmniGraffle/drawio |          |
| 写代码         | vscode      | vscode             | vscode   |
| 记录笔记       | 腾讯文档    | 腾讯文档           | 腾讯文档 |
| 事项清单       | 滴答清单    | 滴答清单           |          |





## Tmux 快捷键 & 速查表

本文内容适用于 Tmux 2.3 及以上的版本，但是绝大部分的特性低版本也都适用，鼠标支持、VI 模式、插件管理在低版本可能会与本文不兼容。

启动新会话：

    tmux [new -s 会话名 -n 窗口名]

恢复会话：

```bash
tmux at [-t 会话名]
tmux a #恢复上一个回话
```

列出所有会话：

    tmux ls

关闭会话：

    tmux kill-session -t 会话名

关闭所有会话：

    tmux ls | grep : | cut -d. -f1 | awk '{print substr($1, 0, length($1)-1)}' | xargs kill

在 Tmux 中，按下 Tmux 前缀 `ctrl+b`，然后：

### 会话

    :new<回车>  启动新会话
    s           列出所有会话
    $           重命名当前会话

### 窗口 (标签页)

    c  创建新窗口
    w  列出所有窗口
    n  后一个窗口
    p  前一个窗口
    f  查找窗口
    ,  重命名当前窗口
    &  关闭当前窗口 **这个真的太难记了**

### 调整窗口排序

    swap-window -s 3 -t 1  交换 3 号和 1 号窗口
    swap-window -t 1       交换当前和 1 号窗口
    move-window -t 1       移动当前窗口到 1 号

### 窗格（分割窗口）

注意这个很常用，尤其是 o 可以和命令键一起连按，十分爽快

    %  垂直分割
    "  水平分割
    o  交换窗格
    x  关闭窗格
    ⍽  左边这个符号代表空格键 - 切换布局
    q 显示每个窗格是第几个，当数字出现的时候按数字几就选中第几个窗格
    { 与上一个窗格交换位置
    } 与下一个窗格交换位置
    z 切换窗格最大化/最小化

### 同步窗格

这么做可以切换到想要的窗口，输入 Tmux 前缀和一个冒号呼出命令提示行，然后输入：

```
:setw synchronize-panes
```

你可以指定开或关，否则重复执行命令会在两者间切换。
这个选项值针对某个窗口有效，不会影响别的会话和窗口。
完事儿之后再次执行命令来关闭。[帮助](http://blog.sanctum.geek.nz/sync-tmux-panes/)

### 调整窗格尺寸

如果你不喜欢默认布局，可以重调窗格的尺寸。虽然这很容易实现，但一般不需要这么干。这几个命令用来调整窗格：

    PREFIX : resize-pane -D          当前窗格向下扩大 1 格
    PREFIX : resize-pane -U          当前窗格向上扩大 1 格
    PREFIX : resize-pane -L          当前窗格向左扩大 1 格
    PREFIX : resize-pane -R          当前窗格向右扩大 1 格
    PREFIX : resize-pane -D 20       当前窗格向下扩大 20 格
    PREFIX : resize-pane -t 2 -L 20  编号为 2 的窗格向左扩大 20 格


​    
### 文本复制模式：

按下 `PREFIX-[` 进入文本复制模式。可以使用方向键在屏幕中移动光标。默认情况下，方向键是启用的。在配置文件中启用 Vim 键盘布局来切换窗口、调整窗格大小。Tmux 也支持 Vi 模式。要是想启用 Vi 模式，只需要把下面这一行添加到 .tmux.conf 中：

    setw -g mode-keys vi

启用这条配置后，就可以使用 h、j、k、l 来移动光标了。

想要退出文本复制模式的话，按下回车键就可以了。然后按下 `PREFIX-]` 粘贴刚才复制的文本。

一次移动一格效率低下，在 Vi 模式启用的情况下，可以辅助一些别的快捷键高效工作。

例如，可以使用 w 键逐词移动，使用 b 键逐词回退。使用 f 键加上任意字符跳转到当前行第一次出现该字符的位置，使用 F 键达到相反的效果。

    vi             emacs        功能
    ^              M-m          反缩进
    Escape         C-g          清除选定内容
    Enter          M-w          复制选定内容
    j              Down         光标下移
    h              Left         光标左移
    l              Right        光标右移
    L                           光标移到尾行
    M              M-r          光标移到中间行
    H              M-R          光标移到首行
    k              Up           光标上移
    d              C-u          删除整行
    D              C-k          删除到行末
    $              C-e          移到行尾
    :              g            前往指定行
    C-d            M-Down       向下滚动半屏
    C-u            M-Up         向上滚动半屏
    C-f            Page down    下一页
    w              M-f          下一个词
    p              C-y          粘贴
    C-b            Page up      上一页
    b              M-b          上一个词
    q              Escape       退出
    C-Down or J    C-Down       向下翻
    C-Up or K      C-Up         向下翻
    n              n            继续搜索
    ?              C-r          向前搜索
    /              C-s          向后搜索
    0              C-a          移到行首
    Space          C-Space      开始选中
                   C-t          字符调序

滚屏

``` 
C-b PageUp/PageDown
q退出滚屏
```





### 杂项：

    d  退出 tmux（tmux 仍在后台运行）
    t  窗口中央显示一个数字时钟
    ?  列出所有快捷键
    :  命令提示符

### 配置选项：

    # 鼠标支持 - 设置为 on 来启用鼠标(与 2.1 之前的版本有区别，请自行查阅 man page)
    * set -g mouse on
    
    # 设置默认终端模式为 256color
    set -g default-terminal "screen-256color"
    
    # 启用活动警告
    setw -g monitor-activity on
    set -g visual-activity on
    
    # 居中窗口列表
    set -g status-justify centre
    
    # 最大化/恢复窗格
    unbind Up bind Up new-window -d -n tmp \; swap-pane -s tmp.1 \; select-window -t tmp
    unbind Down
    bind Down last-window \; swap-pane -s tmp.1 \; kill-window -t tmp

### 参考配置文件（~/.tmux.conf）：

下面这份配置是我使用 Tmux 几年来逐渐精简后的配置，请自取。

```bash
# -----------------------------------------------------------------------------
# Tmux 基本配置 - 要求 Tmux >= 2.3
# 如果不想使用插件，只需要将此节的内容写入 ~/.tmux.conf 即可
# -----------------------------------------------------------------------------

# C-b 和 VIM 冲突，修改 Prefix 组合键为 Control-Z，按键距离近
set -g prefix C-z

set -g base-index         1     # 窗口编号从 1 开始计数
set -g display-panes-time 10000 # PREFIX-Q 显示编号的驻留时长，单位 ms
set -g mouse              on    # 开启鼠标
set -g pane-base-index    1     # 窗格编号从 1 开始计数
set -g renumber-windows   on    # 关掉某个窗口后，编号重排

setw -g allow-rename      off   # 禁止活动进程修改窗口名
setw -g automatic-rename  off   # 禁止自动命名新窗口
setw -g mode-keys         vi    # 进入复制模式的时候使用 vi 键位（默认是 EMACS）

# -----------------------------------------------------------------------------
# 使用插件 - via tpm
#   1. 执行 git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
#   2. 执行 bash ~/.tmux/plugins/tpm/bin/install_plugins
# -----------------------------------------------------------------------------

setenv -g TMUX_PLUGIN_MANAGER_PATH '~/.tmux/plugins'

# 推荐的插件（请去每个插件的仓库下读一读使用教程）
set -g @plugin 'seebi/tmux-colors-solarized'
set -g @plugin 'tmux-plugins/tmux-pain-control'
set -g @plugin 'tmux-plugins/tmux-prefix-highlight'
set -g @plugin 'tmux-plugins/tmux-resurrect'
set -g @plugin 'tmux-plugins/tmux-sensible'
set -g @plugin 'tmux-plugins/tmux-yank'
set -g @plugin 'tmux-plugins/tpm'

# tmux-resurrect
set -g @resurrect-dir '~/.tmux/resurrect'

# tmux-prefix-highlight
set -g status-right '#{prefix_highlight} #H | %a %Y-%m-%d %H:%M'
set -g @prefix_highlight_show_copy_mode 'on'
set -g @prefix_highlight_copy_mode_attr 'fg=white,bg=blue'

# 初始化 TPM 插件管理器 (放在配置文件的最后)
run '~/.tmux/plugins/tpm/tpm'

# -----------------------------------------------------------------------------
# 结束
# -----------------------------------------------------------------------------

```


---



## 参考

- mount <https://www.runoob.com/linux/linux-comm-mount.html>
- tar <https://blog.csdn.net/silvervi/article/details/6325698>
- <https://my.oschina.net/huxuanhui/blog/58119>
- scp <https://linuxtools-rst.readthedocs.io/zh_CN/latest/tool/scp.html>
- putty 保存设置<https://blog.csdn.net/tianlesoftware/article/details/5831605>
- tree https://www.jianshu.com/p/f117be185c6f
  - tree在markdown中格式会乱的解决办法，用 https://stackoverflow.com/questions/19699059/representing-directory-file-structure-in-markdown-syntax
- diff https://blog.csdn.net/longxj04/article/details/7033744
- Docker 
  - https://blog.csdn.net/fandroid/article/details/46817567
  - https://www.cnblogs.com/sparkdev/p/9177283.html
- https://www.zhihu.com/question/19779256  ytzong的答案不错。我在wsl上可以用上面的工具。对于压缩图片来说他那个cssgaga贼破，没法用
- 转自这里<https://gist.github.com/ryerh/14b7c24dfd623ef8edc7>
- 这里有个详细版教程<http://louiszhai.github.io/2017/09/30/tmux/>
- 这有个git修改小操作 https://blog.csdn.net/sodaslay/article/details/72948722






---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>

```

```