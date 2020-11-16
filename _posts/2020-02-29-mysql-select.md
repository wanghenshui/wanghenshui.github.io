---
layout: post
categories: database
title: mysql几个优化
tags: [mysql]
---

  

---

 

## 查询

where子句有没有用错？？索引有没有用错，有没有索引？表规模大不大？能不能并发遍历？

能不能归档？

参考链接 1 2 3

### 插入

1）提高数据库插入性能中心思想：尽量将数据一次性写入到Data File和减少数据库的checkpoint 操作。这次修改了下面四个配置项：

1）将 innodb_flush_log_at_trx_commit 配置设定为0；按过往经验设定为0，插入速度会有很大提高。

0: 日志缓冲每秒一次地被写到日志文件，并且对日志文件做到磁盘操作的刷新，但是在一个事务提交不做任何操作。

1：在每个事务提交时，日志缓冲被写到日志文件，对日志文件做到磁盘操作的刷新。

2：在每个提交，日志缓冲被写到文件，但不对日志文件做到磁盘操作的刷新。对日志文件每秒刷新一次。

默认值是 1，也是最安全的设置，即每个事务提交的时候都会从 log buffer 写

到日志文件，而且会实际刷新磁盘，但是这样性能有一定的损失。如果可以容忍在数

据库崩溃的时候损失一部分数据，那么设置成 0 或者 2 都会有所改善。设置成 0，则

在数据库崩溃的时候会丢失那些没有被写入日志文件的事务，最多丢失 1 秒钟的事

务，这种方式是最不安全的，也是效率最高的。设置成 2 的时候，因为只是没有刷新

到磁盘，但是已经写入日志文件，所以只要操作系统没有崩溃，那么并没有丢失数据 ，

比设置成 0 更安全一些。

在 mysql 的手册中，为了确保事务的持久性和复制设置的耐受性、一致性，都是

建议将这个参数设置为 1 的。

2）将 innodb_autoextend_increment 配置由于默认8M 调整到 128M

此配置项作用主要是当tablespace 空间已经满了后，需要MySQL系统需要自动扩展多少空间，每次tablespace 扩展都会让各个SQL 处于等待状态。增加自动扩展Size可以减少tablespace自动扩展次数。

3）将 innodb_log_buffer_size 配置由于默认1M 调整到 16M

此配置项作用设定innodb 数据库引擎写日志缓存区；将此缓存段增大可以减少数据库写数据文件次数。

4）将 innodb_log_file_size 配置由于默认 8M 调整到 128M

此配置项作用设定innodb 数据库引擎UNDO日志的大小；从而减少数据库checkpoint操作。

经过以上调整，系统插入速度由于原来10分钟几万条提升至1秒1W左右；注：以上参数调整，需要根据不同机器来进行实际调整。特别是 innodb_flush_log_at_trx_commit、innodb_log_buffer_size和 innodb_log_file_size 需要谨慎调整；因为涉及MySQL本身的容灾处理。

（2）提升数据库读取速度，重数据库层面上读取速度提升主要由于几点：简化SQL、加索引和分区； 经过检查程序SQL已经是最简单，查询条件上已经增加索引。我们只能用武器：表分区。

数据库 MySQL分区前准备：在MySQL中，表空间就是存储数据和索引的数据文件。

将S11数据库由于同享tablespace 修改为支持多个tablespace;

将wb_user_info_sina 和 wb_user_info_tx 两个表修改为各自独立表空间；（Sina：1700W数据，2.6G 大数据文件，Tencent 1400W，2.3G大数据文件）；

分区操作：

将现有的主键和索引先删除

重现建立id,uid 的联合主键

再以 uid 为键值进行分区。这时候到/var/data/mysql 查看数据文件，可以看到两个大表各自独立表空间已经分割成若干个较少独立分区空间。（这时候若以uid 为检索条件进行查询，并不提升速度；因为键值只是安排数据存储的分区并不会建立分区索引。我非常郁闷这点比Oracle 差得不是一点半点。）

再以 uid 字段上进行建立索引。再次到/var/data/mysql 文件夹查看数据文件，非常郁闷地发现各个分区Size竟然大了。MySQL还是老样子将索引与数据存储在同一个tablespace里面。若能index 与 数据分离能够更加好管理。

经过以上调整，暂时没能体现出系统读取速度提升；基本都是在 2~3秒完成5K数据更新。

MySQL数据库插入速度调整补充资料：

MySQL 从最开始的时候 1000条/分钟的插入速度调高至 10000条/秒。 相信大家都已经等急了相关介绍，下面我做调优时候的整个过程。提高数据库插入性能中心思想：

1、尽量使数据库一次性写入Data File

2、减少数据库的checkpoint 操作

3、程序上尽量缓冲数据，进行批量式插入与提交

4、减少系统的IO冲突

根据以上四点内容，作为一个业余DBA对MySQL服务进行了下面调整：

修改负责收录记录MySQL服务器配置，提升MySQL整体写速度；具体为下面三个数据库变量值：innodb_autoextend_increment、innodb_log_buffer_size、innodb_log_file_size；此三个变量默认值分别为 5M、8M、8M，根据服务器内存大小与具体使用情况，将此三只分别修改为：128M、16M、128M。同时，也将原来2个 Log File 变更为 8 个Log File。此次修改主要满足第一和第二点，如：增加innodb_autoextend_increment就是为了避免由于频繁自动扩展Data File而导致 MySQL 的checkpoint 操作；

将大表转变为独立表空并且进行分区，然后将不同分区下挂在多个不同硬盘阵列中。

完成了以上修改操作后；我看到下面幸福结果：

获取测试结果：

Query OK, 2500000 rows affected (4 min 4.85 sec)

Records: 2500000 Duplicates: 0 Warnings: 0

Query OK, 2500000 rows affected (4 min 58.89 sec)

Records: 2500000 Duplicates: 0 Warnings: 0

Query OK, 2500000 rows affected (5 min 25.91 sec)份额为

Records: 2500000 Duplicates: 0 Warnings: 0

Query OK, 2500000 rows affected (5 min 22.32 sec)

Records: 2500000 Duplicates: 0 Warnings: 0

最后表的数据量：

+————+

| count(*) |

+————+

| 10000000|

+————+

从上面结果来看，数据量增加会对插入性能有一定影响。不过，整体速度还是非常面议。一天不到时间，就可以完成4亿数据正常处理。



参考链接 4 5 6 7

### 主从复制延时

https://www.wencst.com/archives/1750

https://www.jianshu.com/p/ed19bb0e748a

### mysql数据库优化

https://www.wencst.com/archives/1781

https://www.wencst.com/archives/1774

不得不说资料真多啊



## ref

1. https://blog.csdn.net/lchq1995/article/details/83308290
2. https://blog.csdn.net/u011296485/article/details/77509628
3. https://blog.csdn.net/u011193276/article/details/82195039
4. https://www.jianshu.com/p/d017abaea8d1
5. https://database.51cto.com/art/201901/590958.htm 提到了innodb_flush_log_at_trx_commit
6. https://www.cnblogs.com/jpfss/p/10772962.html 同上
7. 常见的插入慢 http://mysql.taobao.org/monthly/2018/09/07/

### contacts

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
![微信转账](https://wanghenshui.github.io/assets/wepay.png)
</details>


