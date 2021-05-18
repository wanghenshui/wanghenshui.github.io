---
layout: post
title: blog review 第六期
categories: [review]
tags: [cache, pacificA]
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
