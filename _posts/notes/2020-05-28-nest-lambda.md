---
layout: post
title: 嵌套lambda 捕获shared_ptr引发的bug
category: [c++, debug]
tags: [c++]
---
{% include JB/setup %}

---

[toc]

bug代码片抽象成这样

```c++
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
                  //改成传const引用就没问题了
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



问题出在内部的lambda是捕获引用，但是捕获的值是栈上的，这个栈上分配的值在该场景下是复用的，结果有问题。

嵌套lambda，一定要注意捕获参数。参考链接1有详细的介绍，总结五个常见的嵌套lambda搭配

1. 传值，捕获值，没问题，但是会有赋值开销
2. 传值，捕获引用，有问题，传的值是分配在栈上的，捕获引用可能会变，可能不存在等等
3. 传引用，捕获引用，没问题，但是不能传右值
4. 传const引用，捕获引用，没问题，但是传的值失去了左值能修改的特性
5. 传值，移动捕获值，unique_ptr只能这么捕获。也是一个好的捕获方案，省一次拷贝。

上面的案例就犯了2 的错误。改成const 引用就好了



## ref

1. http://lucentbeing.com/writing/archives/nested-lambdas-and-move-capture-in-cpp-14/

2. 关于lambda嵌套。很复杂。https://zh.cppreference.com/w/cpp/language/lambda

3. 一个lambda的分析 https://web.mst.edu/~nmjxv3/articles/lambdas.html

   

---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。