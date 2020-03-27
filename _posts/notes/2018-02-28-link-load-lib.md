---
layout: post
title: 程序员自我修养链接加载库 读书笔记
category: [tools, book review]
tags: [debug, c, gdb, c++, gcc, linux]
---
{% include JB/setup %}

---



[toc]

---

### 静态链接

- 预处理 编译 汇编 链接
  - 预处理，展开# 
    - #define替换
    - #if #endif替换
    - 处理#include 递归替换
    - 删除注释
    - 添加行号和文件名标识
- 词法分析，语法分析，语义分析，中间语言生成
- 链接
  - 地址空间分配
  - 符号决议
  - 重定位



### 目标文件

- relocatable executable shared object

- 格式都一样，布局也一样，代码段数据段

  - .text  代码.data已经初始化的全局变量静态变量 .bss未初始化的全局变量静态变量
    -  ->二进制文件也可以强转成relocatable文件 objcopy
  - .plt .got跳转表/全局入口
  - strtab .debug .rodata .hash .line .dynamic
  - .init .fini 
  - 自定义段 `__attribute__((section("FOO")))`

  elf结构

  | ELF头                                                |
  | ---------------------------------------------------- |
  | .text                                                |
  | .data                                                |
  | .bss                                                 |
  | 其他段                                               |
  | section header table,段表 readelf查看 elf 头串起段表 |
  | string table <br>symbol table...                     |

  特殊符号`__executable_start` `__etext` `__edata`

  符号，name mangleing，extern “C”

  强符号，弱符号，默认强符号 `__attribute__((week))`

  强引用，弱引用，默认强引用 `__attribute__((weakref))` void foo 用来被覆盖

  弱符号典型代表，未初始化的全局变量

  

### 静态链接

- 相似段合并

  - 空间地址分配

    - elf专属地址，其他给个偏移

  - 符号解析重定位

    - 重定位表 object -r a.o
    - 链接需要符号表 readelf -s a.o
    - 链接器不感知类型信息，多个弱符号冲突如何处理？ common block ,一种符号提升手段。类似类型提升。
      - (gcc -fno-common, `__attribute__((nocommon))`)

  - c++相关的链接问题

    - 代码重复消除，模板和虚表造成的膨胀 linkonce段，多余的直接丢弃
    - 函数级别链接，提供接口让函数（或者参数）单独成段
    - 构造函数段和析构函数段
    - ABI问题
    - 静态链接 no-buildin -static --verbose 发生了什么

    

### 装载与动态链接

- 菜谱与炒菜

