---
layout: post
title: malloc是不可重入的
categories: language
tags: [malloc]
---

线程安全不等于可重入

<!-- more -->

[SO](https://stackoverflow.com/questions/3941271/why-are-malloc-and-printf-said-as-non-reentrant)这个答案解释的很清楚



> The `malloc` function could either be thread-safe or thread-unsafe.  Both are not reentrant:
>
> 1. Malloc operates on a global heap, and it's possible that two different invocations of `malloc` that happen at the same time, return the same memory block. (The 2nd  malloc call should happen before an address of the chunk is fetched, but the chunk is not marked as unavailable).  This violates the  postcondition of `malloc`, so this implementation would not be re-entrant.
>
> 2. To prevent this effect, a thread-safe implementation of `malloc` would use lock-based synchronization.  However, if malloc is called from signal handler, the following situation may happen: 
>
>    ```c
>    malloc();            //initial call
>      lock(memory_lock); //acquire lock inside malloc implementation
>    signal_handler();    //interrupt and process signal
>    malloc();            //call malloc() inside signal handler
>      lock(memory_lock); //try to acquire lock in malloc implementation
>      // DEADLOCK!  We wait for release of memory_lock, but 
>      // it won't be released because the original malloc call is interrupted
>    ```
>
>    This situation won't happen when `malloc` is simply called from different threads.  Indeed, the reentrancy concept goes beyond  thread-safety and also requires functions to work properly **even if one of its invocation never terminates**. That's basically the reasoning why any function with locks would be not re-entrant.



[procps-ng](https://gitlab.com/procps-ng) 是探测/proc 的一系列软件，像top，ps之类的

top 代码在这里 https://gitlab.com/procps-ng/procps/-/blob/0bf15c004db6a3342703a3c420a5692e376c457d/top/top.c 



这个patch就是典型的malloc重入bug https://gitlab.com/procps-ng/procps/-/commit/0bf15c004db6a3342703a3c420a5692e376c457d 

和上面描述一毛一样

```c
       fputs(str, stderr);
       exit(EXIT_FAILURE);
    }
-   if (Batch) fputs("\n", stdout);
+   if (Batch) {
+      write(fileno(stdout), "\n", sizeof("\n"));
    }
    exit(EXIT_SUCCESS);
 } // end: bye_bye
```

bye_bye函数是信号触发的，Batch这个分支场景，进入bye_bye前是会发生malloc的，之后进入bye_bye，走到fputs，内部有malloc，发生重入，解决办法就是直接用系统调用write

### 参考

- https://murphypei.github.io/blog/2019/07/thread-safe-reentrant-function

这里有个总结

> - 函数体内使用了静态的数据结构
> - 通过 malloc 和 free 来申请和释放内存，因为 malloc 是通过全局链表来管理堆的
> - 调用了标准 I/O 库，因为库里存在大多数都是以不可重入的方式使用全局变量或者是静态变量




---



