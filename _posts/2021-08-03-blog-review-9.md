---
layout: post
title: blog review 第九期
categories: [review, todo]
tags: [bpf, zip, c++,linux,memory, mutex, tco, disruptor,perf,flamegraph,gc,consistency,memory model]
---

准备把blog阅读和paper阅读都归一，而不是看一篇翻译一篇，效率太低了

后面写博客按照 paper review，blog review，cppcon review之类的集合形式来写，不一篇一片写了。太水了

<!-- more -->

[toc]



## [Writing a Simple Garbage Collector in C](http://maplant.com/gc.html)

非常简单傲

### 获取内存，freep维护

```c
typedef struct header {
    unsigned int    size;
    struct header   *next;
} header_t;

static header_t base;           /* Zero sized block to get us started. */
static header_t *freep = &base; /* Points to first free block of memory. */
static header_t *usedp;         /* Points to first used block of memory. */

/*
 * Scan the free list and look for a place to put the block. Basically, we're 
 * looking for any block that the to-be-freed block might have been partitioned from.
 */
static void
add_to_free_list(header_t *bp)
{
    header_t *p;

    for (p = freep; !(bp > p && bp < p->next); p = p->next)
        if (p >= p->next && (bp > p || bp < p->next))
            break;

    if (bp + bp->size == p->next) {
        bp->size += p->next->size;
        bp->next = p->next->next;
    } else
        bp->next = p->next;

    if (p + p->size == bp) {
        p->size += bp->size;
        p->next = bp->next;
    } else
        p->next = bp;

    freep = p;
}

#define MIN_ALLOC_SIZE 4096 /* We allocate blocks in page sized chunks. */

/*
 * Request more memory from the kernel.
 */
static header_t *
morecore(size_t num_units)
{
    void *vp;
    header_t *up;

    if (num_units > MIN_ALLOC_SIZE)
        num_units = MIN_ALLOC_SIZE / sizeof(header_t);

    if ((vp = sbrk(num_units * sizeof(header_t))) == (void *) -1)
        return NULL;

    up = (header_t *) vp;
    up->size = num_units;
    add_to_free_list (up);
    return freep;
}
```

### 分配内存

```c
/*
 * Find a chunk from the free list and put it in the used list.
 */
void *
GC_malloc(size_t alloc_size)
{
    size_t num_units;
    header_t *p, *prevp;

    num_units = (alloc_size + sizeof(header_t) - 1) / sizeof(header_t) + 1;  
    prevp = freep;

    for (p = prevp->next;; prevp = p, p = p->next) {
        if (p->size >= num_units) { /* Big enough. */
            if (p->size == num_units) /* Exact size. */
                prevp->next = p->next;
            else {
                p->size -= num_units;
                p += p->size;
                p->size = num_units;
            }

            freep = prevp;

            /* Add to p to the used list. */
            if (usedp == NULL)  
                usedp = p->next = p;
            else {
                p->next = usedp->next;
                usedp->next = p;
            }

            return (void *) (p + 1);
        }
        if (p == freep) { /* Not enough memory. */
            p = morecore(num_units);
            if (p == NULL) /* Request for more memory failed. */
                return NULL;
        }
    }
}
```

### Mark and sweep标记

```c
#define UNTAG(p) (((unsigned int) (p)) & 0xfffffffc)

/*
 * Scan a region of memory and mark any items in the used list appropriately.
 * Both arguments should be word aligned.
 */
static void
scan_region(unsigned int *sp, unsigned int *end)
{
    header_t *bp;

    for (; sp < end; sp++) {
        unsigned int v = *sp;
        bp = usedp;
        do {
            if (bp + 1 <= v &&
                bp + 1 + bp->size > v) {
                    bp->next = ((unsigned int) bp->next) | 1;
                    break;
            }
        } while ((bp = UNTAG(bp->next)) != usedp);
    }
}
```

### 扫堆

```c
/*
 * Scan the marked blocks for references to other unmarked blocks.
 */
static void
scan_heap(void)
{
    unsigned int *vp;
    header_t *bp, *up;

    for (bp = UNTAG(usedp->next); bp != usedp; bp = UNTAG(bp->next)) {
        if (!((unsigned int)bp->next & 1))
            continue;
        for (vp = (unsigned int *)(bp + 1);
             vp < (bp + bp->size + 1);
             vp++) {
            unsigned int v = *vp;
            up = UNTAG(bp->next);
            do {
                if (up != bp &&
                    up + 1 <= v &&
                    up + 1 + up->size > v) {
                    up->next = ((unsigned int) up->next) | 1;
                    break;
                }
            } while ((up = UNTAG(up->next)) != bp);
        }
    }
}
```

### 确定边界

