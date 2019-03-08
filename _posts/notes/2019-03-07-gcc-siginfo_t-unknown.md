---
layout: post
category : c++
title: gcc编译提示siginfo_t找不到
tags : [c,gcc]
---
{% include JB/setup %}



gcc编译提示siginfo_t找不到



在redis基础上开发，redis 编译条件是-std=c99

我加了个新文件，包含了一个外部头文件threadpool.h，和server.h

在server.h中有原型

```void sigsegvHandler(int sig, siginfo_t *info, void *secret);```

 编译提示找不到，但其他文件没有这个问题，

我将这两个头文件交换顺序，编过了。判断是threadpool.c的问题，然后进去看，发现有定义

```#define _POSIX_C_SOURCE 200809L```

这引入了posix依赖环境，导致找不到？

解决方案，交换头文件顺序，或者改成-std=gnu99


参考
[1]: https://stackoverflow.com/questions/48332332/what-does-define-posix-source-mean
[2]: https://stackoverflow.com/questions/22912674/unknown-type-name-siginfo-t-with-clang-using-posix-c-source-2-why