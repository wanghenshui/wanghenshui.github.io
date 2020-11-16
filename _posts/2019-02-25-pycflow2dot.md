---
layout: post
title: C/C++ 函数调用画图
categories: tools
tags: [c++]
---
  



##TL;DR

直接安装[pycflow2dot](https://github.com/johnyf/pycflow2dot)

```
pip install pycflow2dot
```

然后使用命令cflow2dot ，具体可以看帮助(-h)

```shell
cflow2dot -i default/berry.c -o b.svg -f svg
```

该包依赖cflow 和graphviz(aka dot)，按需安装即可





---

题外话

刚搜了个cflow +graphviz的方案，需要中间构造dot文件，需要tree2dotx脚本，我搜了一下关键字，直接蹦出来这个pip包了。利器。分析十分带劲。下面是两个刚抓的图，c++画图稍微有点问题，不过也能画出来

![redis.svg0](https://wanghenshui.github.io/assets/redis.svg0.svg)![b.svg0](https://wanghenshui.github.io/assets/b.svg0.svg)

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
![微信转账](https://wanghenshui.github.io/assets/wepay.png)
</details>