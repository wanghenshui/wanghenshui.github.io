---
layout: post
categories: c++
title: Writing a reverse proxy loadbalancer from the ground up in C
tags: [c, linux, proxy, nginx]
---

  

---

### why 

这篇文章是参考链接的翻译，简而言之，如何写一个反向代理

---

第一版，代码在这里 https://github.com/gpjt/rsp/blob/f214f5a75e112311b90c81ad823bf86c3900b03d/src/rsp.c 

下面的介绍错误处理都去掉了

首先要明白反向代理干啥的，就是接收一个连接，转发给设定好的后端节点。代理/转发

那大概就有了框架

主程序负责接收，处理客户端连接 handle_client_connection

```c
int main(int argc, char *argv[]) {
...
    if (argc != 4) {
        fprintf(stderr, 
                "Usage: %s <server_port> <backend_addr> <backend_port>\n", 
                argv[0]);
        exit(1);
    }
    server_port_str = argv[1];
    backend_addr = argv[2];
    backend_port_str = argv[3];
    server_socket_fd = socket(addr_iter->ai_family,
                                  addr_iter->ai_socktype,
                                  addr_iter->ai_protocol);
    bind(server_socket_fd, addr_iter->ai_addr, addr_iter->ai_addrlen)   
    listen(server_socket_fd, MAX_LISTEN_BACKLOG);

    while (1) {
        client_socket_fd = accept(server_socket_fd, NULL, NULL);


        handle_client_connection(client_socket_fd, backend_addr, backend_port_str);
    }

}
```



处理客户端连接呢，就是客户端来啥，我转发啥，后端节点来啥，原样转发给客户端fd

```c
void handle_client_connection(int client_socket_fd, 
                              char *backend_host, 
                              char *backend_port_str) 
{
    backend_socket_fd = socket(addrs_iter->ai_family, 
                                   addrs_iter->ai_socktype,
                                   addrs_iter->ai_protocol);
    connect(backend_socket_fd, 
                    addrs_iter->ai_addr, 
                    addrs_iter->ai_addrlen) != -1) 
    bytes_read = read(client_socket_fd, buffer, BUFFER_SIZE);
    write(backend_socket_fd, buffer, bytes_read);

    while (bytes_read = read(backend_socket_fd, buffer, BUFFER_SIZE)) {
        write(client_socket_fd, buffer, bytes_read);
    }
}
```



这是简单的同步写法。当然nginx肯定要用epoll来尽量异步



----

### ref

1. http://www.gilesthomas.com/2013/08/writing-a-reverse-proxyloadbalancer-from-the-ground-up-in-c-part-1/
2. http://www.gilesthomas.com/2013/09/writing-a-reverse-proxyloadbalancer-from-the-ground-up-in-c-part-2-handling-multiple-connections-with-epoll/
3. 代码仓库 https://github.com/gpjt/rsp
4. 这有个haproxy的代码解析。https://illx10000.github.io/2018/09/03/16.html

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>