---
layout: post
title: blog review 第六期
categories: [review]
tags: [shell, python,database, buffer, sqlite, cache]
---

准备把blog阅读和paper阅读都归一，而不是看一篇翻译一篇，效率太低了

后面写博客按照 paper review，blog review，cppcon review之类的集合形式来写，不一篇一片写了。太水了



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



## 最近的点子

https://github.com/a8m/rql 改成c++的

## 待读

https://github.com/stedolan/jq/wiki/Internals:-the-interpreter

https://github.com/riba2534/TCP-IP-NetworkNote/tree/master/ch03

https://github.com/arximboldi/lager

https://github.com/eatingtomatoes/pure_simd

https://github.com/logicalclocks/rondb

https://github.com/Jason2013/gslcl/blob/master/ch04.rst··

Page cache https://www.yuque.com/jdxj/bq4chm/rug9eq

https://github.com/lj1208/binloglistener/tree/master/src


---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>
