---
layout: post
category: database
title: rocksdb IO error No Space Left
tags: [c++,rocksdb]
---

  

---

遇到两个问题

##### rocksdb一直在compaction，但是compaction有写放大需要额外的空间，然后没空间了，结果就一直阻塞写了

这个解决办法只能是重启，并且需要预估硬盘的使用情况避免这种问题的发生。



##### rocksdb报错IO error No Space Left，但是du查看有空间

这个是发生过compaction已经收回了空间，但是之前有的bg_error一直存在没有清掉。这个是rocksdb故意设计成这样的，上层应用需要决定是否处理这种场景，选择重启还是自己实现高可用



rocksdb的issue在[这里](https://github.com/facebook/rocksdb/issues/919)

crdb的设计讨论在[这里](https://github.com/cockroachdb/cockroach/issues/8473)

ardb的解决办法，[重启]( https://github.com/yinqiwen/ardb/issues/310)



crdb的讨论我没有仔细看，有时间看完补充一下

----

### ref

1. https://github.com/facebook/rocksdb/issues/919
2. crdb的设计讨论https://github.com/cockroachdb/cockroach/issues/8473
3. ardb的解决办法， https://github.com/yinqiwen/ardb/issues/310

### contact

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。