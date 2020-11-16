---
layout: post
categories: c++
title: log4cplus ERROR No appenders could be found for logger root 报错
tags: [c++, linux]
---

  

---

hdfs client 使用log4cplus是需要配置文件的，一般长这个样子

`log.properties`

```
log4cplus.logger.defaultLogger=INFO, LogToFile
log4cplus.appender.LogToFile=log4cplus::RollingFileAppender
log4cplus.appender.LogToFile.MaxFileSize=64MB
log4cplus.appender.LogToFile.MaxBackupIndex=20
log4cplus.appender.LogToFile.File=/opt/hdfs-client.log
log4cplus.appender.LogToFile.ImmediateFlush=true
log4cplus.appender.LogToFile.Append=true
log4cplus.appender.LogToFile.CreateDirs=true 
log4cplus.appender.LogToFile.layout=log4cplus::PatternLayout
log4cplus.appender.LogToFile.layout.ConversionPattern=%D{\%Y-%m-%d %H:%M:%S,%Q} %-5p [pid:%i pth:%t] %m %l%n
```
注意`%D{\%Y-%m`中间多加了个斜线，githubpage编译不过只好出此下策

通常库是所有模块共用同一个，动态库也是放在系统PATH下的。



如果单独打包可能就有问题

```shell
log4cplus:ERROR could not open file ./log.properties
log4cplus:ERROR No appenders could be found for logger (root).
log4cplus:ERROR Please initialize the log4cplus system properly.
```

需要把该文件放到模块同目录下，并且需要提供rootLogger

改成

```
log4cplus.rootLogger=INFO, LogToFile
...
```

就不会报错了。



Google一圈搜到了各种解决方案。被严重误导，只有<sup>1</sup> 贴点边

<sup>2</sup>是别人使用log4cplus遇到该问题以及解决方案。

----

### ref

1. https://bbs.csdn.net/topics/370248522

2. https://github.com/nsacyber/HIRS/issues/95

   

### contact

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>