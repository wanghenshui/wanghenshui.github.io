---
layout: post
title: MongoDB权威指南笔记
categories: database
tags: [c++,mongodb]
---
  

##< MongoDB权威指南>笔记

### MongoDB基础知识

- 文档（行）-》 集合（动态模式的表,集合可以有子集合（GridFS））-》数据库

- 每个文档有个特殊的键_id （唯一生成方式，时间戳+机器ID+PID+计数器）

- 命名
- 集合system保留，注意有些保留字没有强制限定，比如version，就只能用getCollection来访问了，或者跳过直接访问，使用数组迭代语法
- 数据库，admin local config 保留

- JavaScriptShell操作 use db CRUD

#### 基本数据结构 ALL IN JSON

- null 二进制以及代码

- bool 数值，默认64位浮点型，可以用NumberInt类NumberLong类

- 字符串，日期（new Date() 直接调用Date构造函数得到的是个字符串，所以这里用new，标识Date 对象，而不是对象生成的字符串）
- 正则 /foobar/i js正则语法（需要学一下js）

- 数组，数组可以包含不同类型的元素，**数组内容可以建索引，查询以及更新**
- 内嵌文档（*嵌套Json*，**也可以建索引，查询以及更新**）
- 对象ID
- _id默认是ObjectID对象，每个文档都有唯一的 _id ObjectId全局唯一的原理
- 自动生成id 通常能交给客户端驱动程序搞定就不放在服务器，扩展应用层比扩展数据库层要方便

#### JS Shell

- .mongorc.js文件，放在bin下自动运行，可以覆盖危险Shell辅助函数，取消定义，也可以启动Shell时 --norc 取消加载
- Windows用户，该文件会默认生成在用户 用户名或administrator目录下



#### 创建，更新和删除文档

##### 插入文档

- insert， batchinsert 批量插入，多个文档插入到同一个集合中，多个文档插入多个集合不行。

- 导入原始数据使用mongoimport （需要学一下go）
- 插入最大接受48M插入，多于48M会分片插入，如果插入途中有一个文档插入失败，前面的灰尘共，后面的都失败，不是强事务的。
- 插入校验，添加_id字段，检查大小（目前是小于16M）（可能是不良的设计）

##### 删除

- db.foo.remove() 删除集合的所有文档删除数据是永久的，不能撤销，也不能恢复
- drop删除整个表（和数据库一样，快，没有限定条件）

##### 更新文档

