---
layout: post
title: best free is exit
categories: [database]
tags: [rocksdb]
---

省流 不析构，直接退出进程

<!-- more -->


rocksdb 论坛看到的帖子，发现进程关闭很慢

他们的配置

```cpps
rocksdb::LRUCacheOptions lru_block_cache_opts;
lru_block_cache_opts.capacity = 1024*1024*1024*256; // 256 GiB
lru_block_cache_opts.strict_capacity_limit = false;
lru_block_cache_opts.high_pri_pool_ratio = 0.5;
block_cache_ = rocksdb::NewLRUCache(lru_block_cache_opts)
```

内存256G 主要都卡在析构函数上了

我一开始给的点子是WAL或者主动停compaction之类的

blockcache析构一时没有好的点子

Mark Callaghan给了个点子，直接跳过析构就好了

我怎么就没想到呢，脑子思维卡住了


rocksdb提供了跳过析构的接口


```cpp
// Call this on shutdown if you want to speed it up. Cache will disown
// any underlying data and will not free it on delete. This call will leak
// memory - call this only if you're shutting down the process.
// Any attempts of using cache after this call will fail terribly.
// Always delete the DB object before calling this method!
virtual void DisownData() {
// default implementation is noop
}
```

主动停止的时候主动调用一下就好了

我顺便蹭了一个PR https://github.com/apache/kvrocks/pull/2683


