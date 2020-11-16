---
layout: post
categories: database
title: rocksdb 初探 5：iterator
tags : [rocksdb,c++]
---
  



参考链接<sup>1</sup> 说的十分详尽了。我还是总结一下，帮助记忆

---

iteration

1. ArenaWrappedDBIter是暴露给用户的Iterator，它包含DBIter，DBIter则包含InternalIterator，InternalIterator顾名思义，是内部定义，MergeIterator、TwoLevelIterator、BlockIter、MemTableIter、LevelFileNumIterator等都是继承自InternalIterator
2. 图中绿色实体框对应的是各个Iterator，按包含顺序颜色由深至浅
3. 图中虚线框对应的是创建各个Iterator的方法
4. 图中蓝色框对应的则是创建过程中需要的类的对象及它的方法

![](http://kernelmaker.github.io/public/images/2017-04-09/1.png)



---

注意到第二步，构造DBIter, 其中的Seek有`IsVisiable`的判断，也就是实现快照的关键。

每层iterator都会实现iterator头文件中定义好的接口，Seek Next等等，迭代过程中也是逐层调用

另外要注意Seek的语义（SeekForPrev正好相反），不同于Get，查不到不一定返回无效， 会返回所查找的元素的下一个存在于db中的数据

```c++
// Position at the first key in the source that at or past target.
// The iterator is Valid() after this call iff the source contains
// an entry that comes at or past target.
// All Seek*() methods clear any error status() that the iterator had prior to
// the call; after the seek, status() indicates only the error (if any) that
// happened during the seek, not any past errors.
virtual void Seek(const Slice& target) = 0;
```



`iterator 牵连的引用以及生命周期, reseek`

iterator迭代是依赖快照的，所以创建的迭代器是无法获得新加入的数据的。

iterator不释放 ->versionSet析构->cf set析构-> cfd析构，内部会持有引用。debug模式会assert挂掉

根据上面的结论， 如果版本skip设定比较小，是很容易发生reseek的，设定在Options中

```c++
// An iteration->Next() sequentially skips over keys with the same
// user-key unless this option is set. This number specifies the number
// of keys (with the same userkey) that will be sequentially
// skipped before a reseek is issued.
//
// Default: 8
//
// Dynamically changeable through SetOptions() API
uint64_t max_sequential_skip_in_iterations = 8;
```



比如这个没有flush的场景, option中设定skip=3

```c++
Put("a","v1");
Put("a","v2");
Put("b","v1");
Put("a","v3");
iter = NewIterator(RO, CF);
iter->SeekToFirst();//iter指向v4 ，这是最新的数据
int num_reseek = options.statistics->getTickerCount(NUMBER_OF_RESEEKS_IN_ITERATION);
iter->Next();// Seek本身是逆序搜最新的，按理说应该访问下一个，b在a后面，但是没击中，步进大于3，所以就需要重新Seek
assert(options.statistics->getTickerCount(NUMBER_OF_RESEEKS_IN_ITERATION)==num_reseek+1);
```

由于没有合并key a的所有版本都在memtable中，所以就需要找最旧的a，重新seek，下一个就是b

反过来，如果插入了新的b，先找b后找a，也会出现同样的场景

```c++
Put("b","v2");
// 现在是 a3 a2 a1 b2 b1 假设这个iter不指定snapshot
iter = NewIterator(RO, CF);
iter->SeekToLast();// iter指向b v2
iter->Prev();//正常来说是a，但是版本不确定，迭代大于3，就得reseek
```

`iterate_lower_bound, iterate_upper_bound`

ReadOption中带有的这两个选项，限定iterator的有效与否

```c++
  // `iterate_lower_bound` defines the smallest key at which the backward
  // iterator can return an entry. Once the bound is passed, Valid() will be
  // false. `iterate_lower_bound` is inclusive ie the bound value is a valid
  // entry.
  //
  // If prefix_extractor is not null, the Seek target and `iterate_lower_bound`
  // need to have the same prefix. This is because ordering is not guaranteed
  // outside of prefix domain.
  //
  // Default: nullptr
  const Slice* iterate_lower_bound;

  // "iterate_upper_bound" defines the extent upto which the forward iterator
  // can returns entries. Once the bound is reached, Valid() will be false.
  // "iterate_upper_bound" is exclusive ie the bound value is
  // not a valid entry.  If iterator_extractor is not null, the Seek target
  // and iterator_upper_bound need to have the same prefix.
  // This is because ordering is not guaranteed outside of prefix domain.
  //
  // Default: nullptr
  const Slice* iterate_upper_bound;
```

如果有key  a b y z，设定upper_bound x，seek c，这个场景下iter是invalid的，过了x也没找到c，那就是无效的，同理lower_bound

`tombstones, Next`

看SeekAfterHittingManyInternalKeys这个测试用例

### reference

1. <http://kernelmaker.github.io/Rocksdb_Iterator>
2. skiplist <http://www.pandademo.com/2016/03/memtable-and-skiplist-leveldb-source-dissect-3/>
3. skiplist <https://zhuanlan.zhihu.com/p/29277585>
4. memtable <https://www.jianshu.com/p/9e385682ed4e>
5. 看图了解rocksdb <https://yq.aliyun.com/articles/669316?utm_content=m_1000024335>
6. memtable写入 <http://mysql.taobao.org/monthly/2018/08/08/>
7. hashskiplist <http://mysql.taobao.org/monthly/2017/05/08/>
8. <https://github.com/Terark/terarkdb/wiki/%E9%87%8D%E6%96%B0%E5%AE%9E%E7%8E%B0-RocksDB-MemTable>
9. <http://arganzheng.life/arangodb-index-notes.html>



看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。

