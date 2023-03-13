---
layout: post
title: googletest segmentation fault
categories: language
tags: [c++, googletest, debug,gdb,dmesg]
---




> 自己水平有限，总结下来记录自己菜比挣扎过的时光



最近研究googletest 其实研究很久了，只是琢磨如何用到工作中的模块上。

我将工程代码和自己写的空的测试代码放在一块编译，Makefile中

```
CPPFLAGS        := -m32 -O1 -g -Wall -fPIC -fpack-struct=1 
```

然后就遇到崩溃的问题

```
[==========] Running 1 test from 1 test case.
[----------] Global test environment set-up.
[----------] 1 test from Test
[ RUN      ] Test.Test
Segmentation fault
```

gdb 跟进去，提示

```
(gdb) r
Starting program: /mnt/hgfs/share_work/Br_R6.5_r2676/TestCode/RM_TestCode/tes                                                                                 t/run_test.exe
[Thread debugging using libthread_db enabled]
[==========] Running 1 test from 1 test case.
[----------] Global test environment set-up.
[----------] 1 test from Test
[ RUN      ] Test.Test

Program received signal SIGSEGV, Segmentation fault.
testing::internal::scoped_ptr<std::string>::reset (this=0x812d5e8)
    at /usr/include/gtest/internal/gtest-port.h:1172
1172            delete ptr_;
(gdb) q
```

库肯定不可能有错误。问题到这里根据我的经验就卡住了，实际上在string上。

我用dmesg查看

```
[52938.831139] run_test.exe[6391]: segfault at f36968 ip 080cf52d sp bff36920 error 4 in run_test.exe[80480                                                   00+ab000]
```

然后addr2line

```
addr2line -e run_test.exe 080cf52d -                                                   f
_ZNKSs6_M_repEv
/usr/include/c++/4.4/bits/basic_string.h:281
```

basic_string 281是这样的

```
      _Rep*
      _M_rep() const
      { return &((reinterpret_cast<_Rep*> (_M_data()))[-1]); }
```

然后我就搜到了这个帖子

[关于std::string出现在_M_dispose发生SIGABRT错误的问题 - superarhow的专栏 - CSDN博客](http://blog.csdn.net/superarhow/article/details/30063331)



肯定是内存对齐导致的，我搜了代码没有#pragma pack

结果发现makefile中有这个选项。。。-fpack-struct=1 就相当于#pragma pack(1)

去掉问题就解决了。

感谢前人们的铺路

---

