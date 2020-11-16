---
layout: post
title: (译)advanced metaprogramming in classic c++ 1.1 templates
categories: translation
tags : [c++, template]
---

  

### 第一部分 预备知识 #include 

------

//!个人有疑问的地方以及个人简介会加//? //!
//!翻译中可能会有不准的地方，我是结合上下文猜的。不准就不准吧因为水平不到位

- 1.0 模板
  \-
  编程是通过与其中的一台机器交谈来向计算机教授某些东西的过程共同语言。  越接近机器，就越不自然。每种语言都有自己的表现力。  对于任何给定的概念，各种语言的实现有不同的复杂度。在汇编中，我们必须给予非常丰富的描述，（显得不可读）c++的优势就在于在足够接近机器底层的同时又能有优美的表达，C++允许程序员用不同的风格来表达相同的概念，并且更加自然。
  接下来深入了解c++模板系统的细节。

下面是一个代码块

> double x = sq(3.14);

sq是什么？
sq可以是宏

> \#define sq(x) ((x)*(x))

可以是一个函数

> double sq(double x) {return x*x;}

可以是一个模板函数

> template  
>
> inline T sq(const T& x){ return x*x; }

一个类型（没有实例）//函数对象

```
class sq
{
    double s_;   
public:
    sq(double x):s_(x*x)
    {}
    operator double() const
    {
        return s_;
    }
};
```

或者一个全局变量

```
class sq_t
{
public:
    typedef double value_type;
    value_tupe operator() (double x)
    {
        return x*x;
    }
};
const sq_t sq = sq_t();
```

不管如何实现，你看到后在脑海中肯定有一个实现，不过脑海中的实现和现实中的实现是不一样的，如果sq是一个类，放在函数模板中可能会有错误的推导结果

```
template <typename T> void f(T x);

f(cos(3.14)); //实例化f<double>
f(sq(3.14)); //实例化f<sq>？
```

不仅如此，你还要考虑到各种数据类型被sq平方时在实现上要尽可能的高效，不同的实现有不同的效果

```
std::vector<double> v;
std::transform(v.begin(),v.end(),v.begin(),sq);
```

速度瓶颈在sq的实现上。（宏会报错）

\###模板元编程TMP的意义在于

- 所见即所得，不必思考背后的实现
- 效率最高
- “自适应”//?自洽？，与其余程序融合，可移植性强

“自适应”意味着移植性强，不拘泥于编译器实现，不受约束，sq数据从一个抽象基类中继承出来可不满足 自洽自适应。
c++模板真正强大的地方在于类型//不变量
考虑两个表达式

```

double x1 = (-b + sqrt(b\*b - 4\*a\*c))/(2\*a);

double x2 = (-b + sqrt(sq(b) - 4\*a\*c))/(2\*a);
```

模板的参数计算与类型推导都在编译期间完成，运行时不会有消耗。如果sq实现的好的话第二行要比第一行快且可读性强一些

用sq更优雅

- 代码可读性强/逻辑自证
- 没有运行负担
- 最佳优化

事实上在模板基础上可以轻松加上特化

```
template <>
inline double sq(const double & x)
{
    //here ,use any special algorithm you have
}
```

- 1.1. C++ 模板
  \-
  典型的c++模板，函数模板和类模板//备注：当前c++还支持其他模板，但都可以看做它们的扩展
  只要你提供了满足条件的参数，在编译期间模板展开就可以了。
  一个函数模板可以推导函数，一个类模板可以展开成类，TMP的要点可以总结为
- 你可以利用类模板在编译期完成计算。
- 函数模板可以自动推导他们的参数类型

两种模板都需要把参数列表放在尖括号里。可以是类型或者是整数和指针
//备注 理论上所有整数类型都可以，枚举/bool/typedef/连编译器提供的类型都支持(__int64 MSVC)
//    指向全局函数/成员函数的指针也允许，指向变量的指针可能会有限制。在Chapter 11会有讨论
//!当然我能不能翻译到哪里就不好说了 

参数也可以有默认值//! 谁不知道啊

**模板可以理解成一个元函数，将参数映射成函数或类**

比如 sq

```
template <typename T>
T sq(const T& x);
```

 T -> T(*) (const T*)

同样的，类也是一个映射，比如 T ->  basic_string
通过类的模板偏特化来具化元函数，你可以有一个普通的模板和一堆偏特化，它们有没有内容都可以。
定义的时候，类型就是形参，实例化的时候，类型就是实参。
当你向模板提供了实参， 作为元函数//！映射，模板就被实例化，然后生成代码，编译器再将模板生成的代码生成机器码

要明白不同的实参产生不同的实例，即使形参看起来差不多，double和const double实例化的效果可是没有相关性的。

当使用函数模板，编译器会弄明白所有的形参，我们可以理解成形参绑定在模板形参上。

```
template <typename T>
T sq(const T& x) { return x*x; }
double pi = 3.14;
sq(pi); // the compiler "binds" double to T
double x = sq(3.14); // ok: the compiler deduces that T is double
double x = sq<double>(3.14); // this is legal, but less than ideal
```

 所有的模板实参都是编译期常数

