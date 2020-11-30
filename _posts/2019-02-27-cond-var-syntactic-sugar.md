---
layout: post
title: std::condition_variable::wait 一处细节
categories: language
tags: [c++]
---
  
# std::condition_variable::wait 一处细节

[摘选自这里](https://zh.cppreference.com/w/cpp/thread/condition_variable/wait)

简单说，是一个语法糖

```
template< class Predicate >
void wait( std::unique_lock<std::mutex>& lock, Predicate pred );
```

等价于

```
while (!pred()) {
    wait(lock);
}
```

写过pthread_cond_wait 都明白第二种写法，为了避免[虚假唤醒](https://www.zhihu.com/question/271521213)。

标准库还提供不带谓词的wait版本，如果不是用过底层api原语的很容易用错，写成if形式，所以提供了上面这个版本，比较优雅，while形式比较不容易表明意图。

还写了个最佳实践

http://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#Rconc-wait 

~~话说这个我只是收藏了，从来没看完过，可以理解成more modern effective c++~~

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>