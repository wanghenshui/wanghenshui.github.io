---
layout: post
title: (cppcon)Tuning C++ Benchmarks and CPUs and Compilers
categories: [language, translation]
tags: [c++, cppcon, cppcon2015, asm, perf, benchmark]
---



> 一个cppcon演讲中午看的。简单整理下笔记

<!-- more -->


第一个例子是 `Measure first, tune what matters`, 讲了一个查询优化可以快20倍，解决了发现调整where子句条件快了一百倍。。。

然后介绍microbenchmark 用google benchmark做现场演示

benchmark 做好隔离，能准确抓到数据

然后演讲者测了几段代码，发现没有啥明显差异，决定用perf再看

几种perf用法

直接显示count信息

```bash
perf stat ./binary
```

直接显示调用占用的cpu

```bash
perf record ./binary
perf report
```

直接抓占用+调用图

```bash
perf record -g ./binary
perf report -g 'graph,0.5,caller,function,percent'
```

但是只抓了系统调用，没抓本身的函数调用？ 需要flag `-fno-omit-frame-pointer`

默认的优化是会优化掉fp的

> ```
> -fomit-frame-pointer
> ```
>
> Don’t keep the frame pointer in a register for functions that don’t need one.  This avoids the instructions to save, set up and restore frame pointers; it also makes an extra register available in many functions.  **It also makes debugging impossible on some machines.**
>
> On some machines, such as the VAX, this flag has no effect, because the standard calling sequence automatically handles the frame pointer and nothing is saved by pretending it doesn’t exist.  The machine-description macro `FRAME_POINTER_REQUIRED` controls whether a target machine supports this flag.  See [Register Usage](http://gcc.gnu.org/onlinedocs/gccint/Registers.html#Registers) in GNU Compiler Collection (GCC) Internals.
>
> The default setting (when not optimizing for size) for 32-bit GNU/Linux x86 and 32-bit Darwin x86 targets is -fomit-frame-pointer.  You can configure GCC with the --enable-frame-pointer configure option to change the default.
>
> Enabled at levels -O, -O2, -O3, -Os.



注意，后面这串优化成了`--call-graph`

最终看汇编，发现值被优化掉了。。。perf会显示loop ，loop里没有其他动作，直接优化没了。

我不太懂汇编也没看出来怎么是被优化掉了，但确实没有push_back啥的动作

决定对抗优化器！

作者的这段代码google benchmark后面也补充了

```c++
// The DoNotOptimize(...) function can be used to prevent a value or
// expression from being optimized away by the compiler. This function is
// intended to add little to no overhead.
// See: https://youtu.be/nXaxk27zwlk?t=2441
#ifndef BENCHMARK_HAS_NO_INLINE_ASSEMBLY
template <class Tp>
inline BENCHMARK_ALWAYS_INLINE void DoNotOptimize(Tp const& value) {
  // Clang doesn't like the 'X' constraint on `value` and certain GCC versions
  // don't like the 'g' constraint. Attempt to placate them both.
#if defined(__clang__)
  asm volatile("" : : "g"(value) : "memory");
#else
  asm volatile("" : : "i,r,m"(value) : "memory");
#endif
}
```



加上之后能抓到动作了

<img src="https://wanghenshui.github.io/assets/image-20210105190451177.png" alt="" width="60%">



然后展示了一个分支展开调优加速的段子

重点还是这个防优化手段，以及bench / perf方法。在2015年还是很先进的

---

### ref

- 视频链接 https://www.youtube.com/watch?v=nXaxk27zwlk
- Gcc flag 文档 https://gcc.gnu.org/onlinedocs/gcc-7.3.0/gcc/Optimize-Options.html
- 这里了解fp细节 https://stackoverflow.com/questions/14666665/trying-to-understand-gcc-option-fomit-frame-pointer
- perf --call-graph patch https://lore.kernel.org/patchwork/patch/833702/
- 防优化 https://github.com/google/benchmark/blob/5e66248b44747fcfbbc096fa2428680358892f73/include/benchmark/benchmark.h#L299)








