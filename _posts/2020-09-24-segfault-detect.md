---
layout: post
title: 探测指针地址是否有效
categories: [language]
tags: [c, signal, asm]
---


---

 场景，当访问不合法的地址，当场segment fault，为了避免，如何探测？

两种方案

- 捕获sigsegv信号
- 查/proc/self/maps 的地址范围，做个校验
  - 问题：多线程竞争，可能导致误判，不可取

作者写了个简单的代码，这里直接列出来看看原理即可



```c
#define _GNU_SOURCE
#include <stdint.h>
#include <signal.h>
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <ucontext.h>

#ifdef __i386__
typedef uint32_t word_t;
#define IP_REG REG_EIP
#define IP_REG_SKIP 3
#define READ_CODE __asm__ __volatile__(".byte 0x8b, 0x03\n"  /* mov (%ebx), %eax */ \
                                       ".byte 0x41\n"        /* inc %ecx */ \
                                       : "=a"(ret), "=c"(tmp) : "b"(addr), "c"(tmp));
#endif

#ifdef __x86_64__
typedef uint64_t word_t;
#define IP_REG REG_RIP
#define IP_REG_SKIP 6
#define READ_CODE __asm__ __volatile__(".byte 0x48, 0x8b, 0x03\n"  /* mov (%rbx), %rax */ \
                                       ".byte 0x48, 0xff, 0xc1\n"  /* inc %rcx */ \
                                       : "=a"(ret), "=c"(tmp) : "b"(addr), "c"(tmp));
#endif

static void segv_action(int sig, siginfo_t *info, void *ucontext) {
    (void) sig;
    (void) info;
    ucontext_t *uctx = (ucontext_t*) ucontext;
    uctx->uc_mcontext.gregs[IP_REG] += IP_REG_SKIP;
}

struct sigaction peek_sigaction = {
    .sa_sigaction = segv_action,
    .sa_flags = SA_SIGINFO,
    .sa_mask = 0,
};

word_t peek(word_t *addr, int *success) {
    word_t ret;
    int tmp, res;
    struct sigaction prev_act;

    res = sigaction(SIGSEGV, &peek_sigaction, &prev_act);
    assert(res == 0);

    tmp = 0;
    READ_CODE

    res = sigaction(SIGSEGV, &prev_act, NULL);
    assert(res == 0);

    if (success) {
        *success = tmp;
    }

    return ret;
}

int main() {
    int success;
    word_t number = 22;
    word_t value;

    number = 22;
    value = peek(&number, &success);
    printf("%d %d\n", success, value);

    value = peek(NULL, &success);
    printf("%d %d\n", success, value);

    value = peek((word_t*)0x1234, &success);
    printf("%d %d\n", success, value);

    return 0;
}

```

看一乐啊，这里就是操作指针对应的寄存器，不保证正确（多线程下应该不对，这东西应该说进程级别的，放在最外层）

另外，如果不是写什么共享内存程序，segment fault 就挂了的了，别挽救了

---

### ref

- 文章摘抄自这里 https://www.giovannimascellani.eu/having-fun-with-signal-handlers.html#having-fun-with-signal-handlers


---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>