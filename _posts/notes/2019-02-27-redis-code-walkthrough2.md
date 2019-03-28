---
layout: post
title: redis 代码走读 server.c 2
category: database
tags: [redis, c]
---
{% include JB/setup %}
# redis 代码走读 server.c 2

[TOC]

看redis 版本代码变动，感觉和看rocksdb一样累。到处都是小优化。需要掌握全局。~~好像所有项目都这样？~~
异步代码看着还是累。不熟。

##  _redisPanic

```c
void _serverPanic(const char *file, int line, const char *msg, ...) {
...log...
#ifdef HAVE_BACKTRACE
    serverLog(LL_WARNING,"(forcing SIGSEGV in order to print the stack trace)");
#endif
    serverLog(LL_WARNING,"------------------------------------------------");
    *((char*)-1) = 'x';
}
```

指针访问-1  故意段错误，[这里也有讨论](https://stackoverflow.com/questions/20844863/what-does-char-1-x-code-mean)

## overcommit_memory

```c
int linuxOvercommitMemoryValue(void) {
    FILE *fp = fopen("/proc/sys/vm/overcommit_memory","r");
    char buf[64];
if (!fp) return -1;
if (fgets(buf,64,fp) == NULL) {
    fclose(fp);
    return -1;
}
fclose(fp);

return atoi(buf);
}
```

关于这个参数，见<http://linuxperf.com/?p=102>

> 如果/proc/sys/vm/overcommit_memory被设置为0，并且配置了rdb重新功能，如果内存不足，则frok的时候会失败，如果在往redis中塞数据， 会失败，打印 MISCONF Redis is configured to save RDB snapshots, but is currently not able to persist on disk 如果/proc/sys/vm/overcommit_memory被设置为1，则不管内存够不够都会fork失败，这样会引发OOM，最终redis实例会被杀掉。





##  anetNonBlock(char *err, int fd ）

```c
if ((flags = fcntl(fd, F_GETFL)) == -1) 
if (fcntl(fd, F_SETFL, flags | O_NONBLOCK) == -1)
就是这个
::fcntl(sock, F_SETFL, O_NONBLOCK | O_RDWR);
```

## ustime

```c
/* Return the UNIX time in microseconds */
long long ustime(void) {
    struct timeval tv;
    long long ust;
    gettimeofday(&tv, NULL);
    ust = ((long long)tv.tv_sec)*1000000;
    ust += tv.tv_usec;
    return ust;
}

/* Return the UNIX time in milliseconds */
mstime_t mstime(void) {
    return ustime()/1000;
}
```

写了个c++里类似的

```c++
#include <chrono>
auto [] (){ return std::chrono::duration_cast<std::chrono::microseconds>(
                   std::chrono::system_clock::now().time_since_epoch()).count();
};
```

## redisObject


  ```c
typedef struct redisObject {
    unsigned type:4;
    unsigned encoding:4;
    unsigned lru:LRU_BITS; /* LRU time (relative to global lru_clock) or
                            * LFU data (least significant 8 bits frequency
                            * and most significant 16 bits access time). */
    int refcount;
    void *ptr;
} robj;
  ```

一个对象就24字节了。注意type和encoding，就是redis数据结构和实际内部编码，构造也是先type对象->encoding对象初始化，析构也是判断type，判断encoding，然后删encoding对象删type对象。c++就是把这个流程隐藏了。



## client

这个结构就比较复杂了。思考：阻塞命令是怎么阻塞的，为什么影响不到服务端 ->转移到客户端头上了。

阻塞的pop命令，每个客户端都会存个字典，blocking_keys 记录阻塞的key- >客户端链表

- 如果有push变化，就会遍历一遍找到，然后发送命令，解除阻塞，将这个key放到ready_keys链表中。

- 如果是连续的命令，怎么办 - >记录当前客户端连接的状态，阻塞就不执行了
- 如果有事务，那不能阻塞事务，所以直接回复空。事务中用阻塞命令是错误的。

还有很多命令的细节放到命令里面讲比较合适。



client还有很多数据结构 看上去很轻巧，复杂的很。



## 异步事件框架

ae.c，networking这几个文件把epoll 和select kqueue封了一起。用法没差别。epoll用的是LT模式。

- 从客户端读到大数据怎么处理 ->收到事件触发，注册在creatClient -> readQueryFromClient中  如果读出错，EAGAIN就结束，下次EPOLLIN继续处理
- 写大数据到缓冲写不完怎么处理 -> 事件注册在addReply -> prepareClientToWrite sendReplyToClient 中, 循环写缓冲区，如果写出错 EAGAIN就结束，下次EPOLLOUT继续处理，正式结束后删掉写事件（or异常，踢掉客户端流程中会删所有事件）

仔细顺了一遍ET，LT，感觉这个用法有点像ET，没有修改事件, 仔细发现在add/delevent里。。

```c
static int aeApiAddEvent(aeEventLoop *eventLoop, int fd, int mask) {
    aeApiState *state = eventLoop->apidata;
    struct epoll_event ee = {0}; /* avoid valgrind warning */
    /* If the fd was already monitored for some event, we need a MOD
     * operation. Otherwise we need an ADD operation. */
    int op = eventLoop->events[fd].mask == AE_NONE ?
            EPOLL_CTL_ADD : EPOLL_CTL_MOD;

    ee.events = 0;
    mask |= eventLoop->events[fd].mask; /* Merge old events */
    if (mask & AE_READABLE) ee.events |= EPOLLIN;
    if (mask & AE_WRITABLE) ee.events |= EPOLLOUT;
    ee.data.fd = fd;
    if (epoll_ctl(state->epfd,op,fd,&ee) == -1) return -1;
    return 0;
}

static void aeApiDelEvent(aeEventLoop *eventLoop, int fd, int delmask) {
    aeApiState *state = eventLoop->apidata;
    struct epoll_event ee = {0}; /* avoid valgrind warning */
    int mask = eventLoop->events[fd].mask & (~delmask);

    ee.events = 0;
    if (mask & AE_READABLE) ee.events |= EPOLLIN;
    if (mask & AE_WRITABLE) ee.events |= EPOLLOUT;
    ee.data.fd = fd;
    if (mask != AE_NONE) {
        epoll_ctl(state->epfd,EPOLL_CTL_MOD,fd,&ee);
    } else {
        /* Note, Kernel < 2.6.9 requires a non null event pointer even for
         * EPOLL_CTL_DEL. */
        epoll_ctl(state->epfd,EPOLL_CTL_DEL,fd,&ee);
    }
}
```

操作客户端的fd

epoll  LT ET 主要区别在于LT针对EPOLLOUT事件的处理，

首先EPOLLOUT, 缓冲区可写 调用异步写 →  写满了,EAGAIN→继续等EPOLLOUT事件，这时需要在addevent中修改，加上(MOD)EPOLLOUT事件（可写）

如果没写满，结束了，修改fd,去掉EPOLLOUT事件 ,这时在delevent中删掉(OR 屏蔽掉，MOD)，不然这个EPOLLOUT事件会一直触发，就得加屏蔽措施

在比如写一个echo server，或者长连接传文件 ，针对EPOLLOUT事件，写不完，就得手动epoll_ctl MOD一下，暂时屏蔽掉EPOLLOUT事件，然后如果又有了EPOLLOUT事件需要添加就在家上。针对fd得改来改去。如果是ET就没有这么麻烦设定好就行了，要么使劲读到缓冲区读完， or使劲写到缓冲区写满，事件处理完毕，等下一次事件就行。

ET LT是电子信息 信号处理的概念，触发是电平（一直触发）还是毛刺（触发一次），如果用ET，当前框架会不会丢消息？

~~看了一天epoll 脑袋快炸了~~ 

`注意新的版本，回复事件全部放在beforeSleep中注册了，上面的分析是3.0版本。`

## clientsCron

定时任务，处理客户端相关

- 踢掉超时客户端
- 处理内存？

## freememIfNeeded

|策略|说明|
|--|--|
|volatile-lru|从已设置过期时间的数据集（server.db[i].expires）中挑选最近最少使用的数据淘汰|
|volatile-ttl|从已设置过期时间的数据集（server.db[i].expires）中挑选将要过期的数据淘汰|
|volatile-random|从已设置过期时间的数据集（server.db[i].expires）中任意选择数据淘汰|
|allkeys-lru|从数据集（server.db[i].dict）中挑选最近最少使用的数据淘汰|
|allkeys-random|从数据集（server.db[i].dict）中任意选择数据淘汰|
|no-enviction（驱逐）|禁止驱逐数据|

server.maxmemory这个字段用来判断，这个字段有没有推荐设定值？



## call

所有的命令都走它，通过它来执行具体的命令。processCommand ....-> call -> c->cmd->proc(c)

## 命令表

 把redis源码注释抄过来了

| 标识 | 意义                                                         |
| ---- | ------------------------------------------------------------ |
| w    | write command (may modify the key space).                    |
| r    | read command  (will never modify the key space).             |
| m    | may increase memory usage once called. Don't allow if out of memory. |
| a    | admin command, like SAVE or SHUTDOWN.                        |
| p    | Pub/Sub related command.                                     |
| f    | force replication of this command, regardless of server.dirty. |
| s    | command **not allowed** in scripts.                          |
| R    | R: random command.  SPOP                                     |
| l    | Allow command while **loading** the database.                |
| t    | Allow command while a slave has **stale** data but is not allowed to server this data. Normally no command is accepted in this condition but just a few. |
| S    | Sort command output array if called from script, so that the output is deterministic. |
| M    | Do not automatically propagate the command on MONITOR.       |
| k    | Perform an implicit ASKING for this command, so the command will be accepted in cluster mode if the slot is marked as 'importing'. |
| F    | Fast command: O(1) or O(log(N)) command that should never delay its execution as long as the kernel scheduler is giving us time. Note that commands that may trigger a DEL as a side effect (like SET) are not fast commands. |




看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。

