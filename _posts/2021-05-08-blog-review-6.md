---
layout: post
title: blog review 第六期
categories: [review]
tags: [shell, python,database, buffer, sqlite, cache]
---

准备把blog阅读和paper阅读都归一，而不是看一篇翻译一篇，效率太低了

后面写博客按照 paper review，blog review，cppcon review之类的集合形式来写，不一篇一片写了。太水了

[toc]

<!-- more -->

## [cd is not a program](https://seb.jambor.dev/posts/cd-is-not-a-program/)

cd是shell内建的，全靠CDPATH发挥作用，所以脚本中，最好不要用cd或者用到cd的时候清一下CDPATH，否则可能会有意外事故



## [Advanced usage of Python requests - timeouts, retries, hooks](https://hodovi.ch/blog/advanced-usage-python-requests-timeouts-retries-hooks/)

一个工具库介绍了几个用法，代码在这里 https://github.com/requests/toolbelt

### hook

```python
response = requests.get('https://api.github.com/user/repos?page=1')
# Assert that there were no errors
response.raise_for_status()
# 修改的方案
# Create a custom requests object, modifying the global module throws an error
http = requests.Session()

assert_status_hook = lambda response, *args, **kwargs: response.raise_for_status()
http.hooks["response"] = [assert_status_hook]

http.get("https://api.github.com/user/repos?page=1")
# 打印
import requests
from requests_toolbelt.utils import dump

def logging_hook(response, *args, **kwargs):
    data = dump.dump_all(response)
    print(data.decode('utf-8'))

http = requests.Session()
http.hooks["response"] = [logging_hook]

http.get("https://api.openaq.org/v1/cities", params={"country": "BA"})
```

### 设置base url

```python
requests.get('https://api.org/list/')
requests.get('https://api.org/list/3/item')
#修改的方案
from requests_toolbelt import sessions
http = sessions.BaseUrlSession(base_url="https://api.org")
http.get("/list")
http.get("/list/item")
```

### timeout

```python
requests.get('https://github.com/', timeout=0.001)
#修改的方案

from requests.adapters import HTTPAdapter

DEFAULT_TIMEOUT = 5 # seconds

class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = DEFAULT_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)
import requests

http = requests.Session()

# Mount it for both http and https usage
adapter = TimeoutHTTPAdapter(timeout=2.5)
http.mount("https://", adapter)
http.mount("http://", adapter)

# Use the default 2.5s timeout
response = http.get("https://api.twilio.com/")

# Override the timeout as usual for specific requests
response = http.get("https://api.twilio.com/", timeout=10)
```

### retry

```python
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    method_whitelist=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

response = http.get("https://en.wikipedia.org/w/api.php")
```





## [Query Engines: Push vs. Pull](http://justinjaffray.com/query-engines-push-vs.-pull/)

> Push-based execution refers to the fact that relational operators push their results to their downstream operators, rather than waiting for these operators to pull data (classic Volcano-style model). Push-based execution improves cache efficiency, because it removes control flow logic from tight loops. It also enables Snowflake to efficiently process DAG-shaped plans, as opposed to just trees, creating additional opportunities for sharing and pipelining of intermediate results.

push-based DAG处理已经成为事实上的state of the art 新的数据系统都会基于push-based execution来设计

这篇文章分析了引用里提到的优点，简单论证了合理性

目前比较典型的就是naiad timely workflow了



## Buffer

基本的设计想法，就是循环缓冲了

muduo中的buffer，其实libevent中差不多

```c++
  std::vector<char> buffer_;
  size_t readerIndex_;
  size_t writerIndex_;
const char* peek() const
 { return begin() + readerIndex_; }
size_t writableBytes() const
  { return buffer_.size() - writerIndex_; }
size_t readableBytes() const
  { return writerIndex_ - readerIndex_; }
 size_t prependableBytes() const
  { return readerIndex_; }
```

这里如果涉及到扩展还是需要拷贝的，如何zero-copy？iobuf设计，看brpr 的iobuf https://github.com/apache/incubator-brpc/blob/master/src/butil/iobuf.h



## [Hosting SQLite databases on Github Pages](https://phiresky.github.io/blog/2021/hosting-sqlite-databases-on-github-pages/) 

