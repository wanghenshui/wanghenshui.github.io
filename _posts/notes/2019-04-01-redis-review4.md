---
layout: post
title: redis 代码走读 4
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



整体交互流程

![](http://www.zbdba.com/wp-content/uploads/2018/06/img_5b2db3dd70362.png)



#### beforeSleep

- 执行一次快速的主动过期检查，检查是否有过期的key
- 当有客户端阻塞时，向所有从库发送ACK请求
- unblock 在同步复制时候被阻塞的客户端
- 尝试执行之前被阻塞客户端的命令
- 将AOF缓冲区的内容写入到AOF文件中
- 如果是集群，将会根据需要执行故障迁移、更新节点状态、保存node.conf 配置文件



#### Client发起socket连接

![](http://www.zbdba.com/wp-content/uploads/2018/06/img_5b2db3e0f07ab.png)

- 获取客户端参数，如端口、ip地址、dbnum、socket等

- 根据用户指定参数确定客户端处于哪种模式

- 进入上图中step1的cliConnect 方法，cliConnect主要包含redisConnect、redisConnectUnix方法。这两个方法分别用于TCP Socket连接以及Unix Socket连接，Unix Socket用于同一主机进程间的通信。
- 进入redisContextInit方法，redisContextInit方法用于创建一个Context结构体保存在内存中，主要用于保存客户端的一些东西，最重要的就是 write buffer和redisReader，write buffer 用于保存客户端的写入，redisReader用于保存协议解析器的一些状态。

- 进入redisContextConnectTcp 方法，开始获取IP地址和端口用于建立连接

#### server接收socket连接

![](http://www.zbdba.com/wp-content/uploads/2018/06/img_5b2db44739520.png)

- 服务器初始化建立socket监听
- 服务器初始化创建相关连接应答处理器,通过epoll_ctl注册事件
- 客户端初始化创建socket connect 请求
- 服务器接受到请求，用epoll_wait方法取出事件
- 服务器执行事件中的方法(acceptTcpHandler/acceptUnixHandler)并接受socket连接

至此客户端和服务器端的socket连接已经建立，但是此时服务器端还继续做了2件事：

- 采用createClient方法在服务器端为客户端创建一个client，因为I/O复用所以需要为每个客户端维持一个状态。这里的client也在内存中分配了一块区域，用于保存它的一些信息，如套接字描述符、默认数据库、查询缓冲区、命令参数、认证状态、回复缓冲区等。这里提醒一下DBA同学关于client-output-buffer-limit设置，设置不恰当将会引起客户端中断。
- 采用aeCreateFileEvent方法在服务器端创建一个文件读事件并且绑定readQueryFromClient方法。可以从图中得知，aeCreateFileEvent 调用aeApiAddEvent方法最终通过epoll_ctl 方法进行注册事件。



#### server接收写入

![](http://www.zbdba.com/wp-content/uploads/2018/06/img_5b2db406aa309.png)

服务器端依然在进行事件循环，在客户端发来内容的时候触发，对应的文件读取事件。这就是之前创建socket连接的时候建立的事件，该事件绑定的方法是readQueryFromClient 。

- 在readQueryFromClient方法中从服务器端套接字描述符中读取客户端的内容到服务器端初始化client的查询缓冲中，主要方法如下：

- 交给processInputBuffer处理，processInputBuffer　主要包含两个方法，processInlineBuffer和processCommand。processInlineBuffer方法用于采用redis协议解析客户端内容并生成对应的命令并传给processCommand 方法，processCommand方法则用于执行该命令

- processCommand方法会以下操作：
  - 处理是否为quit命令。
  - 对命令语法及参数会进行检查。
  - 这里如果采取认证也会检查认证信息。
  - 如果Redis为集群模式，这里将进行hash计算key所属slot并进行转向操作。
  - 如果设置最大内存，那么检查内存是否超过限制，如果超过限制会根据相应的内存策略删除符合条件的键来释放内存
  - 如果这是一个主服务器，并且这个服务器之前执行bgsave发生了错误，那么不执行命令
  - 如果min-slaves-to-write开启，如果没有足够多的从服务器将不会执行命令
    注：所以DBA在此的设置非常重要，建议不是特殊场景不要设置。
  - 如果这个服务器是一个只读从库的话，拒绝写入命令。
  - 在订阅于发布模式的上下文中，只能执行订阅和退订相关的命令
  - 当这个服务器是从库，master_link down 并且slave-serve-stale-data 为 no 只允许info 和slaveof命令
  - 如果服务器正在载入数据到数据库，那么只执行带有REDIS_CMD_LOADING标识的命令
  - lua脚本超时，只允许执行限定的操作，比如shutdown、script kill 等

- 最后进入call方法, 决定调用具体的命令

- setCommand方法，setCommand方法会调用setGenericCommand方法，该方法首先会判断该key是否已经过期，最后调用setKey方法。

  这里需要说明一点的是，通过以上的分析。redis的key过期包括主动检测以及被动监测

  ##### 主动监测

  - 在beforeSleep方法中执行key快速过期检查，检查模式为ACTIVE_EXPIRE_CYCLE_FAST。周期为每个事件执行完成时间到下一次事件循环开始
  - 在serverCron方法中执行key过期检查，这是key过期检查主要的地方，检查模式为ACTIVE_EXPIRE_CYCLE_SLOW，* serverCron方法执行周期为1秒钟执行server.hz 次，hz默认为10，所以约100ms执行一次。hz设置越大过期键删除就越精准，但是cpu使用率会越高，这里我们线上redis采用的默认值。redis主要是在这个方法里删除大部分的过期键。

  ##### 被动监测

  - 使用内存超过最大内存被迫根据相应的内存策略删除符合条件的key。
  - 在key写入之前进行被动检查，检查key是否过期，过期就进行删除。
  - 还有一种不友好的方式，就是randomkey命令，该命令随机从redis获取键，每次获取到键的时候会检查该键是否过期。
    以上主要是让运维的同学更加清楚redis的key过期删除机制。

  

- 进入setKey方法，setKey方法最终会调用dbAdd方法，其实最终就是将该键值对存入服务器端维护的一个字典中，该字典是在服务器初始化的时候创建，用于存储服务器的相关信息，其中包括各种数据类型的键值存储。完成了写入方法时候，此时服务器端会给客户端返回结果。

- 进入prepareClientToWrite方法然后通过调用_addReplyToBuffer方法将返回结果写入到outbuf中（客户端连接时创建的client）

- 通过aeCreateFileEvent方法注册文件写事件并绑定sendReplyToClient方法

#### server返回写入结果

![](http://www.zbdba.com/wp-content/uploads/2018/06/img_5b2db4b344059.png)



---

### ref

- 大部分都抄自这里 http://www.zbdba.com/2018/06/23/深入浅出-redis-client-server交互流程/

  这个作者写的不错

看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。

