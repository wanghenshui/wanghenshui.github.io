---
layout: post
categories : database
title: systench-tpcc适配mongo踩坑
tags : [linux, mongodb, lua]
---
  



首先安装mongodb 4.0 下载链接 <https://www.mongodb.com/download-center/community> 我用的centos 下载x64然后rpm安装就行了

然后我的实验机器有点小，准备换个外接硬盘，改db目录，这就是一切厄运的开始。

我的做法是改 /etc/mongod.conf

```bash
 +dbPath: /home/vdb/mongo/data
 -dbPath: /var/lib/mongo
```

 报错起不来

然后我试着改 /usr/lib/systemd/system/mongod.service

 ```bash
+Environment="OPTIONS= --dbpath /home/vdb/mongo/data -f /etc/mongod.conf"
-Environment="OPTIONS= -f /etc/mongod.conf"
 ```

还是报错

```shell
* mongod.service - MongoDB Database Server
   Loaded: loaded (/usr/lib/systemd/system/mongod.service; enabled; vendor preset: disabled)
   Active: failed (Result: exit-code) since Wed 2019-04-03 17:32:38 CST; 14min ago
     Docs: https://docs.mongodb.org/manual
  Process: 24223 ExecStart=/usr/bin/mongod $OPTIONS (code=exited, status=100)
  Process: 24221 ExecStartPre=/usr/bin/chmod 0755 /var/run/mongodb (code=exited, status=0/SUCCESS)
  Process: 24217 ExecStartPre=/usr/bin/chown mongod:mongod /var/run/mongodb (code=exited, status=0/SUCCESS)
  Process: 24214 ExecStartPre=/usr/bin/mkdir -p /var/run/mongodb (code=exited, status=0/SUCCESS)

 Main PID: 21976 (code=exited, status=0/SUCCESS)

Apr 03 17:32:38 host-192-168-1-112 systemd[1]: Starting MongoDB Database Server...
Apr 03 17:32:38 host-192-168-1-112 mongod[24223]: about to fork child process, waiting unti...s.

Apr 03 17:32:38 host-192-168-1-112 mongod[24223]: forked process: 24226
Apr 03 17:32:38 host-192-168-1-112 mongod[24223]: ERROR: child process failed, exited with ...00

Apr 03 17:32:38 host-192-168-1-112 mongod[24223]: To see additional information in this out...n.

Apr 03 17:32:38 host-192-168-1-112 systemd[1]: mongod.service: control process exited, code...00

Apr 03 17:32:38 host-192-168-1-112 systemd[1]: Failed to start MongoDB Database Server.
Apr 03 17:32:38 host-192-168-1-112 systemd[1]: Unit mongod.service entered failed state.
Apr 03 17:32:38 host-192-168-1-112 systemd[1]: mongod.service failed.
```

google半天，找了好多解决方案，比如

<https://stackoverflow.com/questions/5961145/changing-mongodb-data-store-directory/5961293> 

<https://stackoverflow.com/questions/21448268/how-to-set-mongod-dbpath>

<https://stackoverflow.com/questions/40829306/mongodb-cant-start-centos-7>

都不好使。systemd实在是搞不懂

最后还是直接执行

```bash
mongod --dbpath /home/vdb/mongo/data -f /etc/mongod.conf
```

搞定了,这点破事儿卡了半天。然后搜到了这个<https://ruby-china.org/topics/35268>，貌似是正解。不验证了。













看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
![微信转账](https://wanghenshui.github.io/assets/wepay.png)
</details>或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。

### reference

1. sysbench repo and build https://github.com/akopytov/sysbench#building-and-installing-from-source

2. <https://github.com/Percona-Lab/sysbench-tpcc>

   1. <https://www.percona.com/blog/2018/03/05/tpcc-like-workload-sysbench-1-0/>

3. 测pg 的例子<https://www.percona.com/blog/2018/06/15/tuning-postgresql-for-sysbench-tpcc/

   另外这个链接下面也有mark的一些测试repo mark callaghan这个哥们有点牛逼。

4. <https://help.ubuntu.com/stable/serverguide/postgresql.html>

5. sysbench 参数介绍 <https://wing324.github.io/2017/02/07/sysbench%E5%8F%82%E6%95%B0%E8%AF%A6%E8%A7%A3/>

6. 一个sysbench-oltp lua脚本。可以改改加上mongodb ，同时也得合入 sysbench mongo driver 是个大活<https://github.com/Percona-Lab/sysbench-mongodb-lua>

7. <https://github.com/Percona-Lab/sysbench/tree/dev-mongodb-support-1.0>

8. <https://www.percona.com/blog/2016/05/13/benchmark-mongodb-sysbench/>

9. iowait 多高算高？https://serverfault.com/questions/722804/what-percentage-of-iowait-is-considered-to-be-high
