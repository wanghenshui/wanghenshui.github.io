```
layout: post
title: 使用perl模块 graph easy 画图
category: tools
tags: perl
```

{% include JB/setup %}

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

## 参考

这里有个教程 https://weishu.gitbooks.io/graph-easy-cn