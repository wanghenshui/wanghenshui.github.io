---
layout: post
title: blog review 第三期
categories: [review]
tags: [hashtable, ttl,asm, gcc]
---

准备把blog阅读和paper阅读都归一，而不是看一篇翻译一篇，效率太低了

后面写博客按照 paper review，blog review，cppcon review之类的集合形式来写，不一篇一片写了。太水了



<!-- more -->



## [How to implement a hash table (in C)](https://benhoyt.com/writings/hash-table-in-c/)

手把手教你写hashtable，这里考虑没用开链法，用的线性探测，这样cache友好一些

## [Staying out of TTL hell](https://calpaterson.com/ttl-hell.html)

TTL过期方案的替代品

- 永不过期
-  Update-on-write/Invalidate-on-write
- 名字空间区分
-  HTTP - and PUSH and PURGE 依赖中间件

## [GCC's assembler syntax](https://www.felixcloutier.com/documents/gcc-asm.html)

是否好奇嵌入c++中的汇编的语法是啥意思，比如`asm("lfence" ::: "memory");` 为什么三个冒号，很让人费解

这个文档教程解释了asm语法，长这样

```c++
	asm <optional stuff> (
	    "assembler template"
	    : outputs
	    : inputs
	    : clobbers
	    : labels)
  
    asm("movq %0, %0" : "+rm" (foo));
    asm("addl %0, %1" : "+r" (foo) : "g" (bar));
    asm("lfence" : /* no output */ : /* no input */ : "memory");
```

`%N` 可以指代参数，从0开始

output/input/clobbers/labels不是必须的，

input和output的格式必须满足

```text
	       "constraint" (expression)
	[Name] "constraint" (expression)
```

共用的限制，有这么几个特殊的字符，rmig

- r specifies that the operand must be a general-purpose register 必须是寄存器
- m specifies that the operand must be a memory address 表示内存地址
- i specifies that the operand must be an integer constant 数字
- g specifies that the operand must be a  general-purpose register, or a memory address, or an integer constant  (effectively the same as "rmi") 上面三个的综合

注意i可能由于编译器的优化程度而导致优化不出来，编译失败

```c++
	int x = 3;
	asm("int %0" :: "i" (x) : "memory");
	// [godbolt] produces "int 3" at -O1 and above; https://godbolt.org/z/2qoisc
	// [godbolt] errors out at -O0 https://godbolt.org/z/QfsBV2
```



对于output，有这么几个特殊的限制，必须得有+/=

- `+` means that the output is actually a read-write value. The operand initially has the value contained by the expression. It's  fine to read from this output operand at any point in the assembly  string.
- `=&` means that the output is an *early-clobber output*. Its initial value is unspecified. It is not a bug to read from an `=&` operand once it has been assigned a value.
- `=` means that the output is write-only. The compiler can choose to give an `=` output the same location as an input: for that reason, it is *usually* a bug to write to it before the last instruction of your assembly snippet.
- `=@cc*COND*` is a special case of `=`  that allows you to query the result of a condition code at the end of  your assembly statement. You cannot reference a condition output in your assembly template.



Clobbers are the list of writable locations that the assembly code  might have modified, and which have not been specified in outputs. These can be:

- Register names (on x86, both `register` and `%register` are accepted, such as `rax` or `%rax`)
- The special name `cc`, which specifies that the assembly  altered condition flags. On platforms that keep multiple sets of  condition flags as separate registers, it's also possible to name  indvidual registers: for instance, on PowerPC, you can specify that you  clobber `cr0`.
- The special name `memory`, which specifies that the  assembly wrote to memory that is not explicitly referenced by an output  (for instance, by dereferencing an input pointer). A `memory` clobber prevents the compiler from reordering memory operations across the `asm` statement (although it *does not* prevent the processor from doing it: you need to use an actual memory fence to achieve this).

labels是结合goto用的，不解释了，看代码

```c++
	// https://godbolt.org/z/XaCgSe
	int add_overflows(long lhs, long rhs) {
	    asm goto(
	        "movq %%rax, %[left]\n  "
	        "addq %[right], %%rax\n  "
	        "jo %2"
	        : // can't have outputs
	        : [left] "g" (lhs), [right] "g" (rhs)
	        : "rax"
	        : on_overflow);
	    return 0; // no overflow
	    on_overflow: return 1; // had an overflow
	}
```



几个特别的例子

```c++
// https://godbolt.org/z/x1hytr
int do_write(int fp, void* ptr, size_t size) {
		int rax = SYS_write;
		asm volatile(
		    "syscall"
		    : "+a"(rax)
		    : "D" (fp), "S" (ptr), "d" (size)
		    : "rcx", "r11");
		return rax;
}
```



## [Getting an Unmangled Type Name at Compile Time](https://bitwizeshift.github.io/posts/2021/03/09/getting-an-unmangled-type-name-at-compile-time/)

编译期拿到函数名已经没意思了，这里探讨编译期拿到类型名，靠返回值。返回值用array存，array用index_sequence来构造。很经典的用法。已经见到很多次了，~~你说你是第一次见？以后肯定还会见到~~

```c++
// This file is a "Hello, world!" in C++ language by GCC for wandbox.
#include <iostream>
#include <vector>
#include <cstdlib>
#include <string>
#include <string_view>
#include <array>   // std::array
#include <utility> // std::index_sequence

template <std::size_t...Idxs>
constexpr auto substring_as_array(std::string_view str, std::index_sequence<Idxs...>)
{
  return std::array{str[Idxs]..., '\n'};
}

template <typename T>
constexpr auto type_name_array()
{
#if defined(__clang__)
  constexpr auto prefix   = std::string_view{"[T = "};
  constexpr auto suffix   = std::string_view{"]"};
  constexpr auto function = std::string_view{__PRETTY_FUNCTION__};
#elif defined(__GNUC__)
  constexpr auto prefix   = std::string_view{"with T = "};
  constexpr auto suffix   = std::string_view{"]"};
  constexpr auto function = std::string_view{__PRETTY_FUNCTION__};
#elif defined(_MSC_VER)
  constexpr auto prefix   = std::string_view{"type_name_array<"};
  constexpr auto suffix   = std::string_view{">(void)"};
  constexpr auto function = std::string_view{__FUNCSIG__};
#else
# error Unsupported compiler
#endif

  constexpr auto start = function.find(prefix) + prefix.size();
  constexpr auto end = function.rfind(suffix);

  static_assert(start < end);

  constexpr auto name = function.substr(start, (end - start));
  return substring_as_array(name, std::make_index_sequence<name.size()>{});
}

template <typename T>
struct type_name_holder {
  static inline constexpr auto value = type_name_array<T>();
};

template <typename T>
constexpr auto type_name() -> std::string_view
{
  constexpr auto& value = type_name_holder<T>::value;
  return std::string_view{value.data(), value.size()};
}


int main()
{
    std::cout << type_name<std::vector<int>>() << std::endl;
}
```

可以在[这里](https://wandbox.org/permlink/Oh2CtRlaSsYiySIE)玩一下




---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>

