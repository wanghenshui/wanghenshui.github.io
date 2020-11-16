---
layout: post
categories : database
title: PPT笔记 InnoDB to MyRocks migration in main MySQL database at Facebook
tags : [rocksdb, innodb, mysql]
---
  

### why

这个ppt<sup>1</sup>十分有趣，决定做个阅读记录，作者是Yoshinori Matsunobu是mysql rocks工程师 ，rocksdb上见过他的pr

---

首先简单介绍了facebook使用mysql数据库的场景

- 存储社交关系图
- 大量共享数据
- PB级别
- 低延迟
- 自动操作
- SSD

在这个场景中，mysql-innodb暴露的问题

- 写放大，innodb两次写<sup>2</sup>带来的放大问题，一次改动1byte，假设一页4~16kb，写两页，每次1M，这放大有点恐怖
- b+tree碎片问题，比如插入造成的页分裂，数据冗余，浪费空间，造成了放大问题
- 压缩问题 16k页压缩到5k，存储 4k单位，总会浪费。

rocksdb相关介绍和LSM工作原理就不多说了

myrocks 基于rocksdb做的引擎层。也可用在mariadb和percona服务，设计目标

- 提高空间利用率，加强性能
  - 压缩后相比innodb节省一半空间
- 更好的写放大
  - 延长ssd寿命
- 更快，一般机器也能有较好吞吐性能，针对场景
  - 大量数据内存放不下
  - 点查询，范围扫描，索引查询，表扫描
  - （点/ 范围）插入更新删除，以及偶尔的批量插入
  - 较小的cpu使用率
  - 争取一个机器两个实例

myrocks的特性

- 集群索引（同innodb）
- 布隆过滤器和Column Family
- 事务，包括rocksdb和binlog的数据一致性
- 更快的数据加载，删除，复制
- 动态配置
- TTL
- 在线备份

后面是他们介绍迁移的过程

迁移挑战

- 开始迁移
  - 起myrocks实例，不能停机
  - 在合适的时间拉数据到myrocks
  - 验证innodb和myrocks数据一致性
- 持续监控
  - 资源使用，比如硬盘空间，iops，cpu 内存等
  - 查询plan详情
  - 停顿和崩溃处理

- myrocks运行在master模式
  - 行级复制
  - 去掉依赖innodb范围锁的查询 （gap lock 范围锁，record lock 行锁）
  - 要保证xa事务支持（binlog rocksdb）

分条阐述

创建myrocks实例过程

选一个innodb备机，停，不影响整体服务，挂上myrocks，开始同步回恢复