- overlay vs paging

  - paging 页映射

    - 创建独立虚拟地址空间

      - 分配一个页，给个页目录结束，不完整的页映射关系，等到页错误再配置

    - 执行文件头，建立虚拟空间与可执行文件的映射，准备照着菜谱炒菜

      - 可执行二进制文件又叫image懂了伐

      - VMA

        ![image-20200313121136446](https://wanghenshui.github.io/assets/image-20200313121136446.png)

    - 将CPU指令集设定成可执行文件入口地址，启动执行

  - 页错误

- ELF文件链接视图和执行视图

  - 不在乎段占用，段到底什么内容，只注意权限，相同权限合到一起映射 同一个VMA
  - 可执行文件会有程序表头 ProgramHeaderTable来保存映射的段信息(segment)

-  堆和栈也是VMA cat /proc/pid/maps

  - 可以看到和可执行文件映射vma不同，没有名字 aka AVMA anonymoout virtual memory area
  - 类似堆和栈，vdso 内核交互vma

- 总结四中VMA类型

  |          | 读   | 写   | 执行 | 映像文件                 |
  | -------- | ---- | ---- | ---- | ------------------------ |
  | 代码 VMA | √    | x    | √    | √                        |
  | 数据VMA  | √    | √    | √    | √                        |
  | 堆VMA    | √    | √    | √    | 匿名，无映像，可向上扩展 |
  | 栈       | √    | √    | x    | 匿名，无映像，可向下拓展 |

-  内核装载ELF的优化
  
  - 直接为0，bss不映射扔到堆里
- 段地址对齐以及优化
  
  - 碎片浪费 ->共享物理页，映射多次
- 进程栈初始化
- 内核装载ELF过程简介
  - exec -> sysexec ->do_exec
    - magic number判断开始解释执行 ->binnary_handle -> load_elf_binary
      - elf有效性
      - .interp段存在否,设置动态链接库路径
      - elf文件映射
      - 初始化elf进程环境
      - 系统调用返回地址改成elf可执行文件的入口点 e_entry
      - eip寄存器调到elf程序入口地址，开始执行





### 动态链接

- 静态链接磁盘一份内存一份造成的浪费

  - gcc -fPIC -shared -o xx.so xx.c

- 动态链接程序运行时地址分布

  - 代码段多出来libc ld和动态库

  - 装载时重定位以及地址无关代码PIC

    - 装载时重定位和链接时重定位差不多，没有重复利用代码。引入地址无关PIC可以重复使用，即尽量让地址相关的代码放到数据段

      - 代码段复用，数据段各自复制

        - 模块内部调用，相对地址调用，无需重定位

        - 模块内部数据访问，拿到PC (内部hack)+ 记录的偏移量

          ```asm
          call 484 <__i686.get_pc_thunk.cx>
          add $0x118c, %ecx
          movl $0x1, 0x28(%ecx)
          ```

          

        - 模块间数据访问，数据段中建立全局偏移表。间接引用

        - 模块间调用 也是全局偏移表，保存目标函数地址 存在性能问题。elf有优化

          ```asm
          call 484 <__i686.get_pc_thunk.cx>
          add $0x118c, %ecx
          mov 0xfffffffc(%ecx), %eax
          call *(%eax)
          ```

      - 全局变量怎么处理
        
        - 可执行文件bss段创建库的全局变量副本 加一条mov来访问
  - 数据段地址无关性
    
      

- 延迟绑定PLT

  - 调用时再绑定（这种理念到处都有啊原来）

    - `_dl_runtime_rosolve()`

    ```asm
    bar@plt:
    jmp *(bar@GOT)
    push n
    push moduleID
    jump _dl_runtime_resolve
    ```

  - 从`.got`段里拆出来。`.got.plt`段

    - `.dynamic`地址
    - 本模块id
    - `_dl_runtime_resolve`地址

- 动态链接相关结构

  - 引入动态链接器
    - `.interp`段，专门记录ld目录，字符串
    - `.dynamic` 导出符号表 `.hash` 加速查找
    -  重定位 `.rel.dyn  ` `.rel.plt ` 
  - 动态链接的步骤和实现
    - 动态链接器自举，本身也是动态链接库，需要自举完成状态切换，自举不能访问全局变量调用函数 ,因为没有重定位。`.dynamic`是入口点
    - 装载共享文件，合并全局符号表
      - 共享库符号冲突？后加入无效
    - 动态链接库的实现
      - 不仅是动态库，还是可执行文件
      - 内核执行不在乎是`ET_EXEC`还是`ET_DYN`，就是装载然后转移给ELF入口
        - `e_entry`, `.interp`
        - 就elf头不一样，扩展名不一样，其他都一样，window dll和exe也是类似的，`rundll32.exe`可以吧dll强行按照可执行文件执行
      - `_dl_start -> boostrap -> _dl_start_final -> _dl_sysdep_start -> _dl_main _dl_main`本身来判断自己是ld还是其他
      - 几点思考
        - 动态链接器本身是动态链接还是静态链接？ldd一下就知道了
        - 动态链接库本身是不是PIC？不是PIC的话，代码段需要重定位，没意义。
        - 动态链接库可以当做可执行文件执行，那么装载地址是？和其他动态库没区别

- 显示运行时链接

  - 灵活注入动态库。
  - `dlopen, dlsym dlerror dlclose`
    - `dlopen`
      1. 查找`LD_LIBRARY_PATH`
      2. 查找`/etc/ld.so.cache`
      3. `/lib` `/usr/lib` 
      4.  返回handle，如果filename为空返回全局符号表
      5. 会执行`.init`
    - `dlsym` 根据dlopen返回的handle来查符号



### Linux共享库的组织

- 版本
  - 兼容性 尽量别用c++接口。ABI灾难
  - 命名规则 `libname.so.x.y.z `
    1. x重大变动，可能不兼容
    2. y增量升级，新增接口
    3. z发布版本号，bugfix，改进等等
  - SO-NAME
    1. 只保留朱版本号的软连
       - 由于历史原因 `libc.so.2.6.1 -> libc.so.6` `ld.so.2.6.1 ->ld-linux.so`
    2. ldconfig
  - 符号版本, 比如glibc的 `GLIBC_2.6.1`，更新符号来保证依赖
- 共享库系统路径
  - `/lib` 系统关键库（动态链接器，c运行时，数学库，`bin` `sbin`用到的库）
  - `/usr/lib` 非系统运行时的关键共享库，静态库，目标文件。不会被用户用到
  - `/usr/local/lib` 第三方库，python解析器的lib，之类的
- 共享库的查找过程
  - `.dynamic`段中`DT_NEED`列出路径，如果是绝对路径，就会找这个文件，如果是相对路径，就会从`/lib` `/usr/lib` `/etc/ld.so.conf`配置文件指定的目录中查找
    - 每次查`/etc/ld.so.conf`中的目录必然很慢，ldconfig会cache一份`/etc/ld.so.cache`
    - 更改/etc/ld.so.conf需要运行`ldconfig` 重新cache一份
- 环境变量
  - `LD_LIBRARY_PATH` 临时更改某个应用程序的共享库查找路径，不影响整体 
    - `LD_LIBRARY_PATH=/home/user /bin/ls`
    - 相同方案，直接启动动态链接器运行程序 `/lib/ld-linux.so.2 -library-path /home/user /bin/ls`
    - 整体查找顺序 `LD_LIBRARY_PATH` -> `/etc/ld.so.cache` -> `/usr/lib`, `/lib`
    - 注意不要滥用`LD_LIBRARY_PATH`，最好不要`export`
  - `LD_PRELOAD` 指定覆盖，优先加载，比`LD_LIBRARY_PATH`优先级还高
    - 同样，有个`/etc/ld.so.preload`
  - `LD_DEBUG` 打开动态链接器的调试功能
    - LD_DEBUG=files ls
      - 还支持libs bindings versions reloc symbols statictics all help
- 共享库的创建和安装
  - `gcc -shared -Wl, -soname, my_soname -o libraty_name source_files libraty_files` 
    - soname 不指定，就没有，ldlconfig就没用
    - 调试先别去掉符号和调试信息（strip），以及`-fomit-frame-pointer`
    - 查找lib目录，可以临时定义`LD_LIBRARY_PATH`，也可以`-rpath=/home/mylib`
    -   符号表，用不到不会导出。如果延迟导入`dlopen`可能就会反向引用失败，使用`-export-dynamic`
  - 清除符号信息 strip libfoo.so
    - 生成库不带信息 ld -s/ld -S S debug symbol， s all symbol
  - 共享库安装 ldconfig -n lib_dir
  - 共享库构造与析构
    - ` __attribute__((constructor))` 在main之前/dlopen返回之前执行
    - `__attribute__((destructor))` 在main执行结束/dlclose返回之前执行
    - 必须依赖startfiles stdlib
  - 共享库脚本

### 内存

- 程序的内存布局

  - 栈，维护函数调用上下文
  - 堆，动态分配内存区
  - 可执行文件映像
  - 保留区

- 栈与调用惯例

  - 堆栈帧 

    - 函数返回地址和参数

    - 临时变量

    - 保存的上下文 寄存器 ebp esp![image-20200324105106459](https://wanghenshui.github.io/assets/image-20200324105106459.png)

      - 参数入栈，有遗漏的参数，分配给寄存器
      - 下一条指令的地址入栈，跳转到函数体执行

      ```asm
      push ebp#后面会出栈恢复
      mov ebp, esp
      #sub esp, xxx
      #push xxx
      
      ####结束后，与开头正好相反
      #pop xxx
      mov esp, ebp
      pop ebp
      ret
      ```

  - 调用惯例

    - 函数参数的传递顺序和方式
    - 栈维护方式
    - 名字修饰策略 name-mangling `cdecl`

  - 函数返回值传递

    - 寄存器有限，如果返回值太大，寄存器传指针，做复制动作`rep move` 或者`call memcpy`
      - 返回值多出来的空间占用，在栈上回预留
    - 流程 栈空间预留，预留地址传给函数-> 函数执行拷贝，把地址传出 ->外层函数把地址指向的对象拷贝 拷贝两次。
      - 返回大对象非常浪费
      - 返回值优化可能会优化掉一次拷贝。

- 堆与内存管理

  - free list 容易损坏，性能差
  - bitmap 碎片浪费
  - 内存池



### 运行时

- main并不是开始

  ```asm
  void _start()
  {
      %ebp = 0;
      int argc = `pop from stack`;
      char** argv = `top of stack`;
      __libc_start_main(main, argc, argv, libc_csu_init, __lib_csu_fini, edx, `top of stack`);
  }
  ```

- exit都做了什么

  - 遍历函数链表，执行atexit __cxa_atexit

    ```asm
    movl 4(%esp), %ebx
    movl $__NR_exit, %eax ;call exit
    int $0x80; halt如果exit退出失败，就强制停止。一般走不到这里
    ```

    

- 运行库与IO

- C/C++运行库

  - 基本功能
    - 启动与退出
    - 标准函数
      - 变长参数，压栈
      - 复杂化printf，所以要指定参数
        - va_list char *
        - va_start 参数末尾
        - va_args获得当前参数的值，调整指针位置
        - va_end，指针清零
    - IO功能封装和实现
    - 堆的封装和实现
    - 语言实现
    - 调试

- glibc

  - crt1.0 _start crti.o init fini开头 crtn.o init fini结尾
  - crtbegin.o crtend.o c++相关全局构造析构目标文件。属于gcc

- 运行库和多线程

  - 栈，tls，寄存器私有，其余共有
  - 线程安全
    1. errno等全局变量
    2. strtok等不可重入函数
    3. 内存分配
    4. 异常
    5. IO函数
    6. 信号相关

- c++全局构造与析构

  - `__libc_csu_init` -> `_init()`   调用init段 -> `__do_global_ctors_aux ` 
    - 和编译系统相关。    来自`crtbegin.o` 由`gcc/Crtstuff.c`编好。内部会有`__CTOR_LIST__`  如何生成？- > 所有的`.ctor`段拼凑-> `crtbegin.o`串起来
      -  `crtend.o`负责定义`__CTOR_END__`指向`.ctor`末尾

- IO  初探，通过fread

  - 缓冲buffer
  - 缓冲溢出保护，枷锁 -> 循环读取，缓冲 ->换行符转换 ->读取api



### 系统调用

- glibc封装系统调用，可绕过
- 系统调用原理
 ![image-20200327205248542](https://wanghenshui.github.io/assets/image-20200327205248542.png)
 - 特权级与中断
    - 中断向量表(  原来内核都有这玩意儿。。我之前玩stm32也有这东西，以为搞的什么新花样)
    - ![image-20200327205619506](https://wanghenshui.github.io/assets/image-20200327205619506.png)
       - 触发中断陷入内核 ->切换堆栈，保存寄存器信息，每个进程都有自己的内核栈

 - linux新型系统调用，由于int指令性能不佳
    - `linux-gate.so.1` aka `[vdso]` 可以通过maps查看，占用4k，可以导出内部细节就是sysenter等



### CRT运行库实现

- 入口以及exit
- 实现堆
  - freelist based 堆空间分配算法 malloc free
  - new delete
- IO与文件操作
- 格式化字符串



---



Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。