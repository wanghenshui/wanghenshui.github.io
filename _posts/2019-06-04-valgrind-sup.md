---
layout: post
categories: tools
title: valgrind sup文件的作用以及生成
tags: [valgrind]
---

  

---

redis的runtest支持valgrind，里面有这么一条

```tcl
if {$::valgrind} {
        set pid [exec valgrind --track-origins=yes --suppressions=src/valgrind.sup --show-reachable=no --show-possibly-lost=no --leak-check=full src/redis-server $config_file > $stdout 2> $stderr &]
    } elseif ($::stack_logging) {
        set pid [exec /usr/bin/env MallocStackLogging=1 MallocLogFile=/tmp/malloc_log.txt src/redis-server $config_file > $stdout 2> $stderr &]
    } else {
        set pid [exec src/redis-server $config_file > $stdout 2> $stderr &]
    }
```

里面引用到sup文件<https://github.com/antirez/redis/blob/unstable/src/valgrind.sup>

sup表示suppress，避免valgrind出错的意思，这个文件定义一系列规则，valgrind检测的时候跳过这些触发条件，比如redis的是这样的

```
{
   <lzf_unitialized_hash_table>
   Memcheck:Cond
   fun:lzf_compress
}

{
   <lzf_unitialized_hash_table>
   Memcheck:Value4
   fun:lzf_compress
}

{
   <lzf_unitialized_hash_table>
   Memcheck:Value8
   fun:lzf_compress
}
```

对于提示unitialized hash table提醒，跳过不处理

再比如我遇到的一个epoll提示

```
...
==13711== Syscall param epoll_ctl(event) points to uninitialised byte(s)
==13711==    at 0x6E30CBA: epoll_ctl (in /usr/lib64/libc-2.17.so)
...
==13711==  Address 0xffefffad8 is on thread 1's stack
==13711==  in frame #1, created by xxxx
==13711==  Uninitialised value was created by a stack allocation
==13711==    at 0x561500: xxxx

```

这个很明显，valgrind有问题，这段代码没问题（问题不大）却告警了

```c++
  struct epoll_event ee;
  ee.data.fd = fd;
  ee.events = mask;
  return epoll_ctl(epfd_, EPOLL_CTL_ADD, fd, &ee);
```

这个原因见参考链接，实际上需要加个memset，由于padding问题。

但是这步完全可以省掉，生成类似的sup规则

```
{
   <epoll_add>
   Memcheck:Param
   epoll_ctl(event)
   fun:epoll_ctl
}
```

读入，就会避免这些告警

#### 如何生成sup规则？

规则肯定不是自己手写的，如果很多告警挨个手写也太低效了，实际上valgrind支持导出sup规则 ，见参考链接, 比如二进制是minimal

```bash
valgrind --leak-check=full --show-reachable=yes --error-limit=no --gen-suppressions=all --log-file=minimalraw.log ./minimal
```

另外，valgrind可以指定log文件。我一直都是重定向` >log 2>&1` 特傻

也可以不像redis这样读入，直接写到 `.valgrindrc`里，套路类似bashrc（不过有污染也不好）

 参考链接中的文章用了两步，先是上面这个命令，提取出log，然后log中已经有一系列sup信息了，再通过一个脚本parse一下。不过据我分析，第一步就能整理出来，不过有重复，冗余比较多，可以整理成上面epoll_ctl这种形式的四行一组就行了。

详情可以读参考链接中的文章。写的很好

### ref

- <https://wiki.wxwidgets.org/Valgrind_Suppression_File_Howto>
- 这有个epoll告警的例子<https://github.com/libuv/libuv/issues/1215>
- 上面这个epoll告警的一个解决办法，实际上屏蔽就可以<https://stackoverflow.com/questions/19364942/points-to-uninitialised-bytes-valgrind-errors>


### contact

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
![微信转账](https://wanghenshui.github.io/assets/wepay.png)
</details>