| Address      | Segment                             |
| ------------ | ----------------------------------- |
| Low address  | Text segment                        |
| ⋮            | Initialized Data                    |
|              | BSS                                 |
|              | Heap (grows low to high)            |
|              | ⋮                                   |
| ⋮            | ⋮                                   |
| High address | Stack (grows high to low (on i386)) |

在其他数据段可能有分配的内存，所以需要一起扫

要确定堆和栈的边界

其中bss段二进制有这个信息，可以通过linker拿到，直接用变量`extern char end, etext`就行

确定栈边界有点麻烦，栈顶就是esp，或者用ebp，好拿，栈底怎么拿？读`/proc/self/stat`

### 合在一起

```c
void
GC_init(void)
{
    static int initted;
    FILE *statfp;

    if (initted)
        return;

    initted = 1;

    statfp = fopen("/proc/self/stat", "r");
    assert(statfp != NULL);
    fscanf(statfp,
           "%*d %*s %*c %*d %*d %*d %*d %*d %*u "
           "%*lu %*lu %*lu %*lu %*lu %*lu %*ld %*ld "
           "%*ld %*ld %*ld %*ld %*llu %*lu %*ld "
           "%*lu %*lu %*lu %lu", &stack_bottom);
    fclose(statfp);

    usedp = NULL;
    base.next = freep = &base;
    base.size = 0;
}
```

回收

```c
/*
 * Mark blocks of memory in use and free the ones not in use.
 */
void
GC_collect(void)
{
    header_t *p, *prevp, *tp;
    unsigned long stack_top;
    extern char end, etext; /* Provided by the linker. */

    if (usedp == NULL)
        return;

    /* Scan the BSS and initialized data segments. */
    scan_region(&etext, &end);

    /* Scan the stack. */
    asm volatile ("movl %%ebp, %0" : "=r" (stack_top));
    scan_region(stack_top, stack_bottom);

    /* Mark from the heap. */
    scan_heap();

    /* And now we collect! */
    for (prevp = usedp, p = UNTAG(usedp->next);; prevp = p, p = UNTAG(p->next)) {
    next_chunk:
        if (!((unsigned int)p->next & 1)) {
            /*
             * The chunk hasn't been marked. Thus, it must be set free. 
             */
            tp = p;
            p = UNTAG(p->next);
            add_to_free_list(tp);

            if (usedp == tp) { 
                usedp = NULL;
                break;
            }

            prevp->next = (unsigned int)p | ((unsigned int) prevp->next & 1);
            goto next_chunk;
        }
        p->next = ((unsigned int) p->next) & ~1;
        if (p == usedp)
            break;
    }
}
```

代码简单易懂，算是GC入门
深入问题

- 更好的标记算法
- STW问题处理
- 并发回收
- 重入问题
- 检查寄存器

## [Time is Partial, or: why do distributed consistency models and weak memory models look so similar, anyway?](http://composition.al/CMPS290S-2018-09/2018/11/17/time-is-partial-or-why-do-distributed-consistency-models-and-weak-memory-models-look-so-similar-anyway.html)

拿数据的单调性和c++内存语义来比较。世界线又收束了起来

事务性内存？需要研究下(技术债太多了)

## [Building BPF applications with libbpf-bootstrap](https://nakryiko.com/posts/libbpf-bootstrap/)



手把手教你写BPF组件



## [使用perf/SystemTap分析pagefault](https://lrita.github.io/2019/09/27/systemtap-profiling-pagefault/)



直接把脚本抄过来

```bash
# -I 1000 每1000ms输出一次，
# -a 采集全部CPU上的事件
# -p <pid> 可以指定进程
perf stat -e page-faults -I 1000 -a
perf stat -e page-faults -I 1000 -a -p 10102

# 采集进程10102的30秒pagefault触发数据
perf record -e page-faults -a -p 10102 -g -- sleep 30
# 导出原始数据，此步必须在采集机器上进行，因为需要解析符号。
perf script > out.stacks
# 下面的步骤就可以移动到其他机器上了
./FlameGraph/stackcollapse-perf.pl < out.stacks | ./FlameGraph/flamegraph.pl --color=mem \
    --title="Page Fault Flame Graph" --countname="pages" > out.svg
```



十秒抓一次pagefault

