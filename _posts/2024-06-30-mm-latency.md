---
layout: post
title: 内存管理机制针对延迟的优化
categories: [language]
tags: [mm]
---
原文

https://johnnysswlab.com/latency-sensitive-application-and-the-memory-subsystem-part-2-memory-management-mechanisms

https://www.jabperf.com/how-to-deter-or-disarm-tlb-shootdowns/

<!-- more -->

这篇文章的视角比较奇怪，可能和已知的信息不同，目标是低延迟避免内存机制影响

page fault会引入延迟，所以要破坏page fault的生成条件 怎么做？

尽可能分配好，而不是用到在分配，有概率触发page fault

- mmap使用MAP_POPULATE
- 使用calloc不用malloc，用malloc/new 强制0填充
- 零初始化数组，立马使用上
- vector 创造时直接构造好大小，不用reserve reserve不一定内存预分配，可能还会造成page fault()
  - 或者重载allocator，预先分配内存
  - 其他容器也是有类似的问题
- 使用内存大页
- 禁用 5-Level Page Walk
- 关闭swap
- TLB shotdown规避 这个一时半会讲不完 


这里展开讲讲，内容来自  [这里](https://www.jabperf.com/how-to-deter-or-disarm-tlb-shootdowns/)



cat /proc/interrupts

观察tlb shutdown

```txt
       CPU0       CPU1       CPU2       CPU3       CPU4       CPU5       CPU6       CPU7       

45:          0          0          0          0          0          0          0          0   PCI-MSI-edge      eth0
46:     192342          0          0          0          0          0          0          0   PCI-MSI-edge      ahci
47:         14          0          0          0          0          0          0          0   PCI-MSI-edge      mei

NMI:          0          0          0          0          0          0          0          0   Non-maskable interrupts
LOC:     552219    1010298    2272333    3179890    1445484    1226202    1800191    1894825   Local timer interrupts
SPU:          0          0          0          0          0          0          0          0   Spurious interrupts

IWI:          0          0          0          0          0          0          0          0   IRQ work interrupts
RTR:          7          0          0          0          0          0          0          0   APIC ICR read retries
RES:      18708       9550        771        528        129        170        151        139   Rescheduling interrupts
CAL:        711        934       1312       1261       1446       1411       1433       1432   Function call interrupts
TLB:       4493       6108      73789       5014       1788       2327       1967        914   TLB shootdowns

```

抓堆栈 native_flush_tlb_others很多 numa自平衡开了 关闭`sysctl -w numa_balancing=0`



TLB失效的原理 IPI触发

- 内核调用native_flush_tlb_others()
- 它填充一个flush_tlb_info结构体，其中包含必须刷新的地址空间部分的信息，将此结构体作为flush_tlb_func()回调函数的参数，然后调用smp_call_function_many()，其中包含一个cpu掩码、上述回调函数和该结构体作为函数参数
-  smp_call_function_many()使用llist_add_batch()将该回调函数和结构体附加到提供的cpumask中每个核心的每cpu“call_single_function”链表
- 然后，内核在__x2apic_send_IPI_mask()中的“for循环”中向上述cpumask中的每个核心发送IPI
- 每个接收到IPI的核心在中断模式下在其“call_single_function”队列中执行flush_tlb_func()回调，清除其中指定的TLB条目
- 向每个核心发送IPI的发起核心在另一个“for循环”中等待每个核心完成其回调程序
-  一旦所有核心完成其flush_tlb_func()回调，发起核心最终可以返回用户模式执行
  

几个关键点

- flush_tlb_info数量？
- cpumask决定 __x2apic_send_IPI_mask循环次数

核心越多影响越大

怎么解决？

预先分配内存，然后从不释放内存。分配器优化/使用mallopt()和mlockall()

内核优化，不走IPI？

测试numa 代码 madvise

```c
pthread_barrier_t barrier;

void* madv(void* mem)
{
  pthread_barrier_wait(&barrier);

  std::chrono::steady_clock::time_point begin = std::chrono::steady_clock::now();
  for (int i = 0;i < 1'000'000; i++)
  {
    madvise(*((char**) mem), 4096, MADV_DONTNEED);
  }
  std::chrono::steady_clock::time_point end = std::chrono::steady_clock::now();
  std::cout << "Time difference = " << std::chrono::duration_cast<std::chrono::milliseconds>(end - begin).count() << "[ms]" << std::endl;
  return 0;
}

int main(int argc, char** argv)
{
  void *mem;
  posix_memalign(&mem, 4096, 8192);

  auto thread_count = atoi(argv[1]);
  auto barrier_count = thread_count + 1;
  pthread_barrier_init(&barrier, nullptr, barrier_count);

  pthread_t threads[thread_count];
  pthread_attr_t attr;
  pthread_attr_init(&attr);
  pthread_attr_setscope(&attr, PTHREAD_SCOPE_SYSTEM);
  cpu_set_t cpus;

  for (int i = 0; i < thread_count; i++)
  {
    CPU_ZERO(&cpus);
    CPU_SET(i, &cpus);
    pthread_attr_setaffinity_np(&attr, sizeof(cpu_set_t), &cpus);
    pthread_create(&threads[i], &attr, madv, &mem);
  }

  sleep(2); pthread_barrier_wait(&barrier);

  for (int i = 0; i < thread_count; i++)
  {
    pthread_join(threads[i], nullptr);
  }
  return 0;
}
```

perf抓 TLB shootdown

```bash
[root@eltoro]# perf stat -r 3 -e probe:native_flush_tlb_others,tlb_flush.stlb_any chrt -f 90 ./madv 2

 Performance counter stats for 'chrt -f 90 ./madv 2' (3 runs):

         3,958,266      probe:native_flush_tlb_others                        ( +-  0.28% )
         7,928,801      tlb_flush.stlb_any                                   ( +-  0.24% )
         
[root@eltoro]# perf stat -r 3 -e probe:native_flush_tlb_others,tlb_flush.stlb_any chrt -f 90 ./madv 8

 Performance counter stats for 'chrt -f 90 ./madv 8' (3 runs):

        15,946,430      probe:native_flush_tlb_others                        ( +-  0.03% )
       123,288,313      tlb_flush.stlb_any                                   ( +-  0.05% )
       
[root@eltoro]# perf stat -r 3 -e probe:native_flush_tlb_others,tlb_flush.stlb_any chrt -f 90 ./madv 14

 Performance counter stats for 'chrt -f 90 ./madv 14' (3 runs):

        27,986,605      probe:native_flush_tlb_others                        ( +-  0.01% )
       376,502,522      tlb_flush.stlb_any                                   ( +-  0.01% )
```


抓一下调用频次

```bash
[root@eltoro]# funclatency.py -p 37344 native_flush_tlb_others
Tracing 1 functions for "native_flush_tlb_others"... Hit Ctrl-C to end.
^C
     nsecs               : count     distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 0        |                                        |
         8 -> 15         : 0        |                                        |
        16 -> 31         : 0        |                                        |
        32 -> 63         : 0        |                                        |
        64 -> 127        : 0        |                                        |
       128 -> 255        : 0        |                                        |
       256 -> 511        : 0        |                                        |
       512 -> 1023       : 87926    |                                        |
      1024 -> 2047       : 3861380  |****************************************|
      2048 -> 4095       : 32924    |                                        |
      4096 -> 8191       : 3628     |                                        |
      8192 -> 16383      : 543      |                                        |
     16384 -> 32767      : 526      |                                        |
     32768 -> 65535      : 7        |                                        |
     65536 -> 131071     : 0        |                                        |
    131072 -> 262143     : 0        |                                        |
    262144 -> 524287     : 0        |                                        |
    524288 -> 1048575    : 0        |                                        |
   1048576 -> 2097151    : 0        |                                        |
   2097152 -> 4194303    : 11       |                                        |

avg = 1398 nsecs, total: 5582920090 nsecs, count: 3991212

[root@eltoro]# funclatency.py -p 37600 native_flush_tlb_others
Tracing 1 functions for "native_flush_tlb_others"... Hit Ctrl-C to end.
^C
     nsecs               : count     distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 0        |                                        |
         8 -> 15         : 0        |                                        |
        16 -> 31         : 0        |                                        |
        32 -> 63         : 0        |                                        |
        64 -> 127        : 0        |                                        |
       128 -> 255        : 0        |                                        |
       256 -> 511        : 0        |                                        |
       512 -> 1023       : 24       |                                        |
      1024 -> 2047       : 224605   |                                        |
      2048 -> 4095       : 9608508  |****************************************|
      4096 -> 8191       : 6012919  |*************************               |
      8192 -> 16383      : 18881    |                                        |
     16384 -> 32767      : 2468     |                                        |
     32768 -> 65535      : 66       |                                        |
     65536 -> 131071     : 41       |                                        |
    131072 -> 262143     : 39       |                                        |
    262144 -> 524287     : 16       |                                        |
    524288 -> 1048575    : 72       |                                        |
   1048576 -> 2097151    : 0        |                                        |
   2097152 -> 4194303    : 86       |                                        |
   4194304 -> 8388607    : 3        |                                        |

avg = 3891 nsecs, total: 62126896400 nsecs, count: 15963897

[root@eltoro]# funclatency.py -p 37786 native_flush_tlb_others
Tracing 1 functions for "native_flush_tlb_others"... Hit Ctrl-C to end.
^C
     nsecs               : count     distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 0        |                                        |
         8 -> 15         : 0        |                                        |
        16 -> 31         : 0        |                                        |
        32 -> 63         : 0        |                                        |
        64 -> 127        : 0        |                                        |
       128 -> 255        : 0        |                                        |
       256 -> 511        : 0        |                                        |
       512 -> 1023       : 23       |                                        |
      1024 -> 2047       : 158263   |                                        |
      2048 -> 4095       : 990737   |*                                       |
      4096 -> 8191       : 22814615 |****************************************|
      8192 -> 16383      : 3699448  |******                                  |
     16384 -> 32767      : 15401    |                                        |
     32768 -> 65535      : 676      |                                        |
     65536 -> 131071     : 53       |                                        |
    131072 -> 262143     : 83       |                                        |
    262144 -> 524287     : 28       |                                        |
    524288 -> 1048575    : 169      |                                        |
   1048576 -> 2097151    : 179      |                                        |
   2097152 -> 4194303    : 131      |                                        |

avg = 6610 nsecs, total: 184948768204 nsecs, count: 27976588
```