- 类型形参可以接受任何类型//!只要是类型
- 非类型形参由最佳转换原则自动推导

一个典型错误例子

```
template <int N>
class SomeClass{};

int main()
{
    const int A = rand();
    SomeClass<A> s; //error

    static const int B = 2;
    SomeClass<C> s; //fine
}
```

模板中常量写法的最佳实践是 static const [[integer type]] name = value;
//!指的应该不是现代c++,是classic C++

当然，局部变量，static可以省略。不过这个并没有什么坏处，更清晰一些//!不必强求

传递到模板中的实参可以在编译期计算出结果，有效地整数运算都会在编译期得到结果。
//!换句话说，无效的运算都会在编译期被捕捉到而不是放在运行时崩一脸

- 除以0会导致编译错误
- 禁止函数调用
- 生成代码中的非整数/指针类型都是不可移植的。//特指浮点型，可以通过整型除法替代

SomeClass<(27+56*5) % 4> s1;SomeClass<sizeof(void* ) *CHAR_BIT>

除以0的错误的前提是模板整体都是常量

```
template <int N>
struct tricky
{
    int f(int i =0)
    { return i/N;} //not a constant
};

int main()
{
    tricky<0> t;
    return t.f();
}

waring: potential divide by 0;
```

改成N/N ，是常数之后就会报错了 实例化N为0或者0/0都会报错

更确切一点，编译期常量包括

- 整型字面量 

- sizeof，类似sizeof的得到整型结果的操作// **alignof**

- 非类型模板形参 在上下文中就是模板wrapper //!原文为”outer” template
    template 
    class AnotherClass
    {`SomeClass<N> _m; `  };

- static 整型常数
    template 
    struct NK
    {

  ```
  static const int PRODUCT = N*K;
  ```

    };
  
    SomeClass::PRODUCT > s1;

- 某些宏 **LINE**
    SomeClass<__line__> s1;
    //备注，一般没人这么用，通常用来自动生成枚举/实现断言

模板形参可以依赖其他形参

```
template<typename T, int (*FUNC)(T)>
class X{};

template<typename T,T VALUE    >
class Y{};

Y<int,7> y1;
Y<double,3> y2;//error  常数3没有这种double类型
```

类（模板类）也可以有模板成员函数

```
struct math
{
    template <typename T>
    T sq(T x) const {return x*x;}
};

template <typename T>
struct _math{
    template <typename _T>//备注 T和_T区分避免被外面的给掩了
    static T product(T x, _T y){return x*y;}
};

double A = math().sq(3.14);
double B = _math<double>().product(3.14,5);
```

- 1.1.1 Typename
- 

这个关键字用来

1. 声明模板形参，替代class歧义
2. 告诉编译器如果不能识别出来，那它就是类型名

举一个编译器不识别的例子

```
template<typename T>
struct MyClass{
    typedef double Y;
    typedef T Type;
};

template<>
struct MyClass<int>{
    static const int Y = 314;
    typedef int Type;
}; 


int Q = 8;

template <typename T>
void SomeFunc(){
    MyClass<T>::Y * Q;
    //    这行代表一个Q的指向double的指针？还是314乘8？
}
```

Y是依赖名字，因为它依赖一个未知的参数T
直接或间接的依赖于一个位置的参数的变量都是依赖名字，都应该明确的用typename说明

//！这解决了我的一个疑问，之前遇到但是没有深究，我太菜了。见[代码和注释](https://github.com/jieyaren/100k/blob/master/cppcook/pad.cpp)

```
template <typename X>
class AnoterClass{
    MyClass<X>::Type t1_;//error
    typename MyClass<X>::Type t2_;//ok 
    MyClass<double>::Type t3_; //ok
};
```

**要明白上面这个例子中,第一个必须有typename，第三个不能有typename**

```
template <typename X>
class AnotherClass{
    typename MyClass<X>::Y member1_;//ok 但是X是int不会编译
    typename MyClass<double>::Y member2_;//error
};
```

当声明了一个没有类型的模板形参时，需要typename引入依赖名字//!来推导出类型

```
template <typename T,typename T::type N>
struct SomeClass{};

struct S1{
    typedef int type;
};

SomeClass<S1,3> x;
```

//!接下来这段不好翻译
对于类型T1::T2如果实例化中发现是没有类型的，需要加上typename，等待后面实例化
直接上代码
​    tmeplate 
​    struct B{
​        static const int N = sizeof(A::X);
​        //应该是sizeof(typename A…)
​    };
直到实例化，B认为应该调用sizeof在没有类型的参数上，当然啦sizeof也会自己推导出来，所以代码没错，如果X是一个类型，这个代码也是合法的//!后面偏特化
见代码
​    template 
​    struct A{
​        static const int X = 7;
​    };

```
template <>
struct A<char>{
    typedef double X;
};
```

上面的例子没有覆盖一些阴暗的角落，有兴趣请点击这个阴暗的[连接](http://www.open-std.org/jtc1/sc22/wg21/docs/cwg_defects.html#666)





---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。