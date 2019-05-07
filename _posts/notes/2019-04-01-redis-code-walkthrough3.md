---
layout: post
title: redis 代码走读 server.c 2
category: database
tags: [redis, c]
---
{% include JB/setup %}
### redis 代码走读 3 server.c

[TOC]

继续看initServer

####     adjustOpenFilesLimit()

调整打开文件大小，如果小，就设置成1024

#### serverCron

一个定时任务，每秒执行server.hz次

里面有run_with_period宏，相当于除，降低次数

#### clientsCron

- 遍历client链表删除超时的客户端
  - 大于BIG_ARG （宏，32k）以及querybuf_peak（远大于，代码写的是二倍）
  - 大于1k且不活跃 idletime>2
- 遍历client链表缩小查询缓冲区大小
  - 如果缓冲越来越大客户端消费不过来redis就oom了

#### freeClient(redisClient *c)

- 判断是不是主备要求断开，这里会有同步问题
- querybuf 
- blockey watchkey pubsubkey
- delete event， close event fd
- reply buf
- 从client链表删掉，从unblocked_clients 链表删掉
- 再次清理主备
- 释放字段内存，释放自己

---


看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。

