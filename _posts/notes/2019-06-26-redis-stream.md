---
layout: post
category: database
title: Redis Stream相关总结
tags: [rocksdb]
---

{% include JB/setup %}

---

#### Why

学习了解

整体架构

![](https://mmbiz.qpic.cn/mmbiz_png/8XkvNnTiapOOhqYNVd3YMNhq94CAEpCuibKK08cZrw89qyh0fmcgDw7gR9pwp1CvDPibiaHxuPbnibv7Pg8BK5hhlvw/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1&wx_co=1.png)



- 每个消息都有一个唯一的ID和对应的内容
- 每个Stream都有唯一的名称，Redis key

- 每个Stream都可以挂多个消费组，每个消费组会有个游标`last_delivered_id`在Stream数组之上往前移动，表示当前消费组已经消费到哪条消息了。每个消费组都有一个Stream内唯一的名称，消费组不会自动创建，它需要单独的指令`xgroup create`进行创建，需要指定从Stream的某个消息ID开始消费，这个ID用来初始化`last_delivered_id`变量。

- 每个消费组(Consumer Group)的状态都是独立的，相互不受影响。也就是说同一份Stream内部的消息会被每个消费组都消费到。

- 同一个消费组(Consumer Group)可以挂接多个消费者(Consumer)，这些消费者之间是竞争关系，任意一个消费者读取了消息都会使游标`last_delivered_id`往前移动。每个消费者者有一个组内唯一名称。

- 消费者(Consumer)内部会有个状态变量`pending_ids`，它记录了当前已经被客户端读取的消息，但是还没有ack。如果客户端没有ack，这个变量里面的消息ID会越来越多，一旦某个消息被ack，它就开始减少。这个pending_ids变量在Redis官方被称之为`PEL`，也就是`Pending Entries List`，这是一个很核心的数据结构，它用来确保客户端至少消费了消息一次，而不会在网络传输的中途丢失了没处理。

简单说

stream key 每条消息存储并生成streamid-seq，然后id和消费组挂钩，消费组内部有游标和消费者，消费者和消费组挂钩。是串行消费游标信息。



如果把stream编码成kv需要怎么做？

首先，stream key本身维护一组信息，需要知道最后一个streamid，需要知道stream个数，本身就算是一个元数据

其次，stream key需要和子字段，streamid编码，方便区分是谁的key的streamID下的字段，



### ref

1. https://mp.weixin.qq.com/s?__biz=MzAwMDU1MTE1OQ==&mid=2653549949&idx=1&sn=7f6c4cf8642478574718ed0f8cf61409&chksm=813a64e5b64dedf357cef4e2894e33a75e3ae51575a4e3211c1da23008ef79173962e9a83c73&mpshare=1&scene=1&srcid=0717FcpVc16q9rNa0yfF78FU#rd
2. http://chenzhenianqing.com/articles/1622.html
3. http://chenzhenianqing.com/articles/1649.html


### contact

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。