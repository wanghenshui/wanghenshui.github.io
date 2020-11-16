---
layout: post
title: be smart about pointers 
categories: c++
tags: [c++, cppcon]
---
  

讲了几种pointer以及背后的惯用法

#### RAII

```c++
class C;
class SBRM{
    C* pc;
public:
    SBRM(C* c):pc(c){}
    ~SBRM(){delete pc;}
    operator C*(){return pc;}
};
...
for(int i=0; i<100; ++i){
   SBRM cc(new C(i)) ;
    C* c= cc;
    /*do sth about c*/
}

//没有SBRM管理是这样的
for(int i=0; i<100; ++i){
    C* c(new C(i)) ;
    /*do sth about c*/
    delete c;
}
```

#### 智能指针

- boost::scoped_ptr  std::unique_ptr
- shared_ptr +make_shared + enable_shared_from_this + weak_ptr

能做什么

- RAII/ 定制deleter/ 引用计数/保证删除 -> 没有内存泄漏或者double free问题，代码更好维护，简化代码逻辑，不用担心内存所有权问题

 `scoped_ptr vs unique_ptr` scoped_ptr是c++11前产物，没有定制deleter和转移所有权(move), 针对a数组有scoped_array unique_ptr没有分开，功能合到一起了

`shared_ptr` RAII，引用计数，可复制，定制deleter, make_shared比new要快（省一次new，避免异常问题）

一个实现结构

![Snipaste_2019-05-20_14-52-24](https://wanghenshui.github.io/assets/Snipaste_2019-05-20_14-52-24.png)

感知share`share-aware` enable_shared_from_this

用this构造shared_ptr是十分危险的，如果这个shared_ptr 多次拷贝，就会有double-free问题

这个问题本质上和`多个shared_ptr由同一个裸指针初始化` 是同一个场景

```c++
struct Bad
{
    std::shared_ptr<Bad> getptr() {
        return std::shared_ptr<Bad>(this);
    }
    ~Bad() { std::cout << "Bad::~Bad() called\n"; }
};
{
    // Bad, each shared_ptr thinks it's the only owner of the object
    std::shared_ptr<Bad> bp1 = std::make_shared<Bad>();
    std::shared_ptr<Bad> bp2 = bp1->getptr();
    std::cout << "bp2.use_count() = " << bp2.use_count() << '\n';
}// UB: double-delete of Bad

struct Good: std::enable_shared_from_this<Good> // note: public inheritance
{
    std::shared_ptr<Good> getptr() {
        return shared_from_this();
    }
};
{
    // Good: the two shared_ptr's share the same object
    std::shared_ptr<Good> gp1 = std::make_shared<Good>();
    std::shared_ptr<Good> gp2 = gp1->getptr();
    std::cout << "gp2.use_count() = " << gp2.use_count() << '\n';
}
```

这个例子也展示出，本质上需要把this提升成shared_ptr，

不放在本体中，就只能放在enable_shared_from_this里，通过继承来侵入，然后调用share_from_this来提升(weak_ptr，shared_ptr有可能循环)

shared_ptr构造中判断是否是enable_shared_from_this基类( 函数重载)来做钩子，构造weak_ptr



 引用计数指针的两种实现 侵入式，非侵入式

对象级别引用计数，侵入式 `boost::intrusive_ptr`（感觉这个早晚也得进标准库） COM （这个应该没人用吧） 方便管理和转换普通指针，但是对象结构复杂

容器级别，`shared_ptr<T>` 干净，就是不能和普通指针混着用，需要转来转去



### ref

- [PPT](https://github.com/CppCon/CppCon2015/blob/master/Lightning Talks and Lunch Sessions/Being Smart About Pointers/Being Smart About Pointers - Michael VanLoon - CppCon 2015.pdf)
- enable_shared_from_this https://en.cppreference.com/w/cpp/memory/enable_shared_from_this
  - shared_from_this http://en.cppreference.com/w/cpp/memory/enable_shared_from_this/shared_from_this
  - 原理<https://yizhi.ren/2016/11/14/sharedptr/>
  - 原理<http://blog.guorongfei.com/2017/01/25/enbale-shared-from-this-implementaion/>
- shared_ptr几个错误用法介绍，还行<https://heleifz.github.io/14696398760857.html>

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>