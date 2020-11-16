---
layout: post
title: C++ Concurrency In Action读书笔记
categories: c++
tags: [c++, thread]
---

  

#### C++ Concurrency In Action

 为什么使用并发

- 分离关注点
- 性能

### 线程管理

`std::thread`

- 当把函数对象传入到线程构造函数中时，需要避免“最令人头痛的语法解析C++’s most vexing parse
  - 解决办法 两层（）或统一初始化方法{}
- 使用lambda规避
- join和detach
- 传递参数，注意std::thread构造函数会复制参数（可以移动，不可以拷贝）

转移线程所有权 （本身可以移动，不可以拷贝）

```c++
class scoped_thread{
    std::thread t_;
public:
    explicit scoped_thread(std::thread t)t_(std::move(t)){
        if (!t_.joinable())
            throw std::logic_error("No thread");
    }
    ~scoped_thread(){
        t.join();
    }
    scoped_thread(scoped_thread const&) = delete;
    scoped_thread& operator=(scoped_thread const&) = delete;
};
```



c++17建议`std::jthread` 自带上面的析构功能，不用手写join 标准库里已经有了

  一行循环join,确实比range-for好看点

```c++
std::for_each(threads,begin(), threads.end(), std::mem_fn(&std::thread::join));
```



`std::thread::hardware_concurrency()` 使用线程数暗示

` std::thread::get_id`  `std::this_thread::get_id()`

## 线程间共享数据

共享数据带来的问题（多用assert）

- 竞态条件 互斥与无锁编程
- 软件事务内存 software transactional memory
- 接口中的竞态条件
  - 解决方案 传引用
  - 解决方案 异常安全的拷贝构造和移动构造
  - 解决方案，返回指针 shared_ptr
- 锁的细粒度 以及死锁的解决方案
  - 避免嵌套锁
  - 持有锁，要保证接下来的动作没有危害（用户侧调用就很容易被坑，所以避免调用用户侧代码）
  - 固定顺序开锁解锁
    - 锁，分优先级，层次
    - unique_lock unlock...lock...
    - lock_guard
- 初始化时保护共享数据
  - std::once_flag std::call_once
  - meyer's singleton
- boost::shared_lock shared_lock<>

### 

### 同步并发操作

- 等待事件与条件
  - 忙等待
  - 条件变量
  - std::condition_variable notify_one wait
  - std::future  一次性时间
    - std::async 类似std::thread 不过最后阻塞的是future.get()
    - std::packaged_task<>
    - std::promise
- future FP
- 消息传递同步 wait().handle<>

### 

### c++内存模型与原子操作

- 原子操作 store load read-modify-write
- 同步操作与顺序
  - 内存顺序
  - 顺序一致与内存同步操作，代价。
  - 非顺序一致的memory-order 线程不闭合时间的顺序一致

---

### ref

1. github翻译地址：https://github.com/xiaoweiChen/CPP-Concurrency-In-Action-2ed-2019
2. gitbook 在线阅读：https://legacy.gitbook.com/book/chenxiaowei/c-concurrency-in-action-second-edition-2019
3. 本书源码下载地址：https://www.manning.com/downloads/1954
4. 第一版github 翻译地址：https://github.com/xiaoweiChen/Cpp_Concurrency_In_Action

---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details> 先谢指教。