```bash
#!/usr/bin/stap

/**
 * Tested on Linux 3.10 (CentOS 7)
 */

global fault_entry_time, fault_latency_all, fault_latency_type

function vm_fault_str(fault_type: long) {
    if(vm_fault_contains(fault_type, VM_FAULT_OOM))
        return "OOM";
    else if(vm_fault_contains(fault_type, VM_FAULT_SIGBUS))
        return "SIGBUS";
    else if(vm_fault_contains(fault_type, VM_FAULT_MINOR))
        return "MINOR";
    else if(vm_fault_contains(fault_type, VM_FAULT_MAJOR))
        return "MAJOR";
    else if(vm_fault_contains(fault_type, VM_FAULT_NOPAGE))
        return "NOPAGE";
    else if(vm_fault_contains(fault_type, VM_FAULT_LOCKED))
        return "LOCKED";
    else if(vm_fault_contains(fault_type, VM_FAULT_ERROR))
        return "ERROR";
    return "???";
}

probe vm.pagefault {
	if (pid() == target()) {
		fault_entry_time[tid()] = gettimeofday_us()
	}
}

probe vm.pagefault.return {
	if (!(tid() in fault_entry_time)) next
	latency = gettimeofday_us() - fault_entry_time[tid()]
	fault_latency_all <<< latency
	fault_latency_type[vm_fault_str(fault_type)] <<< latency
}

probe timer.s(10) {
	print("All:\n")
	print(@hist_log(fault_latency_all))
	delete(fault_latency_all)

	foreach (type in fault_latency_type+) {
		print(type,":\n")
                print(@hist_log(fault_latency_type[type]))
        }
        delete(fault_latency_type)
}

```



## [Disruptor c++使用指南](https://blog.csdn.net/bjrxyz/article/details/53084539)

这里搬一下disruptor的设计思路，将队列弱化为索引问题，同时只能有一个写一个索引，所以就规避了竞争，原子变量+cachelin对齐避免false sharing。代码就不看了。这有个用disruptor实现的队列http://www.enkichen.com/2018/03/10/dispatch-queue/

## [How Tail Call Optimization Works](https://eklitzke.org/how-tail-call-optimization-works)

要了解PC

