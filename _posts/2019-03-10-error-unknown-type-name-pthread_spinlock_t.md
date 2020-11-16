---
layout: post
categories : c++
title: gcc提示未知类型pthread_spinlock_t
tags : [c,gcc]
---
  

>只要遇到的问题多，天天都能水博客

之前遇到一个问题 [link](https://wanghenshui.github.io/2019/03/07/gcc-siginfo_t-unknown)，解决方案是改成-std=gnu99，这是前提

这次我用到了`pthread_spinlock`，实现个简单的队列，我在redis的makefile中改了，但是编译还是提示

```
 error: unknown type name 'pthread_spinlock_t'
  pthread_spinlock_t head_lock;
```

经过我走读makefile，发现 `src/.make-settings`文件中有缓存之前的编译配置，导致make还是按照 -std=c99 编译的，手动改成-std=gnu99就好了。



### 注意

- 这降低了可移植性。（macos貌似没有spinlock？）
- 需要了解redis makefile流程。可能是大家都觉得简单，没见有人讲这个。



## 参考

- gcc使用spinlock https://stackoverflow.com/questions/13661145/using-spinlocks-with-gcc
- features.h https://github.com/bminor/glibc/blob/0a1f1e78fbdfaf2c01e9c2368023b2533e7136cf/include/features.h#L154-L175

- __USE_XOPEN2K 定义，实际上和GNU相关。https://stackoverflow.com/questions/33076175/why-is-struct-addrinfo-defined-only-if-use-xopen2k-is-defined
- 解释__USE_XOPEN2K https://stackoverflow.com/questions/13879302/purpose-of-use-xopen2k8-and-how-to-set-it
- `__GNU_SOURCE`  和`___USE_GNU`区别https://blog.csdn.net/robertsong2004/article/details/52861078
  - 简单说，有`_GNU_SOURCE`就有`__USE_GNU`  ,一个内部用，一个外部用，指定编译选项gnu也会启用
  - g++默认编译带GNU，gcc不带
- 介绍`__GNU_SOURCE`  和`__USE_GNU`https://stackoverflow.com/questions/7296963/gnu-source-and-use-gnu
- 一个-std=c99报错，rwlock也不是标准的，需要pthread.h，也得用gnu https://stackoverflow.com/questions/15673492/gcc-compile-fails-with-pthread-and-option-std-c99
- spinlock manpage ，注意`_POSIX_C_SOURCE >= 200112L` http://man7.org/linux/man-pages/man3/pthread_spin_lock.3.html

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>