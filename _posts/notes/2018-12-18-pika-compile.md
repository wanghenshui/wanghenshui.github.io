---
layout: post
title: pika编译踩坑
category: redis
tags : [c++, redis, rocksdb, glog. callgrind]
---

{% include JB/setup %}

最近想研究一下redis和rocksdb融合的东西，了解到[pika](https://github.com/Qihoo360/pika)是做这个的，开始比较测试和redis的功能差异，以下是踩坑记录



1. 运行测试，二进制文件运行几次测试用例就挂了，应该是不支持wait直接崩了

下面是log记录。我个人猜测是运行环境的问题，准备从头编译

```
bash pikatests.sh wait

ERROR:path : ./tests/tmp/redis.conf.29436.2
-----------Pika server 3.0.5 ----------
-----------Pika config list----------
1 thread-num 1
2 sync-thread-num 6
3 sync-buffer-size 10
4 log-path ./log/
5 loglevel info
6 db-path ./db/
7 write-buffer-size 268435456
8 timeout 60
9 requirepass
10 masterauth
11 userpass
12 userblacklist
13 dump-prefix
14 dump-path ./dump/
15 dump-expire 0
16 pidfile ./pika.pid
17 maxclients 20000
18 target-file-size-base 20971520
19 expire-logs-days 7
20 expire-logs-nums 10
21 root-connection-num 2
22 slowlog-write-errorlog no
23 slowlog-log-slower-than 10000
24 slowlog-max-len 128
25 slave-read-only yes
26 db-sync-path ./dbsync/
27 db-sync-speed -1
28 slave-priority 100
29 server-id 1
30 double-master-ip
31 double-master-port
32 double-master-server-id
33 write-binlog yes
34 binlog-file-size 104857600
35 identify-binlog-type new
36 max-cache-statistic-keys 0
37 small-compaction-threshold 5000
38 compression snappy
39 max-background-flushes 1
40 max-background-compactions 2
41 max-cache-files 5000
42 max-bytes-for-level-multiplier 10
-----------Pika config end----------
WARNING: Logging before InitGoogleLogging() is written to STDERR
W1217 17:22:48.644249 29438 pika.cc:167] your 'limit -n ' of 1024 is not enough for Redis to start. pika have successfully reconfig it to 25000
I1217 17:22:48.644497 29438 pika.cc:184] Server at: ./tests/tmp/redis.conf.29436.2
I1217 17:22:48.644691 29438 pika_server.cc:192] Using Networker Interface: eth0
I1217 17:22:48.644783 29438 pika_server.cc:235] host: 192.168.1.104 port: 0
I1217 17:22:48.644820 29438 pika_server.cc:68] Prepare Blackwidow DB...
I1217 17:22:48.776921 29438 pika_server.cc:73] DB Success
I1217 17:22:48.776942 29438 pika_server.cc:89] Worker queue limit is 20100
I1217 17:22:48.777190 29438 pika_binlog.cc:103] Binlog: Manifest file not exist, we create a new one.
I1217 17:22:48.777328 29438 pika_server.cc:109] double recv info: filenum 0 offset 0
F1217 17:22:48.779913 29438 pika_server.cc:284] Start BinlogReceiver Error: 1: bind port 1000 conflict, Listen on this port to handle the data sent by the Binlog Sender
*** Check failure stack trace: ***
@ 0x83c5aa google::LogMessage::Fail()
@ 0x83e2ff google::LogMessage::SendToLog()
@ 0x83c1f8 google::LogMessage::Flush()
@ 0x83ec2e google::LogMessageFatal::~LogMessageFatal()
@ 0x5f5725 PikaServer::Start()
@ 0x423db4 main
@ 0x7fe733418bb5 __libc_start_main
@ 0x58ac71 (unknown)
[1/1 done]: unit/wait (5 seconds)

The End

Execution time of different units:
5 seconds - unit/wait
```



\2. 源码编译由于我的服务器限制不能访问外网，自己手动git clone然后导回服务器（这里又有一个坑）（win7没有wsl，只能用服务器搞）

然后需要依赖子模块

```
git submodule init
git submodule update
```

重新在windows上更新后传回

分别编译，

子模块编译失败，其中有文件格式不对的问题 手动转dos2unix

然后才发现tortoisegit有个自动添加换行符的选项，默认打勾。所以基本上涉及到的shell文件都得手动dos2unix

![img](https://wanghenshui.github.io/assets/v2-2053ae5cd874a5d77bba250206697858_b.png)



我的服务器只有4.8.3，所以编译rocksdb需要c++11 需要修改Makefile（其实是detect脚本没加权限的问题）

![img](https://wanghenshui.github.io/assets/v2-8d148845e621bc2d5445bcdde12004aa_b.png)



编译glog失败

./configure make失败 提示没有什么repo 

搜到了类似的问题，<https://stackoverflow.com/questions/18839857/deps-po-no-such-file-or-directory-compiler-error>

按照提示 （需要安装libtool）

```
autoreconf -if
```

提示

```
.ibtoolize: AC_CONFIG_MACRO_DIR([m4]) conflicts with ACLOCAL_AMFLAGS=-I m4 
```

结果还是gitwindows加换行符导致的。 **That darn "libtoolize: AC_CONFIG_MACRO_DIR([m4]) conflicts with ACLOCAL_AMFLAGS=-I m4" error**   Is caused by using CRLFs in Makefile.am. "m4<CR>" != "m4" and thus the libtoolize script will produce an error. If you're using git, I strongly advise adding a .gitattributes file with the following: *.sh     -crlf *.ac     -crlf *.am     -crlf  http://pete.akeo.ie/2010/12/that-darn-libtoolize-acconfigmacrodirm4.html  

最终编译过了，运行提示找不到glog 还要手动ldconfig一下

```
echo "/usr/local/lib" >> /etc/ld.so.conf
ldconfig
```



还有一种解决方案，```export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib```

![1552045590285](https://wanghenshui.github.io/assets/1552045590285.png)

 总算能运行测试了。

redis 中runtest脚本不能直接用，但是测试用例可以直接拿过来用，support/server.tcl文件改下start_server函数就行（pika已经改过了，直接用那个文件就好了）



测试，类似下面，改改应该就行了

```
#!/bin/bash
for f in ${PWD}/tests/unit/*;do
    filename=${f##*/}
    tclsh tests/test_helper.tcl --clients 1 --single unit/${filename%.*}
done

for f in ${PWD}/tests/unit/type/*;do
    filename=${f##*/}
    tclsh tests/test_helper.tcl --clients 5 --single  unit/type/${filename%.*}
    #tclsh tests/test_helper.tcl --clients 1 --single unit/type/${filename%.*}
done
```





附调用图一张。组件太多，确实找不到在哪。

![pika](https://wanghenshui.github.io/assets/pika.svg)