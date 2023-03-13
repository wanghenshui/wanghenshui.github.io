---
layout: post
categories: database
title: valgrind跑一个rocksdb应用出现错误，以及背后的write hint
tags: [rocksdb, fs, linux, valgrind]
---

  

---

valgrind 3.10 日志是这样的

```
valgrind: m_syswrap/syswrap-linux.c:5255 (vgSysWrap_linux_sys_fcntl_before): Assertion 'Unimplemented functionality' failed.
valgrind: valgrind

host stacktrace:
==26531==    at 0x3805DC16: ??? (in /usr/lib64/valgrind/memcheck-amd64-linux)
==26531==    by 0x3805DD24: ??? (in /usr/lib64/valgrind/memcheck-amd64-linux)
==26531==    by 0x3805DEA6: ??? (in /usr/lib64/valgrind/memcheck-amd64-linux)
==26531==    by 0x380D53A0: ??? (in /usr/lib64/valgrind/memcheck-amd64-linux)
==26531==    by 0x380B0834: ??? (in /usr/lib64/valgrind/memcheck-amd64-linux)
==26531==    by 0x380AD242: ??? (in /usr/lib64/valgrind/memcheck-amd64-linux)
==26531==    by 0x380AE6F6: ??? (in /usr/lib64/valgrind/memcheck-amd64-linux)
==26531==    by 0x380BDD7C: ??? (in /usr/lib64/valgrind/memcheck-amd64-linux)

sched status:
  running_tid=1

Thread 1: status = VgTs_Runnable
==26531==    at 0x60903A4: fcntl (in /usr/lib64/libpthread-2.17.so)
==26531==    by 0x53571F6: rocksdb::PosixWritableFile::SetWriteLifeTimeHint(rocksdb::Env::WriteLifeTimeHint) (io_posix.cc:897)
...
```

找到rocksdb代码，接口是这样的

`env/io_posix.cc`

```c++
void PosixWritableFile::SetWriteLifeTimeHint(Env::WriteLifeTimeHint hint) {
#ifdef OS_LINUX
// Suppress Valgrind "Unimplemented functionality" error.
#ifndef ROCKSDB_VALGRIND_RUN
  if (hint == write_hint_) {
    return;
  }
  if (fcntl(fd_, F_SET_RW_HINT, &hint) == 0) {
    write_hint_ = hint;
  }
#else
  (void)hint;
#endif // ROCKSDB_VALGRIND_RUN
#else
  (void)hint;
#endif // OS_LINUX
}
```

...结果显然了，不支持`fcntl`  `F_SET_RW_HINT`选项。

注意：

- 如果需要跑valgrind，编译的rocksdb需要定义`ROCKSDB_VALGRIND_RUN`
- 如果有必要，最好也定义PORTABLE，默认是march=native可能会遇到指令集不支持





特意搜了一下，这个参数是这样定义的

`env/io_posix.cc`

```c++
#if defined(OS_LINUX) && !defined(F_SET_RW_HINT)
#define F_LINUX_SPECIFIC_BASE 1024
#define F_SET_RW_HINT (F_LINUX_SPECIFIC_BASE + 12)
#endif
```

在linux中是这样的

https://github.com/torvalds/linux/blob/dd5001e21a991b731d659857cd07acc7a13e6789/include/uapi/linux/fcntl.h#L53

```
/*
 * Set/Get write life time hints. {GET,SET}_RW_HINT operate on the
 * underlying inode, while {GET,SET}_FILE_RW_HINT operate only on
 * the specific file.
 */
#define F_GET_RW_HINT		(F_LINUX_SPECIFIC_BASE + 11)
#define F_SET_RW_HINT		(F_LINUX_SPECIFIC_BASE + 12)
#define F_GET_FILE_RW_HINT	(F_LINUX_SPECIFIC_BASE + 13)
#define F_SET_FILE_RW_HINT	(F_LINUX_SPECIFIC_BASE + 14)
```

另外这里也移植了一个<https://github.com/riscv/riscv-gnu-toolchain/blob/master/linux-headers/include/linux/fcntl.h>

### write life time hints

搜到了这个实现的patch <https://patchwork.kernel.org/patch/9794403/>

和这个介绍，linux 4.13引入的<https://www.phoronix.com/scan.php?page=news_item&px=Linux-4.13-Write-Hints>

简单说，这是为NVMe加上的功能，暗示写入数据是ssd的话，调度就会把数据尽可能靠近，这样方便后续回收

patchset讨论里还特意说到了rocksdb。。。https://lwn.net/Articles/726477/

降低写放大十分可观

>A new iteration of this patchset, previously known as write streams.
>As before, this patchset aims at enabling applications split up
>writes into separate streams, based on the perceived life time
>of the data written. This is useful for a variety of reasons:
>
>- For NVMe, this feature is ratified and released with the NVMe 1.3
>  spec. Devices implementing Directives can expose multiple streams.
>  Separating data written into streams based on life time can
>  drastically reduce the write amplification. This helps device
>  endurance, and increases performance. Testing just performed
>  internally at Facebook with these patches showed up to a 25% reduction
>  in NAND writes in a RocksDB setup.
>
>- Software caching solutions can make more intelligent decisions
>  on how and where to place data.

这背后又有一个NVMe特性，Stream ID，https://lwn.net/Articles/717755/



一个用法，见pg的patch以及讨论  <https://www.postgresql.org/message-id/CA%2Bq6zcX_iz9ekV7MyO6xGH1LHHhiutmHY34n1VHNN3dLf_4C4Q%40mail.gmail.com>

这里还没有更深入讨论。只是罗列了资料。下班了，就到这里

### ref

- valgrind代码 <https://sourceware.org/git/?p=valgrind.git;a=blob_plain;f=coregrind/m_syswrap/syswrap-linux.c;hb=refs/heads/master>

  简单搂了一眼没看到hint选项。

  ```c++
  PRE(sys_fcntl)
  ```

- F_SET_RW_HINT https://github.com/torvalds/linux/blob/dd5001e21a991b731d659857cd07acc7a13e6789/include/uapi/linux/fcntl.h#L53

- patch <https://patchwork.kernel.org/patch/9794403/>

- write hint 介绍<https://www.phoronix.com/scan.php?page=news_item&px=Linux-4.13-Write-Hints>

- 支持write life time的邮件patch 讨论 <https://lwn.net/Articles/726477/>，也提到了下面的stream id

- Stream ID<https://lwn.net/Articles/717755/>

- fcntl 文档 <http://man7.org/linux/man-pages/man2/fcntl.2.html>

### contacts

