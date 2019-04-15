---
layout: post
category : database
title: rocksdb 初探 4：put/write
tags : [rocksdb,c++]
---
{% include JB/setup %}

参考文章<sup>1</sup> 非常详尽，图非常棒。十分好奇咋画的

![](https://upload-images.jianshu.io/upload_images/12472641-7b1b409ad2c15ad0.jpg)

主要流程<sup>1</sup>中写的也很详细。我重新复述一下，加深印象

`WriteBatch, WriteBatchInternal, WriteBatch::handler, WriteAheadLog`

db调用的put等操作，最终调用的都是WriteBatch内部的put，然后调用WriteBatchInternal内部的动作，WriteBatch是一组操作，一起写要比一条条写要高效，并且每一组WriteBatch拥有同一个lsn。

由于WriteBatch是一组动作，putputdelget等等，每一条WriteBatch内部就是个string字节流，第一个字节记录动作类型。内部进行遍历iterate时，调用Handler实现的相关接口，判断是什么动作，最后由memtable执行，putCF等。

另外一个疑问，如何具体区分每一个动作和相关的kv呢，Slice。也就是string_view，每个kv都会有size，这个size提前编码到type的后面，相当于 type+(cfid)+ size+ sv+size+ sv 作为一个单元。del没有第二个size+sv

所以WriteBatch就是 lsn-count-header+{type size sv}..., 多条WriteBatch字节流组合，就是Write Ahead Log

WriteBatch::Handler是个接口类，memtable最终插入数据，memtableinserter要继承handler。

WriteBatchInternal内部工具类。当然是WriteBatch的友元类啦。可以操作WriteBatch的字节流string

编解码是一套很麻烦的动作，rocksdb util/coding.cc/h有很多小函数。可以看看抄一抄。由于string_view是不拥有值的，view嘛，所以复杂的编码动作都需要搞回到string在搞回来。直接搞到string上就append了。如果sv和sv连接，免不了string做交换，有机会找找解决办法。

`Writer, WriteGroup, WriteBatch`， 并发写

每个Writer是持有WriteBatch的。





`dbformat`

internalkey  setinternalkey parsedinternalkey userkey 

简单来说 userkey就是internalkey 因为一个key会把lsn和类型编码进去(PackSequenceAndType)，去掉这八个字节就是userkey，在rocksdb代码中，有些地方就直接是硬编码，-8了，有些地方转换回来还要+8， Jesus

```c++
Slice MemTableRep::UserKey(const char* key) const {
  Slice slice = GetLengthPrefixedSlice(key);
  return Slice(slice.data(), slice.size() - 8);
}
```

其实应该有个更小的封装，因为-8可能变（对于想要用rocksdb来修改的人来说）

---

### reference

1. <https://www.jianshu.com/p/daa18eebf6e1>
2. 这个concat像是我要找的东西<http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1228r1.html>
3. compile-time 直接concat sv不可能。<https://stackoverflow.com/questions/47556948/concatenate-string-views-in-constexpr>



看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。

