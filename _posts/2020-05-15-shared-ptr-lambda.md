---
layout: post
title: 回调lambda引发的shared_ptr循环依赖以及解决办法
categories: [language]
tags: [lambda,shared_ptr,function, c++]
---

> 参考链接资料汇总

如果你是搜索到这里的，请注意这个问题描述的场景

- **对象自身的回调捕获了自己的值**，自己造成了**循环**



出事的代码是这样的

```c++
class my_class {
// ...
public:
  typedef std::function<void()> callback;
  void on_complete(callback cb) { complete_callback = cb; }
private:
  callback complete_callback;
// ...
};
 
// ...
  std::shared_ptr<my_class> obj = std::make_shared<my_class>();
  obj->on_complete([obj]() {
    obj->clean_something_up();
  });
  executor->submit(obj);
// ...
```



注意，lambda默认是const，不改变值 [SO](https://stackoverflow.com/questions/43319352/stdmove-with-stdshared-ptr-in-lambda) 

lambda的本质就是传值的一个指针，如果这里用std::function保存，会导致这个捕获的指针泄漏，导致这个指针永远不释放



解决方案1，weak_ptr，或者weak_from_this

```c++

class my_class {
// ...
public:
  typedef std::function<void()> callback;
  void on_complete(callback cb) { complete_callback = cb; }
private:
  callback complete_callback;
// ...
};
 
// ...
  std::shared_ptr<my_class> obj = std::make_shared<my_class>();
  std::weak_ptr<my_class> weak_obj(obj);
 
  obj->on_complete([weak_obj]() {
    auto obj = weak_obj.lock();
    if (obj) {
      obj->clean_something_up();
    }
  });
  executor->submit(obj);
```



解决方案2 ，lambda加上 mutable，见[这个SO](https://stackoverflow.com/questions/18818260/passing-shared-ptr-to-lambda-by-value-leaks-memory)



参考链接2给出了一个比较经典的循环



```c++
void capture_by_value(uvw::Loop &loop) {
    auto conn = loop.resource<uvw::TcpHandle>();
    auto timer = loop.resource<uvw::TimerHandle>();

    // OK: capture uses [=]
    conn->on<uvw::CloseEvent>([=](const auto &, auto &) {
        timer->close();
    });

    // Now timer has a callback to conn, and vice versa...
    timer->on<uvw::CloseEvent>([=](const auto &, auto &) {
        conn->close();
    });
};
```

这里conn和timer循环了，如何规避？**weak_from_this（前提，继承std::enable_shared_from_this.）**

```c++
void capture_weak_by_value(uvw::Loop &loop) {
    auto conn = loop.resource<uvw::TcpHandle>();
    // Create a std::weak_ptr to the connection. weak_from_this() is new
    // in C++17, and is enabled on all classes that inherit from
    // std::enable_shared_from_this.
    auto w_conn = conn->weak_from_this();

    auto timer = loop.resource<uvw::TimerHandle>();
    auto w_timer = timer->weak_from_this();  // as above

    // OK, uses weak_ptr
    conn->on<uvw::CloseEvent>([=](const auto &, auto &) {
        if (auto t = w_timer.lock()) t->close();
    });

    // OK, uses weak_ptr
    timer->on<uvw::CloseEvent>([=](const auto &, auto &) {
        if (auto c = w_conn.lock()) c->close();
    });
});

```







## ref

1. http://web.archive.org/web/20180324083405/http://https://floating.io/2017/07/lambda-shared_ptr-memory-leak/ 原网址挂了
2. https://eklitzke.org/notes-on-std-shared-ptr-and-std-weak-ptr 介绍weak_from_this



---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>