---
layout: post
title: 一个奇怪的崩溃堆栈
categories: [language]
tags: [c++, popen, jemalloc]
---



<!-- more -->



```gdb
#0  0x00007f227d13870f in raise () from /lib64/libc.so.6
#1  0x00007f227d122b25 in abort () from /lib64/libc.so.6
#2  0x00007f227d1229f9 in __assert_fail_base.cold.0 () from /lib64/libc.so.6
#3  0x00007f227d130cc6 in __assert_fail () from /lib64/libc.so.6
#4  0x00007f227f29caa6 in __pthread_mutex_lock_full () from /lib64/libpthread.so.0
#5  0x00007f227d9907a9 in je_malloc_mutex_lock_slow () from /lib64/libjemalloc.so.2
#6  0x00007f227d990948 in je_malloc_mutex_prefork () from /lib64/libjemalloc.so.2
#7  0x00007f227d95605c in je_arena_prefork0 () from /lib64/libjemalloc.so.2
#8  0x00007f227d945715 in je_jemalloc_prefork () from /lib64/libjemalloc.so.2
#9  0x00007f227d20aa50 in __run_fork_handlers () from /lib64/libc.so.6
#10 0x00007f227d1c92b7 in fork () from /lib64/libc.so.6
#11 0x00007f227d173984 in _IO_proc_open@@GLIBC_2.2.5 () from /lib64/libc.so.6
#12 0x00007f227d173c2c in popen@@GLIBC_2.2.5 () from /lib64/libc.so.6
```



这个popen是调用一个hdfs客户端来下载文件

jemalloc用的 jemalloc-devel-5.2.1-2.el8.x86_64

非常奇怪的错误

我搜了一圈，搜到了个这个 http://jemalloc.net/mailman/jemalloc-discuss/2013-October/000657.html

死锁

感觉有点像，popen调用了什么东西出发了内部的锁，内部然后莫名其妙的挂了。

暂时做一个记录，很难复现

jemalloc马上就升级新的了https://github.com/jemalloc/jemalloc/issues/2213

到时候再说吧

---

