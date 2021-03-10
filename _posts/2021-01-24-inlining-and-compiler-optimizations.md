---
layout: post
title: (译)Inlining and Compiler Optimizations
categories: [language]
tags: [compiler,inline, lto, thinlto, llvm, clang]
---

>  整理自 https://wolchok.org/posts/inlining-and-compiler-optimizations/
>
> 文章串起来了一些知识，读一读，增加一下见解。当然，学习一下clang/llvm更直接一些，这些都是二手复读

<!-- more -->


先引入两个概念，**constant propagation** 和[**loop-invariant code motion**](https://en.wikipedia.org/wiki/Loop-invariant_code_motion) (LICM). 循环不变量外提

第一个概念就是立即数生成，只要是常数复制，直接有优化成立即数，避免取地址

<img src="https://wanghenshui.github.io/assets/image-20210126153719254.png" alt="" width="90%">



第二个概念就是字面意思，看代码

```c++
void multiplyArrayByTwoConstants(std::span<int> arr, int x, int y) {
    for (int& element: arr) {
        element *= x * y;
    }
}
```

x*y和循环没关系，会被外提到for之前算好



讨论inline和这两种优化结合的场景

### inline + constant propagation

inline + const出现的路径都会优化成立即数

<img src="https://wanghenshui.github.io/assets/image-20210126154446811.png" alt="" width="90%">

如果不是inline(实现不在同一个文件)，就会退化成调用函数，[godbolt](https://godbolt.org/#z:OYLghAFBqd5QCxAYwPYBMCmBRdBLAF1QCcAaPECAM1QDsCBlZAQwBtMQBGAFlICsupVs1qhkAUgBMAISnTSAZ0ztkBPHUqZa6AMKpWAVwC2tEJNJb0AGTy1MAOWMAjTMTMAOUgAdUCwuto9QxNBHz81Ohs7RyMXN05FZUxVAIYCZmICIONTcyUVCNo0jIIoh2dXD0V0zOyQhIUa0tty2MrOAEpFVANiZA4AcikAZltkQywAanFhnWRG/FQZ7HEABgBBNfXbAknaOj1aRpjp4YARSclhmdkNrYB6e73UW1YWyaJJo2YAa0wPhD/VAEQHESZeYg7SZUAy0FJ0BRgIYbR6TZgKJSxVgAT0mmHRuM%2BxHx6AAdFsAPoU5gEAiQpwGAiYKlQfavFodDrTDYANxe6HBkPoMQgUNoxi54gA7Ld1pN5ZMFiAQBCdlQIFJJFIAKzocTanS0TWkPYSm5baVnC28/mCnb2A4IggQSUyrYKu3C4wQfaBJ0xDrmu5Sq13G14AWq%2BiHRou6ZujYetBHXZQ5PHYynC7cLXDWUeqMEEXpotmvMWkPW9Z8iOegjYKhUZJqHnKbEx52u/MKqGYRvNvCtnEdk4zC6cK5BuUKwsivtNlJD9v%2Bsuyy1VmuRoUEACStDedg7Ik78e78tn3onw0D5eDZwGXVYIAG2oGpFMA1Wb9Qz50cjkio9H0/wjJwb4EM%2BX6cqQPxmFKpLDDm3AAJzDMMnCrJhnDDKsABsQjPtwb4fl%2BpA/gMb4KCAqykBBn4PqQcCwEgaBYLghAkOQlA0PQTBsBwPD8GYQgiGI/4yIkBQBJo2h1LkniWGUMRxCA%2BFhP4jrBPJ3i%2BBptBKRUbj4fkA50MUtT6DkVQmfCRRNAZbRGdUJRydZ9ktMplS4V0ChAf0z4jGMEwgbM8wEIsyxVuM6IKJMACy2J7rs0r5l4BhOG8yAgO6eIAB5eJlhDxYl9CivQky5VyICTDybAQJVp7romkxQsAmAniWzyYLl/ReAQU52rVTLZc1UK1awU7rremwbAlSXPH6KYilcN5riiTxsvu7yfN8fwAkCIKuHW0KwrZiLIusqIxZgWK4viCiEqgkzEswZKUtStL0oyzIUqyLxbXYnLctWtoXkYZW7OKRhdjl8pKiq27qpqOp6gaRqSOYprQ5NlZhiDtazo6KZxilsN1iKvojsYpJtZ2q0VqGM341uOwdiTCbTvKnVzeVJYijm9PNee27FiuRg0%2B1LqC5suNM5udYNguLZtmzMNC8V83zgOS5U%2BDV7SwWIvelri4q2LEt0zjjNbPLhZ7gemBHqVauc%2BT3o886%2BsW1LVtbAxT4vsRkHfr%2B4nSIBvT9NMVySOBwfQYCr2VC6MFwaSVxStq6FSlcwzIe4uGcNqBEDER77B2Rz6UdRtHx4xMCICgqBGF4eDsGQFAQGgLdt5U0WiJwGEJFQbdMsQVEQE4FdOLYGTYs%2BYGkN3RhaAQADy%2B7z/RpBYN8ojsBX%2BDEqbVHb91yTfQvb47MoV9CHgTjEHPehYBXdJ4EYV9dDxjAsAfgkCASMIUQKAw73ycFRSAXRUB9QCKfAAtGvYYlEki2RkroSy9QLDaAcipBI6lCiuXwbpQouD2iSVMnZFymDTANFQYUcyzRoiGUEI0ahWlWHuWYY5LgPk/ICUfM%2BV85dt7kVygXeBuFuCTH7sASYg9SSrFJJwSYEB2JEDBKBE0ege7t2juhLkf4ZByDjvRBOJJk5dFgpIJR3BODIWQlKFCuEXGYVWO4KUJcy6fwwjREiIcKKKBrnRKC9d4AQBYs3Vu7cuJdyib3NwsjB6rGHqPVwE8p7bxnrQOed9l6rw3jiQ%2BN1RIH23kfbWmBT6kXPsgS%2BAxF43wDovN4j9n4YEGKRd%2Bn8GkMR/nxf%2BvABDmGAWJYxElWmQJTjAwoCCkGTBQVJDQEBLBEOwdYDyLDiHhACGsghAQyHxAobZRhaybIMK4a0PBzkLIcIaJczy8Q%2BGRw4JIQRgcRGkTERIqRMjRnyM4Io5Rqj1EkH0ZjHR0SjojDeZMIxsgZCmKglYswxcA5l38ZXQJVEaIhIfO82OnyAlIvxaQVs49pLcCAA%3D%3D)

### inline + virtual + constant propagation

考虑引入virtual，如果不是传参数，优化效果是一样的，但是如果是传参数，就不一样了

```c++
class MyInt {
 public:
  explicit MyInt(int x) : val(x) {}
  virtual int get() const noexcept {
    return val;
  };
 private:
  int val;
};

MyInt nonConstNum(23);

// noinline to make the other print functions'
// assembly easy to read.
__attribute__((noinline))
void printNum(int num) {
    std::printf("%d\n", num);
}

void printArgByValue(MyInt num) {
    printNum(num.get());
}

void printArgByConstReference(const MyInt& num) {
    printNum(num.get());
}
```

由于类具有多态性，函数不能确认是基类还是子类，所以还是调用虚函数的get

<img src="https://wanghenshui.github.io/assets/image-20210126161152803.png" alt="" width="90%">



### inline + LICM

同样inline的能被优化，放到for循环外提前执行

```c++
class MyInt {
 public:
  explicit MyInt(int x) : val(x) {}
  int get() const noexcept {
    return val;
  };
 private:
  int val;
};

void multiplyArrayByTwoConstants(std::span<int> arr, MyInt x, MyInt y) {
    for (int& element: arr) {
        element *= x.get() * y.get();
    }
}
```

如果不是inline(实现没有放在一个文件中) 就会变成调用，这和get是不是const没关系，主要是inline起作用

在没见到get的实现之前，val是不是被改动了，很难说，即使你的get是const的，内部的实现还是有可能出现const_cast之类的骚操作





### 一个经典LICM例子 strlen

经常建议strlen放到for循环外面

但是放到循环内部也是可以有LICM优化 的

<img src="https://wanghenshui.github.io/assets/image-20210126162813159.png" alt="" width="90%">

可以看到strlen只调用一次，这种场景，由于isupper不会改动改动s，可以放心优化strlen



再举一个反例

<img src="https://wanghenshui.github.io/assets/image-20210126163104292.png" alt="" width="90%">

这个黄色的部分，callq strlen是随着循环一起执行的，调用N次，这是由于循环内改了s

当然，用指针更干净一些，用不上判断长度

```c++
#include <cctype>
#include <cstring>

void toUpperCase(char *s) {
  while (*s) {
    *s = std::toupper(*s);
    s++;
  }
}
```

实际优化后的效果是一样的

### 那是不是 应该全放到头文件里实现？

首先，编译时间太坑爹了，另外某些场景是不允许放到头文件的

另外，链接期间会有[LTO](https://llvm.org/docs/LinkTimeOptimization.html) / [thinLTO](https://clang.llvm.org/docs/ThinLTO.html) 这个期间也会inline，所以说拆开就inline是不正确的，但是LTO thinLTO的威力就很难保证了，clang/llvm加油


---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>