> **程序计数器**（英语：Program Counter，**PC**）是一个[中央处理器](https://zh.wikipedia.org/wiki/中央处理器)中的[寄存器](https://zh.wikipedia.org/wiki/寄存器)，用于指示计算机在其程序序列中的位置。在[Intel](https://zh.wikipedia.org/wiki/Intel) [x86](https://zh.wikipedia.org/wiki/X86)和[Itanium](https://zh.wikipedia.org/wiki/Itanium)[微处理器](https://zh.wikipedia.org/wiki/微处理器)中，它叫做指令指针（instruction pointer，IP），有时又称为指令地址寄存器（instruction address register，IAR）[[1\]](https://zh.wikipedia.org/wiki/程式計數器#cite_note-1)、指令计数器[[2\]](https://zh.wikipedia.org/wiki/程式計數器#cite_note-2)或只是指令序列器的一部分[[3\]](https://zh.wikipedia.org/wiki/程式計數器#cite_note-3)。



TCO就是

>  Tail call optimization happens when the compiler transforms a `call` immediately followed by a `ret` into a single `jmp`

简单例子

```c
void foo(int x) {
  int y = x * 2;
  printf("x = %d, y = %d\n", x, y);
}
```

O1

```asm
(gdb) disas foo
Dump of assembler code for function foo:
   0x0000000000000000 <+0>:	sub    $0x8,%rsp
   0x0000000000000004 <+4>:	mov    %edi,%esi
   0x0000000000000006 <+6>:	lea    (%rdi,%rdi,1),%edx
   0x0000000000000009 <+9>:	mov    $0x0,%edi
   0x000000000000000e <+14>:	mov    $0x0,%eax
   0x0000000000000013 <+19>:	call   0x18 <foo+24>
   0x0000000000000018 <+24>:	add    $0x8,%rsp
   0x000000000000001c <+28>:	ret
```

O2

```asm
(gdb) disas foo
Dump of assembler code for function foo:
   0x0000000000000000 <+0>:	mov    %edi,%esi
   0x0000000000000002 <+2>:	lea    (%rdi,%rdi,1),%edx
   0x0000000000000005 <+5>:	xor    %eax,%eax
   0x0000000000000007 <+7>:	mov    $0x0,%edi
   0x000000000000000c <+12>:	jmp    0x11
```

区别就在于call没了变成jmp

再举个例子

```c
/* Tail-call recursive helper for factorial */
int factorial_accumulate(int n, int accum) {
  return n < 2 ? accum : factorial_accumulate(n - 1, n * accum);
}

int factorial(int n) { return factorial_accumulate(n, 1); }

```

O2

```asm
(gdb) disas factorial
Dump of assembler code for function factorial:
   0x0000000000000040 <+0>:	mov    $0x1,%eax
   0x0000000000000045 <+5>:	cmp    $0x1,%edi
   0x0000000000000048 <+8>:	jle    0x60 <factorial+32>
   0x000000000000004a <+10>:	nopw   0x0(%rax,%rax,1)
   0x0000000000000050 <+16>:	imul   %edi,%eax
   0x0000000000000053 <+19>:	sub    $0x1,%edi
   0x0000000000000056 <+22>:	cmp    $0x1,%edi
   0x0000000000000059 <+25>:	jne    0x50 <factorial+16>
   0x000000000000005b <+27>:	ret
   0x000000000000005c <+28>:	nopl   0x0(%rax)
   0x0000000000000060 <+32>:	ret
End of assembler dump.

(gdb) disas factorial_accumulate
Dump of assembler code for function factorial_accumulate:
   0x0000000000000020 <+0>:	mov    %esi,%eax
   0x0000000000000022 <+2>:	cmp    $0x1,%edi
   0x0000000000000025 <+5>:	jle    0x3b <factorial_accumulate+27>
   0x0000000000000027 <+7>:	nopw   0x0(%rax,%rax,1)
   0x0000000000000030 <+16>:	imul   %edi,%eax
   0x0000000000000033 <+19>:	sub    $0x1,%edi
   0x0000000000000036 <+22>:	cmp    $0x1,%edi
   0x0000000000000039 <+25>:	jne    0x30 <factorial_accumulate+16>
   0x000000000000003b <+27>:	ret
End of assembler dump.
```

能看到没有call，对应的是jne/jle

## [We Make a std::shared_mutex 10 Times Faster](https://www.codeproject.com/Articles/1183423/We-Make-a-std-shared-mutex-10-Times-Faster)

代码在这里 https://github.com/AlexeyAB/object_threadsafe

降低contention。不过我没有测过。实际上最佳方案还是shared_nothing或共享index写循环buffer这种。

> The main reason for slow operation of `std::shared_mutex` and `boost::shared_mutex` is the atomic counter of readers. Each reader thread increments the counter during locking and decrements it upon unlocking. As a result, threads constantly drive one cache line between the cores (namely, drive its exclusive-state (E)). According to the logic of this realization, each reader thread counts the number of readers at the moment, but this is absolutely not important for the reader thread, because it is important only that there is not a single writer. And, since the increment and decrement are RMW operations, they always generate Store-Buffer cleaning (MFENCE x86_64) and, at x86_64 level, asm actually correspond to the slowest semantics of the Sequential Consistency.

## [Trivially copyable does not mean trivially copy constructible](https://www.foonathan.net/2021/03/trivially-copyable/)

`std::is_trivially_copyable `不等于 `std::is_trivially_[copy/move]_[constructible/assignable]`

前者指的是POD，后者指的是构造函数检测，两者没有根本关联

```c++
struct weird
{
    weird() = default;
    weird(const weird&) = default;
    weird(weird&&)      = default;
    ~weird() = default;

    weird& operator=(const volatile weird&) = delete; // (1)

    template <int Dummy = 0>
    weird& operator=(const weird&) // (2)
    {
        return *this;
    }
};

static_assert(std::is_copy_assignable_v<weird>); // (a)
static_assert(!std::is_trivially_copy_assignable_v<weird>); // (b)
static_assert(std::is_trivially_copyable_v<weird>); // (c)
```

前两个好理解，第三个clang和gcc行为不一致。取决于is_trivially_copyable_v实现

[godbolt link](https://godbolt.org/z/fz17bG93P)

## [Splitting the ping](https://blog.benjojo.co.uk/post/ping-with-loss-latency-split)

[代码在这里](https://github.com/benjojo/sping)

小伙写了个split ping。这里考虑写成c++版本

核心就是ICMP Timestamps + NTP时钟

## [Memory Management in Lobster](https://aardappel.github.io/lobster/memory_management.html)

讨论语言内存管理的设计，这个lobster语言之前有过印象

## [The Baked Data architectural pattern](https://simonwillison.net/2021/Jul/28/baked-data/)

这里讲的是离线计算模型，需要数据，直接拷贝传输过来，算，然后数据模型可以多样化，sqlite json csv都行



## [Evil tip: avoid "easy" things](http://yosefk.com/blog/evil-tip-avoid-easy-things.html)

讲的是简单工作没挑战之类的, 用来自勉

## [Zip - How not to design a file format.](https://games.greggman.com/game/zip-rant/)

对zip文件格式对吐槽。。。zip老古董了，很多设计和缺失

> Records do **NOT** follow any standard pattern. To read or even skip a record you must know its format. What I mean is there are several other formats that follow some convention like each record id is followed by the length of the record. So, if you see an id, and you don't understand it, you just read the length, skip that many bytes (*), and you'll be at the next id. Examples of this type include most video container formats, jpgs, tiff, photoshop files, wav files, and many others.
> (*) some formats require rounding the length up to the nearest multiple of 4 or 16.
>
> Zip does **NOT** do this. If you see an id and you don't know how that type of record's content is structured there is no way to know how many bytes to skip.

<img src="https://wanghenshui.github.io/assets/quadraddnt.png" alt="" width="80%">






---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>
