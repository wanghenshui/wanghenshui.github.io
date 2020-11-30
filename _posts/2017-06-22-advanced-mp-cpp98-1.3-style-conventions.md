---
layout: post
title: (译)advanced metaprogramming in classic c++ 1.3 风格惯例，约定 style conventions
categories: [language, translation]
tags: [c++, template]
---

  

比如全都小写，这节主要是风格约定。简单走一遍

---

> `风格约定` 
>
> 在原有的风格基础上保持一致就可以了，比如满足标准库风格，一个好的风格会省不少事儿，就不用跟到函数内部看这个函数到底实现了啥。
>
> 接口功能也是一个注意点，比如是否需要返回错误码/抛异常，接上面的话题，异常风格融合到标准库风格中，不要做多余的事儿。
>
> 命名风格也要注意，标准库预留了一些变量，下划线开头，所以不要用下划线开头的变量。包含$符号的（编译器问题），包含双下划线的
>
> 对于现代编译器来说，应该没什么，会检测到错误。
>
> `注释`
>
> 对于TMP这种trick技术，需要注释，避免误解。
>
> `宏`
>
> 宏在TMP 中比较邪恶但是又很必要。宏是全局可见的，并且可能会有名字冲突
>
> 作者提供了一个方法，前缀 MXT_ 全大写表示全局的，mXT_前缀表示局部的，全部小写的宏用来map标准库，平台
>
> ```c++
> #ifndef MXT_filename_
> #define MXT_filename_
> #define mXT_MYVALUE 3
> const int VALUE = mXT_MYVALUE;
> #undef mXT_MYVALUE
> #ifdef _WIN32
> #define mxt_native_db1_is_finite _finita
> #else
> #define mxt_native_db1_is_finite isfinite
> #endif
> #endif
> ```



还有一些宏替换关键字trick，extern，namespace，visiable等

```c++
#define MXT_NAMESPACE_BEGIN(x) namespace x{
#define MXT_NAMESPACE_END(x) }
#define MXT_NAMESPACE_NULL_BEGIN() namespace x{
#define MXT_NAMESPACE_NULL_END() }
```

还有BOOST_AUTO这种初始化（有点像汇编是怎么回事）

也可以用宏来生成代码。这是比较常用的场景

```c++
#define mXT_C(name, value)			\
static T name()						\
{									\
	static const T name##_ = value;	\
	return name##_;					\
}

template <typename T>
struct constant {
    mXT_C(Pi, acos(T(-1)));
    mXT_C(TwoPi, 2*acos(T(-1)));
    mXT_C(Log2, log(T(2)));
};
#undef mXT_C
double x = xonstant<double>::TwoPi();

//也有一些常用的宏
```

```c++
#define MXT_M_MAX(a, b) ((a)<(b)?(b):(a))
#define MXT_M_MIN(a, b) ((a)<(b)?(a):(b))
#define MXT_M_ABS(a)    ((a)<0?-(a):(a))
#define MXT_M_SQ(a)		((a)*(a))
template <int N> 
struct SomeClass{
    static const int value = MXT_M_SQ(N)/MXT_M_MAX(N,1)
};
```



c++11 有constexpr能更好的实现上面这段

```c++
constexpr int sq(int) {return n*n;}
constexpr int max(int a, int b) {return a<b?b:a;}
template <int N>
struct SomeClass {
  static const int value = sq(N)  /max(N,1);
};
```





符号`

就是命名风格，作者给的方案，系统级别函数，和标准库风格等同，（c也是这风格，单词还短。算是陋习）

文件名，就都小写，

项目级别类，驼峰

functor和函数风格相同

`泛型`

提高泛型化的方法就是复用标准库，std::pair, std::tuple

拿std::pair来说，可能p.first和p.second丢失名字信息，如何解决这个问题?几种方案

```c++
struct id_value{
    int id;
    double value;
};

//std::pair<int,double>更泛型，但是名字信息丢了

//用宏，保留名字信息
//第一种实现，不建议使用
#define id first 
#define value second
//第二种，稍微强一点
#define id(P) P.first
#define value(P) P,second

