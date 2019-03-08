---
layout: post
title: redis 代码走读 server.c
category: database
tags: [redis, c]
---
{% include JB/setup %}
#redis 代码走读 server.c

[TOC]



## tzset

time zone set的意思。初始化全局的时间记录

[API文档](http://manpages.ubuntu.com/manpages/cosmic/en/man3/tzset.3.html)



如果前面有setenv设置了timezone `setenv("TZ", "GMT-8", 1);`，这里就会更新。

主要更新

| 全局变量    | 说明                             | 缺省值                                                       |
| ----------- | -------------------------------- | ------------------------------------------------------------ |
| __daylight  | 如果在TZ设置中指定夏令时时区     | 1则为非0值;否则为0                                           |
| __timezone  | UTC和本地时间之间的时差,单位为秒 | 28800(28800秒等于8小时)                                      |
| __tzname[0] | TZ环境变量的时区名称的字符串值   | 如果TZ未设置则为空 PST                                       |
| __tzname[1] | 夏令时时区的字符串值;            | 如果TZ环境变量中忽略夏令时时区则为空PDT在上表中daylight和tzname数组的缺省值对应于"PST8PDT |

在glibc中代码 `time/tzset.c`

```c
void 
__tzset (void)
{
  __libc_lock_lock (tzset_lock);
  tzset_internal (1);
  if (!__use_tzfile)// 注意这里没有设置过TZ就不会进来。
    {
      /* Set `tzname'.  */ 
      __tzname[0] = (char *) tz_rules[0].name;
      __tzname[1] = (char *) tz_rules[1].name;
    }
  __libc_lock_unlock (tzset_lock);
}
```



实现在tzset_internal中

```c
static void
tzset_internal (int always)
{
  static int is_initialized;
  const char *tz;

  if (is_initialized && !always)//tzset只会执行一次，初始化过就不会再执行
    return;
  is_initialized = 1;
  /* Examine the TZ environment variable.  */
  tz = getenv ("TZ");
  if (tz && *tz == '\0')
    /* User specified the empty string; use UTC explicitly.  */
    tz = "Universal";
  	
    // 处理tz 字符串，过滤掉：...
	// 检查tz字符串是不是和上次相同，相同就直接返回...
    // 新的tz是NULL 就设定成默认的TZDEFAULT "/etc/localtime"...
    //保存到old_tz...

  //  去读tzfile ,获取daylight和timezone 这里十分繁琐,也有几处好玩的
  // 1. 打开文件校验是硬编码的，We must not allow to read an arbitrary file in a  `setuid` program
  // 2. FD_CLOSEXEC
       /* Note the file is opened with cancellation in the I/O functions
       disabled and if available FD_CLOEXEC set.  */
      //f = fopen (file, "rce"); 具体解释看api文档
       //这个mode参数是glibc扩展https://www.gnu.org/software/libc/manual/html_node/Opening-Streams.html
  __tzfile_read (tz, 0, NULL);
  //后续是没读到文件的默认复制动作...  
}
```

## setlocale



## getRandomHexChars

getRandomHexChars -> getRandomBytes 

生成随机数直接用

```
FILE *fp = fopen("/dev/urandom","r");
if (fp == NULL || fread(seed,sizeof(seed),1,fp) != 1){
    /* Revert to a weaker seed, and in this case reseed again
     * at every call.*/
     for (unsigned int j = 0; j < sizeof(seed); j++) {
            struct timeval tv;
            gettimeofday(&tv,NULL);
            pid_t pid = getpid();
            seed[j] = tv.tv_sec ^ tv.tv_usec ^ pid ^ (long)fp;
     }
 }
```

保证安全，如果失败就先用时间戳和pid生成一个，但是还是不安全，还是会用fopen重新生成

有个局部静态counter ，每次hash都不一样

## initServerConfig

初始化server参数

有几个有意思的点：

1. cachedtime 保存一份时间，优化，因为很多对象用这个，就存一份，比直接调用time要快

2. server.tcp_backlog设置成了521.

3. 默认的客户端连接空闲时间是0，无限

4. tcpkeepalive设置成了300

   ...参数太多

5. server.commands 用hashtable存了起来，在一开始已经用数组存好了。

   1. 优化点，经常使用的命令单独又存了一遍，也有可能后续读配置文件被改。 /* Fast pointers to often looked up command */

6. 检查backlog FILE *fp = fopen("/proc/sys/net/core/somaxconn","r");

7. daemonize 不说了，很常见的操作，fork +exit父进程退出，setsid 改权限，重定向标准fd，打开垃圾桶open("/dev/null", O_RDWR)

   1. 如果是守护进程得建立个pidfile，这个目录写死，在var/run/redis.pid

8. initServer 忽略SIGHUP SIGPIPE，SIGPIPE比较常见

   1. catch TERM，INT，kill
   2. segment fault 信号，会直接死掉，OR，打印堆栈和寄存器，在sigsegvhandler中，这个实现值得一看了解怎么获取堆栈

9. 下面就是listen和处理socket ipc了。

10. 然后是各种初始化，LRU初始化

    未完待续
