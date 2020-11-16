---
layout: post
title: redis 代码走读 networking.c 
categories: database
tags: [redis, c]
---
  


[TOC]



6.0带来的一大改动就是多线程IO了。

## IOThreadMain

多线程IO读。提高并发。核心代码

```c
        listRewind(io_threads_list[id],&li);
        while((ln = listNext(&li))) {
            client *c = listNodeValue(ln);
            if (io_threads_op == IO_THREADS_OP_WRITE) {
                writeToClient(c,0);
            } else if (io_threads_op == IO_THREADS_OP_READ) {
                readQueryFromClient(c->conn);
            } else {
                serverPanic("io_threads_op value is unknown");
            }
        }
```

### readQueryFromClient

核心代码没什么好说的

```c
    nread = connRead(c->conn, c->querybuf+qblen, readlen);
    if (nread == -1) {
        if (connGetState(conn) == CONN_STATE_CONNECTED) {
            return;
        } else {
            serverLog(LL_VERBOSE, "Reading from client: %s",connGetLastError(c->conn));
            freeClientAsync(c);
            return;
        }
    } else if (nread == 0) {
        serverLog(LL_VERBOSE, "Client closed connection");
        freeClientAsync(c);
        return;
    } else if (c->flags & CLIENT_MASTER) {
        /* Append the query buffer to the pending (not applied) buffer
         * of the master. We'll use this buffer later in order to have a
         * copy of the string applied by the last command executed. */
        c->pending_querybuf = sdscatlen(c->pending_querybuf,
                                        c->querybuf+qblen,nread);
    }
```

这里读完，后面是`processInputBufferAndReplicate->processInputBuffer`   解析完命令等执行

从客户链接读数据，几个优化点

- 内存预分配，和redis业务相关。不讲
- postponeClientRead 如果IO线程没读完，接着读，别处理

## createClient

- 绑定handler等等
  - noblock, tcpnodelay, keepalive
- 上线文设定，buf，db，cmd，auth等等
- 对应freeclient
  - 各种释放缓存，unwatch unpubsub
  - unlinkClient 处理handler，关掉fd，如果有pending，扔掉

## prepareClientToWrite

-  如果不能写，需要把client标记成pending_write，等调度



各种accept略过

### processInputBufferAndReplicate

各种buffer处理总入口，processInputBuffer的一层封装

redis支持两种协议，redis protocol，或者inline，按行读

processInputBuffer在检查各种flag之后，根据字符串开头是不是array来判断是processMultibulkBuffer还是processInlineBuffer



Client相关的帮助函数这里省略

---


看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。

