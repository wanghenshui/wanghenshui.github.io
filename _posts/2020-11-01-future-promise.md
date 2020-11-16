---
layout: post
title: future promise实现程度调研
categories: [c++]
tags: [future]
---

 

| Future promise<br>接口实现程度              | std::future | boost::future | seastar::future | Folly::Future |
| ------------------------------------------- | ----------- | ------------- | --------------- | ------------- |
| continuations/then()                        | X           | √             | √               | √             |
| when_all                                    | X           | √             | √               | √*            |
| when_any                                    | X           | √             | X               | √             |
| whenN                                       | X           | X             | X               | √             |
| future超时                                  | X*          | √             | √               | √             |
| 指定Executor/线程池                         | X*          | X*            | √*              | √             |
| Executor动态调度<br>(包括增删线程/主动调度) | X           | X             | X*              | X*            |
| 异步文件io                                  | X           | X             | √*              | √*            |



- 关于continuations，folly的when_all/when_any接口叫collect*

- 关于超时，api不太一样，std::future::wait_for (从wait来的) 没有回调接口，folly::future::onTimeout

- 关于指定Executor， boost::future 可以在then里指定 , 有接口但是没有样例。executor和future暂时不能结合使用

  

- folly指定Executor通过via接口，不同的异步流程交给不同的executor来工作，，避免引入数据竞争，Executor可以说线程池(ThreadPollExecutor)也可以一个事件循环EventBase(封装libevent)

```c++
makeFutureWith(x)
  .via(exe1).then(y)
  .via(exe2).then(z);
```

可以中途变更executor，改执行策略，这也是标准库演进的方向，尽可能的泛型

- ~~std::future 和executor配合使用本来计划本来concurrency-ts中实现，规划c++20，后来作废了。支持std::experiental::executor 和std::experiential::future没有编译器实现，ASIO作者有个实现但是是很久以前的了~~

  ~~新的executor得等到c++23了，目前标准库还在评审，一时半会是用不上了~~

但是ASIO是实现了executor了的，这里的异步抽象更高一些，和future接口没啥关系

```c++
void connection::do_read() 
{
  socket_.async_read_some(in_buffer_, 
    wrap(strand_, [this](error_code ec, size_t n)
      {
        if (!ec) do_read();
      }));
}
//strand_ 是asio中的概念，可以简单理解成executor，换成pool之类的也是可以的 
```

- seastar 可以使用scheduling_group来规划不同的future，分阶段调度

  - 文件异步io AIO 系统api封装



---

### ref

- https://www.cnblogs.com/chenyangyao/p/folly-future.html
- https://engineering.fb.com/developer-tools/futures-for-c-11-at-facebook/
- https://www.modernescpp.com/index.php/std-future-extensions
- https://www.modernescpp.com/index.php/a-short-detour-executors
- https://stackoverflow.com/questions/44355747/how-to-implement-stdwhen-any-without-polling
- asio的概念 executor/strandhttps://www.cnblogs.com/bbqzsl/p/11919502.html




---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>