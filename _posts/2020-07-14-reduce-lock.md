---
layout: post
title: 改造pika如何去掉key锁
categories: [database]
tags: [rocksdb,redis]
---
  

---

[toc]

> 这个是同事的修改经验，虽然是针对业务而言的，但是这个思路十分的降维打击，我直接抄过来了

现有模型是slot-proxy-shard结构，上层有代理来转发，shard节点，也就是pika，只负责一部分数据

但是pika本身是有key锁的

比如https://github.com/Qihoo360/blackwidow/blob/ae38f5b4c5c01c7f8b9deec58db752e056659264/src/redis_lists.cc#L273

```c++
Status RedisLists::LInsert(const Slice& key,
                           const BeforeOrAfter& before_or_after,
                           const std::string& pivot,
                           const std::string& value,
                           int64_t* ret) {
  *ret = 0;
  rocksdb::WriteBatch batch;
  ScopeRecordLock l(lock_mgr_, key);
  std::string meta_value;
  Status s = db_->Get(default_read_options_, handles_[0], key, &meta_value);
  if (s.ok()) {
    ParsedListsMetaValue parsed_lists_meta_value(&meta_value);
    if (parsed_lists_meta_value.IsStale()) {
      return Status::NotFound("Stale");
    } else if (parsed_lists_meta_value.count() == 0) {
      return Status::NotFound();
    } else {
        ...
```



前面已经有一层proxy转发了，这层转发是根据hash来算还是根据range来算不重要，重要的是到计算节点，已经缩小了key范围了，还要加锁，这层锁是可以优化掉的

- 保证落到这个db的key的顺序，也就是说，相同hash/range用同一个连接，保证了命令的顺序，就不会有锁的问题，锁也就可以省掉。从上层来解决掉这个锁的问题
  - shard节点的命令处理线程，要保证hash/range相同的用同一个连接线程工作。多一点计算，省掉一个锁。



pika单机版，用的是同一个db，同一个db是很难去掉key锁的。要想应用上面的改造，也要改成多db模式，把db改成slot，然后根据slot划分线程，然后根据线程来分配命令，保证命令的顺序，省掉锁。

省掉key锁的收益是很大的。尤其是一个命令里有很多次get，get很吃延迟，导致锁占用很长，导致积少成多的影响

### ref

1. 

   

---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。