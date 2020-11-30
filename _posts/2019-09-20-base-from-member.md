---
layout: post
categories: language
title: base from member 
tags: [c++]
---

  

一个遇到的技巧

---

场景是这样的，基类需要子类的成员变量来初始化父类

```c++
#include <streambuf>  // for std::streambuf
#include <ostream>    // for std::ostream

class fdoutbuf : public std::streambuf {
public:
    explicit fdoutbuf(int fd);
    //...
};

class fdostream : public std::ostream {
protected:
    fdoutbuf buf;
public:
    explicit fdostream(int fd) : buf(fd), std::ostream(&buf) {}
};
```

这种场景是无法编译通过的，因为需要基类先初始化

但交换初始化列表和基类构造函数的位置

```c++
    explicit fdostream(int fd) :  std::ostream(&buf), buf(fd) {}
```

这样语义不对，buf十有八九是错的。

需要提前把buf初始化。所以加了一个中间层，把buf放到另外一个基类里，让这个基类先于原来的基类。

```c++
class fdoutbuf : public std::streambuf {
public:
    explicit fdoutbuf(int fd);
    //...
};

struct fdostream_pbase {
    fdoutbuf sbuffer;
    explicit fdostream_pbase(int fd) : sbuffer(fd) {}
};

class fdostream : private fdostream_pbase, public std::ostream{
    typedef fdostream_pbase  pbase_type;
    typedef std::ostream     base_type;
public:
    explicit fdostream(int fd): pbase_type(fd), base_type(&sbuffer)  {}
    //...
};
```

就解决了。

boost提供了一个base_from_member类，用于托管你要抽离出来的字段

用法是这样的

```c++
#include <boost/utility/base_from_member.hpp>
#include <streambuf>  // for std::streambuf
#include <ostream>    // for std::ostream

class fdoutbuf : public std::streambuf {
public:
    explicit fdoutbuf(int fd);
    //...
};

class fdostream : private boost::base_from_member<fdoutbuf> , public std::ostream {
    // Helper typedef's
    typedef boost::base_from_member<fdoutbuf>  pbase_type;
    typedef std::ostream                        base_type;

public:
    explicit fdostream(int fd) : pbase_type(fd), base_type(&member) {}
    //...
};
```

base_from_member有个member字段就是要抽离出来托管的字段。

实际上这个类也没那么复杂，自己写一个`base_from_member`或者自己写个类似的类，不用`base_from_member`这种模板继承也是可以的

```c++
template < typename MemberType, int UniqueID = 0 >
class boost::base_from_member
{
protected:
    MemberType  member;
    base_from_member();
    template< typename T1 >
    explicit  base_from_member( T1 x1 );
    //...
};
```







----

### ref

1. 介绍
   1. http://sns.hwcrazy.com/boost_1_41_0/libs/utility/base_from_member.html boost相关中文翻译
   2. http://www.josuttis.com/cppcode/ronsmember.html
   3. https://remonstrate.wordpress.com/tag/base-from-member/
   4. [https://remonstrate.wordpress.com/2011/01/26/boost-%e7%9a%84-utility/](https://remonstrate.wordpress.com/2011/01/26/boost-的-utility/) 这个博客其实还可以。文章不错
   5. https://stackoverflow.com/questions/4815956/base-from-member-idiom-in-c
   6. https://en.wikibooks.org/wiki/More_C%2B%2B_Idioms/Base-from-Member
2. 一个类似的应用例子 https://stackoverflow.com/questions/16613191/stl-initializing-a-container-with-an-unconstructed-stateful-comparator 值得一看



看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>