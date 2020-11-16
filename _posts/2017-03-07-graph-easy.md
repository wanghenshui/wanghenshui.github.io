---
layout: post
title: 使用perl模块 graph easy 画图
categories: tools
tags: perl
---

  

graph-easy

两种装法

- 从命令行安装（我没有网，没试过）

```
cpan install Graph::Easy
或者
perl -MCPAN -e shell
install Graph::Easy
```

- 编译源码 [下载地址](https://metacpan.org/pod/Graph::Easy) 解压进入目录下

    perl Makefile.PL
    make
    make test
    make install


graph-easy文件在bin目录下，拷贝到usr/bin或者使用路径访问都可以

```
[hot data limit\n data cold out] ->
[consumed cold data enqueue\n pipe event write] -> 
[pipe event noticed,\n read and dequeue ]-> 
[thread pool add job\n do queuejob asyc]
```
生成图像

+----------------+     +----------------------------+     +---------------------+     +---------------------+
| hot data limit |     | consumed cold data enqueue |     | pipe event noticed, |     | thread pool add job |
| data cold out  | --> |      pipe event write      | --> |  read and dequeue   | --> |  do queuejob asyc   |
+----------------+     +----------------------------+     +---------------------+     +---------------------+



还算省事儿，有机会读读代码实现。（又挖坑）

---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。