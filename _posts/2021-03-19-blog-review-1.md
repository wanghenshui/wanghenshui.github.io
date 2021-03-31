---
layout: post
title: blog review 第一期
categories: [review]
tags: [mysql, bash, proc, iostat, boost, template, gdb,bash, cpp]
---

准备把blog阅读和paper阅读都归一，而不是看一篇翻译一篇，效率太低了

后面写博客按照 paper review，blog review，cppcon review之类的集合形式来写，不一篇一片写了。太水了



<!-- more -->

## [Memory saturated MySQL](https://blog.koehntopp.info/2021/02/28/memory-saturated-mysql.html)

- cache都是ns级，磁盘是ms级别,尽可能的把working set都放到内存里
- memory就是buffer pool，算下需要多少

```sql
 SELECT sum(data_length+index_length)/1024/1024 AS total_mb FROM information_schema.tables WHERE table_type = “base table” AND table_schema IN (<list of schema names>)
```



## [如何设计安全的用户登录功能](https://my.oschina.net/u/1269381/blog/852679)

在cookie中，保存三个东西——用户名，登录序列，登录token。
 用户名：明文存放。
 登录序列：一个被MD5散列过的随机数，仅当强制用户输入口令时更新（如：用户修改了口令）。
 登录token：一个被MD5散列过的随机数，仅一个登录session内有效，新的登录session会更新它。

登陆id密码 盐，随机盐。定期更新

后段存密码加盐hash，存盐

经典方案，做个备忘



## [Variadic expansion in aggregate initialization](https://jgreitemann.github.io/2018/09/15/variadic-expansion-in-aggregate-initialization/)

这里讨论如何给array初始化的同时填好值

```c++
struct foo {
    foo(int i) : data(i) {}
    friend inline std::ostream& operator<<(std::ostream& os,
                                           foo const& f)
    { return os << "foo(" << f.data << ")"; }
private:
    int data;
};
// 典型，笨拙
std::array<foo, 10> arr;
for (int i = 0; i < arr.size(); ++i)
    arr[i] = foo(i);
// 不能编译，因为有十个，你只提供了一个构造，推导不出init list。引入默认构造也不是一个好点子
// 因为需要各种值
std::array<foo, 10> arr {};

//典型vector方案
std::vector<foo> vec;
vec.reserve(10);
std::generate_n(std::back_inserter(vec), 10,
                [i=0]() mutable -> foo { return i++; });

```



这里为了解决这个问题，引入标题描述的技术

```c++
template <typename Container, int... I>
Container iota_impl(std::integer_sequence<int, I...>) {
    return {I...};
} 

template <typename T, size_t N>
auto iota_array() {
    using Sequence = std::make_integer_sequence<int, N>;
    return iota_impl<std::array<T, N>>(Sequence{});
}

auto arr = iota_array<foo, 10>();
std::copy(arr.begin(), arr.end(),
          std::ostream_iterator<foo>{std::cout, ", "});
/* output: foo(0), foo(1), foo(2), foo(3), foo(4), ... */
```

上面的代码是从0开始，要是从任意位置开始呢

```c++
template <typename T, size_t N, size_t... I>
auto subarray_impl(std::array<T, N> const& arr,
                   size_t first,
                   std::index_sequence<I...>)
    -> std::array<T, sizeof...(I)>
{
    return {arr[first + I]...};
}

template <size_t S, typename T, size_t N>
auto subarray(std::array<T, N> const& arr, size_t first) {
    using Indices = std::make_index_sequence<S>;
    return subarray_impl(arr, first, Indices{});
}

auto sub = subarray<4>(arr, 2);
/* foo(2), foo(3), foo(4), foo(5) */
```

- sizeof ...算个数

## [4 Features of Boost HOF That Will Make Your Code Simpler](https://www.fluentcpp.com/2021/01/15/4-features-of-boost-hof-that-will-make-your-code-simpler/)

介绍boost.hof库

- 一个经典的to_string，旧的方案

