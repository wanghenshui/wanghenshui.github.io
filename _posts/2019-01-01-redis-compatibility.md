---
layout: post
title: redis release note 与 redis命令cheatsheet
categories: database
tags: [redis, c]
---
  



## redis release note

|redis版本 | 功能点 |
| --------- | ------------------------------------------------------------ |
| 2.6 | Lua脚本支持 |
| 2.6 | 新增PEXIRE、PTTL、PSETEX过期设置命令，key过期时间可以设置为毫秒级 |
| 2.6 | 新增位操作命令：BITCOUNT、BITOP |
| 2.6 | 新增命令：dump、restore，即序列化与反序列化操作 |
| 2.6 | 新增命令：INCRBYFLOAT、HINCRBYFLOAT，用于对值进行浮点数的加减操作 |
| 2.6 | 新增命令：MIGRATE，用于将key原子性地从当前实例传送到目标实例的指定数据库上 |
| 2.6 | 放开了对客户端的连接数限制 |
| 2.6 | hash函数种子随机化，有效防止碰撞 |
| 2.6 | SHUTDOWN命令添加SAVE和NOSAVE两个参数，分别用于指定SHUTDOWN时用不用执行写RDB的操作 |
| 2.6 | 虚拟内存Virtual Memory相关代码全部去掉 |
| 2.6 | sort命令会拒绝无法转换成数字的数据模型元素进行排序 |
| 2.6 | 不同客户端输出缓冲区分级，比如普通客户端、slave机器、pubsub客户端，可以分别控制对它们的输出缓冲区大小 |
| 2.6 | 更多的增量过期(减少阻塞)的过期key收集算法 ,当非常多的key在同一时间失效的时候,意味着redis可以提高响应的速度 |
| 2.6 | 底层数据结构优化，提高存储大数据时的性能 |
| 2.8 | 引入PSYNC，主从可以增量同步，这样当主从链接短时间中断恢复后，无需做完整的RDB完全同步 |
| 2.8 | 从显式ping主，主可以扫描到可能超时的从 |
| 2.8 | 新增命令：SCAN、SSCAN、HSCAN和ZSCAN |
| 2.8 | crash的时候自动内存检查 |
| 2.8 | 新增键空间通知功能，客户端可以通过订阅/发布机制，接收改动了redis指定数据集的事件 |
| 2.8 | 可绑定多个IP地址 |
| 2.8 | 可通过CONFIGSET设置客户端最大连接数 |
| 2.8 | 新增CONFIGREWRITE命令，可以直接把CONFIGSET的配置修改到redis.conf里 |
| 2.8 | 新增pubsub命令，可查看pub/sub相关状态 |
| 2.8 | 支持引用字符串，如set 'foo bar' "hello world\n" |
| 2.8 | 新增redis master-slave集群高可用解决方案（Redis-Sentinel） |
| 2.8 | 当使用SLAVEOF命令时日志会记录下新的主机 |
| 3.0 | 实现了分布式的Redis即Redis Cluster，从而做到了对集群的支持 |
| 3.0 | 全新的"embedded string"对象编码方式，从而实现了更少的缓存丢失和性能的提升 |
| 3.0 | 大幅优化LRU近似算法的性能 |
| 3.0 | 新增CLIENT PAUSE命令，可以在指定时间内停止处理客户端请求 |
| 3.0 | 新增WAIT命令，可以阻塞当前客户端，直到所有以前的写命令都成功传输并和指定的slaves确认 |
| 3.0 | AOF重写过程中的"last write"操作降低了AOF child -> parent数据传输的延迟 |
| 3.0 | 实现了对MIGRATE连接缓存的支持，从而大幅提升key迁移的性能 |
| 3.0 | 为MIGRATE命令新增参数：copy和replace，copy不移除源实例上的key，replace替换目标实例上已存在的key |
| 3.0 | 提高了BITCOUNT、INCR操作的性能 |
| 3.0 | 调整Redis日志格式 |
| 3.2 | 新增对GEO（地理位置）功能的支持 |
| 3.2 | 新增Lua脚本远程debug功能 |
| 3.2 | SDS相关的优化，提高redis性能 |
| 3.2 | 修改Jemalloc相关代码，提高redis内存使用效率 |
| 3.2 | 提高了主从redis之间关于过期key的一致性 |
| 3.2 | 支持利用upstart和systemd管理redis进程 |
| 3.2 | 将list底层数据结构类型修改为quicklist，在内存占用和RDB文件大小方面有极大的提升 |
| 3.2 | SPOP命令新增count参数，可控制随机删除元素的个数 |
| 3.2 | 支持为RDB文件增加辅助字段，比如创建日期，版本号等，新版本可以兼容老版本RDB文件，反之不行 |
| 3.2 | 通过调整哈希表大小的操作码RDB_OPCODE_RESIZEDB，redis可以更快得读RDB文件 |
| 3.2 | 新增HSTRLEN命令，返回hash数据类型的value长度 |
| 3.2 | 提供了一个基于流水线的MIGRATE命令，极大提升了命令执行速度 |
| 3.2 | redis-trib.rb中实现将slot进行负载均衡的功能 |
| 3.2 | 改进了从机迁移的功能 |
| 3.2 | 改进redis sentine高可用方案，使之可以更方便地监控多个redis主从集群 |
| 4.0 | 加入模块系统，用户可以自己编写代码来扩展和实现redis本身不具备的功能，它与redis内核完全分离，互不干扰 |
| 4.0 | 优化了PSYNC主从复制策略，使之效率更高 |
| 4.0 | 为DEL、FLUSHDB、FLUSHALL命令提供非阻塞选项，可以将这些删除操作放在单独线程中执行，从而尽可能地避免服务器阻塞 |
| 4.0 | 新增SWAPDB命令，可以将同一redis实例指定的两个数据库互换 |
| 4.0 | 新增RDB-AOF持久化格式，开启后，AOF重写产生的文件将同时包含RDB格式的内容和AOF格式的内容，其中 RDB格式的内容用于记录已有的数据，而AOF格式的内存则用于记录最近发生了变化的数据 |
| 4.0 | 新增MEMORY内存命令，可以用于查看某个key的内存使用、查看整体内存使用细节、申请释放内存、深入查看内存分配器内部状态等功能 |
| 4.0 | 兼容NAT和Docker |
| 5.0 | 新的流数据类型(Stream data type) https://redis.io/topics/streams-intro |
| 5.0 |  新的 Redis 模块 API：定时器、集群和字典 API(Timers, Cluster and Dictionary APIs)|
| 5.0 |  RDB 现在可存储 LFU 和 LRU 信息|
| 5.0 |  redis-cli 中的集群管理器从 Ruby (redis-trib.rb) 移植到了 C 语言代码。|执行 redis-cli --cluster help 命令以了解更多信息|
| 5.0 |  新的有序集合(sorted set)命令：ZPOPMIN/MAX 和阻塞变体(blocking variants)|
| 5.0 |  升级 Active defragmentation 至 v2 版本|
| 5.0 |  增强 HyperLogLog 的实现|
| 5.0 |  更好的内存统计报告|
| 5.0 |  许多包含子命令的命令现在都有一个 HELP 子命令|
| 5.0 |  客户端频繁连接和断开连接时，性能表现更好|
| 5.0 |  许多错误修复和其他方面的改进|
| 5.0 |  升级 Jemalloc 至 5.1 版本|
| 5.0 |  引入 CLIENT UNBLOCK 和 CLIENT ID|
| 5.0 |  新增 LOLWUT 命令 http://antirez.com/news/123|
| 5.0 |  在不存在需要保持向后兼容性的地方，弃用 "slave" 术语|
| 5.0 |  网络层中的差异优化|
| 5.0 |  Lua 相关的改进：将 Lua 脚本更好地传播到 replicas / AOF， Lua 脚本现在可以超时并在副本中进入 -BUSY 状态|
| 5.0 |  引入动态的 HZ(Dynamic HZ) 以平衡空闲 CPU 使用率和响应性|
| 5.0 |  对 Redis 核心代码进行了重构并在许多方面进行了改进|



