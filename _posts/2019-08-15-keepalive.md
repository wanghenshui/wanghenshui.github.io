layout: post
title: tcp keepalive
category: [linux]
tags: [tcp,linux,c]

  

---



```c
int opt_val = 1;
setsockopt(sock_fd, SOL_SOCKET, SO_KEEPALIVE, &opt_val, sizeof(opt_val)) 
```

启用后，socket **默认**的检测参数使用**内核参数**，使用` sysctl -a|grep tcp_keepalive`查看，或者使用以下命令查看：

```bash
cat /proc/sys/net/ipv4/tcp_keepalive_time
cat /proc/sys/net/ipv4/tcp_keepalive_intvl
cat /proc/sys/net/ipv4/tcp_keepalive_probes
```

修改内核的参数可以使用 vim /etc/sysctl.conf 修改，然后使用 sysctl -p 应用



如果需要设置自定义的心跳参数，则需要使用 setsockopt 函数设置：

```c
setsockopt (sock_fd,  SOL_TCP,  TCP_KEEPIDLE,  &idle, sizeof(idle)) 
setsockopt (sock_fd,  SOL_TCP,  TCP_KEEPINTVL,  &intvl, sizeof(intvl)) 
setsockopt (sock_fd,  SOL_TCP,  TCP_KEEPCNT,  &cnt,  sizeof(cnt))
```



以上几个参数含义为：

- TCP_KEEPIDLE：多久没有交互时，发送一个心跳包
- TCP_KEEPINTVL：每次探活间隔多久
- TCP_KEEPCNT：一共探活多少次