---
layout: post
category : database
title: rocksdb perfix extrator
tags : [rocksdb,c++]
---
{% include JB/setup %}

这里实际上是涉及到一个prefix bloom filter的，参考链接2给出了很详细的介绍和使用说明，我就直接抄过来了

# Prefix Seek

Prefix seek是RocksDB的一种模式，主要影响Iterator的行为。
 在这种模式下，RocksDB的Iterator并不保证所有key是有序的，而只保证具有相同前缀的key是有序的。这样可以保证具有相同特征的key（例如具有相同前缀的key）尽量地被聚合在一起。

## 使用方法

prefix seek模式的使用如下，

```
int main() {
  DB* db;
  Options options;
  options.IncreaseParallelism();
  options.OptimizeLevelStyleCompaction();
  options.create_if_missing = true;
  options.prefix_extractor.reset(rocksdb::NewFixedPrefixTransform(3));

  Status s = DB::Open(options, kDBPath, &db);
  assert(s.ok());

  s = db->Put(WriteOptions(), "key1", "value1");
  assert(s.ok());
  s = db->Put(WriteOptions(), "key2", "value2");
  assert(s.ok());
  s = db->Put(WriteOptions(), "key3", "value3");
  assert(s.ok());
  s = db->Put(WriteOptions(), "key4", "value4");
  assert(s.ok());
  s = db->Put(WriteOptions(), "otherPrefix1", "otherValue1");
  assert(s.ok());
  s = db->Put(WriteOptions(), "abc", "abcvalue1");
  assert(s.ok());

  auto iter = db->NewIterator(ReadOptions());
  for (iter->Seek("key2"); iter->Valid(); iter->Next())
  {
    std::cout << iter->key().ToString() << ": " << iter->value().ToString() << std::endl;
  }

  delete db;
  return 0;
}
```

输出如下

```
key2: value2
key3: value3
key4: value4
otherPrefix1: otherValue1
```

从上面的输出，我们可以看到prefix seek模式下iterator的几个特性

1. 首先seek(targetKey)方法会将iterator定位到具有相同前缀的区间，并且大于或等于targetKey的位置.
2. Next()方法是会跨prefix的，就像例子中，当以"key"为前缀的key都遍历完之后，跨到了下一个prefix "oth"上继续遍历，直到遍历完所有的key，Valid()方法返回false.
3. 在遍历的时候，如果只想遍历相同前缀的key，需要在每一次Next之后，判断一次key是前缀是否符合预期.

```
  auto iter = db->NewIterator(ReadOptions());
  Slice prefix = options.prefix_extractor->Transform("key0");
  for (iter->Seek("key0"); iter->Valid() && iter->key().starts_with(prefix); iter->Next())
  {
    std::cout << iter->key().ToString() << ": " << iter->value().ToString() << std::endl;
  }
```

输出如下：

```
key1: value1
key2: value2
key3: value3
key4: value4
```

## Prefix Seek相关的一些优化

为了更快地定位指定prefix的key，或者排除不存在的key，RocksDB做了一些优化，包括：

1. prefix bloom  filter for block based table
2. prefix bloom for memtable
3. memtable底层使用hash skiplist
4. 使用plain table

一个典型的优化设置见下例

```
Options options;

// Enable prefix bloom for mem tables
options.prefix_extractor.reset(NewFixedPrefixTransform(3));
options.memtable_prefix_bloom_bits = 100000000;
options.memtable_prefix_bloom_probes = 6;

// Enable prefix bloom for SST files
BlockBasedTableOptions table_options;
table_options.filter_policy.reset(NewBloomFilterPolicy(10, true));
options.table_factory.reset(NewBlockBasedTableFactory(table_options));

DB* db;
Status s = DB::Open(options, "/tmp/rocksdb",  &db);

......

auto iter = db->NewIterator(ReadOptions());
iter->Seek("foobar"); // Seek inside prefix "foo"
```

# Prefix Seek相关类图



