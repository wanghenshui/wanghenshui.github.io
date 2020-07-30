---
layout: post
title: rocksdb涉及到关闭开启的时间优化
category: [database]
tags: [rocksdb]
---
{% include JB/setup %}

---

[toc]

这个是同事调参的经验，我直接抄过来了

不少都是经常提到的

rocksdb配置：

- compaction加速设置compaction_readahead_size 很常规。值可以改改试试，16k 256k都有
- wal日志调小  max_manifest_file_size, max-total-wal-size
- close db的时候停掉compaction
  - rocksdb里有compaction任务，可能还会耗时，能停掉就更好了
- close会主动flush flush可能触发compaction和write stall。先跳过
- open会读wal恢复memtable，所以最好不要有wal，close的时候刷掉

### ref

1. 

   

---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。