​	把sqlite编译到wasm 妙啊

这也提供了思路，想做一个二进制程序，可以编译到wasm然后放到github page上进行演示



## [Dropping cache didn’t drop cache](https://blog.twitter.com/engineering/en_us/topics/open-source/2021/dropping-cache-didnt-drop-cache.html)

这个是twitter公司找bug记录，顺便了解page cache的功能逻辑。twitter使用的内核是比较激进的，上面的 不稳定变动可能导致引入bug

最终问题的解决的patch https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=8199be001a470209f5c938570cc199abb012fe53

```c
diff --git a/mm/list_lru.c b/mm/list_lru.c
index 8de5e37..1e61161 100644
--- a/mm/list_lru.c
+++ b/mm/list_lru.c
@@ -534,7 +534,6 @@ static void memcg_drain_list_lru_node(struct list_lru *lru, int nid,
 	struct list_lru_node *nlru = &lru->node[nid];
 	int dst_idx = dst_memcg->kmemcg_id;
 	struct list_lru_one *src, *dst;
-	bool set;
 
 	/*
 	 * Since list_lru_{add,del} may be called under an IRQ-safe lock,
@@ -546,11 +545,12 @@ static void memcg_drain_list_lru_node(struct list_lru *lru, int nid,
 	dst = list_lru_from_memcg_idx(nlru, dst_idx);
 
 	list_splice_init(&src->list, &dst->list);
-	set = (!dst->nr_items && src->nr_items);
-	dst->nr_items += src->nr_items;
-	if (set)
+
+	if (src->nr_items) {
+		dst->nr_items += src->nr_items;
 		memcg_set_shrinker_bit(dst_memcg, nid, lru_shrinker_id(lru));
-	src->nr_items = 0;
+		src->nr_items = 0;
+	}
 
 	spin_unlock_irq(&nlru->lock);
 }
```





### [snowflake 算法原理](https://www.luozhiyun.com/archives/527)

```c++
#pragma once
#include <cstdint>
#include <chrono>
#include <stdexcept>
#include <mutex>

class snowflake_nonlock
{
public:
    void lock()
    {
    }
    void unlock()
    {
    }
};

template<int64_t Twepoch, typename Lock = snowflake_nonlock>
class snowflake
{
    using lock_type = Lock;
    static constexpr int64_t TWEPOCH = Twepoch;
    static constexpr int64_t WORKER_ID_BITS = 5L;
    static constexpr int64_t DATACENTER_ID_BITS = 5L;
    static constexpr int64_t MAX_WORKER_ID = (1 << WORKER_ID_BITS) - 1;
    static constexpr int64_t MAX_DATACENTER_ID = (1 << DATACENTER_ID_BITS) - 1;
    static constexpr int64_t SEQUENCE_BITS = 12L;
    static constexpr int64_t WORKER_ID_SHIFT = SEQUENCE_BITS;
    static constexpr int64_t DATACENTER_ID_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS;
    static constexpr int64_t TIMESTAMP_LEFT_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS + DATACENTER_ID_BITS;
    static constexpr int64_t SEQUENCE_MASK = (1 << SEQUENCE_BITS) - 1;

    using time_point = std::chrono::time_point<std::chrono::steady_clock>;

    time_point start_time_point_ = std::chrono::steady_clock::now();
    int64_t start_millsecond_ = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch()).count();

    int64_t last_timestamp_ = -1;
    int64_t workerid_ = 0;
    int64_t datacenterid_ = 0;
    int64_t sequence_ = 0;
    lock_type lock_;
public:
    snowflake() = default;

    snowflake(const snowflake&) = delete;

    snowflake& operator=(const snowflake&) = delete;

    void init(int64_t workerid, int64_t datacenterid)
    {
        if (workerid > MAX_WORKER_ID || workerid < 0) {
            throw std::runtime_error("worker Id can't be greater than 31 or less than 0");
        }

        if (datacenterid > MAX_DATACENTER_ID || datacenterid < 0) {
            throw std::runtime_error("datacenter Id can't be greater than 31 or less than 0");
        }

        workerid_ = workerid;
        datacenterid_ = datacenterid;
    }

    int64_t nextid()
    {
        std::lock_guard<lock_type> lock(lock_);
        //std::chrono::steady_clock  cannot decrease as physical time moves forward
        auto timestamp = millsecond();
        if (last_timestamp_ == timestamp)
        {
          // 当同一时间戳（精度：毫秒）下多次生成id会增加序列号
            sequence_ = (sequence_ + 1)&SEQUENCE_MASK;
            if (sequence_ == 0)
            {
                // 如果当前序列超出12bit长度，则需要等待下一毫秒
                // 下一毫秒将使用sequence:0
                // 为什么这里不直接+1
                timestamp = wait_next_millis(last_timestamp_);
            }
        }
        else
        {
            sequence_ = 0;
        }

        last_timestamp_ = timestamp;

        return ((timestamp - TWEPOCH) << TIMESTAMP_LEFT_SHIFT)
            | (datacenterid_ << DATACENTER_ID_SHIFT)
            | (workerid_ << WORKER_ID_SHIFT)
            | sequence_;
    }

private:
    int64_t millsecond() const noexcept
    {
        auto diff = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - start_time_point_);
        return start_millsecond_ + diff.count();
    }

    int64_t wait_next_millis(int64_t last) const noexcept
    {
        auto timestamp = millsecond();
        while (timestamp <= last)
        {
            timestamp = millsecond();
        }
        return timestamp;
    }
};
```



