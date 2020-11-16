---
layout: post
categories: c++
title: copy elision
tags: [c++]
---

  

---

#### Why

这是参考链接中ppt的总结

copy elision到底做了什么

---

`RVO 返回值优化`

这个在copy elision之前就有的优化，copy elision算是大一统理论？

简单说

```c++
std::string f(){
    ...
    std::string a;
    ...
    return a;
}
```

这里的a不会在stack上分配空间，而是直接放到返回值那个地址上。

`Argument Passing 参数传递优化`

在copy elision之前，传值的赋值就是复制，直接拷贝一份，有了copy elision，直接折叠掉

注意，产生条件只是右值，左值不会省略。因为左值地址不能直接用。

```c++
void f(std::string a){
    ...
    int b{23};
    ...
    return;
}
void g(){
    ...
    f(std::string{"A"});
    ...
}
```

这里原本是为这个临时变量在当前栈生成一个然后压栈再生成一个，直接折叠复用同一个。

### ref

1. https://github.com/boostcon/cppnow_presentations_2018/blob/master/lightning_talks/copy_elision__jon_kalb__cppnow_05092018.pdf


### contact

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。