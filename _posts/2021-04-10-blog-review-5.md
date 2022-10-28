---
layout: post
title: blog review 第五期
categories: [review]
tags: [cache, pacificA]
---

看tag知内容


<!-- more -->

## [What exactly was the point of [ “x$var” = “xval” ]?](https://www.vidarholen.net/contents/blog/?p=1035)

看到老员工写bash的条件判断都要加个x，为什么呢？上古bug遗留的代码的风格

文章里讨论了各种bug触发场景，并且shellcheck工具现在已经加上了这种风格的告警

```text
- SC2268: Warn about unnecessary x-comparisons like `[ x$var = xval ]`
```

是时候放弃这种写法了



## [Read-only benchmarks with an LSM are complicated](https://smalldatum.blogspot.com/2021/02/read-only-benchmarks-with-lsm-are.html?fbclid=IwAR3rerRkvXJDULA1ci4mN1cQwL8CqkNuVRggVgjxqt543d8AhlmQ_IJEkfo)



## [Snapshot Isolation综述](https://zhuanlan.zhihu.com/p/54979396)

## **Snapshot Is**olation(SI)

”snapshot isolation”的出现主要解决”two-phase locking”带来的性能底下的问题，其原理如下：

- 每一个数据都多个版本，读写能够并发进行
- 每个事务相当于看到数据的一个快照
- 写写不能并发，写写操作时需要加上行锁
- 谁加行锁，谁可以顺利执行（采用了“first win”的原则），后面的写事务要么abort，要么等待前面的事务执行完成后再执行（以Oracle 和 SQL Server 、MySQL等为代表）。

但是”snapshot isolation”带来一个大问题：”**write skew**“，即写偏序问题(不能够达到串行化的事务隔离级别)。

为了解决”write  skew”（写偏序） 问题，出现了”Serial Snapshot Isolation”理论，其实现方法有很多种，”Write Snapshot Isolation”作为”Serial Snapshot Isolation”理论的典型代表解决”write skew”问题, 基本思想：

>  冲突检测发生在事务的运行阶段，而不是事务的提交阶段。

因此，它的原理就是：增加读写冲突检测来解决”write skew”问题。如下是”Write Snapshot Isolation”的定义：

> Similarly to Snapshot isolation，write Snapshot isolation assigns unique start and commit timestamps to transactions and ensures that txni reads the  latest version of data with commit timestamp δ<Ts(txni) 

与SI 一样每个事务都有一个事务开始时间戳与事务结束时间戳。Write Snapshot isolation 需要保证一个事务读的数据的最近一个版本的提交时间要早于事务的开始时间。
 换一种简单的描述：如果两个读写事务”txni”，”txnj”同时满足下面两个条件，那么这两个事务不能同时提交成功：

- 读写在空间上重叠：”txni”的写操作与”txnj”的读操作发生在同一行
- 读写在时间上重叠：Ts(txni) < Tc(txnj) < Tc(txni)注：Ts(txni)代表txni的事务开始时间, Tc(txni)代表事务txni的事务提交时间

Write Snapshot Isolation事务虽然解决”write skew”问题，还存在另外一个难以解决的问题：**全序问题**。
 基于 Snapshot isolation理论，每个事务都有两个事件：

- 事务的开始事件（时间）
- 事务的提交事件（时间）

所有的事件必须是全序的，即所有事件都有先后顺序。一般情况用时间轴表示事件的发生的前后关系，实现事件的全序。我们给事务分配一个事务的开始时间，一个事务的结束时间，这样在整个系统中，所有的事件都可以比较先后关系。
 但是在分布式系统中，时间就变成一个非常大的难题，因为各个节点的时间可能有误差。而且根据侠义相对论，时空的事件并不存在一个始终如一的全序关系。



## **Clock-SI**

Clock-SI是2013年EPFL的作品，一作目前在Google工作（据Linkedin信息）。虽在国内没有什么讨论，但据悉，工业界已经有了实践。在PGCon2018的一个talk《Towards ACID scalable PostgreSQL with partitioning and logical  replication》就提到，他们已经在应用Clock-SI的算法到PostgreSQL中，实现去中心化的SI；而MongoDB虽然未曾提及他们使用分布式事务算法，但据目前提交的代码来看，使用Clock-SI的可能性也非常大。

Clock-SI首先高屋建瓴地指出，Snapshot Isolation的正确性包含三点：

