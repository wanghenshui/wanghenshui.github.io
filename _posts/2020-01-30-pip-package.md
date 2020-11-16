---
layout: post
title: 如何快速制作一个python包
categories: language
tags: [pip, python]
---
  



主要是依靠[modern-package-template](https://github.com/srid/modern-package-template)这个工具。非常方便，推荐给大家

按照readme一步一步来就可以了



以我这个包 https://github.com/wanghenshui/fake_redis_command为例子

首先安装

```python
pip install modern-package-template
```

然后创建一个包项目

```shell
paster create -t modern_package helloworld
```

 然后项目就搞好了，按照生成文件夹里的hacking一步一步搞就行了，当然最后 

```python
python setup.py install
```

就可以安装了。后面还有上传到pip仓库的操作。很简单，但是我网络不行传不上去。



要注意的只有`setup.py文件`的写法

目录结构不重要，重要的是`setup.py文件`要写好

以我的包为例，目录结构是



```
fake_redis_command/
├── HACKING.txt
├── MANIFEST.in
├── NEWS.txt
├── README.rst
├── bootstrap.py
├── build
├── dist
│   ├── fake_redis_command-0.1-py3.6.egg
│   └── fake_redis_command-0.1.tar.gz
├── examples
│   └── random_command.py
├── setup.py
└── src
    ├── fake_redis_command
    │   └── `__init__`.py
    └── fake_redis_command.egg-info
        ├── PKG-INFO
        ├── SOURCES.txt
        ├── dependency_links.txt
        ├── entry_points.txt
        ├── not-zip-safe
        ├── requires.txt
        └── top_level.txt
```

大部分都是和包不相关的，主要`setup.py文件`要写对，比如我的文件只有src/fake_redis_command/下一个文件，还是`__init__.py`文件，所以`setup.py文件`里写的

```python
    packages=find_packages('src'),
    package_dir = {'': 'src'},include_package_data=True,
```

使用就可以直接用

```python
from fake_redis_command import redis_command
```

因为我的redis_command实现在`__init__.py`文件, 最简单。但是项目复杂一些，不可能放在同一个文件，来看看redis-py的`setup.py文件` https://github.com/andymccurdy/redis-py/blob/master/setup.py



```python
packages=['redis'],
```

redis的目录也很简单，就一层redis目录，没有我那层src嵌套（模板生成的我也不想）

写的很简单，说明其他定义在redis目录下的`__init__.py`文件里，但是目录下有很多文件，那肯定就是只导出了。

再看https://github.com/andymccurdy/redis-py/blob/master/redis/__init__.py

果不其然，把所有的类和异常都暴露出来了。这样`import redis`就能直接用了。



说的十分粗糙，但是临时用一下造一个粗糙的轮子包够用了。



---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
![微信转账](https://wanghenshui.github.io/assets/wepay.png)
</details>