## [ClickHouse使用姿势系列之分布式JOIN](https://zhuanlan.zhihu.com/p/377506070)

join的几种写法

> ##  **分布式JOIN最佳实践**
>
> 在清楚了ClickHouse 分布式JOIN查询实现后，我们总结一些实际经验。
>
> - **一、尽量减少JOIN右表数据量**
>
> ClickHouse根据JOIN的右表数据，构建HASH MAP，并将SQL中所需的列全部读入内存中。如果右表数据量过大，节点内存无法容纳后，无法完成计算。
>
> 在实际中，我们通常将较小的表作为右表，并尽可能增加过滤条件，降低进入JOIN计算的数据量。
>
> - **二、利用GLOBAL JOIN 避免查询放大带来性能损失**
>
> 如果右表或者子查询的数据量可控，可以使用GLOBAL JOIN来避免读放大。需要注意的是，GLOBAL JOIN 会触发数据在节点之间传播，占用部分网络流量。如果数据量较大，同样会带来性能损失。
>
> - **三、数据预分布实现Colocate JOIN**
>
> 当JOIN涉及的表数据量都非常大时，读放大，或网络广播都带来巨大性能损失时，我们就需要采取另外一种方式来完成JOIN计算了。
>
> 根据“相同JOIN KEY必定相同分片”原理，我们将涉及JOIN计算的表，按JOIN KEY在集群维度作分片。将分布式JOIN转为为节点的本地JOIN，极大减少了查询放大问题

建议看看这个https://jiamaoxiang.top/2020/11/01/Spark%E7%9A%84%E4%BA%94%E7%A7%8DJOIN%E6%96%B9%E5%BC%8F%E8%A7%A3%E6%9E%90/ 

## [A robust distributed locking algorithm based on Google Cloud Storage](https://www.joyfulbikeshedding.com/blog/2021-05-19-robust-distributed-locking-algorithm-based-on-google-cloud-storage.html)

讲分布式锁的简单实现，以及经典问题，以及解决方案(ttl)

## 最近的点子

https://github.com/a8m/rql 改成c++的

https://github.com/stateright/stateright

https://docs.rs/stateright/0.28.0/stateright/

## 待读

https://github.com/stedolan/jq/wiki/Internals:-the-interpreter

https://github.com/riba2534/TCP-IP-NetworkNote/tree/master/ch03

https://github.com/arximboldi/lager

https://github.com/eatingtomatoes/pure_simd

https://github.com/logicalclocks/rondb

https://github.com/Jason2013/gslcl/blob/master/ch04.rst··

Page cache https://www.yuque.com/jdxj/bq4chm/rug9eq

https://github.com/lj1208/binloglistener/tree/master/src

oceanbase开源了 https://open.oceanbase.com/docs/community/oceanbase-database/V3.1.0/overall-architecture

代码走读https://zhuanlan.zhihu.com/p/392107745

https://github.com/wangzzu/awesome/issues/31


---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>
