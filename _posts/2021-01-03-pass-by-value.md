---
layout: post
title: c++参数传值以及move
categories: [language, translation]
tags: [c++, move]

---

> https://xania.org/202101/cpp-by-value-args

就是使用move需要注意的地方，取决于原来的值到底能不能move，move就是偷，掏空

作者贴了一个对比 https://godbolt.org/z/G4hYrT

注意到一个调用了一次 `std::string::_M_create` 另一个调用了两次，

这两种accessor 一种是传值 move，一种是传const引用 （不是常量引用是编不过的）

```c++
//调用一次_M_create
#include <string>

struct Thing {
  std::string s_;
  void set_s(std::string s) { s_ = std::move(s); }
};

void test(Thing &t) {
  t.set_s("this is a long string to show something off");
}
```



```c++
//调用两次_M_create
#include <string>

struct Thing {
  std::string s_;
  void set_s(const std::string &s) { s_ = s; //s_ = std::move(s); }
};

void test(Thing &t) {
  t.set_s("this is a long string to show something off");
}
```



为什么结果不同？主要原因是常量引用初始化之后，根本无法调用move，于是又拷贝构造一遍，所以调用两次create

而第一种写法，只一次构造。这也是现在推荐的accessor的写法



PS: 另外，测试代码的string要足够长 > 24，不然会有SBO优化，不会调用M_create

不过小串的版本，move也是要比传常量引用要省的 看这个对比 https://godbolt.org/z/xr1bno



PPS: 如果参数是move

```c++
#include <string>
#include <memory>
struct Thing {
  std::unique_ptr<std::string> s_;
  void set_s(std::unique_ptr<std::string> s) { s_ = std::move(s); }
};

void test(Thing &t) {
  auto s = std::make_unique<std::string>("this is a long string to show something off")
  //t.set_s(s);
  t.set_s(std::move(s));
}
```

传参数不能发生构造，必须强制move，不move直接编译不过，也不能直接传右值


---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>