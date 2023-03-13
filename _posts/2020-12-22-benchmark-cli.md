---
layout: post
title: 实现一个benchmark cli应该考虑点啥
categories: [language]
tags: [c++, template, map]
---



benchmark的典型架子，网络端

- 多线程worker，worker死循环干活
- 统计信息，统计p99统计
- 后台线程实时打印qps/打印进度条
- 参数读取
- 日志打印设计，日志要方便解析，最好支持open traceing那种，这样不用人来看了
  - 还可以设计unique id，这样来区分不同的bench
- 数据打印更直观一些histogram

一个典型的例子是memtier-benchmark，多线程worker，worker内部潜入libevent填数据，这个架构

cli典型架子

- repl 循环

- 补全

- 参数读取

典型例子redis-cli



Arangodb 的cli/bench就设计的很有意思，值得解读并把他的代码抽出来抽成公共库

---

### ref

- https://clig.dev/


---




