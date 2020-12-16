---
layout: post
title: rocksdb涉及到关闭开启的时间优化
categories: [database]
tags: [rocksdb]
---


---

 

> 这个是同事调参的经验，我直接抄过来了

不少都是经常提到的

rocksdb配置：

- compaction加速设置compaction_readahead_size 很常规。值可以改改试试，16k 256k都有
- wal日志调小  max_manifest_file_size, max-total-wal-size
- close db的时候停掉compaction
  - rocksdb里有compaction任务，可能还会耗时，能停掉就更好了
- close会主动flush flush可能触发compaction和write stall。先跳过
- open会读wal恢复memtable，所以最好不要有wal，close的时候刷掉
- targetbase和放大因子要根据自身的存储来调整 比如写入hdfs，设置60M就比较合适，不会频繁更新元数据

打开rocksdb文件过多 GetFileSize时间太长

- 看到一个PR https://github.com/facebook/rocksdb/pull/6353/files 6.8版本在open阶段规避调用 GetFileSize

- 我们这边同事的解决方案是hack OnAddFile调用的地方，改成多线程cv来添加。

这两个优化点位置不一样，一个在打开 恢复校验阶段，一个在打开阶段，这个打开阶段OnAddFile有GetFileSize，所以在OnAddFile之前，调用一把查文件大小，避开GetFileSize

```c++
    std::vector<LiveFileMetaData> metadata;

    impl->mutex_.Lock();
    impl->versions_->GetLiveFilesMetaData(&metadata);
    impl->mutex_.Unlock();
```

~~后面OnAddFile阶段就不用查size了，通过这里拿到的metadata~~，但是有的文件查不到，这里，原生rocksdb用的是GetFileSize，同事是用多线程异步去查，相比原生一个一个查能加速一点



---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>