```c++
std::string const& my_to_string(std::string const& s)
{
    return s;
}

template<typename T>
std::string my_to_string(T const& value)
{
    return std::to_string(value);
}

template<typename Range>
std::string my_to_string(Range const& range)
{
    std::ostringstream result;
    for (auto const& value : range)
    {
        result << value << ' ';
    }
    return result.str();
}
```

新方案，一个函数，多个匹配

```c++
auto my_to_string = boost::hof::first_of(
    [](std::string const& s) -> std::string const&
    {
        return s;
    },
    [](auto const& value) -> decltype(std::to_string(value))
    {
        return std::to_string(value);
    },
    [](auto const& range)
    {
        std::ostringstream result;
        for (auto const& value : range)
        {
            result << value << ' ';
        }
        return result.str();
    }
);
```

- 对一个序列做构造

```c++
class Circle
{
public:
    explicit Circle(double radius) : radius_(radius) {}
    
    double radius() const { return radius_; };

    // rest of the Circle’s interface
    
private:
    double radius_;    
};

auto const input = std::vector<double>{1, 2, 3, 4, 5};
auto results = std::vector<Circle>{};

std::transform(begin(input), end(input), back_inserter(results), boost::hof::construct<Circle>());
```

- 映射

```c++
std::sort(begin(circles), end(circles), [](Circle const& circle1, Circle const& circle2)
                                        {
                                            return circle1.radius() < circle2.radius();
                                        }); // 1
std::ranges::sort(circles, {}, &Circle::radius_); //2
using namespace boost::hof;
std::sort(begin(circles), end(circles), proj(&Circle::radius, _ < _)); //3
```

方法3和方法2差不多其实，见仁见智

- 组合

```c++
int plusOne(int i)
{
    return i + 1;
}

int timesTwo(int i)
{
    return i * 2;
}

auto const input = std::vector<int>{1, 2, 3, 4, 5};
auto results = std::vector<int>{};

std::transform(begin(input), end(input), back_inserter(results), boost::hof::compose(timesTwo, plusOne));

//当然c++20也足够优雅
auto const input = std::vector<int>{1, 2, 3, 4, 5};

auto range = inputs
                | std::views::transform(plusOne)
                | std::views::transform(timesTwo);

auto result = std::vector<int>{range.begin(), range.end()};
```



- 函数调用，保证顺序

```c++
g(f1(), f2()); //不一定保证顺序
boost::hof::apply_eval(g, [](){ return f1(); }, [](){ return f2(); });//保证顺序
```



## [Two traps in iostat: %util and svctm](https://brooker.co.za/blog/2014/07/04/iostat-pct.html)

一个iostat -x输出 ,两个SSD

```text
Device:     rrqm/s   wrqm/s       r/s     w/s    rkB/s    wkB/s avgrq-sz 
sdd           0.00     0.00  13823.00    0.00 55292.00     0.00     8.00
             avgqu-sz   await r_await w_await  svctm  %util
                 0.78    0.06    0.06    0.00   0.06  78.40

Device:     rrqm/s   wrqm/s       r/s     w/s    rkB/s    wkB/s avgrq-sz
sdd           0.00     0.00  72914.67    0.00 291658.67    0.00     8.00
             avgqu-sz   await r_await w_await  svctm  %util
                15.27    0.21    0.21    0.00   0.01 100.00
```

78% util 读是13823, 100% util读是72814，差20%CPU怎么差这么多读？ 两个的svctm也有差距，为啥上面是60us下面是10us？

读的少反而响应慢，读的多反而响应快？

iostat有个备注

> Device saturation occurs when this value is close to 100% for devices  serving requests serially.  But for devices serving requests in  parallel, such as RAID arrays and modern SSDs, this number does not  reflect their performance limits.

由于ssd的并行化处理，吞吐很高响应很低，计算util可能会出现错误

## [How We Beat C++ STL Binary Search](https://academy.realm.io/posts/how-we-beat-cpp-stl-binary-search/)

upper_bound长这样https://github.com/gcc-mirror/gcc/blob/master/libstdc%2B%2B-v3/include/bits/stl_algo.h



