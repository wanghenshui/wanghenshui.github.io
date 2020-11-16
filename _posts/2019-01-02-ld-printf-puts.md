---
layout: post
title: LD_PRELOAD为何不能劫持printf
categories: c++
tags: [linux, gcc, c]
---
  



# LD_PRELOAD为何不能劫持printf

环境gcc linux

简而言之是gcc在某些时刻会优化掉printf，优化成puts

---

下面是牢骚。群友们针对printf咋被优化的进行了探讨，可能是弱符号，或者涉及到变参的复杂场景，以及printf可以使用寄存器作为参数。一顿天马行空



[这个链接](https://www.cnblogs.com/fanzhidongyzby/p/3519838.html)具有一定的参考性

特别摘抄过来，作为后续分析glibc的一个参考思路

**printf的代码在哪里？**

显然，Helloworld的源代码需要经过编译器编译，操作系统的加载才能正确执行。而编译器包含预编译、编译、汇编和链接四个步骤。

```
#include<stdio.h>
int main()
{
​    **printf("Hello World !\n");**
​    return 0;
}
```

首先，预编译器处理源代码中的宏，比如#include。预编译结束后，我们发现printf函数的声明。

$/usr/lib/gcc/i686-linux-gnu/4.7/cc1 -E -quiet              \
​    main.c -o main.i
\# 1 "main.c"
\# 1 "<命令行>"
\# 1 "main.c"
...
extern int printf (const char *__restrict __format, ...);
...

int main()
{
 printf("Hello World！\n");
 return 0;
}

然后编译器将高级语言程序转化为汇编代码。

```
$/usr/lib/gcc/i686-linux-gnu/4.7/cc1 -fpreprocessed -quiet  \
​    main.i -o main.s
​    .file      "main.c"
​    .section   .rodata
.LC0:
​    .string    "Hello World!"
​    .text
​    .globl     main
​    .type      main, @function
main:
​    pushl      %ebp
​    movl       %esp,  %ebp
​    andl       $-16,  %esp
​    subl       $16,   %esp
​    movl       $.LC0, (%esp)
​    `call       puts`
​    movl       $0,    %eax
​    leave
​    ret
​    .size      main, .-main
...
```

我们发现printf函数调用被转化为call  puts指令，而不是call  printf指令，这好像有点出乎意料。不过不用担心，这是编译器对printf的一种优化。实践证明，对于printf的参数如果是以'\n'结束的纯字符串，printf会被优化为puts函数，而字符串的结尾'\n'符号被消除。除此之外，都会正常生成call  printf指令。

如果我们仍希望通过printf调用"Hello World !\n"的话，只需要按照如下方式修改即可。不过这样做就不能在printf调用结束后立即看到打印字符串了，因为puts函数可以立即刷新输出缓冲区。我们仍然使用puts作为例子继续阐述。

```
    .section   .rodata
.LC0:
​    .string    "hello world!\n"
​    ...
​    call       printf
...
```

接下来，汇编器开始工作。将汇编文件转化为我们不能直接阅读的二进制格式——可重定位目标文件，这里我们需要gcc工具包的objdump命令查看它的二进制信息。可是我们发现call puts指令里保存了无效的符号地址。

```
$as -o main.o main.s
$objdump –d main.o
main.o：     文件格式 elf32-i386
Disassembly of section .text:
00000000 <main>:
   0:  55                     push   %ebp
   1:  89 e5                  mov    %esp,%ebp
   3:  83 e4 f0               and    $0xfffffff0,%esp
   6:  83 ec 10               sub    $0x10,%esp
   9:  c7 04 24 00 00 00 00   movl   $0x0,(%esp)
  10:  e8 fc ff ff ff         call   11 <main+0x11>
  15:  b8 00 00 00 00         mov    $0x0,%eax
  1a:  c9                     leave  
  1b:  c3                     ret
```

而链接器最终会将puts的符号地址修正。由于链接方式分为静态链接和动态链接两种，虽然链接方式不同，但是不影响最终代码对库函数的调用。我们这里关注printf函数背后的原理，因此使用更易说明问题的静态链接的方式阐述。

```
$/usr/lib/gcc/i686-linux-gnu/4.7/collect2                   \
​    -static -o main                                         \
​    /usr/lib/i386-linux-gnu/crt1.o                          \
​    /usr/lib/i386-linux-gnu/crti.o                          \
​    /usr/lib/gcc/i686-linux-gnu/4.7/crtbeginT.o             \
​    main.o                                                  \
​    --start-group                                           \
​    /usr/lib/gcc/i686-linux-gnu/4.7/libgcc.a                \
​    /usr/lib/gcc/i686-linux-gnu/4.7/libgcc_eh.a             
​    /usr/lib/i386-linux-gnu/libc.a                          \
​    --end-group                                             \
​    /usr/lib/gcc/i686-linux-gnu/4.7/crtend.o                \
​    /usr/lib/i386-linux-gnu/crtn.o

$objdump –sd main

Disassembly of section .text:

...

08048ea4 <main>:
 8048ea4:  55                     push   %ebp
 8048ea5:  89 e5                  mov    %esp,%ebp
 8048ea7:  83 e4 f0               and    $0xfffffff0,%esp
 8048eaa:  83 ec 10               sub    $0x10,%esp
 8048ead:  c7 04 24 e8 86 0c 08   movl   $0x80c86e8,(%esp)
 8048eb4:  e8 57 0a 00 00         call   8049910 <_IO_puts>
 8048eb9:  b8 00 00 00 00         mov    $0x0,%eax
 8048ebe:  c9                     leave  
 8048ebf:  c3                     ret
...
```

静态链接时，链接器将C语言的运行库（CRT）链接到可执行文件，其中crt1.o、crti.o、crtbeginT.o、crtend.o、crtn.o便是这五个核心的文件，它们按照上述命令显示的顺序分居在用户目标文件和库文件的两侧。由于我们使用了库函数puts，因此需要库文件libc.a，而libc.a与libgcc.a和libgcc_eh.a有相互依赖关系，因此需要使用-start-group和-end-group将它们包含起来。

链接后，call   puts的地址被修正，但是反汇编显示的符号是_IO_puts而不是puts！难道我们找的文件不对吗？当然不是，我们使用readelf命令查看一下main的符号表。竟然发现puts和_IO_puts这两个符号的性质是等价的！objdump命令只是显示了全局的符号_IO_puts而已。

```
$readelf main –s
Symbol table '.symtab' contains 2307 entries:
   Num:    Value  Size Type    Bind   Vis      Ndx Name
...
  1345: 08049910   352 FUNC    WEAK   DEFAULT    6 puts
...
  1674: 08049910   352 FUNC    GLOBAL DEFAULT    6 _IO_puts
...
```

那么puts函数的定义真的是在libc.a里吗？我们需要对此确认。我们将libc.a解压缩，然后全局符号_IO_puts所在的二进制文件，输出结果为ioputs.o。然后查看该文件的符号表。发现ioputs.o定义了puts和_IO_puts符号，因此可以确定ioputs.o就是puts函数的代码文件，且在库文件libc.a内。

```
$ar -x /usr/lib/i386-linux-gnu/libc.a
$grep -rin "_IO_puts" *.o
​    $readelf -s ioputs.o
Symbol table '.symtab' contains 20 entries:
   Num:    Value  Size Type    Bind   Vis      Ndx Name
...
​    11: 00000000   352 FUNC    GLOBAL DEFAULT    1 _IO_puts
...
​    19: 00000000   352 FUNC    WEAK   DEFAULT    1 puts
```

**二、printf的调用轨迹**

我们知道对于"Hello World !\n"的printf调用被转化为puts函数，并且我们找到了puts的实现代码是在库文件libc.a内的，并且知道它是以二进制的形式存储在文件ioputs.o内的，那么我们如何寻找printf函数的调用轨迹呢？换句话说，printf函数是如何一步步执行，最终使用Linux的int  0x80软中断进行系统调用陷入内核的呢？

如果让我们向终端输出一段字符串信息，我们一般会使用系统调用write()。那么打印Helloworld的printf最终是这样做的吗？我们借助于gdb来追踪这个过程，不过我们需要在编译源文件的时候添加-g选项，支持调试时使用符号表。

$/usr/lib/gcc/i686-linux-gnu/4.7/cc1 -fpreprocessed -quiet -g\

​    main.i -o main.s

然后使用gdb调试可执行文件。

$gdb ./main

(gdb)break main

(gdb)run

(gdb)stepi

在main函数内下断点，然后调试执行，接着不断的使用stepi指令执行代码，直到看到Hello World !输出为止。这也是为什么我们使用puts作为示例而不是使用printf的原因。

(gdb) 

0xb7fff419 in __kernel_vsyscall ()

(gdb) 

**Hello World!**

我们发现Hello World!打印位置的上一行代码的执行位置为0xb7fff419。我们查看此处的反汇编代码。

```
(gdb)disassemble
Dump of assembler code for function __kernel_vsyscall:
   0xb7fff414 <+0>:  push   %ecx
   0xb7fff415 <+1>:  push   %edx
   0xb7fff416 <+2>:  push   %ebp
   0xb7fff417 <+3>:  mov    %esp,%ebp
   0xb7fff419 <+5>:  sysenter
   0xb7fff41b <+7>:  nop
   0xb7fff41c <+8>:  nop
   0xb7fff41d <+9>:  nop
   0xb7fff41e <+10>: nop
   0xb7fff41f <+11>: nop
   0xb7fff420 <+12>: nop
   0xb7fff421 <+13>: nop
   0xb7fff422 <+14>: int    $0x80
=> 0xb7fff424 <+16>: pop    %ebp
   0xb7fff425 <+17>: pop    %edx
   0xb7fff426 <+18>: pop    %ecx
   0xb7fff427 <+19>: ret    
End of assembler dump.
```



我们惊奇的发现，地址0xb7fff419正是指向sysenter指令的位置！这里便是系统调用的入口。如果想了解这里为什么不是int 0x80指令，请参考文章[《Linux 2.6 对新型 CPU 快速系统调用的支持》](https://www.ibm.com/developerworks/cn/linux/kernel/l-k26ncpu/)。或者参考Linus在邮件列表里的文章[《Intel P6 vs P7 system call performance》](https://lkml.org/lkml/2002/12/18/218)。

系统调用的位置已经是printf函数调用的末端了，我们只需要按照函数调用关系便能得到printf的调用轨迹了。

```
(gdb)backtrace
#0  0xb7fff424 in __kernel_vsyscall ()
#1  0x080588b2 in __write_nocancel ()
#2  0x0806fa11 in _IO_new_file_write ()
#3  0x0806f8ed in new_do_write ()
#4  0x080708dd in _IO_new_do_write ()
#5  0x08070aa5 in _IO_new_file_overflow ()
#6  0x08049a37 in puts ()
#7  0x08048eb9 in main () at main.c:4
```

我们发现系统调用前执行的函数是__write_nocancel，它执行了系统调用__write！

**三、printf源码阅读**

虽然我们找到了Hello World的printf调用轨迹，但是仍然无法看到函数的源码。跟踪反汇编代码不是个好主意，最好的方式是直接阅读glibc的源代码！我们可以从官网下载最新的[glibc源代码](http://ftp.gnu.org/gnu/glibc/glibc-2.18.tar.gz)（glibc-2.18）进行阅读分析，或者直接访问在线源码分析网站[LXR](http://koala.cs.pub.ro/lxr/glibc)。然后按照调用轨迹的的逆序查找函数的调用点。

**1.puts** **调用 _IO_new_file_xsputn**

具体的符号转化关系为：`_IO_puts => _IO_sputn => _IO_XSPUTN => __xsputn => _IO_file_xsputn => _IO_new_file_xsputn`

```
$cat ./libio/ioputs.c
int
_IO_puts (str)
​     const char *str;
{
  int result = EOF;
  _IO_size_t len = strlen (str);
  _IO_acquire_lock (_IO_stdout);

  if ((_IO_vtable_offset (_IO_stdout) != 0
​       || _IO_fwide (_IO_stdout, -1) == -1)
​      && **_IO_sputn (_IO_stdout, str, len)** == len
​      && _IO_putc_unlocked ('\n', _IO_stdout) != EOF)
​    result = MIN (INT_MAX, len + 1);
  _IO_release_lock (_IO_stdout);
  return result;
}
#ifdef weak_alias
weak_alias (_IO_puts, puts)
#endif
```

这里注意weak_alias宏的含义，即将puts绑定到符号_IO_puts，并且puts符号为weak类型的。这也就解释了puts符号被解析为_IO_puts的真正原因。

**2._IO_new_file_xsputn** **调用 _IO_new_file_overflow**

具体的符号转化关系为：_IO_new_file_xsputn => _IO_OVERFLOW => __overflow => _IO_new_file_overflow

```
$cat ./libio/fileops.c
_IO_size_t
_IO_new_file_xsputn (f, data, n)
​     _IO_FILE *f;
​     const void *data;
​     _IO_size_t n;
{
 ...
  if (to_do + must_flush > 0)
​    {
​      _IO_size_t block_size, do_write;
​      /* Next flush the (full) buffer. */
​      if (**_IO_OVERFLOW (f, EOF)** == EOF)
​    /* If nothing else has to be written or nothing has been written, we
​       must not signal the caller that the call was even partially
​       successful.  */
​    return (to_do == 0 || to_do == n) ? EOF : n - to_do;
...
```

**3.****_IO_new_file_overflow** **调用 _IO_new_do_write** 

具体的符号转化关系为：_IO_new_file_overflow =>_IO_do_write =>_IO_new_do_write

```
$cat ./libio/fileops.c
int
_IO_new_file_overflow (f, ch)
​      _IO_FILE *f;
​      int ch;
{
 ...
  if (INTUSE(**_IO_do_write**) (f, f->_IO_write_base,
  f->_IO_write_ptr - f->_IO_write_base) == EOF)
  return EOF;
  return (unsigned char) ch;
}
```

**4. _IO_new_do_write** **调用 new_do_write** 

具体的符号转化关系为：_IO_new_do_write => new_do_write

```
$cat ./libio/fileops.c
int
_IO_new_do_write (fp, data, to_do)
​     _IO_FILE *fp;
​     const char *data;
​     _IO_size_t to_do;
{
  return (to_do == 0
​      || (_IO_size_t) **new_do_write** (fp, data, to_do) == to_do) ? 0 : EOF;
}
```

**5. new_do_write****调用 _IO_new_file_write**

具体的符号转化关系为：new_do_write =>_IO_SYSWRITE => __write() => write() => _IO_new_file_write

```
$cat ./libio/fileops.c
_IO_size_t
new_do_write (fp, data, to_do)
_IO_FILE *fp;
const char *data;
_IO_size_t to_do;
{
 ...
  count = **_IO_SYSWRITE** (fp, data, to_do);
  if (fp->_cur_column && count)
  fp->_cur_column = INTUSE(_IO_adjust_column) (fp->_cur_column - 1, data, count) + 1;
 ...
}
```

**6. _IO_new_file_write****调用 write_nocancel**

具体的符号转化关系为：_IO_new_file_write=>write_not_cancel => write_nocancel 

```
$cat ./libio/fileops.c
_IO_ssize_t
_IO_new_file_write (f, data, n)
_IO_FILE *f;
const void *data;
_IO_ssize_t n;
{
 _IO_ssize_t to_do = n;
  while (to_do > 0)
  {
​    _IO_ssize_t count = (__builtin_expect (f->_flags2& _IO_FLAGS2_NOTCANCEL, 0)? **write_not_cancel** (f->_fileno, data, to_do): write (f->_fileno, data, to_do));
...
}
```

**7. write_nocancel** **调用 linux-gate.so::__kernel_vsyscall**

具体的符号转化关系为：write_nocancel => INLINE_SYSCALL  => INTERNAL_SYSCALL =>__kernel_vsyscall

注意 linux-gate.so在磁盘上并不存在，它是内核镜像中的特定页，由内核编译生成。关于它的更多信息，可以参考文章[《linux-gate.so技术细节》](http://www.newsmth.net/bbsanc.php?path=/groups/comp.faq/KernelTech/innovate/solofox/M.1222336489.G0)和《[What is linux-gate.so.1?》](http://www.trilithium.com/johan/2005/08/linux-gate/)。

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
![微信转账](https://wanghenshui.github.io/assets/wepay.png)
</details>
