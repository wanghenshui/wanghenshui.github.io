---
layout: post
title: 如何从c++导出c接口
category: cpp
tags: cpp, rocksdb
---

# 如何从c++导出c接口

[TOC]

最近一周做一个第三方c++库糊c wrapper的工作，干的太慢了，一周啊没搞定。我原本的计划是打算这一周就把这个活搞定，结果连10%都没做完。高估自己能力了。

前两天主要是搞定原来的库，去掉对其他库的依赖（锁用的还是pthread api，我给去掉了），剩下的时间，思考怎么把cpp导出c接口。。这也太闹心了。学习了一下rocksdb导出的实现。

### 结构体封装

类的字段全都要导出接口，天哪。

### 参数处理

首先说下我个人的暴力替换法

- std::vector\<T\> 改成 T*

- std::vector\<std::string\>(&) 直接改成 char**

- std::vector\<std::string\>* 直接变成char *** 感觉已经招架不住了

### 返回值

- 返回指针还是传入指针or传入buffer指针？buffer指针咋设置合适，or 传入指针在内部分配？不如直接返回指针

- 返回的话管理内存就得交给调用方？

Rocksdb做法

```C++
char* rocksdb_get(
    rocksdb_t* db,
    const rocksdb_readoptions_t* options,
    const char* key, size_t keylen,
    size_t* vallen,
    char** errptr) {
  char* result = nullptr;
  std::string tmp;
  Status s = db->rep->Get(options->rep, Slice(key, keylen), &tmp);
  if (s.ok()) {
    *vallen = tmp.size();
    result = CopyString(tmp);
  } else {
    *vallen = 0;
    if (!s.IsNotFound()) {
      SaveError(errptr, s);
    }
  }
  return result;
}
```

返回指针，传入长度，这只是一个kv，如果是多个呢，如果是复杂的数据结构呢？



### 错误处理

Rocksdb 是怎么把错误导出的。传入错误指针，saveerror

```C++
static bool SaveError(char** errptr, const Status& s) {
  assert(errptr != nullptr);
  if (s.ok()) {
    return false;
  } else if (*errptr == nullptr) {
    *errptr = strdup(s.ToString().c_str());
  } else {
    // This is a bug if *errptr is not created by malloc()
    free(*errptr);
    *errptr = strdup(s.ToString().c_str());
  }
  return true;
}
```



char* err = NULL; 传入&err （为啥二级指针？） err本身是个字符串，传字符串地址。