- 文档替换，直接更改文档的字段，扩展，重命名，建立子文档等 可以用=，直接用delete删除字段（只能用替换，不能直接删数据库，[用findOne，find返回值是个cursor](https://stackoverflow.com/questions/18041356/mongodb-javascript-execution-failed-cant-save-a-dbquery-object-at-src-mongo)）

- 文档更新相同字段导致的更新错误（不唯一，有可能给id在前的更新了），索引问题，用id来查找

- 修改器，一个Json封起来。key是动作，value是个修改的Json，其中，内部key对应修改的字段，value对应修改的值

- $set == replace or insert, $unset 直接就可以删掉这个键 可以修改内嵌文档

- $inc == add or insert

- 数组修改器

- $push 添加元素 添加一个数组元素，$push 和$each结合使用，添加多个数组
- 数组作为数据集，保证数据不重复 $ne一个限定集，或使用$addToSet（$addToSet和$each可以结合使用）

- 删除元素 {"$pop":{"key":-1}}基于位置，如果基于条件，使用$pull
- 基于位置的数组修改器 直接使用定位符$来匹配，匹配第一个 db.blog.update({"cmt.author":"John"},{"$set":{"cmt.$.author":"Jim"}})

- 修改器速度, 主要取决于文档大小是否变化，如果有变化，就会影响速度，因为插入是相邻的，如果一个文档变大，位置就放不下，就会有移动
- paddingFactor，填充因子，MongoDB位每个新文档预留的增长空间，(db.coll.stats()，Windows上我运行这个没找到paddingFactor项，比较尴尬)

- upsert update + insert Update第三个参数true 原子性
- $setOnInsert 考虑寻找并修改同一个字段，多次运行可能会生成多个文档，setOnInsert会找到之前生成的文档，不会多次生成。
- save shell （db.foo.save(x)）在写到这行之前我都是先findOne查回来，改，在Update回去。。。

- 更新多个文档 db.user.update({"birthday":"10/13/1978"},{""$set":{"gift":"Happy Birthday"}},faset,true)
- db.runCommand({getLaseError:1}) 查看更新文档数量

- 返回被更新的文档 findAndModify ？有点没理解

##### 写入安全

#### 查询

- find 默认匹配全部文档{}，也可以写多个条件（and关系）
- 指定返回，第二个参数指定{"key":1/0}，类似select指定，其中1是选中，0是排除
- 限制 ？有点没理解

- 查询条件 "$lt" "$lte" "$gt" "$gte" "$ne"
- OR "$in" "$or " "$not" "$nin"
- 条件语义

##### 特定类型的查询

- null
- 正则表达式
- 查询数组 与查询普通文档是一样的，直接find value能匹配到数组中的元素，就会被选出来
- $all 特定元素的并列条件，顺序无关紧要，普通find子数组的形式不行，会有顺序限制，如果想找特定位置的元素，需要使用key.index （上面的 key.$就是个迭代形式。）
- $size 指定长度的数组
- $slice 返回一个子集 截取一段
- 数组和范围查询的相互作用，因为查找数组会匹配所有元素，有满足的就会被选出来，所以范围查询可能会和设想的结果不一样
- 针对数组，使用 $elemMatch 效率稍低
- 如果该列有索引，直接用min max

- 查询内嵌文档 用.访问 （URL作为键的弊端）
- $where 结合函数 会很慢，用不了索引，还有文档转换为js（配合where函数）的开销
- 注意可能引入的注入攻击

- 游标 find

- while(cursor.hasNext()){obj=cursor.next(),do....}
- cursor.forEach(function(x){...})
- limit skip sort 类似SQL中的limit sort
- skip不要过滤大量结果，会慢
- 不要用skip对结果分页
- 注意比较顺序
- 随机选取文档，不要算出所有然后在找随机数，太坑了。可以每个文档加一个随机数key，在key上建索引，然后用随机随机数过滤就ok
- 也有可能找不到结果，那就反向找一下，还没有那就是空的

- 高级查询选项
- 获取一致结果：迭代器修改文档可能引入的问题，修改的文档大小发生变化，结果只能放在文档最后，导致同一个文档返回多次（太坑了）
- 解决方案，snapshot，会使查询变慢，只在必要的时候使用快照，mongodump

- 游标的生命周期 默认十分钟自动销毁，有immortal选项

- 数据库命令 runCommand 实际上内置命令是db.$cmd.findOne({""})的语法糖

### 设计应用

#### 索引

- 和关系型数据库类似，也有explain
- 复合索引 db.coll.ensureIndex({"key1:1","key2:!"})
- 覆盖索引与隐式索引
- $如何使用索引
- 低效率的操作符，基本都不能用索引
- 范围 要考虑与索引结合导致的效率低下问题
- $or使用索引

- 索引对象和数组
- 可以嵌套对象的任意层级来做索引 a.b.c.d.e.f ，得用最后级别的对象来搜索才能用上这个索引，只用其中一个字段是不行的。
- 索引数组 实际上是对每一个数组元素都建立了索引，代价很大，如果有更新操作，那就完了，不过这里可以对字段来查找，毕竟每个字段都有索引。但是索引不包含位置信息。没法针对特定位置来找。
- 限定只有一个数组可以索引。为了避免多键索引中索引条目爆炸

- 多键索引 多键索引可能会有多个索引条目指向同一个文档 <u>？为什么</u> 会很慢，mongo要先去重

##### 索引基数

- 基数 衡量复杂度，某个字段拥有不同值的数量，基数越高索引越有效，索引能将搜索范围缩小到一个小的结果集

- 查询优化器

##### 何时不应该使用索引

- 索引扫描和全盘扫描在集合与返回结果上进行比较

索引类型

- 唯一索引 和主键概念一致（虽然已经有_id 这个主键了,新增的唯一索引是可以删除的）db.coll.ensureindex({"ukey":1},{"unique":true})

- 复合唯一索引。一例 GridFS files_id:ObjectId, n:1 所有索引键的组合必须唯一

- 去处重复，建唯一索引失败 ,加个条件ensureindex({"ukey":1},{"unique":true，"dropDups":true}) ~~( 慎用)~~

- 稀疏索引 和关系型数据库中的索引不同？
- 有些文档可能没有索引这个字段，建立稀疏索引就把这种过滤掉了。

- 索引管理 system.indexes db.coll.getIndexes()
- 标识索引 keyname1_dir1_keyname2_dir2....keynameN_dirN 名字，方向
- 修改索引 db.coll.dropIndex("indexname")

#### 特殊的索引和集合

##### 固定集合capped collection

- 事先创建好，大小固定，类似循环队列 在机械硬盘写入速度很快 ~~顺序写入，没有随机访问。如果拥有专属磁盘，没有其他集合的写开销，更快~~

- db.createCollection("my_coll",{"capped":true,"size":100000,"max":100}); 也可以用普通的集合转成固定集合 db.runCommand("convertToCapped":"test","size":100000)，无法将固定集合改成非固定集合，只能删掉
- 自然排序
- 循环游标 tailable cursor 判断cursor是否tailable 一直循环处理，直到cursor死了~~（灵感来自tail命令）~~

- 没有_id索引的集合，在插入上带来速度提上，但是不符合mongod复制策略

##### TTL索引

- 创建索引有个expireAfterSecs参数 db.foo.ensureIndex({}"lastUpdated":1},{"expireAfterSecs":60\*60\*24})

##### 全文本索引

- 自然语言处理？

- 优化的全文本索引

- ##### 在其他语言中搜索，设定语言

地理空间索引2dsphere

- 复合地理空间索引
- 2D索引

##### 使用GridFS存储文件

- 使用场景，不经常改变的需要连续访问的大文件，缺点性能低，文件是多个文档，无法同一时间对所有文档加锁
- mongofiles put foo.txt get foo.txt

#### 聚合

##### 聚合框架

- 管道pipeline 投射project 过滤filter 分组group 排序sort限制limit跳过skip，都在内存中进行，顺序不影响结果~~（但可能影响性能）~~

```javascript
db.articles.aggregate({"$project"：{"author"：1}}，

{"$group":{"_id":"author","count":{"$sum":1}}},

{"$sort":{"$count":-1}},

{"$limit":5})
```

$match 最开始用可以用上索引减小结果集

$project 修改字段前先用上索引

- 管道表达式 数学表达式 $add $ subtract $multiply $divide $mod 都是接一个数组对象的

- 日期表达式 $year $month $week $dayOfMonth $dayOfWeek $dayOfYear $hour $minute $second

- 字符串表达式 $substr $concat $toLower:expr $toUpper:expr

- 逻辑表达式

- $cmp $strcasecmp $eq ne ge get lt lte and or not

- $cond :[boolexpr,trueexpr, falseexpr] $ifNull:[expr,replacementexpr]


$group 分组 ~~SQL - groupby~~

- 算术操作符 $sum $average:value
- 极值操作符 $max:expr $min:expr $first:expr $last:expr
- 数组操作符 $addToSet $push
- 分组行为不能用于流式工作，有个归结的过程，是个整体
- $unwind 拆分成独立的文档
- $sort limit skip
- 使用管道开始阶段前尽可能把多于的文档和字段过滤掉，可以排序来方便使用索引 $match

##### mapreduce？

##### 聚合命令 ~~和上面的不一样，但是感觉差不多。~~

- db.col.count()
- runCommand({"distinct":"key1","..."}
- runCommand({"group":} SQL group by

#### 应用程序设计

注意一致性，以及mongodb不支持事务

### 复制

#### 创建副本集 replica set

副本集概念 大多数，半数以上，低于半数，全部降备

选举机制

选举仲裁者 最多一个 arbiter 只参与选举，放在外部观察的故障域中，与其他成员分开，尽量不要用，虽然轻量，极端场景 1主1备1仲裁，主挂掉，备升主，新主机还要承担起复制备机的责任

尽量使用奇数个数据成员

优先级与被动成员

隐藏成员~~？为啥有这个设定~~

延迟备份节点，主节点意外被毁被删库还能活过来 ~~不支持回滚只好这么搞~~

备份节点可以手动设定不创建索引（得是被动成员~~，优先级为0~~）

#### 副本集的组合

同步 操作日志oplog，主节点local数据库的一个固定集合，备份节点查这个集合来进行复制，每个节点维护自己的oplog，每个成员都可以作为同步源提供给其他成员使用

- oplog同一条记录执行一次和执行多次效果一致

初始化同步 会先将现有的数据删除 克隆 通过oplog复制数据，然后复制oplog 然后建索引

- 如果当前节点远远落后于同步源，oplog通不过城最后一步就是将创建索引期间的所有操作全同步过来，防止该成员成为备份节点
- 克隆可能损坏同步元的工作集?
- 克隆或创建索引耗时过长，导致新成员与同步源oplog脱节 初始化同步无法正常进行

处理陈旧数据 stale 会从成员中的oplog（足够详尽）中同步恢复，如果都没有参考价值，这个成员的复制操作就会停止，这个成员需要重新进行完全同步

- 心跳 让主节点知道自己是否满足集合的大多数条件
- 成员状态 主节点备份节点
- STARTUP成员刚启动 ->STARTUP2初始化同步 ->RECOVERING 成员运转正常，但暂时还不能处理读取请求 比如成为备份节点前的准备活动，在处理非常耗时的操作（压缩，replSetMaintenance），成员脱节
- ARBITER 仲裁者
- DOWN变的不可达 UNKNOWN 无法到达其他成员 分别描述对端和自己
- REMOVED移除工作集
- ROLLBACK 数据回滚
- FATAL发生了不可挽回的错误 grep replSet FATAL 通常只能重启服务器

- 选举 选举通常很快，太多错误发生比较倒霉的话可能花费较长
- 回滚
- 一个场景，假如主节点op写写死了，然后选举新的主节点没有这条记录，则原主节点需要回滚
- 如果回滚失败，备分节点差的太多，升主回滚内容太多，mongodb受不了。

#### 从应用程序连接副本集

##### 主节点崩溃的错误？最后一次操作成功失败？留给应用程序去查询

- db.runCommand({"getLastError":1,"w":majority})检查是否写入操作被同步到了副本集的大多数 阻塞，可以设置超时时间，阻塞不一定失败，超时不一定失败

- 使用majority选项可以避免一场写入失败导致的回滚丢失。一直阻塞直到大家都有这条数据，或失败。
- "w"也可以设定其他值，值包含主节点。应该设置成n+1 ~~默认1~~

##### 自定义复制保证规则

- 保证复制到每个数据中心的一台服务器上
- 重写rs.config~~，rs.reconfig(config)~~ 添加字段
- 隐藏节点到底是干啥的？

##### 将读请求发送到备份节点

- 对一致性要求不是特别的高
- 分布式负载~~（另一个选择，分片分布式负载）~~
- 何时可以从备份节点读取数据？
- 失去主节点时，应用程序进入只读状态-》主节点优先

#### 管理

##### 维护独立的成员

- 单机模式启动成员 改端口，重启时不使用replSet选项，然后访问维护，其他成员会连接失败，认为它挂了，维护结束后重新以原有的参数启动，自动连接原来的副本集，进行同步

##### 副本集设置

local.system.replSet

```javascript
var config = {"_id":setname,

"members":["_id":0,"host":host1,

"_id":1,"host":host2,

"_id":2,"host":host3

]}

re.initiate(config)
```

修改副本集成员rs.add remove reconfig

修改成员状态 re.stepDown降备rs.freeze (time)在time时间内阻止升主

使用维护模式 RECOVERING replSetManitenanceMode

监控复制

获取状态 replSetGetStatus

复制图谱，指定复制syncFrom

- 复制循环
- 禁用复制链，强制从主节点复制

计算延迟 lag

调整oplog大小 维护工作的时间窗，超过改时间就不得不重新进行完全同步

- 在被填满之前，没有办法确认大小~~，即使他是个capped collection~~，也不可以运行时调整大小，~~因为他是个capped collection~~

- 修改步骤，如果是主节点，先退位，关闭服务器，单机模式启动，临时将oplog中最后一条insert操作保存到其他集合中 **确认保存成功** 删除当前oplog，创建一个新的oplog，将最后一条操作记录写回oplog**确保写入成功**

```javascript
var cursor = db.oplog.rs.find({"op":i})
var lastInser = cusor.sort({"$narutal":-1}).limit(1).next()
db.tempLastOp.save(lastInsert)
db.tempLastOp.findOne()
db.oplog.rs.drop()
db.createCollection("oplog.rs",{"capped":1,"size":10000})
var temp = db.tempLastOp.findOne()
db.oplog.rs.insert(temp)
db.oplog.rs.findOne()
```


##### 从延迟备份节点中恢复

- 简单粗暴方法，关闭所有其他成员，删掉其他成员的数据，重启所有成员，数据量大可能会过载
- 稍作修改，关闭所有成员，删掉其他成员的数据，把延迟备份节点数据文件复制到其他数据目录，重启所有成员，所有服务器都与延迟被分界点拥有同样大小的oplog

##### 创建索引

创建索引消耗巨大，成员不可用，避免最糟糕的情况，所有成员节点同时创建索引

- 可以每次只在一个成员创建索引，分别备份节点单机启动创建索引然后重新启动，然后主节点创建索引
- 可以直接创建，选择负载较少的空闲期间
- 修改读取首选项，在创建节点期间把读分散在备份节点上
- 主节点创建索引后，备份节点仍然会复制这个操作，但是由于备份节点中已经有同样的索引，实际上不会再次创建索引

- 让主节点退化为备份节点，执行上面的步骤，这时就会发生故障转移
- 可以使用这个技术为某个备份节点创建与其他成员不同的索引，在离线数据处理时非常有用？
- 但是如果某个备份节点的索引与其他成员不同，它永远不会成为主节点，应该将它的优先级设为0
- 如果要创建唯一的索引，需要确保主节点中没有被插入重复的数据，或者首先为主节点穿件唯一索引，否则主节点重复数据，备份节点复制出错，备份节点下线，你不得不单机启动，删除索引，重新加入副本集

##### 在预算有限的情况下进行复制

没有多台高性能服务器，考虑将备份节点只用于灾难恢复

- "priority":0 优先级0， 永远不会成为主节点
- "hidden":1 隐藏，客户端无法将读请求发送给他
- "buildIndexes":0 optional 备份节点创建索引的话开极大地降低备份节点的性能。如果不在备份节点上创建索引，从备份节点上恢复数据需要重新创建索引
- "votes":0 只有两台服务器的情况下，备份节点挂掉后，主节点仍然一直会是主节点，不会因为达不到大多数要求而推诿，如果还有第三台服务器，设为仲裁者

##### 主节点如何跟踪延迟

local.me local.slaves

#####　主从模式　传统模式，会被废弃

从主从模式切换到副本集模式　

- 停止所有系统的写操作哦，关闭所有mongod 使用--replSet选项重启主节点不再使用--master 初始化这个只有一个成员的副本集，这个成员会成为副本集中的主节点，使用--replSet和--fastsync启动从节点，使用rs.add将之前的从节点添加到副本集，然后去掉fastsync

让副本集模仿主从模式行为

- 除了主节点，都是优先级0投票0 备份节点挂了无所谓，主节点不会退位，主节点下线手动选父节点，指定优先级和投票~~，运行rs.reconfig(config,{"force",1})~~



### 分片

##### 配置分片 数据分片

##### 拆分块

- 有服务器不可达，尝试拆分，拆分失败 拆分风暴
- mongos频繁重启，,重新记录点，永远达不到阈值点

##### 均衡器 config.locks

均衡阈值

#### 选择片键

如何在多个可用的片键中作出选择？不同使用场景中的片键选择？哪些键不能作为片键？自定义数据分发的可选策略？如何手动对数据分片

##### 分片的目的

- 减少读写延迟？将请求分布在近的机器或高性能服务器
- 增大读写吞吐量？集群1000次/20 ms 可能需要5000次/20ms，需要提高并行，保证请求均匀分布在各个集群成员上
- 增加系统资源？每GB数据提供Mongodb更多的可用RAM，使工作集尽量小

##### 数据分发

- 升序片键 date ObjectId

- 随机分发片键
- 基于位置片键 tag

##### 片键策略

- 散列片键 数据加载速度
- 缺点 无法范围查询
- 无法使用unique和数组字段
- 浮点型的值会被先取整，然后算hash

- GridFStab的散列片键
- 流水策略，一个SSD接着写，指定tag，更新tag范围，把片转到其他磁盘上
- 多热点？

##### 片键规则和指导方针

- 不能是数组
- 片键的势要高一些，或者组合起来

#####　控制数据分发

- addShardTag第二个参数可以指定高低，然后tagrange将不同集合放到不同的分片上。

- 手动分片 moveChunk

#### 分片管理

检查集群状态 sh.status() use config config.shards config.chunks config.collections cofig.changelog



### 应用管理

了解应用的动态

mongotop

mongostat

- insert/query/update/delete/getmore/command

- fulshed mongod将数据刷新到磁盘的次数
- mapped所映射的内存大小，约等于数据目录大小
- vsize 虚拟内存大小，通常为数据目录二倍
- res正在使用的内存大小
- locked db锁定时间最长的数据库
- qrw 阻塞的读写队列大小
- arw正在读写的客户端数量
- netin 网络传输进来的字节数
- netOut网络传输输出的字节数
- conn打开的连接数

数据管理

身份认证

建立和删除索引

OOM Killer 日志在/var/log/messages

数据预热

```shell
for file in /data/db/* do

dd if=$file of=/dev/null

done
```

- fine-grained 细粒度的预热

- 将集合移动至内存

```javascript
db.runCommand({"touch":"logs","data":1,"index":1})
```

- 加载特定的索引 覆盖查询
- 加载最新的文档
- 加载最近创建的文档 结合ObjectId
- 重放应用使用记录 诊断日志？

##### 压缩数据

- 会进入RECOVERING模式

- 运行repair来回收磁盘空间，需要有当前数据大小同样的空闲空间，或指定外部的磁盘目录，修复路径。

##### 移动集合

- renameCollection 改集合名。不用担心性能消耗
- 数据库间移动，只能dump&restore也可以用cloneCollection

预分配数据文件

```shell
if test $# -lt 2 || test $# -gt 3 then
echo "$0 <db> <number-of-files> "
fi

db =$1
num=$2
for i in {0..$num}
do
echo "preallocation %db.$i"
head -c 2146435072 /dev/zero >$db.$i
done
```



#### 持久性

日记系统

批量提交写入操作 100ms 或写入数据MB以上

设定提交时间间隔

关闭日记系统 数据可能损坏，两种替代方案

- 替换数据文件，用副本集的，或者初始化同步，重启同步
- 修复数据文件，mongod内置（repair）或mongodump 耗时较长

关于mongod.lock文件，别手动删。。恢复数据再搞。也有可能是隐蔽的异常退出

MongoDB无法保证的事项

- 检验数据损坏
- 副本集的持久性

### 服务器管理

停止和启动MongoDB

监控MongoDB

- 内存使用情况
- 跟踪监测缺页中断
- 索引树的脱靶次数
- IO延迟
- 后台刷新平均时间，将脏页写入磁盘所花费的时间
- 跟踪监测性能状况
- 空余空间
- 监控副本集
- oplog长度

备份

- 文件系统快照，开启日记系统，文件系统本身支持快照
- 复制数据文件，先db.fsyncLock() 然后cp就完了
- 不要同时使用fsyncLock和mongodump 会死锁

部署

