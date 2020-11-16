---
layout: post
title:  Introduction to Modern C++ Techniques 
categories: c++
tags: [c++, boost, cppnow]
---

  

### cppnow2012 Michael Caisse Introduction to Modern C++ Techniques 



这个讲的是一些小组件，部分在AA的书中介绍过

**Functor , RAII, Concepts**  这些老生常谈不说了

**Policy Class**

作者列举了AA书中的NullPointer的例子，其实这个Policy Class更像type traits中的tag dispatch手法。或者说，Concept约束。没啥好讲的

**CRTP**

静多态

写了个cloneable

```c++
template <typename Derived>
struct cloneable{
  Derived* clone() const{
  return new Derived(static_cast<Derived const&>(*this));
  }
};
struct bar : clonealbe<bar>{...};
```

还有一个经典的例子是enable_shared_from_this, 作为一个观测者(weak_ptr),需要shared的时候抛出去shared_ptr

```c++
template <class T>
class enable_shared_from_this{
mutable weak_ptr<T> weak_this_;
public:
    shared_ptr<T> shared_from_this(){
        shared_ptr<T> p(weak_this_);
        return p;
    }
    ...
};
```



总之这是公共接口静多态实现的一个方法，可以把子类的this拿过来霍霍，比如

```c++
template<class Derived>
struct enable_profit{
    float profit(){
        Derived const & d = static_cast<Derived const &>(*this);
        return 42*(d.output)/d.input;
    }
};
struct department : enable_profit<department>}{
    int output;
    int input;
};
```

**Type Traits** 没啥好讲的

**Tag Dispatching or SFINAE**

![1556623095110](https://wanghenshui.github.io/assets/1556623095110.png)

这个典型就是enable_if



看完感觉就是在复习。

### ref

- <https://github.com/boostcon/cppnow_presentations_2012/blob/master/wed/modern_cpp.pdf?raw=true
- 作者列举的两本书
  - <https://book.douban.com/subject/4136223/>
  - AA  大神的书<https://book.douban.com/subject/1119904/>


看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>