- Consistent Snapshot：所谓Consistent，即快照包含且仅包含Commit先于SnapshotTS的所有事务
- Commit Total Order：所有事务提交构成一个全序关系，每次提交都会生成一个快照，由CommitTS标识
- Write-Write Conflict: 事务Ti和Tj有冲突，即它们WriteSet有交集，且[SnapshotTS, CommitTS]有交集

1. StartTS：直接从本地时钟获取
2. Read：当目标节点的时钟小于StartTS时，进行等待，即上图中的Read  Delay；当事务处于Prepared或者Committing状态时，也进行等待；等待结束之后，即可读小于StartTS的最新数据；这里的Read Delay是为了保证Consistent Snapshot
3. CommitTS：区分出单Partition事务和分布式事务，单Partition事务可以使用本地时钟作为CommitTS直接提交；而分布式事务则选择max{PrepareTS}作为CommitTS进行2PC提交；为了保证CommitTS的全序，会在时间戳上加上节点的id，和Lamport Clock的方法一致
4. Commit：不论是单partition还是多partition事务，都由单机引擎进行WW冲突检测

ClockSI有几点创新：

- 使用普通的物理时钟，不再依赖中心节点分配时间戳
- 对单机事务引擎的侵入较小，能够基于一个单机的Snapshot Isolation数据库实现分布式的SI
- 区分单机事务和分布式事务，几乎不会降低单机事务的性能；分布式使用2PC进行原子性提交

在工程实现中，还需考虑这几个问题：

- StartTS选择：可以使用较旧的快照时间，从而不被并发事务阻塞
- 时钟漂移：虽然算法的正确性不受时钟漂移的影响，但时钟漂移会增加事务的延迟，增加abort rate
- Session Consistency：事务提交后将时间戳返回给客户端记为latestTS，客户端下次请求带上这个latestTS，并进行等待

WSI

基于RW冲突检测的思想，作者提出Write Snapshot Isolation，将之前的Snapshot Isolation命名为Read Snapshot Isolation。例如图中：

- TXNn和TXNc'有冲突，因为TXNc'修改了TXNn的ReadSet
- TXNn和TXNc没有冲突，虽然他们都修改了r'这条记录，Basic SI会认为有冲突，但WriteSI认为TXNc没有修改TXNn的ReadSet，则没有RW冲突

如何检测RW冲突：事务读写过程中维护ReadSet，提交时检查自己的ReadSet是否被其他事务修改过，over。但实际也不会这么简单，因为通常维护ReadSet的开销比WriteSet要大，且这个冲突检查如何做，难道加读锁？所以在原文中，作者只解释了中心化的WSI如何实现，至于去中心化的实现，可从Cockroach找到一点影子。

不过RW检测会带来很多好处：

- 只读事务不需要检测冲突，它的StartTS和CommitTS一样
- 只写事务不需要检测冲突，它的ReadSet为空

更重要的是，这种算法实现的隔离级别是Serializable而不是Snapshot Isolation。



## [Virtual machine in C](https://felix.engineer/blogs/virtual-machine-in-c)

很简单的VM实现，代码在这里 https://github.com/felixangell/mac/blob/master/mac-improved/mac.c

一个stack虚拟机实现

stack指针SP维护，stack维护，一个数组

指令维护，状态机切指令

寄存器，放数据

还是比较简单的

后面可以把这个练习做了 https://blog.holbertonschool.com/hack-virtual-memory-stack-registers-assembly-code/

## [PostgreSQL 通信协议](http://mysql.taobao.org/monthly/2020/03/02/)

介绍了pg的消息流程

普通的消息就是 type+len+payload，还是比较简单的

客户端发起的第一条消息 startup 带版本号[len + version + str name ...+...] 带表名账号等信息

客户端取消请求 CancelRequest ，是用startup返回的cancelkey带上返回的，和startup类似没有type

取消不一定成功。Q: 为啥要设计成这样拆开的形式？让cancel更灵活吗？