```c++
template<typename _ForwardIterator, typename _Tp, typename _Compare>
_GLIBCXX20_CONSTEXPR
_ForwardIterator
__upper_bound(_ForwardIterator __first, _ForwardIterator __last,
              const _Tp& __val, _Compare __comp)
{
  typedef typename iterator_traits<_ForwardIterator>::difference_type
    _DistanceType;

  _DistanceType __len = std::distance(__first, __last);

  while (__len > 0)
  {
    _DistanceType __half = __len >> 1;
    _ForwardIterator __middle = __first;
    std::advance(__middle, __half);
    if (__comp(__val, __middle))
      __len = __half;
    else
    {
      __first = __middle;
      ++__first;
      __len = __len - __half - 1;
    }
  }
  return __first;
}
 template <class T> INLINE size_t fast_upper_bound0(const vector<T>& vec, T value)
{
  return std::upper_bound(vec.begin(), vec.end(), value) - vec.begin();
}
```



省掉if，终极重写版本

```c++
template <class T> INLINE size_t fast_upper_bound1(const vector<T>& vec, T value)
{
    size_t size = vec.size();
    size_t low = 0;

    while (size > 0) {
        size_t half = size / 2;
        size_t other_half = size - half;
        size_t probe = low + half;
        size_t other_low = low + other_half;
        T v = vec[probe];
        size = half;
        low = v >= value ? other_low : low;
    }

    return low;
}
```



?:表达式改成汇编

```c++
template <class T> INLINE size_t choose(T a, T b, size_t src1, size_t src2)
{
#if defined(__clang__) && defined(__x86_64)
    size_t res = src1;
    asm("cmpq %1, %2; cmovaeq %4, %0"
        :
    "=q" (res)
        :
        "q" (a),
        "q" (b),
        "q" (src1),
        "q" (src2),
        "0" (res)
        :
        "cc");
    return res;
#else
    return b >= a ? src2 : src1;
#endif
}
```



循环展开

```c++
template <class T> INLINE size_t fast_upper_bound2(const vector<T>& vec, T value)
{
    size_t size = vec.size();
    size_t low = 0;

    while (size >= 8) {
        size_t half = size / 2;
        size_t other_half = size - half;
        size_t probe = low + half;
        size_t other_low = low + other_half;
        T v = vec[probe];
        size = half;
        low = choose(v, value, low, other_low);

        half = size / 2;
        other_half = size - half;
        probe = low + half;
        other_low = low + other_half;
        v = vec[probe];
        size = half;
        low = choose(v, value, low, other_low);

        half = size / 2;
        other_half = size - half;
        probe = low + half;
        other_low = low + other_half;
        v = vec[probe];
        size = half;
        low = choose(v, value, low, other_low);
    }

    while (size > 0) {
        size_t half = size / 2;
        size_t other_half = size - half;
        size_t probe = low + half;
        size_t other_low = low + other_half;
        T v = vec[probe];
        size = half;
        low = choose(v, value, low, other_low);
    };

    return low;
}
```



最终省了24%左右

注意这个测试是2015年的

