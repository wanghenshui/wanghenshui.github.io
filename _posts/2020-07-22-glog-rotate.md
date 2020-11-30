---
layout: post
title: 改造glog 提供日志轮转
categories: [language]
tags: [log,glog]
---


---

 

> 这个是同事的修改经验，写的挺有意思的，我直接抄过来了



glog是写日志的。选型pika使用，没改。存在的弊端

- 没有日志删除。最新glog是按照日志轮转的，而不是按照个数/大小轮转
  - glog支持按照大小来切割轮转，但是不支持清理，清理，一个unlink的事儿。
- 各种日志级别的信息是区分保存的，对于查看来说很不方便

我的同事在这两点上根据pika已有的结构来进行优化，优化的很巧妙：

- 加上日志个数的glog接口，暴露出来，也就是实现一个接口来unlink
  - 对应的，所有的日志名字要保留到一个数组里。那这个数组的更新也要加锁
    - LogFileObject::CreateLogfile 更新数组，新增接口里改数组
  - 不能频繁检查。放到epoll时间时间里，定时触发

- 对于第二点，在LogFileObject::Write里有具体的格式，level，去掉就行。LogDestination::FlushLogFilesUnsafe里去掉不同level的flush，改成一个



LogFileObject是具体的操作 LogDestination是底层具体的写入，会持有LogFileObject对象，所有接口从LogMessage暴露



总之挺巧妙的。学习一波经验

### ref

1. https://github.com/google/glog

   

---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>