![img](https:////upload-images.jianshu.io/upload_images/3262084-a58b2a3c7879225a.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1000/format/webp)

prefix seek相关的iterator类图

说是Prefix Seek相关的类图，其实就是rocksdb的Iterator类图。这里列出了几个主要的类。

- InternalIterator
   接口类，定义了iterator的接口，包括Seek、Next、Prev等接口。
- MergingIterator
   返回给用户的实际Iterator类型，之所以叫"Merging"，是因为它持有memtable和sst文件的iterater，对外提供了统一的iterator接口。
- MemTableIterator
   用于遍历memtable的iterator。主要的分析对象。
- TwoLevelIterator
   用于遍历sst文件的iterator。

# Prefix Seek工作流程

## Iterator简单分析

通过Iterator的相关接口，来逐层分析，持有PrefixTransform对象的option.prefix_extractor选项是如何工作的。
 DB的Iterator由三部分组成

1. 当前memtable的iterator
2. 所有不可修改的memtable的iterator
3. 所有level上的sst文件的iterator(TwoLevelIterator)

这些iterator统一由MergeIterator来管理。MergeIterator持有一个vector成员，上面三类iterator都会添加到该成员中。

```
autovector<IteratorWrapper, kNumIterReserve> children_;
```

autovector是对std::vector的完全模板特化版本

```
class autovector : public std::vector<T> {
  using std::vector<T>::vector;
};
```

autovector主要针对在栈上分配的数组，保存数量较少的item这种使用场景做了优化。
 IteratorWrapper是对InternalIterator*类型的对象的一个简单封装，主要cache了iter)->Valid()和iter_->key()的结果，提供更好的局部性访问性能。其他接口和InternalIterator一样，只是转发请求给iter_。

DB的Iterator添加当前使用的memtable的iterator的代码如下

```
InternalIterator* DBImpl::NewInternalIterator(
    const ReadOptions& read_options, ColumnFamilyData* cfd,
    SuperVersion* super_version, Arena* arena,
    RangeDelAggregator* range_del_agg) {
  ...
    merge_iter_builder.AddIterator(
      super_version->mem->NewIterator(read_options, arena));
  ...
```

arena是为所有iterator已经分配的一块内存。
 向MergeIterator添加Iterator的实现：

1. 先将要添加的iter加入到vector成员children_中
2. 如果iter是有效的iterator，将该iter添加到一个最小堆成员中。

```
  virtual void AddIterator(InternalIterator* iter) {
    assert(direction_ == kForward);
    children_.emplace_back(iter);
    if (pinned_iters_mgr_) {
      iter->SetPinnedItersMgr(pinned_iters_mgr_);
    }
    auto new_wrapper = children_.back();
    if (new_wrapper.Valid()) {
      minHeap_.push(&new_wrapper);
      current_ = CurrentForward();
    }
  }
```

这里的最小堆minHeap_用于维护上面所有合法iterator的访问顺序，指向key较小的iter，越靠近堆顶，这样，当连续多次调用Next接口时，都在同一个child iterator上，可以直接通过堆顶的iterator来获取Next，而不用遍历所有children。
 如果堆顶iterator的下一个元素的不是合法的，则将该iterator从堆中pop出去，调整堆之后，拿到新的堆顶元素。
 DB的Iterator MergingIterator的Next接口主要实现如下

```
  virtual void Next() override {
    assert(Valid());
    ...
    // For the heap modifications below to be correct, current_ must be the
    // current top of the heap.
    assert(current_ == CurrentForward());

    // as the current points to the current record. move the iterator forward.
    current_->Next();
    if (current_->Valid()) {
      // current is still valid after the Next() call above.  Call
      // replace_top() to restore the heap property.  When the same child
      // iterator yields a sequence of keys, this is cheap.
      minHeap_.replace_top(current_);
    } else {
      // current stopped being valid, remove it from the heap.
      minHeap_.pop();
    }
    current_ = CurrentForward();
```

## Seek接口的实现

Seek一个target的实现，通过遍历每个child iterator，然后将合法的iterator插入到最小堆minHeap中，将current_成员指向minHeap的堆顶。

```
  virtual void Seek(const Slice& target) override {
    ClearHeaps();
    for (auto& child : children_) {
      {
        PERF_TIMER_GUARD(seek_child_seek_time);
        child.Seek(target);
      }
      PERF_COUNTER_ADD(seek_child_seek_count, 1);

      if (child.Valid()) {
        PERF_TIMER_GUARD(seek_min_heap_time);
        minHeap_.push(&child);
      }
    }
    direction_ = kForward;
    {
      PERF_TIMER_GUARD(seek_min_heap_time);
      current_ = CurrentForward();
    }
  }
```

以当前可写的memtable的iterator为例，当用户调用Seek接口时，如何定位到memtable中的目标key。

## MemTableIterator的Seek

在memtable中持有一个MemTableRep::Iterator*类型的iterator指针iter_，iter_指向的对象的实际类型由MemTableRep的子类中分别定义。以SkipListRep为例，
 在MemTableIterator的构造函数中，当设置了prefix_seek模式时，调用MemTableRep的GetDynamicPrefixIterator接口来获取具体的iterator对象。