我用clang编不过，没去研究汇编。用gcc跑了一版本，[QB](https://quick-bench.com/q/AcGpgcinwrPcF45bprPFVW8aYJg)

只有版本2快一些。循环展开帮助不大。在2015年的时候，编译器比较拉胯，没有很好的提升，改成gcc5.5 自己主动展开版本和循环版就一样快了，改成gcc7/10 编译器就给你优化了。没必要自己去循环展开，性能反而很差

clang版本，这个汇编我不知道怎么改，就没有继续深究



## [Time Travel Debugging for C/C++](https://pspdfkit.com/blog/2021/time-travel-debugging-for-c/)

讲GDB怎么重放

```gdb
 target record-full
 continue
```

遇到错误，是gdb不兼容指令，使用下面的patch

```bash
 perl -0777 -pe 's/\x31\xc0.{0,32}?\K\x0f\xa2/\x66\x90/' \
  < /lib64/ld-linux-x86-64.so.2 > ld-linux
$ chmod u+rx ld-linux
$ patchelf --set-interpreter `pwd`/ld-linux stack-smasher
$ LD_BIND_NOW=1 gdb ./stack-smasher
```

继续gdb

```gdb
(gdb) reverse-stepi
(gdb) layout asm
0x55555555521d <main(int, char**)>       push   %rbp
   0x55555555521e <main(int, char**)+1>     mov    %rsp,%rbp
   0x555555555221 <main(int, char**)+4>     sub    $0x30,%rsp
   0x555555555225 <main(int, char**)+8>     mov    %edi,-0x24(%rbp)
   0x555555555228 <main(int, char**)+11>    mov    %rsi,-0x30(%rbp)
B+ 0x55555555522c <main(int, char**)+15>    lea    -0x20(%rbp),%rax
   0x555555555230 <main(int, char**)+19>    mov    %rax,%rdi
   0x555555555233 <main(int, char**)+22>    callq  0x555555555277 <std::data<std::array<wchar_t, 8ul> >(std::array<wchar_t, 8ul>&)>
   0x555555555238 <main(int, char**)+27>    mov    $0x20,%esi
   0x55555555523d <main(int, char**)+32>    mov    %rax,%rdi
   0x555555555240 <main(int, char**)+35>    callq  0x555555555175 <fill(wchar_t*, unsigned long)>
   0x555555555245 <main(int, char**)+40>    mov    $0x0,%eax
   0x55555555524a <main(int, char**)+45>    leaveq
  >0x55555555524b <main(int, char**)+46>    retq
(gdb) x $rsp
0x7fffffffda48: 0x0000006c
(gdb) set can-use-hw-watchpoints 0
(gdb) watch *0x7fffffffda48
Watchpoint 2: *0x7fffffffda48
(gdb) reverse-continue
Watchpoint 2: *0x7fffffffda48
__memmove_sse2_unaligned_erms () at ../sysdeps/x86_64/multiarch/memmove-vec-unaligned-erms.S:371
(gdb) backtrace
#0  __memmove_sse2_unaligned_erms () at ../sysdeps/x86_64/multiarch/memmove-vec-unaligned-erms.S:371
#1  0x000055555555521a in fill (dst=0x7fffffffda20 L"Hello, W\x555552c0啕\xf7a34e3b翿𑰀", sz=32) at stack-smasher.cc:9
#2  0x0000555555555245 in main () at stack-smasher.cc:15
```

就找到问题了 



## [优雅的写bash条件](https://timvisee.com/blog/elegant-bash-conditionals/)


用[control operator](https://www.gnu.org/software/bash/manual/html_node/Definitions.html#Definitions)来改写，这里特指 && ||

```bash
if [ expression ]
then
    command
fi
if [ expression ]; then command; fi
echo $?
ls ~/            # exit code: 0
ls ~/nonexistent # exit code: 2
if [ -r ~/.profile ]; then
    source ~/.profile
fi
#改写效果
[ -r ~/.profile ] && . ~/.profile
```





## [To Cage a Dragon An obscure quirk of proc](https://offlinemark.com/2021/02/11/an-obscure-quirk-of-proc/)

通过`/proc/pid/mem`这个文件可以访问进程的变量，这里也叫做 `“punch through” semantics`

比如juliajit 也在用https://lkml.org/lkml/2017/5/29/541 类似的rr debuger也在用

问题？怎么实现的？正常来说这应该是不可写的，怎么就写成功了，并且透传到用户层了？？

硬件层来说，就是有pagefault，然后COW了

看下`/proc/*/mem`[实现](https://elixir.bootlin.com/linux/v5.9-rc3/source/fs/proc/base.c)

调用[mem_rw()](https://elixir.bootlin.com/linux/v5.9-rc3/source/fs/proc/base.c#L835)  -> 

调用 [access_remote_vm()](https://elixir.bootlin.com/linux/v5.9-rc3/source/mm/memory.c#L4805)去写 -> 

get_user_pages_remote找物理页 -> FOLL_FORCE flag, which mem_rw() passes.  [check_vma_flags](https://elixir.bootlin.com/linux/v5.9-rc3/source/mm/gup.c#L930) 不会校验是不是不可写

kmap()标记写 -> 

copy_to_user_page 写


---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>