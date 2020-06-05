---
layout: post
title: 多线程lambda 捕获shared_ptr引发的bug
category: [c++, debug]
tags: [c++]
---
{% include JB/setup %}

---

[toc]

bug代码片抽象成这样

```c++
// This file is a "Hello, world!" in C++ language by GCC for wandbox.
#include <iostream>
#include <cstdlib>
#include <string>
#include <functional>
#include <vector>
#include <algorithm>
#include <thread>
#include <memory>
using namespace std;
int main()
{

    std::vector<shared_ptr<int>> v;
    for(int i=0;i<10; i++)
        v.push_back(make_shared<int>(i));
    std::vector<std::thread> threads;
    std::for_each(v.begin(), v.end(),
                  [&](shared_ptr<int> p) {
                  //[&](const shared_ptr<int>& p) {
                    threads.emplace_back(std::move(std::thread([&]() {
                      std::cout << *p<< '\n';
                    })));
                  });
    
    
    /*for (auto &e : v) {
         threads.emplace_back(std::move(std::thread([&]() {
                      std::cout << *e << '\n';
                    })));
    }*/
    for (auto &t :threads)
        t.join();
}
```

注意，捕获shared_ptr的参数不是引用，结果遍历的不是数组中的全部数据，有



## ref

1. 

   

---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。