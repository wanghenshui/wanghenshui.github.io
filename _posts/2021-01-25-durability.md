---
layout: post
title: (翻译)关于Linux API 持久性的讨论
categories: [database, linux, translation]
tags: [fsync]

---

<img src="https://wanghenshui.github.io/assets/quadraddnt.png" alt="" width="80%">

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



# 

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

---

### ref


---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>

