---
layout: post
category : database
title: rocksdb 初探 3：get
tags : [rocksdb,c++]
---
  

参考链接<sup>1, 2</sup>写的非常到位。本文基本上是复述这两个链接，梳理自己的理解

`DBImpl::GetImpl`

- db, cfd, sv之间的关系： column family data，cfd就相当于db键空间，cfd 有super version sv，这个就是version的上层抽象，version的集合
- snapshot，lsn 。 get指定快照多是在事务中。快照实现事务。当然建立过快照，指定快照来取也可以。和git拉分支类似。增加引用计数。snapshot实际上就是lsn的一层薄封装，内部是链表。lsn，版本号。可以理解成两者等同
  - 如果不指定，就会算出一个，通常是versionSet中有的最后一个发布的lsn。versionSet会维护这个lsn
  - rocksdb内部key是有lsn编码的，会有查找构造类lookupkey，需要snapshot参数。

如果read_option没有指定跳过memtable，那就会从memtable开始遍历

`sv->mem->Get`

- bloomFilter
- Saver
- MemTableRep，`table_->Get` memtable抽象。后面调用具体的实现。
- 会有对Merge的判断。Merge途中就跳过。

`sv->imm->Get`

- imm实际上是MemTableListVersion 是一系列version的list。不可插入，add就是插入链表。数据本身不变了。
- 调用GetFromList最后内部遍历还是调用mem->Get，lsn做边界条件，同上，会有对Merge的判断

`sv->current->Get`

- 通过Version中记录的信息遍历Level中的所有SST文件，利用SST文件记录的边界最大，最小key- `smallest_key`和`largest_key`来判断查找的key是否有可能存在
- 如果在该Level中可能存在，调用TableReader的接口来查找SST文件
  - 首先通过SST文件中的Filter来初判key是否存在
  - 如果存在key存在，进入Data Block中查找
  - 在Data Block利用Block的迭代器`BlockIter`利用二分查找`BinarySeek`或者前缀查找`PrefixSeek`
- 如果查找成功则返回，如果该Level不存在查找的Key，继续利用Version中的信息进行下一个Level的查找，直到最大的一个Level

table_cache_->Get(k)

```
#4   ./db_test() [0x6ae065] rocksdb::MemTable::KeyComparator::operator()(char const*, rocksdb::Slice const&) const      ??:?
#5   ./db_test() [0x7525f2] rocksdb::InlineSkipList<rocksdb::MemTableRep::KeyComparator const&>::FindGreaterOrEqual(char const*) const  ??:?
#6   ./db_test() [0x7516d5] rocksdb::(anonymous namespace)::SkipListRep::Get(rocksdb::LookupKey const&, void*, bool (*)(void*, char const*))skiplistrep.cc:?
#7   ./db_test() [0x6af31f] rocksdb::MemTable::Get(rocksdb::LookupKey const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >*, rocksdb::Status*, rocksdb::MergeContext*, rocksdb::RangeDelAggregator*, unsigned long*, rocksdb::ReadOptions const&, rocksb::ReadCallback*, bool*)        ??:?
#8   ./db_test() [0x62f49b] rocksdb::DBImpl::GetImpl(rocksdb::ReadOptions const&, rocksdb::ColumnFamilyHandle*, rocksdb::Slice const&, rocksdb::PinnableSlice*, bool*, rocksdb::ReadCallback*, bool*)        ??:?
#9   ./db_test() [0x62fc07] rocksdb::DBImpl::Get(rocksdb::ReadOptions const&, rocksdb::ColumnFamilyHandle*, rocksdb::Slice const&, rocksdb::PinnableSlice*)  ??:?
#10  ./db_test() [0x59c9cd] rocksdb::DB::Get(rocksdb::ReadOptions const&, rocksdb::ColumnFamilyHandle*, rocksdb::Slice const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >*)     ??:?
#11  ./db_test() [0x58fc9d] rocksdb::DB::Get(rocksdb::ReadOptions const&, rocksdb::Slice const&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >*)   ??:?
#12  ./db_test() [0x51c3a3] rocksdb::DBTest_MockEnvWithTimestamp_Test::TestBody()       ??:?
#13  ./db_test() [0x9401c8] void testing::internal::HandleExceptionsInMethodIfSupported<testing::Test, void>(testing::Test*, void (testing::Test::*)(), char const*) ??:?
#14  ./db_test() [0x93799c] testing::Test::Run() [clone .part.476]      gtest-all.cc:?
#15  ./db_test() [0x937b6d] testing::TestInfo::Run() [clone .part.477]  gtest-all.cc:?
#16  ./db_test() [0x937ce5] testing::TestCase::Run() [clone .part.478]  gtest-all.cc:?
#17  ./db_test() [0x93812d] testing::internal::UnitTestImpl::RunAllTests()      ??:?
#18  ./db_test() [0x940678] bool testing::internal::HandleExceptionsInMethodIfSupported<testing::internal::UnitTestImpl, bool>(testing::internal::UnitTestImpl*, bool (testing::internal::UnitTestImpl::*)(), char const*)   ??:?
#19  ./db_test() [0x93843f] testing::UnitTest::Run()    ??:?
#20  ./db_test() [0x40d9bd] main        ??:?
#21  /lib64/libc.so.6(__libc_start_main+0xf5) [0x7f3f6c423bb5] ??       ??:0
#22  ./db_test() [0x513761] _start      ??:?

```



`OptimizeForPointLookup`

```c++
ColumnFamilyOptions* ColumnFamilyOptions::OptimizeForPointLookup(
    uint64_t block_cache_size_mb) {
  prefix_extractor.reset(NewNoopTransform());
  BlockBasedTableOptions block_based_options;
  block_based_options.index_type = BlockBasedTableOptions::kHashSearch;
  block_based_options.filter_policy.reset(NewBloomFilterPolicy(10));
  block_based_options.block_cache =
      NewLRUCache(static_cast<size_t>(block_cache_size_mb * 1024 * 1024));
  table_factory.reset(new BlockBasedTableFactory(block_based_options));
  memtable_prefix_bloom_size_ratio = 0.02;
  return this;
}
```

优化点查询，实际上是改变了BlockBasedTable的index_type, 变成hash自然就不可迭代，主要是bloomfilter prefix tranform哪里会有hash查找

```c++
  bool const may_contain =
      nullptr == prefix_bloom_
          ? false
          : prefix_bloom_->MayContain(prefix_extractor_->Transform(user_key));
```



---

### reference

1. <https://www.pagefault.info/2018/11/13/mysql-rocksdb.-data-reading-(i).html>
2. <https://www.pagefault.info/2018/12/19/mysql-rocksdb.-data-reading-(ii).html>
3. <http://leviathan.vip/2018/02/08/Rocksdb%E7%9A%84Get/>
4. <http://www.leviathan.vip/2018/03/13/Rocksdb%E7%9A%84SST/>
5. <http://idning.github.io/leveldb-rocksdb-on-large-value.html>
6. <http://www.d-kai.me/leveldb%E8%AF%BB%E6%B5%81%E7%A8%8B1/>
7. <http://www.d-kai.me/leveldb%E8%AF%BB%E6%B5%81%E7%A8%8B2/>
8. 点查询优化，不可迭代 https://stackoverflow.com/questions/52139349/iterating-when-using-optimizeforpointlookup
9. 优化点查询，介绍<https://rocksdb.org/blog/2018/08/23/data-block-hash-index.html>



看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。