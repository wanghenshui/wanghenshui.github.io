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



PPS: 如果参数是unique_ptr

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



PPPS:

如果是循环中调用setter，可能分配会更多

```c++
std::string s;
Thing t;
for (int i = 0 ; i < 900 ; ++i) {
  set_next_string(s, i);
  t.set_s(s);
}
```

不过作为setter/accessor，不像是正常人的用法，这种场景下，s_是最开始有分配，后面有足够的空间，能省一些malloc，但是传右值+move绝对会多次malloc

如果能保证s的声明周期，并不是非得落在Thing中，那么用std::string_view会更好。

没有绝对正确的方案，取决于你怎么用


---

