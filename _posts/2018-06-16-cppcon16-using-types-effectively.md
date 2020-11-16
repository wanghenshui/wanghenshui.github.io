---
layout: post
title: (cppcon)using types effectively
category: c++
tags: [c++, cppcon]
---
  

#### cppcon2016 using types effectively

本来还在看cppcon2014，偶然翻到个和类型相关的演讲，以为是以为是PLT那种东西。学习过之后发现还是讨论的代数类型



sum type 和product type就不说了，主要是类型带来的重复和内耗，c++17带来了std::optional和 std::variant ，组织状态就可以用这俩，放弃原来的switch做法，转用match，缩小范围，全变成类型，更可控

中间有大量的篇幅推导product type的数量级，函数的数量级是指数级！

还讨论了个小插曲，在lua中1==true结果为false，因为不是同一个类型



作者的一个改造例子

原有方案

```c++
enum class ConnectionState{
    DISCONNECTED,
    CONNECTING,
    CONNECTED,
    CONNECTION_INTERRUPTED
};
struct Connection{
    ConnectionState m_connectionState;
    std::string m_serverAddress;
    std::chrono::system_clock::time_point m_connectedTime;
    std::chrono::millisecondes m_lastPingTime;
    Timer m_reconnectTimer;
};
```

 在看改造后

```c++
struct Connection{
    std::string m_serverAddress;
    struct Disconnected{};
    struct Connecting{};
    struct Connected{
        ConnectionId m_id;
        std::chrono::system_clock::time_point m_connectedTime;
        std::chrono::millisecondes m_lastPingTime;
    };
    struct ConnectionInterrupted{
        std::chrono::system_clock::time_point m_disconnectedTime;
        Timer m_reconnectTimer;
    };
    std::variant<Disconnected,Connecting,Connected,ConnectionInterrupted> m_connection;
};
```



再举一个例子

 ```c++
class Friend{
    std::string m_alias;
    bool m_aliasPopulated;
};
 ```

 两个字段到处同步，坑爹 -> std::optional\<string> m_alias



### ref

- [https://github.com/CppCon/CppCon2016/blob/master/Tutorials/Using%20Types%20Effectively/Using%20Types%20Effectively%20-%20Ben%20Deane%20-%20CppCon%202016.pdf

看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。