//用全局函数，也就是accessor
inline int& id(std::pair<int, double> p){return p.first;}
inline double& value(std::pair<int,double> p){return p.second;}

//evil，使用成员指针
typedef std::pair<int, double> id_value;
int id_value::*ID = &id_value::first;
double id_value::VALUE = &id_value::second;
std::pair<int,double> p;
p.*ID = -5;
p.*VALUE = 3.14;
//make them const
int id_value::* const ID = &id_value::first;


```

`模板参数`

作者给的建议是非类型模板参数 Non-Type template paremeter建议全部大写

```c++
template <typename T, bool BIGENDIAN=false>
class SomeClass{};

template <typename T>
class SomeClass<T, true>{};

//更干净的声明
template<typename T, bool = false>
class SomeClass;
```

类型的话通常都是T, 如果有指代信息，会用 A, R  表示参数和返回值（arguments， results）

```c++
int foo(double x){return 6+x;}
template <typename R, typename A>
inline R apply(R (*F)(A),A arg)
{
    return F(arg);
}
double x = apply(&foo, 3.14);
```



其他场景，作者建议直接写小写，后缀_t , 比如int_t， scalar_t

后缀_t通常是c惯用法，typedef，同样，在c++中也有很多类似的用法，（c++更多的是后缀\_type, 场景通常是类内部typeder，把模板参数封装一下，作者也是推荐的）

`元函数`

stateless，无状态，只转发，只做map

```c++
template <typename T, int N>
struct F{
    typedef T* pointer_type;
    typedef T& reference_type;
    static const size_t value = sizeof(T)*N;
};
```

这个元函数做了以下映射

(T,N) -> (pointer_type, reference_type, value)

{type}x{int} ->{type}X{type}X{size_t}

大多数元函数只是做类型映射，或者常量映射

两个例子

```c++
//type set -> smaller type set
template <typename T>
struct largest_precision_type;
typename <>
struct largest_precision_type<float>{
    typedef double type;
};
typename <>
struct largest_precision_type<double>{
    typedef double type;
};
typename <>
struct largest_precision_type<int>{
    typedef long type;
};
// const -> const
template <unsigned int N>
struct two_to{
    static const unsigned int value = (1<<N);
};

template <unsigned int N>
struct another_two_to{
  enum{value}= (1<<N)} ;// enum hack
};

unsigned int i = two_to<5>::value;
largest_precision<int>::type j = i+100;
//c++ 11 
largest_precision<decltype(i)>::type j = i+100;

```

 通常，使用enum hack而不是用static const ，不占用空间，而且某些编译器static const有问题。还有一个问题是，static const可能会被取地址，用来做一些evil的事情（复用成普通int，全局变量），enum不会有这种问题。

```c++
template <int N>
is_prime{
    enum{value =0};
};
template <>
is_prime<2>{
    enmu{value = 1};
};
template <>
is_prime<3>{
    enmu{value = 1};
};
...
```



进一步说还有其它问题，比如static const 不一定是编译期计算的。

```c++
static const int z = rand();
```

enum也有问题，因为看起来是int实际上是enum类型，某些场景就需要cast

```c++
double data[10];
std::fill_n(data, is_prime<3>::value, 3.14);//perhaps not ok
std::fill_n(data, int(is_prime<3>::value), 3.14);//ok

```

metafunction helper

一个例子

```c++
template <int N>
struct ttnp1_helper{
    static const int value = (1<<N);
};
template <int N>
struct two_to_plus_one{
    static const int value = ttnp1_helper<N>::value+1;
};

//或者直接这么写
template <int N>
struct two_to_olus_one{
private:
    static const int aux =(1<<N);
public:
    static const int value = aux+1;
};
```

helper 应该不被使用，可以匿名空间或者有个规范，加后缀_helper表示库能用客户端别用？

` 命名空间和using`

命名空间别嵌套太多，否则影响ADL

using可别放在头文件，命名空间混一起就麻烦了

---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>