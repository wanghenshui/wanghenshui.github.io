---
layout: post
category : database
title: rocksdb 目录创建的一个坑
tags : [rocksdb,c++]
---
{% include JB/setup %}

虽然有CreateIfMiss，但有时候目录还会创建失败，场景就是级联目录 rocksdb没有这种语义

 在env_posix.cc 里，实现如下

```c++
  virtual Status CreateDirIfMissing(const std::string& name) override {
    Status result;
    if (mkdir(name.c_str(), 0755) != 0) {
      if (errno != EEXIST) {
        result = IOError("While mkdir if missing", name, errno);
      } else if (!DirExists(name)) { // Check that name is actually a
                                     // directory.
        // Message is taken from mkdir
        result = Status::IOError("`"+name+"' exists but is not a directory");
      }
    }
    return result;
  };
```

如果报错 While mkdir if missing dirxx 就是这里了。

当然接口是透明的，rocksdb推荐自己实现env，实现对应的接口就可以了

mkdir(1)命令是有-p指令的(p for parent) 而mkdir(3)函数接口没有这个语义，所以就得循环调用，参考链接1有个粗糙版本

可以看看mkdir(1)的实现，见参考链接2





### reference

1.  mkdir 多级目录 <https://www.jianshu.com/p/4468e388f85c>
2.  mkdir linux实现 <https://github.com/coreutils/coreutils/blob/master/src/mkdir.c
3.   mkdir api https://linux.die.net/man/3/mkdir

看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。

