---
layout: post
title: 译-Debugging a futex crash
categories: [languages]
tags: [asm,c++]
---

[Debugging a futex crash](https://rustylife.github.io/2023/08/15/futex-crash.html)

很精彩的文章, 水友群一个朋友遇到了一个ceph挂掉的问题，现象非常像这个文章，分析后发现一样

水友的堆栈是这样的


<img src="https://wanghenshui.github.io/assets/ceph-futex.png" width="100%">


这里分享给大家，已经获得原作者授权

<!-- more -->

首先core的堆栈仅有 futex相关

```txt
>>> bt
#0  0x00007f7430470fbb in raise () from /home/rusty/futex/sysroot/lib/x86_64-linux-gnu/libc.so.6
#1  0x00007f7430456864 in abort () from /home/rusty/futex/sysroot/lib/x86_64-linux-gnu/libc.so.6
#2  0x00007f74304b949c in ?? () from /home/rusty/futex/sysroot/lib/x86_64-linux-gnu/libc.so.6
#3  0x00007f74304b97b0 in __libc_fatal () from /home/rusty/futex/sysroot/lib/x86_64-linux-gnu/libc.so.6
#4  0x00007f743062f01c in __lll_lock_wait () from /home/rusty/futex/sysroot/lib/x86_64-linux-gnu/libpthread.so.0
#5  0x00007f7430627733 in pthread_mutex_lock () from /home/rusty/futex/sysroot/lib/x86_64-linux-gnu/libpthread.so.0
#6  0x0000000001acedc0 in ?? ()
#7  0x0000000000000000 in ?? ()
```

怎么抓bug？

首先有__libc_fatal或者futex_fatal_error 基本能定位到是futex_wait上出问题了
ll_futex_wait基本包一层futex_wait

```c+
void
__lll_lock_wait (int *futex, int private)
{
  if (atomic_load_relaxed (futex) == 2)
    goto futex;

  while (atomic_exchange_acquire (futex, 2) != 0)
    {
    futex:
      LIBC_PROBE (lll_lock_wait, 1, futex);
      futex_wait ((unsigned int *) futex, 2, private); /* Wait if *futex == 2.  */
    }
}
libc_hidden_def (__lll_lock_wait)

```
futex_wait的代码如下

```c++
static __always_inline int
futex_wait (unsigned int *futex_word, unsigned int expected, int private)
{
  int err = lll_futex_timed_wait (futex_word, expected, NULL, private);
  switch (err)
    {
    case 0:
    case -EAGAIN:
    case -EINTR:
      return -err;

    case -ETIMEDOUT: /* Cannot have happened as we provided no timeout.  */
    case -EFAULT: /* Must have been caused by a glibc or application bug.  */
    case -EINVAL: /* Either due to wrong alignment or due to the timeout not
		     being normalized.  Must have been caused by a glibc or
		     application bug.  */
    case -ENOSYS: /* Must have been caused by a glibc bug.  */
    /* No other errors are documented at this time.  */
    default:
      futex_fatal_error ();
    }
}

```

这几个错误是最值得关注的，按图索骥就行了
首先不是ETIMEDOUT，其次EFAULT和ENOSYS是比较难查的，EINVAL反而比较好查，先确认是不是wrong alignment  对齐问题，简单来说，就是查地址，思路有了，怎么查？切到frame 5

```gdb
>>> frame 5
#5  0x00007f7430627733 in pthread_mutex_lock () from /home/rusty/futex/sysroot/lib/x86_64-linux-gnu/libpthread.so.0

>>> disassemble pthread_mutex_lock
...
   0x00007f7430627723 <+211>:	mov    %rdi,0x8(%rsp)
   0x00007f7430627728 <+216>:	and    $0x80,%esi
   0x00007f743062772e <+222>:	call   0x7f743062efc0 <__lll_lock_wait>
=> 0x00007f7430627733 <+227>:	mov    0x8(%rsp),%rdi
   0x00007f7430627738 <+232>:	jmp    0x7f7430627689 <pthread_mutex_lock+57>
...

>>> x/w ($rsp + 8)
0x7f7371ff1ce8:	0x08001ea1
```

抓到了不对齐？？看懂怎么定位的了没？

__lll_lock_wait (int *futex, int private) 怎么传futex和private？

mov    0x8(%rsp),%rdi到lock_wait，说明 退回去就是futex和private，对吧

不记得的琢磨一下汇编哈，看看这个 https://godbolt.org/z/bbET88a1x


复现一下

```c
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <pthread.h>

pthread_mutex_t mutex __attribute__((section(".reproducer"))) __attribute__ ((aligned(1)));

int main(int argc, char **argv)
{
	printf("mutex %p\n", &mutex);
	pthread_mutex_lock(&mutex);
	pthread_mutex_lock(&mutex);
}

```
为什么锁两次，因为锁一次不能复现,正常来说顶多死锁

编译执行

```bash
rusty@nuc10:~/futex$ gcc -g futex0.c -lpthread  -Wl,--section-start=.reproducer=0x8001ea1
rusty@nuc10:~/futex$ ./a.out 
mutex 0x8001ea1
The futex facility returned an unexpected error code.
Aborted (core dumped)
rusty@nuc10:~/futex$ 

```

能复现，接下来就要确认futex哪里报错了

```bash
rusty@nuc10:~/code/kernel$ git grep -c "\-EINVAL" kernel/futex/
kernel/futex/core.c:1
kernel/futex/pi.c:4
kernel/futex/requeue.c:11
kernel/futex/syscalls.c:8
kernel/futex/waitwake.c:7
```

trace-cmd 录一下调用栈

```bash
rusty@nuc10:~/futex$ sudo trace-cmd record -q -F -p function_graph ./a.out
mutex 0x8001ea1
The futex facility returned an unexpected error code.

rusty@nuc10:~/futex$ sudo trace-cmd report
...
           a.out-867356 [004] 112365.616487: funcgraph_entry:        0.168 us   |  exit_to_user_mode_prepare();
           a.out-867356 [004] 112365.616487: funcgraph_entry:                   |  __x64_sys_futex() {
           a.out-867356 [004] 112365.616488: funcgraph_entry:                   |    do_futex() {
           a.out-867356 [004] 112365.616488: funcgraph_entry:                   |      futex_wait() {
           a.out-867356 [004] 112365.616488: funcgraph_entry:        0.150 us   |        futex_setup_timer();
           a.out-867356 [004] 112365.616488: funcgraph_entry:                   |        futex_wait_setup() {
           a.out-867356 [004] 112365.616488: funcgraph_entry:        0.199 us   |          get_futex_key();
           a.out-867356 [004] 112365.616489: funcgraph_exit:         0.425 us   |        }       
           a.out-867356 [004] 112365.616489: funcgraph_exit:         0.954 us   |      }         
           a.out-867356 [004] 112365.616489: funcgraph_exit:         1.205 us   |    }         
           a.out-867356 [004] 112365.616489: funcgraph_exit:         1.581 us   |  }
```

能看到死在get_futex_key里，看一下代码

```c++
         /*
          * The futex address must be "naturally" aligned.
          */
         key->both.offset = address % PAGE_SIZE;
         if (unlikely((address % sizeof(u32)) != 0))
                  return -EINVAL;

```
就是你了

---

2024 0413 后记

1. 我和水友群的朋友都尝试复现没成功，通过strace能确定EINVAL报错的，但是并没有崩溃，不同glibc的行为可能不一致，注意

2. 开头提到的崩溃是他们模块使用pack(1) 编译，手动padding之后，就不崩溃了。强烈不建议pack1 ，要知道自己在做什么
