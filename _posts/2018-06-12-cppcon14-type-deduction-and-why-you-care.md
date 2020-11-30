---
layout: post
title: (cppcon)类型推导以及为什么需要关注这个
categories: language
tags: [c++, cppcon, type]
---


作者是Scott Meyers，这个内容就是他写的modern effective c++ 前几条

用一个图来概括

![1556106456533](https://wanghenshui.github.io/assets/1556106456533.png)

和auto相关的类型推导

一例

```c++
template <typenamet T>
void f(ParamType param);
f(expr);//  从expr推导T和ParamType
```

三种场景，ParamType可能是1)T& /T*  不是T&& 2)T&& 3)T

 推导规则十分简单，

- 如果expr是T&, 就忽略
- 模式匹配expr类型和ParamType来决定T

`  场景，ParamType=T&`

```c++
template <typename T>
void f(T& param);

int x=22;
const int cx = x;
const int& rx = x;
f(x); //  T = int,       param = int&
f(cx); // T = const int, param = const int&
f(rx); // T = const int, param = const int& 注意，此处的T ，expr是T& 直接忽略了&
```

`  场景，ParamType=const T&`

```c++
template <typename T>
void f(const T& praam);

int x=22;
const int cx = x;
const int& rx = x;
f(x); //  T = int,       param = const int& 注意，此处的T ，expr是const T& 直接忽略了
f(cx); // T = const int, param = const int&
f(rx); // T = const int, param = const int& 
```

`场景， ParamType=T*`

```c++
template <typename T>
void f(T* praam);

int x=22;
const int *pcx = &x;
f(&x);  //  T = int,       param = int *
f(pcx); //  T = const int, param = const int *
```



`场景，ParamType=T&&`

如果涉及到万能引用，场景就会复杂，万能引用的退化方向比较多，值语义就是值语义，引用语义就是引用语义，万能引用表达的引用语义就比较杂，大部分场景和引用是一致的，除了

`如果expr是左值，能推导出E,T能推导出E&，等价于expr是左值引用就会有引用折叠`

听起来很复杂，就是所有左值的T都被推导出T&，右值推导出T&&，如果左值T是T&就折叠一个&，还是T&

 ```c++
template <typename T>
void f(T&& param);
//f(expr)
int x = 22;
const int cx = x;
const int& rx = x;
f(x); //  T = int&,       param = int&
f(cx); // T = const int&, param = const int&
f(rx); // T = const int&, param = const int&   折叠了一个&
f(22); // T = int,        param = int&&  右值专属场景，完美转发
 ```



涉及到auto，如何推导？类似上面，引用会退化

```c++
int x = 22;
const int cx = x;
const int& rx = x;

auto& v1 = x; //auto = int;
auto& v2 = cx; //auto = const int
auto& v3 = rx; // auto = const int
const auto& v4 = x; // auto = int
const auto& v5 = cx; // auto =int
const auto& v6 = rx; // auto =int
auto v7 = x;// auto =int
auto v8 = cx;// auto = int
auto v9 = rx;// auto = int
auto&& v10=rx;// type=const int&   左值，引用折叠了
```

指针const auto推导

```c++
void someFunc(const int* const param1,
              const int*       param2,
                    int*       param3)
{
    auto p1=param1;// auto = const int* 忽略了最后那个
    auto p2=param2;// const int*
    auto& p2v2=param2;// const int* const&，这个没忽略，注意区别
    auto p3=param3;// int*
}
```

会忽略指针const ， 视*param为一体

- 如果expr是const 或者volatile，直接忽略cv限定

- 还有针对函数指针和数组指针退化行为的边角场景，一律退化成指针

- {}表达式推导成初始化列表，注意函数参数会推导失败

还有一大堆细节不列了，有点语言律师的赶脚



lambda捕获类型推导

默认lambda是const的捕获内部参数不能直接改，需要显式mutable



observing deduced types

作者的一个小技巧，不实现类，来通过编译器的推导和编译报错观察推导类型

```c++
template <typename T>
class TD;
template <typename T>
void f(T& param){
    TD<T> tType;
    TD<decltype(param)> paramType;
}
```

作者也介绍了type_info和boost::type_index 不赘述

decltype推导

- 左值就是T， 双括号强制T&
- 左值表达式T&

函数返回值类型推导

- auto
- decltype(auto) 表达式通常是T&，左值是T，加括号强制T&

### ref

- [https://github.com/CppCon/CppCon2014/blob/master/Presentations/Type%20Deduction%20and%20Why%20You%20Care/C%2B%2B%20Type%20Deduction%20and%20Why%20You%20Care%20-%20Scott%20Meyers%20-%20CppCon%202014%20-%20CppCon%202014.pdf](https://github.com/CppCon/CppCon2014/blob/master/Presentations/Type Deduction and Why You Care/C%2B%2B Type Deduction and Why You Care - Scott Meyers - CppCon 2014 - CppCon 2014.pdf)

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>