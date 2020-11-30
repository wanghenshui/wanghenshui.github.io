---
layout: post
title: (译)The Hunt for the Fastest Zero
categories: [language]
tags: [libcxx, stl]
---



一个场景，把长度为n的字符数组用0填满
如果用c的话，大家肯定都用memset ，这个文章的主题是c++，咱们用c++来写，是这样的

```c++
void fill1(char *p, size_t n) {
    std::fill(p, p + n, 0);
}
```

但是，只添加几个字符，就会快29倍，很容易就写出性能比上面代码片更好的代码来，像这样

```c++
void fill2(char *p, size_t n) {
    std::fill(p, p + n, '\0');
}
```

作者用的是O2优化

| 函数 | Bytes/Cycle|
| ---- |---- |
| fill1 | 1.0 |
| fill2 | 29.1 |

这两种写法有啥区别呢
看汇编

fill1是这样的

```asm
fill1(char*, unsigned long):
      add rsi, rdi
      cmp rsi, rdi
      je .L1

.L3:
      mov BYTE PTR [rdi], 0 ;rdi存0
      add rdi, 1            ;rdi ++
      cmp rsi, rdi          ;比较rdi 和size大小
      jne .L3               ;继续循环L3
.L1:
      ret
```
能看出来这段代码就是按位赋值
根据参考链接2方法论，这段代码主要瓶颈就是每个周期要有一次选择分支和保存值
但是fill2可完全不一样

fill2:
```asm
fill2(char*, unsigned long):
        test rsi,rdi
        jne .L8
        ret
.L8:
        mov rdx, rsi
        xor esi, esi
        jmp memset ;尾调用memset
```

这里就不再分析为啥memset要快了。肯定比手写copy要快，有循环展开，且省掉了很多分支选择

但是为什么第一种写法不会直接调用memset呢
作者一开始以为编译器做了手脚，试了O3优化，结果都优化成memset了

但是真正的原因，在`std::fill`的实现上

```c++
  /*
   *  ...
   *
   *  This function fills a range with copies of the same value.  For char
   *  types filling contiguous areas of memory, this becomes an inline call
   *  to @c memset or @c wmemset.
  */
  template<typename _ForwardIterator, typename _Tp>
  inline void fill(_ForwardIterator __first, _ForwardIterator __last, const _Tp& __value)
  {
    std::__fill_a(std::__niter_base(__first), std::__niter_base(__last), __value);
  }
```
std::fill根据某些traits做了优化，至于是那种场景呢？看`std::__fill_a`
```c++
  template<typename _ForwardIterator, typename _Tp>
  inline typename
  __gnu_cxx::__enable_if<!__is_scalar<_Tp>::__value, void>::__type
  __fill_a(_ForwardIterator __first, _ForwardIterator __last, const _Tp& __value)
  {
    for (; __first != __last; ++__first)
      *__first = __value;
  }

  // Specialization: for char types we can use memset.
  template<typename _Tp>
  inline typename
  __gnu_cxx::__enable_if<__is_byte<_Tp>::__value, void>::__type
  __fill_a(_Tp* __first, _Tp* __last, const _Tp& __c)
  {
    const _Tp __tmp = __c;
    if (const size_t __len = __last - __first)
      __builtin_memset(__first, static_cast<unsigned char>(__tmp), __len);
  }

```

根据这个SFINAE规则能看到，当T是is_byte的时候，才会触发调用memset
fill1的写法，T的类型是整型常量，所以没触发优化成memset的版本
等同于
```c++
std::fill<char *, int>(p, p + n, 0);
```

显式的指定函数模板参数，不用编译器推导，也能触发优化，像下面这个fill3

```c++
void fill3(char * p, size_t n) {
    std::file<char *, char>(p, p + n, 0);
}
```
按位复制优化成memset是编译器优化器做的。（优化器怎么做的？idiom recognition） gcc O3/ clang O2


对于第二种写法，不传'\0',也可以使用 `static_cast<char>(0)`

后面作者给了个标准库 的修改patch
value的类型不必非得和指针类型一致就可以了
```c++
  template<typename _Tp, typename _Tvalue>
  inline typename
  __gnu_cxx::__enable_if<__is_byte<_Tp>::__value, void>::__type
  __fill_a(_Tp* __first, _Tp* __last, const _Tvalue& __c)
  {
    const _Tvalue __tmp = __c;
    if (const size_t __len = __last - __first)
      __builtin_memset(__first, static_cast<unsigned char>(__tmp), __len);
  }
```
但是这种改法，对自定义类型就不行
```c++
struct conv_counting_int {
    int v_;
    mutable size_t count_ = 0;

    operator char() const {
        count_++;
        return (char)v_;
    }
};

size_t fill5(char *p, size_t n) {
    conv_counting_int zero{0};
    std::fill(p, p + n, zero);
    return zero.count_;
}
```
返回值是1而不是n，优化反而让结果不对。这种场景，最好让这种自定义类型不合法
比如
```c++


  template<typename _Tpointer, typename _Tp>
    inline typename
    __gnu_cxx::__enable_if<__is_byte<_Tpointer>::__value && __is_scalar<_Tp>::__value, void>::__type
    __fill_a( _Tpointer* __first,  _Tpointer* __last, const _Tp& __value) {
      ...

```


## ref

1. https://travisdowns.github.io/blog/2020/01/20/zero.html
2. 值得一看 https://travisdowns.github.io/blog/2019/06/11/speed-limits.html
3.  这人的博客非常牛逼https://travisdowns.github.io 值得都看看

   

---
看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>