## redis cheatsheet

| 命令 | 版本 | 复杂度 | 可选 | 返回值 |
| ------------------------------------------------------------ | -------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| SET | 1.0 | O1 | 2.6.12后增加EX PX NX XX | 2.6.12永远回复ok，之后如果有NX XX导致的失败，NULL Bulk Reply |
| SETNX | 1.0 | O(1) | | 1/0 |
| SETEX | 2.0 | O(1) | set +expire 院子 | ok |
| PSETEX | 2.6 | O(1) | s时间单位毫秒 | ok |
| GET | 1.0 | O(1) | | value/nil/特定的错误字符串 |
| GETSET | 1.0 | O(1) | | value/nil/特定的错误字符串 |
| STRLEN | 2.2 | O(1) | | 不存在返回0 |
| APPEND | 2.0 | 平摊O(1) | | 返回长度 |
| SETRANGE | 2.2 | 如果本身字符串短。平摊O(1)，否则为O(len(value)) | 如果字符串长会阻塞（？不是inplace？） | 返回长度 |
| GETRANGE | 2.4 | O(N)N为返回字符串的长度 | 2.0以前是SUBSTR | 子串 |
| INCR | 1.0 | O(1) | | 返回+1之后的值字符串，如果不是数字，会报错(error) ERR value is not an integer or out of range |
| INCRBY | 1.0 | O(1) | 负数也可以。 | 返回增量之后的值字符串 |
| INCRBYFLOAT | 2.6 | O(1) | | 返回增量之后的值字符串 |
| DECR | 1.0 | O(1) | | 返回-1之后的值字符串 |
| DECRBY | 1.0 | O(1) | | 返回减法操作之后的值字符串 |
| MSET | 1.0.1 | O(N) N为键个数 | multiple set，原子性 | |
| MSETNX | 1.0.1 | O(N) N为键个数 | 都不存在则进行操作，否则都不操作。 | |
| MGET | 1.0.0 | O(N) N为键个数 | | 如果有不存在的键，返回nil |
| SETBIT | 2.2 | O(1) | `offset` 参数必须大于或等于 `0` ，小于 2^32 (bit 映射被限制在 512 MB 之内) | 该位原来的值 |
| GETBIT | 2.2 | O(1) | | |
| BITCOUNT | 2.6 | O(N) | | |
| BITPOS | 2.8.7 | O(N) | | |
| BITOP | 2.6 | O(N) | | |
| BITFIELD | 3.2 | O(1) | ？这个命令的需求？ | |
| HSET | 2.0 | O(1) | | 新的值返回1 覆盖了返回0 |
| HSETNX | 2.0 | O(1) | | 设置成功返回1，已经存在放弃执行返回0 |
| HGET | 2.0 | O(1) | | 不存在返回nil |
| HEXISTS | 2.0 | O(1) | | 字段存在返回1不存在返回0 |
| HDEL | 2.0 | O(N) N为删除的字段个数 | 2.4之前只能一个字段一个字段的删除，如果要求原子需要MULTI+EXEC，后续版本支持多字段删除 | 被成功移除的字段数量 (<=N) |
| HLEN | 2.0 | O(1) | | 返回字段数量，不存在返回0 |
| HSTRLEN | 3.2 | O(1) | 类似STRLEN，操作哈希表的字段 | 返回字段关联的值的字符串长度 |
| HINCRBY | 2.0 | O(1) | 类似INCRBY，操作哈希表的字段 | |
| HINCRBYFLOAT | 2.6 | O(1) | 类似INCRBYFLOAT | |
| HMSET | 2.0 | O(N) N为filed-value数量 | 类似MSET 能不能用在集群？ | OK |
| HMGET | 2.0 | O(N) | 类似MGET 能不能用在集群？ | 不存在的字段返回nil |
| HKEYS | 2.0 | O(N)N为哈希表大小？ | | 返回所有字段的一个表(list or set)不存在返回空表 |
| HVALS | 2.0 | O(N) | | 返回所有字段对应的值的表 |
| HGETALL | 2.0 | O(N) | | 返回字段和值的表，奇数字段偶数值 |
| HSCAN | 2.0 | O(N)？ | 类似SCAN | |
| LPUSH | 1.0 | O(1) | 2.4以前只接受单个值，之后接受多个值。 | 返回列表长度 |
| LPUSHX | 2.2 | O(1) | key不存在什么也不做 | 返回长度，不存在返回0 |
| RPUSH | 1.0 | O(1) | 2.4以前只接受单个值 | |
| RPUSHX | 2.2 | O(1) | | |
| LPOP | 1.0 | O(1) | | 不存在返回nil |
| RPOP | 1.0 | O(1) | | 不存在返回nil |
| RPOPLPUSH | 1.2 | O(1) | 原子的，原地址右边弹出目的地址左边插入。如果源地址目的地址相同就是旋转列表，可以实现循环列表 | 返回弹出元素，不存在就是nil |
| LREM | 1.0 | O(N) | LREM key count value 移除与value相等的count个值，0表示所有，负数从右向左正数从左向右 | 被移除的数量。 |
| LLEN | 1.0 | O(1) | | 返回列表长度 |
| LINDEX | 1.0 | O(N) N为遍历到index经过的数量 | 为啥不叫LGET，怕使用者漏了index参数吗？参数和GET系命令不一致做个区分？ | 返回下表为index的值，不存在返回nil |
| LINSERT | 2.2 | O(N) N 为寻找目标值经过的值 | | 返回成功后列表的长度。如果没找到目标值pivot，返回-1，不存在或空列表返回0 |
| LSET | 1.0 | O(N) N为遍历到index处的元素个数 | | OK |
| LRANGE | 1.0 | O(S+N) S为start偏移量，N为区间stop-start | LRANGE的区间是全闭区间，包含最后一个元素，注意stop取值范围。不过超出下表范围不会引起命令错误。可以使用负数下表，和python用法一致 | 返回一个列表 |
| LTRIM | 1.0 | O(N) N为被移除元素的数量 | 和LRANGE类似，要注意下标 | OK |
| BLPOP | 2.0 | O(1) | LPOP阻塞版本，timeout0表示不超时 阻塞命令和事务组合没有意义，因为会阻塞整个服务器，其他客户端无法PUSH，会退化成LPOP | |
| BRPOP | 2.0 | O(1) | | |
| BRPOPLPUSH | 2.2 | O(1) | 实现安全队列 | |
| SADD | 1.0 | O(N) N是元素个数 | 2.4版本之前只能一个一个添加 | 返回总数 |
| SISMEMBER | 1.0 | O(1) | | 1/0 |
| SPOP | 1.0 | O(1) | 随机返回一个值并移除， | 值或nil |
| SRANDMEMBER | 1.0 | O(N) N为返回值的个数 | 2.6开始支持count 类似SPOP但是不移除 | 值 nil/数组 |
| SREM | 1.0 | O(N) N为移除的元素个数 | 2.4以前只支持单个移除 | 移除成功的数量 |
| SMOVE | 1.0 | O(1) | 原子的，移除src添加dst | 移除成功1，其他0或者错误 |
| SCARD | 1.0 | O(1) | cardinalty基数 | 不存在返回0 |
| SMEMBERS | 1.0 | O(N) N为集合基数 | | 不存在返回空集合 |
| SSCAN | | | SCAN | |
| SINTER | 1.0 | O(NxM) N是集合最小基数，M是集合个数 | 交集 | |
| SINTERSTORE | 1.0 | O(N*M) | 同上，返回并保存结果 | |
| SUION | 1.0 | O(N) N是所有给定元素之和 | 并集 | |
| SUIONSTORE | 1.0 | O(N) | 同上，返回并保存结果 | |
| SDIFF | 1.0 | O(N) | 差集 | |
| SDIFFSTORE | 1.0 | O(N) | | |
| ZADD | 1.2 | O(M*logN) N 是基数M是添加新成员个数 | 2.4之前只能一个一个加 | 成员数量 |
| ZSCORE | 1.2 | O(1) | HGET和LINDEX api风格 | |
| ZINCRBY | 1.2 | O(logN) | HINCRBY | |
| ZCARD | 1.2 | O(1) | SCARD | |
| ZCOUNT | 2.0 | O(logN) | ZRANGEBYSCORE拼的 | 返回score在所给范围内的个数 |
| ZRANGE | 1.2 | O(logN+M) M结果集基数 N有序集基数 | 从小到大排序 | |
| ZREVRANGE | 1.2 | O(logN+M) M结果集基数 N有序集基数 | 和上面相反 | |
| ZRANGEBYSCORE | 1.05 | O(logN+M) M结果集基数 N有序集基数 | 按照score过滤 | |
| ZREVRANGEBYSCORE | 1.05 | O(logN+M) M结果集基数 N有序集基数 | | |
| ZRANK | 2.0 | O(logN) | | 返回排名，从0开始，从小到大，0最小 |
| ZREVRANK | 2.0 | O(logN) | | 从大到小 0最大 |
| ZREM | 1.2 | O(logN*M) N基数M被移除的个数 | 2.4之前只能删除一个 | 个数 |
| ZREMRANGEBYRANK | 2.0 | O(logN+M) N基数 M被移除数量 | | 被移除的数量 |
| ZREMRANGEBYSCORE | 1.2 | O(logN+M) N基数 M被移除数量 | | 被移除的数量 |
| ZRANGEBYLEX | 2.8.9 | O(logN+M) N基数 M返回元素数量 | 分值相同 字典序 | |
| ZLEXCOUNT | 2.8.9 | O(logN) N为元素个数 | 类似ZCOUNT，前提是分值相同，不然没意义 | 数量 |
| ZREMRANGEBYLEX | 2.8.9 | O(logN+M) N基数 M被移除数量 | 分值相同 | 被移除数量 |
| ZSCAN | | | SCAN | |
| ZUNIONSTORE | 2.0 | 时间复杂度: O(N)+O(M log(M))， `N` 为给定有序集基数的总和， `M` 为结果集的基数。 | | 结果集基数 |
| ZINTERSTORE | 2.0 | O(N*K)+O(M*log(M))， `N` 为给定 `key` 中基数最小的有序集， `K` 为给定有序集的数量， `M` 为结果集的基数。 | 交集 | 结果集基数 |
| ZPOPMAX | 5.0 | O(log(N)*M) M最大值个数 | | |
| ZPOPMIN | 5.0 | O(log(N)*M) | | |
| BZPOPMAX | 5.0 | O(log(N)) | | |
| BZPOPMIN | 5.0 | O(log(N)) | | |
| PFADD | 2.8.9 | O(1) | | 变化返回1不变0 |
| PFCOUNT | 2.8.9 | O(1)，多个keyO(N) | | 个数 |
| PFMERGE | 2.8.9 | O(N) | | OK |
| GEOADD | 3.2 | O(logN) | | |
| GEOPOS | 3.2 | O(logN) | GET | |
| GEODIST | 3.2 | O(logN) | | 返回距离，节点不存在就返回nil |
| GEORADIUS | 3.2 | O(N+logM)N元素个数M被返回的个数 | 范围内所有元素 | |
| GEORADIUSBYMEMBER | 3.2 | O(N+logM) | | |
| GEOHASH | 3.2 | O(logN) | | 字段的hash |
| XADD | 5.0 | O(1) | | |
| XACK | 5.0 | O(1) | | |
| XCLAIM | 5.0 | O(log N) | | |
| XDEL | 5.0 | O(1) | | |
| XGROUP | 5.0 | O(1) | | |
| XINFO | 5.0 | O(N) | | |
| XLEN | 5.0 | O(1) | | |
| XPENDING | 5.0 | O(N) 可以退化为O(1) | | |
| XRANGE | 5.0 | O(N) | | |
| XREAD | 5.0 | O(N) 可以退化为O(1) | | |
| XREADGROUP | 5.0 | O(M) 可以退化为O(1) | | |
| XREVRANGE | 5.0 | O(N) 可以退化为O(1) | | |
| XTRIM | 5.0 | O(N) | | |
| EXISTS | 1.0 | O(1) | | |
| TYPE | 1.0 | O(1) | | 类型 |
| RENAME | 1.0 | O(1) | rocksdb不能in-place改key，seek出来，复制value，写旧key删除，写新key。pika为什么不支持？ | OK |
| RENAMENX | 1.0 | O(1) | 新key不存在才改 | 1成功 |
| MOVE | 1.0 | O(1) | redis支持多库，redis多库数据导入pika？ | 1成功0失败 |
| DEL | 1.0 | O(N) N为key个数 | | |
| RANDOMKEY | 1.0 | O(1) | 怎么实现的O1？pika O(N) | |
| DBSIZE | 1.0 | O(1) | | 所有key数量 |
| KEYS | 1.0 | O(N) | N大会阻塞redis | |
| SCAN | 2.8 | O(1)迭代，O(N)完整迭代 | keys替代品 | |
| SORT | 1.0 | O(N+MlogM) | 返回结果不是in-place，可以STORE保存 | |
| FLUSHDB | 1.0 | O(1) | drop db | OK |
| FLUSHALL | 1.0 | O(1) | drop all db | OK |
| SELECT | 1.0 | O(1) | 切换数据库 | OK |
| SWAPDB | 4.0 | O(1) | 交换数据库 | OK |
| EXPIRE | 1.0 | O(1) | 单位秒 随机的过期时间防止雪崩 | 1成功0失败 |
| EXPIREAT | 1.2 | O(1) | 时间戳 | |
| TTL | 1.0 | O(1) | | 不存在返回-2过期返回-1其余返回时间 |
| PERSIST | 2.2 | O(1) | 去除失效时间 | 1成功 |
| PEXPIRE | 2.6 | O(1) | 毫秒为单位 | 1成功 |
| PEXPIREAT | 2.6 | O(1) | 同expireat | |
| PTTL | 2.6 | O(1) | 同ttl，2.8以前 失败或不存在都返，回-1后来用-2区分不存在 | |
| MULTI | 1.2 | O(1) | 事务块开始 | OK |
| EXEC | 1.2 | 事务块内执行的命令复杂度和 | 执行事务块 | 被打断返回nil |
| DISCARD | 2.2 | O(1) | 放弃事务块内命令 | OK |
| WATCH | 2.2 | O(1) | 乐观锁 | OK |
| UNWATCH | 2.2 | O(1) | 当EXEC DISCARD没执行的时候取消WATCH | OK |
| EVAL | 2.6 | O(1) 找到脚本。其余复杂度取决于脚本本身 | 推荐纯函数，有全局变量会报错 | |
| EVALSHA | 2.6 | 根据脚本的复杂度而定 | 缓存过的脚本。可能不存在 | |
| SCRIPT LOAD | 2.6 | O(N) N为脚本长度 | 添加到脚本缓存 | |
| SCRIPT EXISTS | 2.6 | O(N) N为判断的sha个数 | | 0 1 |
| SCRIPT FLUSH | 2.6 | O(N) N为缓存中脚本个数 | | OK |
| SCRIPT KILL | 2.6 | O(1) | 如果脚本中没有写，能杀掉，否则无效，只能shutdown nosave | |
| SAVE | 1.0 | O(N) N为key个数 | 保存当前快照到rdb，阻塞，保存数据的最后手段 | OK |
| BGSAVE | 1.0 | O(N) | fork执行复制。，lastsave查看bgsave执行成功 | 反馈信息 |
| BGREWRITEAOF | 1.0 | O(N) N为追加到AOF文件中的数据数量 | AOF redis自己会重写，该命令是手动重写 | 反馈信息 |
| LASTSAVE | 1.0 | O(1) | | 时间戳 |
| PUBLISH | 2.0 | O(M+N) channel订阅者数量+模式订阅客户端数量 | | 收到消息的个数 |
| SUBSCRIBE | 2.0 | O(N) N是channel个数 | | |
| PSUBSCRIBE | 2.0 | O(N) N是模式的个数 | 通配符模式。满足该通配符字符串的channel | |
| UNSUBSCRIBE | 2.0 | O(N) N是channel个数 | 不指定则退订所有 | |
| PUNSUBSCRIBE | 2.0 | O(N) N是channel个数 | | |
| PUBSUB CHANNELS<br/>PUBSUB NUMSUB<br/>PUBSUB NUMPAT | 2.8 | O(N) N是频道个数 | 统计信息，活跃频道，频道关注数 频道模式个数 | |
| SLAVEOF | 1.0 | O(1) | SLAVEOF NO ONE升主 | OK |
| ROLE | 2.8.12 | O(1) | | |
| AUTH | 1.0 | O(1) | | |
| QUIT | 1.0 | O(1) | | |
| INFO | 1.0 | O(1) | | |
| SHUTDOWN | 1.0 | O(1) | SAVE QUIT有可能丢失数据 该命令屏蔽了后续的写动作？ | |
| TIME | 2.6 | O(1) | | 时间戳 |
| CLIENT GETNAME CLIENT KILL CLIENT LIST SETNAME  PAUSE  REPLY ID | 2.6.9<br/>2.4 | O(1)<br/>O(N<br/>O(N))<br/>O(1) | | |
| CONFIG SET CONFIG GET CONFIG RESETSTAT CONFIG REWRITE | 2.0...2.8 | O(1)O(N)O(1)O(N) | | |
| PING | 1.0 | O(1) | | pong |
| ECHO | 1.0 | O(1) | | |
| OBJECT | 2.2.3 | O(1) | 查引用次数，编码格式，空闲状态 | |
| SLOWLOG | 2.2.12 | O(1) | | |
| MONITOR | 1.0 | O(N) | 监视命令 | |
| DEBUG OBJECT<br/>DEBUG SEGFAULT | 1.0 | O(1) | 调试命令，查对象信息，模拟segfault | |
| MIGRATE | 2.6 | O(N) | dump key + restore | |
| DUMP | 2.6 | O(1)查找O(N*size)序列化 | | |
| RESTORE | 2.6 | O(1)查找O(N*size)反序列化，有序集合还要再乘logN，插入排序的代价 | | |
| SYNC | 1.0 | O(N) | | |
| PSYNC | 2.8 | NA | | |





| Strings     | List | Set  | Sorted Set | hash | stream |
| ----------- | ---- | ---- | ---------- | ---- | ------ |
| APPEND      |      |      |            |      |        |
| BITCOUNT    |      |      |            |      |        |
| BITFIELD    |      |      |            |      |        |
| BITOP       |      |      |            |      |        |
| BITPOS      |      |      |            |      |        |
| DECR        |      |      |            |      |        |
| DECRBY      |      |      |            |      |        |
| GET         |      |      |            |      |        |
| GETBIT      |      |      |            |      |        |
| GETRANGE    |      |      |            |      |        |
| GETSET      |      |      |            |      |        |
| INCR        |      |      |            |      |        |
| INCRBY      |      |      |            |      |        |
| INCRBYFLOAT |      |      |            |      |        |
| MGET        |      |      |            |      |        |
| MSET        |      |      |            |      |        |
| MSETNX      |      |      |            |      |        |
| PSETEX      |      |      |            |      |        |
| SET         |      |      |            |      |        |
| SETBIT      |      |      |            |      |        |
| SETEX       |      |      |            |      |        |
| SETNX       |      |      |            |      |        |
| SETRANGE    |      |      |            |      |        |
| STRLEN      |      |      |            |      |        |

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>