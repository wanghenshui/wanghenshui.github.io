---
layout: post
title: 如何从c++导出c接口
categories: c++
tags: [c++, rocksdb]
---
  



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

### 编译问题

gcc编译c程序，链接c++的静态库，需要-lstdc++，不然会有连接错误。或者用g++编译，默认带stdc++ runtime
其实这背后有更恶心的问题，如果你链接一个静态库，这个静态库依赖其他静态库，这里头的依赖关系就很恶心了。
~~最近看pika，主程序依赖rocksdb和blackwidow，blackwidow也依赖rocksdb，链接都是静态。就很混乱。~~

`一个示例`
```bash
[root@host]# tree
|-- libp.so
|-- libstaticp.a
|-- p.cpp
|-- p.h
|-- p.o
|-- p_test.c
|-- ptest_d
`-- ptest_s
```

`p.cpp`
```cpp
#include "p.h"
#include <iostream>
using namespace std;
extern "C"{
void print_int(int a){
    cout<<a<<endl;
}
}
```
`p.h`
```c++
#ifndef _P_
#define _P_
#ifdef __cplusplus 
extern "C" {
#endif
void print_int(int a);
#ifdef __cplusplus
}
#endif
#endif
```

`p_test.c`
```c
#include "p.h"
int main(){
    print_int(111);
    return 0;
}
```

- 需要导入当前目录到环境中，方便ld
```bash
export LD_LIBRARY_PATH=.:$LD_LIBRARY_PATH
```
- 编译动态库
```bash
g++ p.cpp -fPIC -shared -o libp.so
```
- 编译静态库
```bash
g++ -c p.cpp
ar cqs libstaticp.a p.o
```
- 编译程序
```bash
gcc -o ptest_d p_test.c -L. -lp					#ok
g++ -o ptest_s p_test.c -L. -lstaticp			#ok
gcc -o ptest_s p_test.c -L. -lstaticp -lstdc++	#ok
gcc -o ptest_s p_test.c -L. -lstaticp			#not ok
./libstaticp.a(p.o): In function `print_int':
p.cpp:(.text+0x11): undefined reference to `std::cout'
p.cpp:(.text+0x16): undefined reference to `std::ostream::operator<<(int)'
p.cpp:(.text+0x1b): undefined reference to `std::basic_ostream<char, std::char_traits<char> >& std::endl<char, std::char_traits<char> >(std::basic_ostream<char, std::char_traits<char> >&)'
p.cpp:(.text+0x23): undefined reference to `std::ostream::operator<<(std::ostream& (*)(std::ostream&))'
./libstaticp.a(p.o): In function `__static_initialization_and_destruction_0(int, int)':
p.cpp:(.text+0x4c): undefined reference to `std::ios_base::Init::Init()'
p.cpp:(.text+0x5b): undefined reference to `std::ios_base::Init::~Init()'
collect2: error: ld returned 1 exit status
```
### reference
- 参考这个 写的例子 https://blog.csdn.net/surgewong/article/details/39236707
- 注意p.h中需要有__cplusplus marco guard, 因为extern "C" 不是c的内容，会报错 https://stackoverflow.com/questions/10307762/error-expected-before-string-constant
- https://arne-mertz.de/2018/10/calling-cpp-code-from-c-with-extern-c/ 这个链接说了extern "C"在c++中的风格干净的用法，注意，在c中还是用不了。

看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。