---
layout: post
title: (译)关于Linux IO 持久性的讨论，以及page cache
categories: [database, linux, translation]
tags: [fsync,O_DIRECT, fdatasync, O_SYNC, sync_file_range, page cache]

---



> 这篇文章很有干货，整理一下 https://www.evanjones.ca/durability-filesystem.html



| flag\action         | page cache    | buffer cache  | inode cache      | directory cache  |
| :------------------ | :------------ | :------------ | :--------------- | :--------------- |
| O_DIRECT            | write bypass  | write bypass  | write & no flush | write & no flush |
| O_DSYNC/fdatasync() | write & flush | write & flush | write & no flush | write & no flush |
| O_SYNC/fsync()      | write & flush | write & flush | write & flush    | write & flush    |
| sync_file_range()   | write & flush | write & flush | no write         | no write         |

flag和函数的区别是：flag表示每次io操作都会执行，函数是在执行函数的时候触发；

O_Direct优劣势：

- 优势：直接绕过page cache/buffer cache，节省操作系统内存；使用O_DIRECT方式提示操作系统尽量使用DMA方式来进行存储设备操作，节省CPU；
- 劣势：字节对齐写（logic block size）；无法进行IO合并；读写绕过cache，小数据读写效率低；

关于函数的问题

- fsync遇到过bug ，fsync可能报错EIO，系统没把脏页刷盘，但数据库层认为刷完了，导致这段数据丢了 https://wiki.postgresql.org/wiki/Fsync_Errors
- sync_file_range这里有个[原理](http://yoshinorimatsunobu.blogspot.com/2014/03/how-syncfilerange-really-works.html) ,不刷元数据！rocksdb会用这个来刷盘，看这个[注释](https://github.com/facebook/rocksdb/blob/d1c510baecc1aef758f91f786c4fbee3bc847a63/include/rocksdb/options.h#L868)，额外再用fdatasync。除非你知道你在做什么，否则不要用这个api



作者总结

- fdatasync or fsync after a write (prefer fdatasync).
- write on a file descriptor opened with O_DSYNC or O_SYNC (prefer O_DSYNC).

- pwritev2 with the RWF_DSYNC or RWF_SYNC flag (prefer RWF_DSYNC).

结论，推荐使用`O_DSYNC/fdatasync()`



一些关于随机(写)的性能观察

- 覆盖写比追加写快(~2-100% faster) 追加写要原子修改元数据。
- 和system call相比，用flag更省，性能更好(~5% faster)





### page cache

系统对page cache的管理，在一些情况下可能有所欠缺，我们可以通过内核提供的`posix_fadvise`予以干预。

```
#include <fcntl.h>

int posix_fadvise(int fd, off_t offset, off_t len, int advice);
```

posix_fadvise是linux上对文件进行预取的系统调用，其中第四个参数int advice为预取的方式，主要有以下几种：

POSIX_FADV_NORMAL           无特别建议                    重置预读大小为默认值
POSIX_FADV_SEQUENTIAL        将要进行顺序操作               设预读大小为默认值的2 倍
POSIX_FADV_RANDOM           将要进行随机操作              将预读大小清零（禁止预读）
POSIX_FADV_NOREUSE           指定的数据将只访问一次       （暂无动作）
POSIX_FADV_WILLNEED          指定的数据即将被访问          立即预读数据到page cache
POSIX_FADV_DONTNEED         指定的数据近期不会被访问      立即从page cache 中丢弃数据



/proc/sys/vm/dirty_writeback_centisecs：flush检查的周期。单位为0.01秒，默认值500，即5秒。每次检查都会按照以下三个参数控制的逻辑来处理。

/proc/sys/vm/dirty_expire_centisecs：如果page cache中的页被标记为dirty的时间超过了这个值，就会被直接刷到磁盘。单位为0.01秒。默认值3000，即半分钟。

/proc/sys/vm/dirty_background_ratio：如果dirty page的总大小占空闲内存量的比例超过了该值，就会在后台调度flusher线程异步写磁盘，不会阻塞当前的write()操作。默认值为10%。

/proc/sys/vm/dirty_ratio：如果dirty page的总大小占总内存量的比例超过了该值，就会阻塞所有进程的write()操作，并且强制每个进程将自己的文件写入磁盘。默认值为20%。



---

### ref

- linux IOhttps://www.scylladb.com/2017/10/05/io-access-methods-scylla/ 这几个图画的还行。不过原理也比较简单。不多说
- page cache https://www.jianshu.com/p/92f33aa0ff52


---



