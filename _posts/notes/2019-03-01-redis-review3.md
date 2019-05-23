---
layout: post
title: redis 代码走读 server.c 3
category: database
tags: [redis, c]
---
{% include JB/setup %}
[TOC]

### why

redisbook 讲的太详细了，huangz还给了个阅读建议。我重写主要是落实一下脑海中的概念，便于后续翻阅。redis代码走读的东西太多了，我的方向偏向于改动源码需要了解的东西。

---

### dictType

 ```c
typedef struct dictType {
    unsigned int (*hashFunction)(const void *key);
    void *(*keyDup)(void *privdata, const void *key);
    void *(*valDup)(void *privdata, const void *obj);
    int (*keyCompare)(void *privdata, const void *key1, const void *key2);
    void (*keyDestructor)(void *privdata, void *key);
    void (*valDestructor)(void *privdata, void *obj);
} dictType;
 ```

基本上看字段名字就明白啥意思了。就是指针。实现多态用的。

redis所有对外呈现的数据类型，都是dict对象来保存。这个dictType就是用来实例化各个类型对象，具体的类型在通过这个类型对象来初始化。举例，redisdb有个expire，这个dict是用来存有设定过期时间的key，    

```c
  expire= dictCreate(&expireDictType,NULL);

```

这样就绑定了类型，内部构造析构都用同一个函数指针就行了。

要让dict发挥多态的效果，就要增加一个类型字段，也就是dictType，通过绑定指针来实现，这就相当于元数据。或者说c++中的构造语义，编译器帮你搞or你自己手动搞，手动搞就要自己设计字段搞定

```c

typedef struct dict {
	dictType *type;
	void *privdata;
	dictht ht[2];
	int rehashidx; /* rehashing not in progress if rehashidx == -1 */
	int iterators; /* number of iterators currently running */
} dict;

```

说到这，不如考虑一下hashtable的实现。



### reference

- redis设计与实现试读内容，基本上一大半。还有源码注释做的不错。我基本上照着注释写的。<http://redisbook.com/>
- huangz给的建议，如何阅读redis代码<http://blog.huangz.me/diary/2014/how-to-read-redis-source-code.html>

看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。





