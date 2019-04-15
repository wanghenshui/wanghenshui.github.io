---
layout: post
category : database
title: rocksdb 初探 5 db_iter
tags : [rocksdb,c++]
---
{% include JB/setup %}

参考链接<sup>1</sup> 说的十分详尽了。我还是总结一下，帮助记忆

---

iteration

1. ArenaWrappedDBIter是暴露给用户的Iterator，它包含DBIter，DBIter则包含InternalIterator，InternalIterator顾名思义，是内部定义，MergeIterator、TwoLevelIterator、BlockIter、MemTableIter、LevelFileNumIterator等都是继承自InternalIterator
2. 图中绿色实体框对应的是各个Iterator，按包含顺序颜色由深至浅
3. 图中虚线框对应的是创建各个Iterator的方法
4. 图中蓝色框对应的则是创建过程中需要的类的对象及它的方法

![](http://kernelmaker.github.io/public/images/2017-04-09/1.png)



---

### reference

1. <http://kernelmaker.github.io/Rocksdb_Iterator>



看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。