![](https://viewer.diagrams.net/?highlight=0000ff&edit=_blank&layers=1&nav=1&title=pg1.xml#R7ZhdU6MwGIV%2FTS%2Bd4cPW9tK26l64q9vurN29i%2BQVMoaEDcG2%2B%2Bs3QIBC0NZaOjruVclJeEnOk54J9NxJuLoSKAq%2Bcgy051h41XOnPcexbWugflJlnSvDkZMLviBYD6qEOfkLWrS0mhAMcW2g5JxKEtVFjzMGnqxpSAi%2BrA974LT%2B1Aj5YAhzD1FTvSNYBnoVfavSvwDxA1kuWPeEqBishThAmC83JPei504E5zK%2FClcToKl5hS%2F5fZfP9JYTE8DkLje4LBlfrsTIW19bEbu5%2B%2BGgqxNd5QnRRC94QklaMJ%2ByXBc%2BqNlH6WUS0mvyAJQw1RpHIEgIEoTqoVq%2BrbSxoiKR0tJ%2BO2tTiqKY3GdlLaUI8BIRkyeYQZzDz1SeMAxYt0rnsoYU%2FLFkkRY1jShWBULCakPSxlwBVxMUazWk6HU1pGKX6uayQl6CDTZwu4WI9Dbzy9IVCXWhYbwCjGOAMZBEnDCZPbc%2F7vWnDRxcyID7nCG6CeSNxr64h3Z2%2B7RfM%2FuszWzTa8ftymvX8BqTOELSCwzP00USlQ7nlPhMSfdcSh5m7iEhz9PASb1XpZQGDBfKPeXeYzFMp9zw0ARUbR9eGqf3EOBa5pmcBFAk1X%2BynqYttutbb9OdWPE9sdsBFxVinggP9E0NduUs9sfZN3DOQShwnyzTymx6N5k2%2BDiZ1n%2Bt241MazW7JdOcrrweGl5%2FT0DX3SnQWsJLWSbWC21t1vj1xt2cJ8H2xNqabIPjJJtzVsdsD44bbSOD6owvpxB7gkSScHYYvPbR8B4L22k9Cp1mxD2DzShkD7cUyjfqIfhb16NvM2fx%2B%2BaPOz%2FHnsCLn4uW4%2Fq75t81V7eRuiXnN3NtFuqYq3nanyKJFNvPDnTHo%2BN2oM1CHQM1Xyn%2BA209XO4L1CjUMdBTA%2BiEhyFiWP1EVJ1EPzvY5tv53mCbhToGa76UzADh9SUXBzwwf1ysOx5wt2NtFtobq2pWH03z4dWnZ%2FfiHw%3D%3D)



## [异步schema变更](https://github.com/ngaut/builddatabase/blob/master/f1/schema-change.md)

讲F1算法，把schema变成KV，在DDL过程中同步KV





## [Tail Latency Might Matter More Than You Think](https://brooker.co.za/blog/2021/04/19/latency.html)



 There are many causes of tail latency in the world, including  contention, garbage collection, packet loss, host failure, and weird  stuff operating systems do in the background. It's tempting to look at  the 99.9th percentile, and feel that it doesn't matter. After all, 999  of 1000 calls are seeing lower latency than that.

讲了几个应用串联在了一起，导致延迟过高的问题。这没有什么好的解法。使用的时候注意





## [How we scaled the GitHub API with a sharded, replicated rate limiter in Redis](https://github.blog/2021-04-05-how-we-scaled-github-api-sharded-replicated-rate-limiter-redis/)

github使用redis做限流器的一个demo

针对api做的限流

```lua
-- RATE_SCRIPT:
--   count a request for a client
--   and return the current state for the client
-- rename the inputs for clarity below
local rate_limit_key = KEYS[1]
local increment_amount = tonumber(ARGV[1])
local next_expires_at = tonumber(ARGV[2])
local current_time = tonumber(ARGV[3])
local expires_at_key = rate_limit_key .. ":exp"
local expires_at = tonumber(redis.call("get", expires_at_key))
if not expires_at or expires_at < current_time then
  -- this is either a brand new window,
  -- or this window has closed, but redis hasn't cleaned up the key yet
  -- (redis will clean it up in one more second)
  -- initialize a new rate limit window
  redis.call("set", rate_limit_key, 0)
  redis.call("set", expires_at_key, next_expires_at)
  -- tell Redis to clean this up _one second after_ the expires-at time.
  -- that way, clock differences between Ruby and Redis won't cause data to disappear.
  -- (Redis will only clean up these keys "long after" the window has passed)
  redis.call("expireat", rate_limit_key, next_expires_at + 1)
  redis.call("expireat", expires_at_key, next_expires_at + 1)
  -- since the database was updated, return the new value
  expires_at = next_expires_at
end
-- Now that the window is either known to already exist _or_ be freshly initialized,
-- increment the counter (`incrby` returns a number)
local current = redis.call("incrby", rate_limit_key, increment_amount)
return { current, expires_at }
 
-- CHECK_SCRIPT:
--   Getting both the value and the expiration
--   of key as needed by our algorithm needs to be ran
--   in an atomic way, hence the script.

-- rename the inputs for clarity below
local rate_limit_key = KEYS[1]
local expires_at_key = rate_limit_key .. ":exp"
local current_time = tonumber(ARGV[1])
local tries = tonumber(redis.call("get", rate_limit_key))
local expires_at = nil -- maybe overridden below
if not tries then
  -- this client hasn't initialized a window yet
  -- let this fall through to returning {nil, nil},
  -- where the application will provide defaults
else
  -- we found a number of tries, now check
  -- if this window is actually expired
  expires_at = tonumber(redis.call("get", expires_at_key))
  if not expires_at or expires_at < current_time then
    -- this window hasn't been cleaned up by Redis yet, but it has closed.
    -- (maybe it was _partly_ cleaned up, if we found `tries` but not `expires_at`)
    -- ignore the data in the database; return a fresh window instead
    tries = nil
    expires_at = nil
  end
end
-- Maybe {nil, nil} if the window is brand new (or expired)
return { tries, expires_at }
```

他们参考的的这个 https://gist.github.com/ptarjan/e38f45f2dfe601419ca3af937fff574d和这个https://redis.io/commands/incr#pattern-rate-limiter 意思都差不多

原理很简单，就是在一个时间段对一个key进行incr，到了限制就停止，然后下个时间段换个key，原来的key过期淘汰掉

## [What is unified function call syntax anyway?](https://brevzin.github.io/c++/2019/04/13/ufcs-history/)

介绍一种扩展语法，统一类调用和函数传参数调用。不过至今没有通过

```c++
struct X {
    void f(Y);
};

// ill-formed today, but with CS:FreeFindsMember would
// be able to call x.f(y)
f(x, y);

struct X { };
void g(X, Y);

// ill-formed today, but with CS:MemberFindsFree would
// be able to call g(x, y)
x.g(y);

```

这两种语法的归一

归一可能造成类的任意扩展行为。而且这种行为可能有害。目前不知道这个进展如何。偶尔发现，做个记录

## [URL shortener Base-62 encoder / decoder C++ Proof-of-Concept](https://gist.github.com/jaytaylor/a11fadf61a869ade0dfe568606b216c8)

一个url short原型，简单介绍一下

首先，网址要能映射成一个hash或者整数，要保证唯一性，然后就是这个整数生成url，url反推出整数。然后整数持久化，就好了

```c++
string id_to_short_url(unsigned int n) {
    // Mapping which defines the 62 possible output characters.
    char map[] = "abcdefghijklmnopqrstuvwxyzABCDEF"
                 "GHIJKLMNOPQRSTUVWXYZ0123456789";

    string short_url;

    // Convert given ID to a base-62 number.
    while (n) {
        // Append each character mapped by the remainder.
        short_url.push_back(map[n % 62]);
        n /= 62;
    }

    // Reverse the string to complete the base conversion.
    std::reverse(short_url.begin(), short_url.end());
    return short_url;
}

/**
 * short_url_to_id converts a short URL into the corresponding ID.
 *
 * Base-62 decodes the input string.
 */
unsigned int short_url_to_id(string short_url) {
    unsigned int id = 0;

    // Base decode conversion logic.
    for (int i = 0; i < short_url.length(); ++i) {
        if ('a' <= short_url[i] && short_url[i] <= 'z') {
            id = id * 62 + short_url[i] - 'a';
        }
        if ('A' <= short_url[i] && short_url[i] <= 'Z') {
            id = id * 62 + short_url[i] - 'A' + 26;
        }
        if ('0' <= short_url[i] && short_url[i] <= '9') {
            id = id * 62 + short_url[i] - '0' + 52;
        }
    }
    return id;
}
```



## 其他

一个不错的教程文档，写的很好，公众号运营 的https://ng-tech.icu/books/#infras

这个博客整理了阿里数据库月报，很有意思 https://github.com/tangwz/db-monthly


---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>
