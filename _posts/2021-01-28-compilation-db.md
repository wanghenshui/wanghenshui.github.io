---
layout: post
title: 一个查看函数调用的新方案-操作compliation database
categories: [database]
tags: [c++, python, bazel]
---



最近在网上看到一篇抓堆栈的脚本[工具介绍](https://zhuanlan.zhihu.com/p/339910341)

工具还挺漂亮的，但是我的问题在于

1. perl写的，还依赖魔改ag，首先我看不懂，其次部署使用稍微有点成本(我看评论区有人帮忙打包)，然后是参数费解有点学习成本
   1. 主要是我看不懂，不是我写的，我可能就只会简单的查
2. 调用细节可能不够清晰，虽然足够用了

所以有了两个想法

1. 学一下perl，改写成python的工具？搜了一圈perl2python没有工具能用

2. 能不能用clang的工具？









---

PS：如何导出**compliation database**，也就是`compile_commands.json`

我折腾了半天导出，但是我根本用不到，这里把折腾记录放在下面

[compilation database](http://clang.llvm.org/docs/JSONCompilationDatabase.html)是clang/llvm的一个功能，作为一个语言后端支持language support protocol，需要有能力导出符号

所有的标记符号可以汇总成这个compilation database (clangd就是这个功能，对解析好的compilation database进行服务化，支持IDE的查询)

背后的技术是libclang，也有很多例子，这里就不展开了，可以看这个[链接](https://clang.llvm.org/docs/ExternalClangExamples.html)

既然都能支持IDE，难道还不能支持简单的函数调用查看，调用图生成吗，我似乎找到了新方案

~~但是这些方案都躲不开编译一遍，虽然只是简单的parser一遍，没有那么慢, 后面如果有时间，改写成python更好一些~~

如果编译环境是bazel，有https://github.com/grailbio/bazel-compilation-database支持

简单来说，就是改项目的BUILD和WORKSPACE

BUILD要加上

```bazel
## Replace workspace_name and dir_path as per your setup.
load("@com_grail_bazel_compdb//:aspects.bzl", "compilation_database")

compilation_database(
    name = "compdb",
    targets = [
        "yourtargetname",
    ],
)
```

这里target写你自己的target，可以多个target分割，name随便，这里我写成compdb



然后WORKSPACE要加上

```bazel
http_archive(
    name = "com_grail_bazel_compdb",
    strip_prefix = "bazel-compilation-database-master",
    urls = ["https://github.com/grailbio/bazel-compilation-database/archive/master.tar.gz"],
)
```



最后编译

```bash
bazel build //path/yourtargetnamedir:compdb
```

就生成compile_commands.json了



**其他编译环境，用[bear](https://github.com/rizsotto/Bear/)**

bear本身支持macos和linux，尝试命令行安装一下，安装不上的话源码安装

如果是makefile系列的编译系统，直接

```bash
bear -- make
```

就可以了，这里以memcached为例子

用python解析

PS：

如果遇到报错

```python
    raise LibclangError(msg)
clang.cindex.LibclangError: dlopen(libclang.dylib, 6): image not found. To provide a path to libclang use Config.set_library_path() or Config.set_library_file().
```

说明找不到libclang，需要指定一下，比如

```bash
export DYLD_LIBRARY_PATH=/usr/local/Cellar/llvm/11.0.0/lib/
```


---