![1553741804550](https://wanghenshui.github.io/assets/1553741804550.png)



数据迁移步骤

- 目标机器 create table... engine=rocksdb
- 目标及其alter table drop index ...
- 源机器停掉slave
- mysqldump –host=innodb-host --order-by-primary | mysql –host=myrocks-host –initcommand=“set sql_log_bin=0; set rocksdb_bulk_load=1”
  - myrocks 加快数据加载的trick 暂时设置禁止WAL，直接存level max SST
- 目标机器 alter table add index ...
- 源机器，目标机器 start slave

数据验证 rocksdb是新的，相比innodb没有那么稳定，需要保证没有数据不一致的冲突

验证测试

- 检查主键和辅键索引 
  - 如果索引有问题，可以检查出来
  - SELECT ‘PRIMARY’, COUNT(\*) FROM t FORCE INDEX (PRIMARY)
    UNION SELECT ‘idx1’, COUNT(*) FROM t FORCE INDEX (idx1)
  - 如果没有其他键还有辅助索引那肯定用不上，删掉
- 索引状态
  - 检查show table status行数和实际行数一样
- checksum 测试
  - 比对innodb myrocks实例
  - 在同一个GTID位置建立一个事务一致行快照，然后比对checksum
- shadow 验证检查
  - 抓读的流量

shadow traffic 测试<sup>4</sup>

- facebook内部有个shadow测试框架
  - mysql audit plugin从线上环境中抓读写查询
  - 重放到测试主节点啊实例
- 主机shadow测试
- 客户端错误
- 重写依赖范围锁的查询
  - gap_lock_raise_error=1, gap_lock_write_log=1



![1553744009375](https://wanghenshui.github.io/assets/1553744009375.png)

![1553744041879](https://wanghenshui.github.io/assets/1553744041879.png)



崩溃安全性

崩溃安全让操作更简单了，重启就行，反正数据都在 ppt列举了主机设置

![1553744404585](https://wanghenshui.github.io/assets/1553744404585.png)



在迁移过程中几个值得注意的issue

- 快照冲突错误 Snapshot Conflict
  - 由于rocksdb实现的快照隔离和innodb不同（pg style），事务隔离级别不同，改成tx-isolation=READ-COMMITTED
- 备机由于io错误停了
  - 只要错误直接重启
- 索引数据的bug
  - 批量加载 行数长度错误
  - 索引创建之后基数没及时更新
- 崩溃安全性的问题 修复rocksdb bug

避免停顿 大量写可能导致大量的compaction造成写停顿（write stall）

- 典型write stall 场景
  - 在线模式改变
  - 数据迁移大量写
- 使用前面说到的快速数据加载trick，直接写文件，跳过wal memtable
  - 缺陷 迁移中，写入已经存在的表可能不好处理？ why

当write stall 发生时

- 可能达到pending compaction上限 hard_pending_compaction_bytes 调大
- 可能达到l0数目上限 检查L0 triger设置 level0_slowdown stop_writes_trigger调大
- 可能memtable已经写满 检查memtable 限制  max_write_buffer_number 调大
- 检查LOG中WARN 级别的日志
- 检查每个column family的配置（option）



写停顿真正发生了什么

软停顿

- commit执行时间稍长
- 整体的写入速度被限制在rocksdb_delayed_write_rate中，直到slowdown 触发条件被清除干净

硬停顿

- 所有的写被commit阻塞。直到解锁

Mitigating write stall 缓解写停顿

- 加速compaction
  - 使用快速的压缩算法，LZ4或者ZSTD
  - 增加rocksdb_max_background_compactions数量
- 减少写入
  - 但要避免使用太强的压缩算法？
  - 使用更高效的压缩算法
    - compaction_pri=kMinOverlappingRatio ?
- 文件慢删除
  - 删除太多大文件会触发SSD的trim stall
  - myrocks限制throttles 删除文件的速度 64mb/s 
  - 删除binlog也应该尽可能 的慢

监控数据

- myrocks文件
- show engine rocksdb status ->调的rocksdb staticis 的接口
- show engin rocksdb transaction status
- LOG文件
- information_schema 表
- sst_dump 工具
- ldb

总结

- 迁移动机 省空间
- 在线数据纠正检查工具帮助检测了很多bug避免了很多线上实例数据不一致的问题
- 批量载入能降低compaction stall
- 支持事务和崩溃安全性



#### Update

2019-5-22 19:38:18

热备不支持Innodb，不能转系统表

限制

- 不支持分区表，Online ddl,外键，全文索引，空间索引，表空间transport
- gap lock支持不健全(仅primary key上支持), 使用statement方式复制会导致不一致
- 不支持select … in share mode
- 大小写敏感，不支持*_bin collation
- binlog与RocksDB之间没有xa，异常crash可能丢数据。所以，MyRocks一般开启semi-sync.
- 不支持savepoint
- order by 不比较慢
- 不支持MRR
- 暂不支持O_DIRECT
- innodb和RocksDB混合使用还不稳定

来源 <http://mysql.taobao.org/monthly/2016/08/03/>



mysql直接热备innodb还原到myrocks 5.7应该是无解的

不过percona的xbackup支持8.0版本。

看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。

### reference

1. <https://www.usenix.org/sites/default/files/conference/protected-files/srecon17asia_slides_yoshinori.pdf>
2. 两次写 https://www.percona.com/blog/2006/08/04/innodb-double-write/ 另外每次写1M写两次是百度到的。。这个数据不确定。感觉写放大有点大的离谱了。
3. b树碎片
   1. 索引碎片 讲的很详细<https://www.cnblogs.com/woodytu/p/4513562.html>
   2. Avoiding Fragmentation with Fractal Trees 科普一下新的数据结构设计<https://www.percona.com/blog/2010/11/17/avoiding-fragmentation-with-fractal-trees/>
4. shadow traffic test 
   1. 这是介绍<https://zhuanlan.zhihu.com/p/50610215>
   2. 这是一个思考，如何把线上流量导入测试环境<https://zhuanlan.zhihu.com/p/35021628>
5. 范围锁 主要是提升事务性能。行锁效率太低 <https://www.percona.com/blog/2012/03/27/innodbs-gap-locks/>
6. 作者这哥们的pr 挺有意思的。<https://github.com/facebook/rocksdb/pull/1721>
7. myrocks介绍，有时间写个博客顺一下<https://www.percona.com/live/17/sites/default/files/slides/MyRocks_Tutorial.pdf>
8. yc上myrocks的讨论，有点意思<https://news.ycombinator.com/item?id=15835188>
9. yc 上关于rocksdb cockroachdb的讨论 需要做个笔记<https://news.ycombinator.com/item?id=18938737>
10. MyRocks以及使用场景 <https://zhuanlan.zhihu.com/p/45652076>
11. Mysql与Innodb <https://draveness.me/mysql-innodb>



