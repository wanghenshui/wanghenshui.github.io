---
layout: post
categories: debug
title: gprof和oprofile使用
tags: [gprof,oprofile]
---

  

---

 

## gprof

### 编译

如果是makefile or 命令行 需要在编译选项里加上`-pg  -g` 在链接里加上 `-pg`

cmake见参考链接<sup>1</sup>

```cmake
cmake -DCMAKE_CXX_FLAGS=-pg -DCMAKE_EXE_LINKER_FLAGS=-pg -DCMAKE_SHARED_LINKER_FLAGS=-pg <SOURCE_DIR>
```

### 使用

见参考链接4

主要用法，编译生成二进制，运行一段时间，正常退出后生成`gmon.out`,然后gprof解析

```shell
gprof ./prog gmon.out -b 
```



具体的参数解析见参考链接4

###  缺陷 /注意事项

如果进程不是正常退出，程序不会生成`gmon.out`文件。详见参考链接2和3，3也有规避方法，利用信号让他正常退出即可，参考链接4内记录了一些注意事项。列在引用。值得一看







## oprofile

安装<sup>5</sup>

```shell
yum -y install oprofile
yum -y install kernel-debuginfo
```

注意debuginfo必须，不然没有vmlinux文件`/usr/lib/debug/lib/modules/3.10.0.x86_64/vmlinux`

启动需要设置

```bash
opcontrol --vmlinux=/usr/lib/debug/lib/modules/3.10.0.x86_64/vmlinux
opcontrol --start-daemon
opcontrol --start
opcontrol --dump
opreport
opreport --symbols
opannotate -s --source=binname  >opannotate.log

```

## ref

1. https://stackoverflow.com/questions/26491948/how-to-use-gprof-with-cmake

2. https://web.eecs.umich.edu/~sugih/pointers/gprof_quick.html

   > ​      Things to keep in mind:            
   >
   > - If `gmon.out` already exists,            it will be overwritten.        
   > - The program must exit normally.  Pressing control-c            or killing the process is **not** a normal exit.        
   > - Since you are trying to analyze your program in a real-world            situation, you should run the program exactly the same            way as you normally would (same inputs, command line            arguments, etc.).      

3. https://blog.csdn.net/crazyhacking/article/details/11972889

   > gprof不能产生gmom.out文件的原因：gprof只能在程序正常结束退出之后才能生成程序测评报告，原因是gprof通过在atexit()里注册了一个函数来产生结果信息，任何非正常退出都不会执行atexit()的动作，所以不会产生gmon.out文件。所以，以下情况可能不会有gmon.out文件产生：
   >      1，程序不是从main return或exit()退出，则可能不生成gmon.out。
   >      2，程序如果崩溃，可能不生成gmon.out。
   >      3，测试发现在虚拟机上运行，可能不生成gmon.out。
   >      4，程序忽略SIGPROF信号！一定不能捕获、忽略SIGPROF信号。man手册对SIGPROF的解释是：profiling  timer expired. 如果忽略这个信号，gprof的输出则是：Each sample counts as 0.01 seconds.  no time accumulated.
   >      5，如果程序运行时间非常短，则gprof可能无效。因为受到启动、初始化、退出等函数运行时间的影响。如果你的程序是一个不会退出的服务程序，那就只有修改代码来达到目的。如果不想改变程序的运行方式，可以添加一个信号处理函数解决问题（这样对代码修改最少），例如： 
   >  　static void sighandler( int sig_no ) 
   >  　{ 
   >  　exit(0); 
   >  　} 
   >  　signal( SIGUSR1, sighandler )； 
   >  这样当使用kill -USR1 pid 后，程序退出，生成gmon.out文件。

4. https://www.cnblogs.com/youxin/p/7988479.html

   > 1. g++在编译和链接两个过程，都要使用-pg选项。
   >
   > 2. 只能使用静态连接libc库，否则在初始化*.so之前就调用profile代码会引起“segmentation fault”，解决办法是编译时加上-static-libgcc或-static。
   >
   > 3. 如果不用g++而使用ld直接链接程序，要加上链接文件/lib/gcrt0.o，如ld -o myprog /lib/gcrt0.o myprog.o utils.o -lc_p。也可能是gcrt1.o
   >
   > 4. 要监控到第三方库函数的执行时间，第三方库也必须是添加 –pg 选项编译的。
   >
   > 5. gprof只能分析应用程序所消耗掉的用户时间.
   >
   > 6. 程序不能以demon方式运行。否则采集不到时间。（可采集到调用次数）
   >
   > 7. 首先使用 time 来运行程序从而判断 gprof 是否能产生有用信息是个好方法。
   >
   > 8. 如果 gprof 不适合您的剖析需要，那么还有其他一些工具可以克服 gprof 部分缺陷，包括 OProfile 和 Sysprof。
   >
   > 9. gprof对于代码大部分是用户空间的CPU密集型的程序用处明显。对于大部分时间运行在内核空间或者由于外部因素（例如操作系统的 I/O 子系统过载）而运行得非常慢的程序难以进行优化。
   >
   > 10. gprof 不支持多线程应用，多线程下只能采集主线程性能数据。原因是gprof采用ITIMER_PROF信号，在多线程内只有主线程才能响应该信号。但是有一个简单的方法可以解决这一问题：http://sam.zoy.org/writings/programming/gprof.html
   >
   > 11. gprof只能在程序正常结束退出之后才能生成报告（gmon.out）。
   >
   >     a) 原因： gprof通过在atexit()里注册了一个函数来产生结果信息，任何非正常退出都不会执行atexit()的动作，所以不会产生gmon.out文件。
   >
   >     b) 程序可从main函数中正常退出，或者通过系统调用exit()函数退出。

5. http://www.serpentine.com/blog/2006/12/17/make-linux-performance-analysis-easier-with-oprofile/

### contacts

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>


