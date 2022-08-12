---
layout: post
title: blog review 第十六期
categories: [review]
tags: [fork,Monarch,rocksdb,epoch, postgresql,DuckDB,art]
---
准备把blog阅读和paper阅读都归一，而不是看一篇翻译一篇，效率太低了

后面写博客按照 paper review，blog review，cppcon review之类的集合形式来写，不一篇一片写了。太水了

<!-- more -->

## [fork() without exec() is dangerous in large programs](https://www.evanjones.ca/fork-is-dangerous.html)

老生常谈了。fork完要立即exec。或者像nginx那样的用法，否则会有问题

## [Monarch: Google’s Planet-Scale In-Memory Time Series Database](https://www.micahlerner.com/2022/04/24/monarch-googles-planet-scale-in-memory-time-series-database.html)

![](https://www.micahlerner.com/assets/monarch/fig1.png)

很有意思，有点map-reduce的感觉。mixer无限扩，index负责一部分数据拉取

父mixer接受请求 推送给所有子mixer，子mixer再推送给子index，拿到数据 mixer汇总

## [Removing Double-Logging with Passive Data Persistence in LSM-tree based Relational Databases](https://www.usenix.org/conference/fast22/presentation/huang)

代码 https://github.com/ericaloha/MyRocks-PASV

改rocksdb，加上epoch。挺有意思。不过真的能保证数据不丢吗？

## [My Notes on GitLab Postgres Schema Design](https://shekhargulati.com/2022/07/08/my-notes-on-gitlabs-postgres-schema-design/)

一些PG使用经验

PK  选对类型，bigserial，bigint等等。考虑清楚

![](https://whyjava.files.wordpress.com/2022/06/pk_types.png)

使用两套id ，避免数据被猜到？

```sql
CREATE TABLE issues (
    id integer NOT NULL,
    title character varying,
      project_id integer,
    iid integer,
    // rest of the columns removed
)
```

使用text加上条件

```sql
create table text_exp (id bigint primary key, 
s text default gen_random_uuid() not null,
CONSTRAINT check_15e644d856 CHECK ((char_length(s) <= 200)));
```

命名尽可能小写下划线，类别用前缀来搞定

时间戳加不加zone信息？create_at可以不加，但close_at得加。区别在用这个时间戳谁用，系统内部meta的话无所谓，但是外部用户可见的话可能得考虑用户体验

外键限制。不懂

```sql
ALTER TABLE ONLY todos
    ADD CONSTRAINT fk_rails_a27c483435 FOREIGN KEY (group_id) REFERENCES namespaces(id) ON DELETE CASCADE;
 
ALTER TABLE ONLY projects
    ADD CONSTRAINT fk_projects_namespace_id FOREIGN KEY (namespace_id) REFERENCES namespaces(id) ON DELETE RESTRICT;
 
ALTER TABLE ONLY authentication_events
    ADD CONSTRAINT fk_rails_b204656a54 FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;
```

三种分片模式

范围，比如时间范围，audit_events  web_hook_logs
？？这样倾斜很严重吧

list分区，这种要定制枚举列表，和范围差不太多其实 loose_foreign_keys_deleted_records

hash没啥说的

## [Persistent Storage of Adaptive Radix Trees in DuckDB](https://duckdb.org/2022/07/27/art-storage.html)

代码在这里 https://github.com/duckdb/duckdb/tree/2c623978d700443665d519282ee52891e4573a3d/src/include/duckdb/execution/index/art

## [小红书自研KV存储架构如何实现万亿量级存储与跨云多活](https://zhuanlan.zhihu.com/p/537691368)

proxy压缩网络包，挺有意思

## [DGraph: A Large-Scale Financial Dataset for Graph Anomaly Detection](https://zhuanlan.zhihu.com/p/546872168)

欺诈者和普通用户通常具有不同的图结构和邻居特征, 有意思

很多数据能说明问题，比如联系人多，比如使用共同的联系人/默认值等等。数据可以挖掘的点有很多。不过这种指向型怎么挖掘出来呢

## [服务器内存故障预测居然可以这样做！](https://mp.weixin.qq.com/s?__biz=MzI4NjY4MTU5Nw==&mid=2247494145&idx=2&sn=4b462c9fc4d9bb1ef2db3fded0a955bb)

edac使用 https://github.com/grondo/edac-utils/

## [使用tcmalloc抓内存泄漏](https://gperftools.github.io/gperftools/heap_checker.html)

 env HEAPPROFILE binxx

会生成调用图，啥都看得清清楚楚

## [Cache made consistent: Meta’s cache invalidation solution](https://engineering.fb.com/2022/06/08/core-data/cache-invalidation/)

![](https://engineering.fb.com/wp-content/uploads/2022/06/Cache-made-consisent-image-8.png)

写了一个库来跟踪CURD的时间窗。太复杂了

## tcp_autocorking发包延迟

每次写都要调用一下？

```c
int zero = 0;
setsockopt(sock_fd, IPPROTO_TCP, TCP_CORK, &zero, sizeof(zero));
```

## [MySQL 源码解读 —— Binlog 事件格式解析](https://zhjwpku.com/2020/11/01/binlog-event-format.html)

## [Abase2：字节跳动新一代高可用 NoSQL 数据库](https://mp.weixin.qq.com/s/UaiL8goZ_u0Jo9dDNnBP0w?st=94B8665CDB3BAF6D999E08498014C6CAE77FA2FA36E4F6B8469B51890F2024D2750FE6279586F3FEF8D537D05085FBA412EA2615AB2B4C24AC6DF548F90529381F18E8238A2AD1B121A400A5214E01D3F5128BE506BB16771C68D1BFA6B7EF9BE4A238376EF2C7F64A3899345B2F6935896EA66DC3763C00B27273E05FD13DC1D2F38A5320AE62C7A307DA8A950483FA7E8E3A4BBC62E7BFF600181CF8EF119D954AD40431186127E0A474CB324703A708F7B529A202CDB04B0925C4748A1CA39601BACC1476121EE2B3C49481C3213B&vid=1688850557715316&cst=17B6CC5655DE4CC871465F3264784A5E0E91499C06FF8DDB1D743D061F623A384E7A1C065DFE304A847ADF15A6B693A4&deviceid=7cd8b283-1663-4180-9b21-44ee69551c54&version=4.0.8.90588&platform=mac)

ZSet: 广泛应用于榜单拉链等在线业务场景，区别于直接使用 String+Scan 方式进行包装，Abase 在 ZSet 结构中做了大量优化，从设计上避免了大量 ZIncrBy 造成的读性能退化；

问了一下zset的实现。人家用的最终一致性+cache抗一层。直接用rocksdb写性能太差

```txt
多点写入带来可用性提升的同时，也带来一个问题，相同数据在不同 Replica 上的写入可能产生冲突，检测并解决冲突是多写系统必须要处理的问题。

为了解决冲突，我们将所有写入数据版本化，为每次写入的数据分配一个唯一可比较的版本号，形成一个不可变的数据版本。

Abase 基于 Hybrid Logical Clock 算法生成全局唯一时间戳，称为 HLC timestamp，并使用 HLC timestamp 作为数据的版本号，使得不同版本与时间相关联，且可比较。

通过业务调研，我们发现在发生数据冲突时，大部分业务希望保留最新写入的数据，部分业务自身也无法判断哪个版本数据更有意义（复杂的上下游关系），反而保留最新版本数据更简洁也更有意义，因此 Abase 决定采用 Last Write Wins 策略来解决写入冲突。

在引擎层面，最初我们采用 RocksDB 直接存储多版本数据，将 key 与版本号一起编码，使得相同 key 的版本连续存储在一起；查询时通过 seek 方式找到最新版本返回；同时通过后台版本合并任务和 compaction filter 将过期版本回收。

在实践中我们发现，上述方式存在几个问题：

    多版本数据通常能在短时间内（秒级）决定哪个版本最终有效，而直接将所有版本写入 RocksDB，使得即使已经确定了最终有效数据，也无法及时回收无效的版本数据；同时，使用 seek 查询相比 get 消耗更高，性能更低。
    需要后台任务扫描所有版本数据完成无效数据的回收，消耗额外的 CPU 和 IO 资源。
    引擎层与多版本耦合，使得引擎层无法方便地做到插件化，根据业务场景做性能优化。

为了解决以上问题，我们把引擎层拆分为数据暂存层与通用引擎层，数据多版本将在暂存层完成冲突解决和合并，只将最终结果写入到底层通用引擎层中。

得益于 Multi-Leader 与 Anti-Entropy 机制，在正常情况下，多版本数据能在很小的时间窗口内决定最终有效数据，因此数据暂存层通常只需要将这个时间窗口内的数据缓存在内存中即可。Abase 基于 SkipList 作为数据暂存层的数据结构（实践中直接使用 RocksDB memtable），周期性地将冲突数据合并后写入底层
```


CRDT也挺有意思的

```txt
CRDTs

对于幂等类命令如 Set，LWW 能简单有效地解决数据冲突问题，但 Redis String 还需要考虑 Append, Incrby 等非幂等操作的兼容，并且，其它例如 Hash, ZSet 等数据结构则更为复杂。于是，我们引入了 CRDT 支持，实现了 Redis 常见数据结构的 CRDT，包括 String/Hash/Zset/List，并且保持语义完全兼容 Redis。

以 IncrBy 为例，由于 IncrBy 与 Set 会产生冲突，我们发现实际上难以通过 State-based 的 CRDT 来解决问题， 故而我们选用 Operation-based 方案，并结合定期合并 Operation 来满足性能要求。

为了完全兼容 Redis 语义，我们的做法如下：

    给所有 Operation 分配全球唯一的 HLC timestamp，作为操作的全排序依据；
    记录写入的 Operation 日志（上文 ReplicaLog）， 每个 key 的最终值等于这些 Operation 日志按照时间戳排序后合并的结果。副本间只要 Operation 日志达成一致，最终状态必然完全一致；
    为了防止 Operation 日志过多引发的空间和性能问题，我们定期做 Checkpoint，将达成一致的时间戳之前的操作合并成单一结果；
    为了避免每次查询都需要合并 Operation 日志带来的性能开销，我们结合内存缓存，设计了高效的查询机制，将最终结果缓存在 Cache 中，保证查询过程不需要访问这些 Operation 日志。
```
## TODO

- https://github.com/weicao/cascadb/tree/master/
- [写一个代码分析调用工具](https://github.com/sighingnow/libclang/blob/master/python/examples/cindex/cindex-dump.py)

---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>