```
  MemTableIterator(const MemTable& mem, const ReadOptions& read_options,
                   Arena* arena, bool use_range_del_table = false)
      : bloom_(nullptr),
        prefix_extractor_(mem.prefix_extractor_),
        comparator_(mem.comparator_),
        valid_(false),
        arena_mode_(arena != nullptr),
        value_pinned_(!mem.GetMemTableOptions()->inplace_update_support) {
    if (use_range_del_table) {
      iter_ = mem.range_del_table_->GetIterator(arena);
    } else if (prefix_extractor_ != nullptr && !read_options.total_order_seek) {
      bloom_ = mem.prefix_bloom_.get();
      iter_ = mem.table_->GetDynamicPrefixIterator(arena);
    } else {
      iter_ = mem.table_->GetIterator(arena);
    }
  }
```

对于SkipList来说，`GetDynamicPrefixIterator`也是调用GetIterator，只有对HashLinkListRep和HashSkipListRe，这个方法才有不同的实现。

```
  virtual MemTableRep::Iterator* GetIterator(Arena* arena = nullptr) override {
    if (lookahead_ > 0) {
      void *mem =
        arena ? arena->AllocateAligned(sizeof(SkipListRep::LookaheadIterator))
              : operator new(sizeof(SkipListRep::LookaheadIterator));
      return new (mem) SkipListRep::LookaheadIterator(*this);
    } else {
      void *mem =
        arena ? arena->AllocateAligned(sizeof(SkipListRep::Iterator))
              : operator new(sizeof(SkipListRep::Iterator));
      return new (mem) SkipListRep::Iterator(&skip_list_);
    }
  }
```

这样就创建了MemTableIterator。
 当调用到MemTableIterator的`Seek`接口时：

- 首先在DynamicBloom成员bloom_中查找目标key的prefix是否**可能**在当前的memtable中存在。
- 如果不存在，则一定不存在，可以直接返回。
- 如果可能存在，则调用MemTableRep的iterator进行Seek。

```
  virtual void Seek(const Slice& k) override {
    PERF_TIMER_GUARD(seek_on_memtable_time);
    PERF_COUNTER_ADD(seek_on_memtable_count, 1);
    if (bloom_ != nullptr) {
      if (!bloom_->MayContain(
              prefix_extractor_->Transform(ExtractUserKey(k)))) {
        PERF_COUNTER_ADD(bloom_memtable_miss_count, 1);
        valid_ = false;
        return;
      } else {
        PERF_COUNTER_ADD(bloom_memtable_hit_count, 1);
      }
    }
    iter_->Seek(k, nullptr);
    valid_ = iter_->Valid();
  }
```

当调用MemTableRep的iterator进行Seek时，则是通过调用实际使用的数据结构的Seek接口，找到第一个大于或等于key的目标。

```
    // Advance to the first entry with a key >= target
    virtual void Seek(const Slice& user_key, const char* memtable_key)
        override {
      if (memtable_key != nullptr) {
        iter_.Seek(memtable_key);
      } else {
        iter_.Seek(EncodeKey(&tmp_, user_key));
      }
    }
```

第一个分支主要用于确定在memtable中的key，做update类的操作.

## MemTable Prefix Bloom的构建

prefix bloom作为memtable的一个成员，当向memtable插入一个key value时，会截取key的prefix，插入到prefix bloom中。

```
void MemTable::Add(SequenceNumber s, ValueType type,
                   const Slice& key, /* user key */
                   const Slice& value, bool allow_concurrent,
                   MemTablePostProcessInfo* post_process_info) {
  ...
  if (!allow_concurrent) {
    ...
    if (prefix_bloom_) {
      assert(prefix_extractor_);
      prefix_bloom_->Add(prefix_extractor_->Transform(key));
    }
    ...
  else {
    ...
    if (prefix_bloom_) {
      assert(prefix_extractor_);
      prefix_bloom_->AddConcurrently(prefix_extractor_->Transform(key));
    }
    ...
  }
  ...
}
```

关于bloom filter的原理和实现可以参考前文。[传送门](https://www.jianshu.com/p/b534dc48bb59)
 因为再BlockBasedTable中，对bloom filter的用法不同，所以使用了不同实现的bloom filter。基本原理是相同的。





### reference

1.  一个应用，作者是tikv的 https://www.jianshu.com/p/26214e45fd4a
2.  源码分析 https://www.jianshu.com/p/9848a376d41d

### contact

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。

