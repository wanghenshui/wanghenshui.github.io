---
layout: post
title: asan常见的抓错报告
categories: [tools, c,]
tags: [debug, c, gcc]
---
  

---

 

---
asan常见的 抓错报告 编译带上 -fsanitize=address 链接带上 -lasan



### global-buffer-overflow  memcmp的长度可能越界

R: AddressSanitizer: global-buffer-overflow on address 0x000000a8f8ff at pc 0x7ff6eafde870 bp 0x7ffc75471220 sp 0x7ffc754709d0
READ of size 49 at 0x000000a8f8ff thread T0
    #0 0x7ff6eafde86f in __interceptor_memcmp ../../../../gcc-5.4.0/libsanitizer/asan/asan_interceptors.cc:333

注意memcmp的第三个参数，取两个字符串中最小的长度



相关概念 OOB memory access

### heap-buffer-overflow  strlen访问内存越界

  assert(n == strlen(val)); AddressSanitizer: heap-buffer-overflow 

可能字符串没有分配'\0'的空间，用strlen会导致堆空间越界

### AddressSanitizer: attempting to call malloc_usable_size

这个rocksdb的报错。 搜了一圈，二进制是jemalloc编的，和asan和rocksdb 有冲突产生的报错。临时禁止掉

```bash
ASAN_OPTIONS=check_malloc_usable_size=0
```

重编二进制，不带jemalloc，好使了

```bash
AddressSanitizer: attempting to call malloc_usable_size() for pointer which is not owned: 0x7f121aed6000
    #0 0x7f121f506990 in __interceptor_malloc_usable_size ../../../../gcc-5.4.0/libsanitizer/asan/asan_malloc_linux.cc:104
    #1 0x8c7929 in rocksdb::Arena::AllocateNewBlock(unsigned long) util/arena.cc:221
    #2 0x8c79c4 in rocksdb::Arena::AllocateFallback(unsigned long, bool) util/arena.cc:114
    #3 0x8df67a in rocksdb::LogBuffer::AddLogToBuffer(unsigned long, char const*, __va_list_tag*) util/log_buffer.cc:24
    #4 0x8df8c8 in rocksdb::LogToBuffer(rocksdb::LogBuffer*, char const*, ...) util/log_buffer.cc:88
    #5 0x749300 in rocksdb::DBImpl::FlushMemTableToOutputFile(rocksdb::ColumnFamilyData*, rocksdb::MutableCFOptions const&, bool*, rocksdb::JobContext*, rocksdb::SuperVersionContext*, rocksdb::LogBuffer*) db/db_impl_compaction_flush.cc:183
    #6 0x74c1f4 in rocksdb::DBImpl::FlushMemTablesToOutputFiles(rocksdb::autovector<rocksdb::DBImpl::BGFlushArg, 8ul> const&, bool*, rocksdb::JobContext*, rocksdb::LogBuffer*) db/db_impl_compaction_flush.cc:229
    #7 0x74d3b0 in rocksdb::DBImpl::BackgroundFlush(bool*, rocksdb::JobContext*, rocksdb::LogBuffer*, rocksdb::FlushReason*) db/db_impl_compaction_flush.cc:2025
    #8 0x74da4f in rocksdb::DBImpl::BackgroundCallFlush() db/db_impl_compaction_flush.cc:2059
    #9 0x8e8a27 in std::function<void ()>::operator()() const /usr/local/include/c++/5.4.0/functional:2267
    #10 0x8e8a27 in rocksdb::ThreadPoolImpl::Impl::BGThread(unsigned long) util/threadpool_imp.cc:265
    #11 0x8e8c0e in rocksdb::ThreadPoolImpl::Impl::BGThreadWrapper(void*) util/threadpool_imp.cc:303
    #12 0x7f121e1fb8ef in execute_native_thread_routine ../../../../../gcc-5.4.0/libstdc++-v3/src/c++11/thread.cc:84
    #13 0x7f121dd19dc4 in start_thread (/lib64/libpthread.so.0+0x7dc4)
    #14 0x7f121da477fc in __clone (/lib64/libc.so.6+0xf67fc)

AddressSanitizer can not describe address in more detail (wild memory access suspected).
SUMMARY: AddressSanitizer: bad-malloc_usable_size ../../../../gcc-5.4.0/libsanitizer/asan/asan_malloc_linux.cc:104 __interceptor_malloc_usable_size
Thread T2 created by T0 here:
    #0 0x7f121f4a80d4 in __interceptor_pthread_create ../../../../gcc-5.4.0/libsanitizer/asan/asan_interceptors.cc:179
    #1 0x7f121e1fba32 in __gthread_create /home/vdb/gcc-5.4-build/x86_64-unknown-linux-gnu/libstdc++-v3/include/x86_64-unknown-linux-gnu/bits/gthr-default.h:662
    #2 0x7f121e1fba32 in std::thread::_M_start_thread(std::shared_ptr<std::thread::_Impl_base>, void (*)()) ../../../../../gcc-5.4.0/libstdc++-v3/src/c++11/thread.cc:149

```



### ref

- 这里有建议不要使用memcmp的讨论，还是怕越界 https://github.com/cesanta/mongoose/issues/564
- https://github.com/pcrain/slippc/issues/16 一个global buffer overflow case



---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
![微信转账](https://wanghenshui.github.io/assets/wepay.png)
</details>