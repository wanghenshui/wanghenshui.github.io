---
layout: post
title: Valgrind & CallGrind
categories: tools
tags: [c, python]
---
  





** TL; DR **

valgrind也可以画函数调用图！鹅妹子樱！

需要安装valgrind和kcachegrind

```shell
valgrind --tool=callgrind python xxx.py
kcachegrind
```

即可

如果kcachegrind实在编不出来~~（我就是）~~

可以考虑转成dot文件用graphviz处理

有gprof2dot工具 [地址](https://github.com/jrfonseca/gprof2dot) [单文件](https://raw.githubusercontent.com/jrfonseca/gprof2dot/master/gprof2dot.py)

```shell
python gprof2dot.py --format=callgrind --output=out.dot  callgrind.out.32281
dot -Tsvg out.dot -o graph1.svg
```



---



今天知乎上看到一个问题，问python pow是怎么实现的，首先想到的是dis看字节码

```python
>>> import dis
>>> dis.dis(pow)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/usr/lib64/python2.7/dis.py", line 49, in dis
    type(x).__name__
TypeError: don't know how to disassemble builtin_function_or_method objects
```

只能找翻源码，随手一搜，发现了个[解答](https://stackoverflow.com/questions/50724862/python-source-code-for-math-exponent-function?rq=1)，利用valgrind找定义，真是个好方法，我以前都是直接翻代码，比较hardcore但是费时间。

网上介绍valgrind，都是什么内存检测工具，实际上还可以做[profile](https://baptiste-wicht.com/posts/2011/09/profile-c-application-with-callgrind-kcachegrind.html), 也可以生成调用关系。



KDE我装了一下午！我曹！各种难装！kde开发太吃苦了吧，搭个环境这么费劲谁还愿意折腾！最后编kcachegrind提示缺少kde4！KDE4安装各种依赖我放弃。

找到了另一个生成图的解决方案，gprof2dot，不多说了

测试代码

```python
for _ in range(10000000):
    pow(2,2)
```



按照上面的操作之后，画图如下![graph1](https://wanghenshui.github.io/assets/graph1.svg)



能看到调用到PyNumber_Power下面就没了。libpython2.7.so.1.0我用各种操作抓这个地址符号，都抓不到。

```shell
 readelf -Ws libpython2.7.so.1.0	#这个grep不到结果
 objdump -TC libpython2.7.so.1.0	#这个grep 地址得不到结果
 nm -gC libpython2.7.so.1.0 		#这个空的
```

代码在这https://github.com/python/cpython/blob/a24107b04c1277e3c1105f98aff5bfa3a98b33a0/Objects/abstract.c#L1030

没仔细研究，应该内部调用的还是glibc

