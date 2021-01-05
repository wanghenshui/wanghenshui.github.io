---
layout: post
title: 用python做个小debug
categories: [tools, translation debug]
tags: [python, mysql]

---

<img src="https://wanghenshui.github.io/assets/quadrant.png" alt="" width="60%">

> 翻译整理自这几片文章 [链接1](https://blog.asrpo.com/making_a_low_level_debugger)

 

作者自制了个[语言](https://github.com/asrp/flpc) 设计到底层原语的调试，需要调试器，他用 [python-ptrace library](http://python-ptrace.readthedocs.io/en/latest/gdb.html), [pyelftools](https://github.com/eliben/pyelftools) 和[distorm3](https://pypi.org/project/distorm3/) 糊了一个

下面是介绍

先安装

```bash
pip3 install python-ptrace
```

然后执行下面的python语句，注意: a.out 随便写个c程序，生成可执行文件，这个程序不能直接退出，否则会出现错误

```c++
ptrace.error.PtraceError: ptrace(cmd=16, pid=30165, 0, 0) error #1: Operation not permitted
```

这个错误会误导你以为什么系统错误，实际上不是的，进程pid不在strace肯定错误的

作者的代码是这样的

```c
#include <stdio.h>
#include <unistd.h>

int my_var;
typedef int (*func_ptr_t)(void);

void test_function(){
  printf("Called test_function! Probably from the debugger.\n");
  printf("my_var=%i\n", my_var);
}

int main(){
  printf("Starting main loop\n");
  my_var = 1;
  while (1){
    usleep(100000);
  }
}
```



python脚本准备

```python
import ptrace.debugger
import subprocess
shell_command = ["./a.out"]
child_proc = subprocess.Popen(shell_command)
pid = child_proc.pid
debugger = ptrace.debugger.PtraceDebugger()
process = debugger.addProcess(pid, False)
```



这样就有了一个简单的调试环境，和操作gdb是一样的，不过更清晰一些

获取寄存器

```python
regs = process.getregs()
registers = {k:getattr(regs, k) for k in dir(regs) if not k.startswith('_')}
registers
{'cs': 51, 'ds': 0, 'eflags': 582, 'es': 0, 'fs': 0, 'fs_base': 139788087355200, 'gs': 0, 'gs_base': 0, 'orig_rax': 35, 'r10': 140721172406752, 'r11': 582, 'r12': 4195536, 'r13': 140721172408432, 'r14': 0, 'r15': 0, 'r8': 18446744073709551615, 'r9': 0, 'rax': 18446744073709551100, 'rbp': 140721172408208, 'rbx': 0, 'rcx': 18446744073709551615, 'rdi': 140721172408176, 'rdx': 0, 'rip': 139788083114400, 'rsi': 0, 'rsp': 140721172408168, 'ss': 43}
```



读内存

```python
import binascii
binascii.hexlify(process.readBytes(registers['rsp'], 8))
b'd4be0cf3227f0000'
```

单步执行汇编

```python
process.getreg('rip')  #139788083114406
process.singleStep()
process.getreg('rip') #139788083114408
```

触发信号

```python
import signal
process.waitSignals(signal.SIGTRAP)
```

这里是埋信号，后面主动写寄存器出发

也可以把这两步结合起来

```python
def step():
    process.singleStep()
    process.waitSignals(signal.SIGTRAP)
```

Int 3触发，对应0xCC

直接写入

```python
process.writeBytes(process.getreg('rip'), bytes(0xCC))
process.cont()
process.waitSignals(signal.SIGTRAP)
```



---

### ref

- 作者的演示代码仓库 https://github.com/asrp/ptracedbg/blob/master/
- strace遇到错误的解决方案 https://blog.packagecloud.io/eng/2015/11/15/strace-cheat-sheet/


---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>

