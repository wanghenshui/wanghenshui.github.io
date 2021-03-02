---
layout: post
title: (译)advanced metaprogramming in classic c++ 1 templates
categories: [language, translation]
tags : [c++, template]
---

  

# 第一部分 预备知识 #include

------

//!个人有疑问的地方以及个人简介会加//? //!
//!翻译中可能会有不准的地方，我是结合上下文猜的。不准就不准吧因为水平不到位

## 1 模板
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

//！这解决了我的一个疑问，之前遇到但是没有深究，我太菜了。见[代码和注释](https://github.com/wanghenshui/hello-world/blob/master/cppcook/pad.cpp)

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



`尖括号 angle brackets`

即使模板参数有默认参数，你也不能省略尖括号

```c++
template<typename T=double> 
class sum{};
sum<> s1;//ok
sum s2;//err
```

模板参数T可以有不同的含义

- 表示泛型，比如std::vector<T> std::set<T> 可能要求T有构造比较的语义（conceptual）不影响整体泛型
- 表示满足固定的条件。这个场景下，仅有部分T实现。比如basic_string\<T\>

 在第二个场景下，你可能想省掉尖括号，两种解决方法，继承或者typedef

```c++
template<typename char_t = char>
class basic_string{...};
class my_string : public basic_string<>{
    ...
    // 注意 析构函数不是虚函数
};
typedef basic_string<wchar_t> your_string;
```

在c++98环境， 复合模板，两个 >>连起来可能会被解析成operator >> (猜测是parser的贪心解析) c++11解决了这个问题

---

`通用构造函数`

赋值构造函数和拷贝构造函数都是泛型的，当类型相同可能匹配不到无法调用

```c++
template<typename T>
class something{
    public:
    //S==T 不会调用
    template<typename S>
    something(const something<T>& s){}
    
    //S==T 不会调用
    template<typename S>
    something& operator=(const something<S>& that){
        return *this;
    }
}

something<int> s0;
something<double> s1, s2;
s0=s1;// 调用用户定义的复制构造
s1=s2;// 调用编译器生成的赋值构造
```

这种用户定义模板成员被称作通用(universal)拷贝构造和通用赋值,这些函数接受something\<X\> 而不是X

c++标准12.8有描述

- 模板构造函数永远不会是拷贝构造函数(?), 这种模板不会影响隐式拷贝构造函数生成
- 模板构造函数与其他构造函数（包括拷贝构造）一起参与重载决议，如果模板构造函数提供更好的匹配那就用模板构造函数来复制

实际上，基类特别泛型的模板成员函数会引入bug，一例

```c++
struct base{
  base(){}
  template<typename T>
  base(T x){}
};
struct derived :base{
    derived(){}
    derived(const derived& that):base(that){}
};
derived d1;
derived d2=d1;// stack overflow
```

隐式拷贝构造函数调用，永远不会调用通用模板构造函数，对于derived，通常来说，编译器为他生成了隐式拷贝构造函数，来调用base的隐式构造函数，但是derived实现了一个拷贝构造函数，转发给了base，调用了通用构造函数，T=derived，在base (T x)中，由于值语义，又调用了T的拷贝构造函数，递归了。

---

`函数类型与函数指针`

注意区别

```c++
template<double F(int)>
struct A{};
template<double (*F)(int)>
struct B{};

double f(int){return 3.14;}
A<f> t1;
B<f> t2;
```

通常一个函数会退化成函数指针，这和数组退化成数组指针是一个道理，但是函数类型是不能被构造的(函数唯一)。指针可以。

```c++
template<typename T>
struct X{
    T member_;
    X(T value):member_(value){}
};
X<double(int)> tl(f);// err 不能构造
X<double (*)(int)> t2(f); // 指针可以

```

所以需要functor出场。函数模板参数需要传入引用来避免退化（先加一层）

```c++
template<typename T>
X<T> identify_by_val(T x){
    return X<T>(X);
}
template<typename T>
X<T> identify_by_ref(const T& x){
    return X<T>(x);
}
identify_by_val(f); // 退化
identify_by_ref(f); //没问题
```

对于指针而言，函数还是显式参数的模板函数没有差别

```c++
double f(double x){return x+1;}
template <typename T> T g(T x) {return x+1;}
typename double (*pointer_type)(double);
pointer_type f1=f;
pointer_type f2 = g<double>
```

但是如果这个赋值语境在一个还不确定的模板参数中，就需要template关键字

```c++
template <typename X> 
struct outer{
    template <typename T>
    static T g(T x){
        return x+1;
    }
};
template <typename X>
void do_it(){
    pointer_type f1=outer<X>::g<double>; //err
    pointer_type f2=outer<X>::template g<double>;//ok
}
```

如果要是一个内部类，那就需要typename和template

```c++
template <typename X>
struct outer{
    template<typename T>
    struct inner{};
};

template <typename X>
void do_it(){
    typename outer<X>::template inner<double> I;
}
```

---

`不是模板的基类`

如果模板类成员不依赖模板参数，可拆出来放到普通类中

```c++
template <typename T>
class MyClass{
    double value_;
    std::string name_;
    std::vector<T> data_;
public:
	std::string getName() const;
};

//改进

class MyBaseClass{
protected:
    ~MyBaseClass(){}
    double value_;
    std::string name_;
public:
    std::string getName() const;
};

template <typename T>
class Myclass :MyBaseclass{
    std::vector<T> data_;
public:
    using MyBaseClass::getName;
};
```

如果这个模板被实例化很多次的话这也算是个小优化。

----

`模板位置`

模板函数类在编译器实例化的期间都必须可见，因此通常的头文件实现分开的做法可能不能直接用，所有实现都放在头文件中，或者改名，hpp

有时候需要前向声明某个特别的实例，前向声明可能通过编译，但是链接还是会有问题，不过有特殊的语法来帮助

```c++
template class X<double>;
template double sq<double>(const double&);
```

可以理解成“导出” c++11 之后有extern 模板

## 特化和参数推导

> 前提知识，作用域。命名空间作用域，类空间作用域，函数空间作用域

 函数模板和重载，自动推导参数，通常来说，编译器会选择参数最匹配的特化函数，通常一个已经存在的匹配如果可以的话总是会被选中？但是如果存在转化就会有其他场景。

如果函数f比函数g更特化，那就可以把所有调用g的地方都换成调用f，反之则不行。另外，一个非模板函数总是比模板函数更特化一点。

 ```c++
template <typename T> inline 
T sq(const T& x); // 函数模板 1
inline double sq(const double& x);//重载 2
template <> inline
int sq(const int& x);//前面函数模板的特化 3
inline double sq(float x);//重载，可以有不同参数，没问题 4
template <> inline
int sq(const int x);//无效的特化，参数不一致了。需要和前面的函数模板模式一致 5
 ```



重载和特化函数的区别就在于函数模板当作一个实体，尽管能特化出各种函数。比如在只有1 2 3的条件下调用sq(y)，会在 1 2中选择，如果y是double，就选2，否则就选1 然后1 实例化一个y类型的函数，如果y是int，恰好有个已经特化好的实例3，就选3

考虑下面这个例子

```c++
template <typename T>
void f(const T& x){
    std::cout<<"i am f(reference)";
}//1
template <typename T>
void f(const T* x){
    std::cout<<"i am f(pointer)";
}//2

template <typename T> void f(T){}//3
template <typename T> void f(T*){}//4
template <> void f(int*){}//  冲突！ 有很多特化路径
template <> void f<int>(int*){}//可以
```

以上这些特化场景是在命名空间范围内的，考虑一个类空间的例子

```c++
class mathematics{
    template <typenmae T> inline 
    T sq(const T&x){}//模板成员函数
    template <> inline int sq(const int&x ){} // err!
};

//解决办法，扔到外面去
template <typename T> inline 
T gsq(const T&x){}
template <> inline 
int gsq(const int& x){}

class mathmatics{
    template<typename T> inline 
    T sq(const T&x){
        return gsq(x);
    }
};
```

有时候会有不需要推导的函数模板参数，参数只是做个tag dispatch

```c++
class crr32{/*...*/};
class adler{/*...*/};
template <typename algorithm_t>
size_t hash_using(const char* x){/*...*/}
size_t j = hash_using<crc32>("this is the string to be hashed");
// 可以加上下面这个，不改变原意
template <typename algotirhm_t, typename string_t>
int hash_using(const string_t& x);
std::string arg("hash me");
int j= hash_using<crc32>(arg);
```

注意参数推导只针对函数模板，类模板不行。

上面不依靠推导而显式提供模板参数是个坏主意，但有些时候也没法避免，比如

```c++
//确实有歧义了
template <typename T>
T max(const T& a, const T&b){/*...*/}
int a=7;
long b=6;
long m1=max(a,b);// err! ambiguous, T==int or long?
long m2=max<long>(a,b);

//参数不需要推导，模板参数做dispatch用
template <typename T>
T get_random(){}
double r=get_random<double>();

//想要一个类似c++ cast方法的函数模板
template <typename X, typename T>
X sabotage_cast(T* p){
    return reinterpret_cast<X>(p+1);
}
std::sring s="don't do this";
double *p =sabotage_cast<double*>(&s);

//想要转换类型
double y = sq<int>(6.28); //把6.28转成int

//模板有默认参数，通常是个tag类，要改变tag
template <typename LessCompare>
void nonstd_sort(..., LessCompare cmp=LessCompare()){};
nonstd_sort<std::less<...> >(...);//传模板参数
nonstd_sort(..., std::less<...>());//传函数参数
```



一个模板的名字，比如std::vector 和具体实例化的名字是不一样的。但是在类作用域中，他们是一样的

```c++
template <typename T>
class something{
public:
	something(){}// 在这层写something<T>是错误的
	something(const something& that);// something& 就是something<T>&
	...
};
```

如果单独写something, 就代表一个模板. c++中有模板的模板参数, 可以声明模板,模板参数依赖一个模板.

 ```c++
template <template <typename T> class X>
class example{
    X<int> x1_;
    X<double> X2_;
};
typedef example<somthing> some_example; //ok
//注意，这里的class和typename不相等
 template <template <typename T> typename X> //err
 ```

类模板可以全特化/偏特化

```c++
//1 通常T不是指针
template <typename T>
struct is_a_pointer_type{
    static const int value =1;
};
//2 针对void* 全特化
template<>
struct is_a_pointer_type<void*>
{
	static const int value =2; 	   
};
偏特化所有其他指针类型
template<typename X>
struct is_a_pointer_type<X*>
{
    static const int value =3;
};

int b1= is_a_pointer_type<int*>::value;//匹配3
int b2= is_a_pointer_type<void*>::value;//匹配2
int b3= is_a_pointer_type<float>::value;//匹配1，普通版本

//偏特化可以递归！
template<typename X>
struct is_a_pointer_type<const X>{
    static const int value =is_a_pointer_type<X>::value;
};
```

至于const 又有一个pointer paradox问题

```c++
template <typename T> void f(const T& x){std::cout<< "ref";}
template <typename T> void f(const T* x){std::cout<< "ptr";}
const char* s="text";
f(s);//ptr
f(3.14);//ref
double p=0;
f(&p);//?
```

也许你会觉得传的指针应该打印ptr，事实上double* 匹配const T*多了个const，这个加const会有副作用，但是匹配const T&正好是值语义，加const 无影响

---

 `推导`

函数模板可以推导自己的参数，根据函数签名匹配参数类型，这个推导是模式匹配，编译器不会多做其他的计算

```c++
template <typename T> struct arg;
template <typename T> void f(arg<T>);
template <typename T> void g(arg<const T>);
arg<int* >a;
f(a);// T=int*
arg<const int>b;
f(b);// T=const int
g(b);// T=int

template <int I> struct argi;
template <int I> arg<I+1> h(argi<I>);
argi<3> c;
h(c);// I=3
// 但是编译器不会帮你计算参数内部的值
template <int I> arg<I> h(argi<I+1>);
argi<3>d;
h(d);//err

```

另外，如果一个类型包含一个类模板，这个上下文不能被推倒出来

```c++
template <typename T> 
void f(typename std::vector<T>::iterator);
std::vector<double> v;
f(v.begin());//err
f<double>(v.begin());//ok
```

这个错误的原因是无法判断T的类型，理论上T可以是任意类型，T和T::value不相关

```c++
template <typename T>
struct A{typedef double type;};
```

解决方法的弊端上面提到过，尽可能利用推倒而不是手写，下面有几个相关场景的代码片



```c++
struct base{
    template<int I, typename X> 
    void foo(X,X){}
};

struct derived :public base{
    void foo(int i){
        foo<314>(i,i);
    }
};

//编译错误
1>error: 'derived::foo': function call missing argument list; use
'&derived::foo' to create a pointer to member
1>error: '<' : no conversion from 'int' to 'void (__cdecl
derived::* )(int)'
1> There are no conversions from integral values to pointer-to-
member values
1>error: '<' : illegal, left operand has type 'void (__cdecl
derived::* )(int)'
1>warning: '>' : unsafe use of type 'bool' in operation
1>warning: '>' : operator has no effect; expected operator with
side-effect
```

还有一点，如果名字查找有多个结果，显式提供参数会限制重载决议

```c++
template <typename T> void f();
template <int N> void f();
f<double>();
f<7>();
```

但会忽略掉一些重载结果。

```c++
template <typename T> void g(T x);
double pi = 3.14;
g<double>(pi);//ok 
template <typename T> void h(T x);//1
void h(double x);//2
h<double>(pi);// 糟糕！调用1
```

另一例

```c++
template <int I> class X{};
template <int I, typename T> void g(X<i>,T x);//1
template <typename T> void g(X<0>, T x);//2 特化X<0>注意，这是g<T> ,不是g<0,T>
double pi = 3.14;
X<0> x;
g<0>(x,pi);//1
g(x,pi);//2
```

---

`特化`

模板特化只在命名空间作用域有效

```c++
struct X{
  template<typename T>  
  class Y{};
  template<>
  class Y<double>{};//err, 但是通常编译器不报错。
};

template <>
class X::Y<double>{}; //ok
```



要注意可见性，推导的前后顺序问题

```c++
template <ytpename T> T sq(const T& x){}
struct A{
    A(int i=3){
        int j=sq(i);//已经推导完毕
    }
};
template<>
int sq(const int& x){}//err
```



再比如

```c++
template <typename T> 
struct C{
    C(C<void>){}
};

template <>
struct C<void>{} //err

//解决方法，前置声明
template<typename T> struct D;
template <> 
struct D<void>{}
template <typename T> 
struct D{
    D(D<void>){}
};
```

也可以偏特化非类型模板参数(int)

 ```c++
template <typename T, int N>
class MyClass{};//1
template <typename T>
class MyClass<T,0>{};//2
template <typename T, int N>
class MyClass<T*,N>{};
Myclass<void*, 0> m; //err 用1 还是2？

//  组合解决
template<typename T>
class MyClass<T*,0>{};
 ```

另外，模板参数依赖前提下，也不可以偏特化，除非完全特化

```c++
template <typename int_t, int_t N>
class AnotherClass{};
template <typename T>
class AnotherClass<T,0>{}; //err 0依赖T

template<>
class AnotherClass<int,0>{}; //ok, 全特化
```

一个模板的特化也许和模板参数完全没关系，不必非得相同成员，函数也可以有不同的签名

```c++
template<typename T, int N>
struct base_with_array{
    T data_[N];
    void fill(const T&x){
        std::fill_n(data_,N,x);
    }
};

template<typename T>
struct base_with_array<T,0>{
    void file(const T&){}
};

template <typename T, size_t N>
class cached_vector : private base_with_array<T,N>{
//...
public:
    cached_vector(){
        this->fill(T());
    }
};
```

---

`内部类模板`

一个类模板可以使另一个模板的成员，关键点在于，内部类拥有自己的参数，但了解所有的外部类参数

```c++
template<typename T>
class outer{
public:
	template<typename X> 
	class inner{
        //可以用T 和X
	};
};
```

如果T确定(well-defined)类型，就可以用`outer<T>::inner<X>` 来访问，如果T是模板模板参数，需要加template `outer<T>::template inner<X>`

内部类通常很难特化。特化应该在outer就列好。列出一些组合场景

```c++
template <typename T>
class outer{
    template<typename X>    class inner{}; //inner1
};

template<>
class outer<int>
{
    template <typename X>    class inner{}; //inner2这种全特化前提下，肯定会略过inner1
};

template <>
class outer <int>::inner<float>{}: //inner3, inner2全特化

template <>
template <typename X>
class outer<double>::inner }{};     //inner4, inner1特化，就像inner2

template <>
template <>
class outer<double>:;:inner<char>{}; //inner5, inner4  全特化

template<typename T>
template <>
class outer<T>::inner<float>{}; //err 保持T泛型特化X，这样做的潜台词是无论t是什么inner<X> 都是一致的，从同一个空间的角度就能证伪

int main(){
    outer<double>::inner<void> I1;
    outer<int>::inner<void> I2;
    I1=I2;//err
}

```

想用一个函数来证明两个inner\<X>是相同的也是不现实的(?) 因为无法推导外部的outer\<T>

解决办法也有，提升到全局模板。

```c++
template <typename X> // typedef //
struct basic_inner{};

template <typename T>
struct outer{
	//typedef basic_inner inner;    
	template <typename X>
	struct inner : public basic_inner<X>{
      inner& operator=(const basic_inner<X>& that){
          static_cast<basic_inner<X>&>(*this)=that;
          return *this;
      }
	};
};
template<>
struct outer<int>{
    //typedef basic_inner inner
    template <typename X>
	struct inner : public basic_inner<X>{
      inner& operator=(const basic_inner<X>& that){
          static_cast<basic_inner<X>&>(*this)=that;
          return *this;
      }
	};
};


```

然后，需要把basic_inner设计的更泛型支持多种操作

```c++
template <typename X, typename T>
struct basic_inner
{
	template <typename T2>
	basic_inner& operator=(const basic_inner<X, T2>&)
	{ /* ... */ }
};
template <typename T>
struct outer
{
	template <typename X>
	struct inner : public basic_inner<X, T>
	{
		template <typename ANOTHER_T>
		inner& operator=(const basic_inner<X, ANOTHER_T>& that)
		{
			static_cast<basic_inner<X, T>&>(*this) = that;
			return *this;
		}
	};
};

template <>
struct outer<int>
{
	template <typename X>
	struct inner : public basic_inner<X, int>
	{
		template <typename ANOTHER_T>
		inner& operator=(const basic_inner<X, ANOTHER_T>& that)
		{
			static_cast<basic_inner<X, int>&>(*this) = that;
			return *this;
		}
	};
};

int main()
{
	outer<double>::inner<void> I1;
	outer<int>::inner<void> I2;
	I1 = I2; // ok: it ends up calling basic_inner::operator=
}
```

这种实现被叫做SCARY initialization ` N2911 explains that the acronym SCARY “describes assignments and initializations that are Seemingly erroneous (Constrained by conflicting generic parameters), but Actually work with the Right implementation (unconstrained bY the conflict due to minimized dependencies).` 简单说就是共享同一份内部实现。

看参考中援引的论文学习一哈



再考虑内部类中的函数。

如果偏特化出现的比使用晚，就会选取模板，如果使用全特化，直接报错已经实例化了。

```c++
struct A
{
	template <typename X, typename Y>
	struct B
	{
		void do_it() {} // do it 1
	};
	
    void f()
	{
		B<int,int> b; //实例化了
		b.do_it();
    }
};

template <typename X>
struct A::B<X, X> 
B<X,X> //   太晚了
{
	void do_it() {} // do_it 2
};
A a;
a.f(); // do it 1
template <>
struct A::B<int, int>
{
	void do_it() {} // compile err
};
```





## 风格惯例，约定 style conventions

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





## 典型模式 classic patterns

`size_t ptrdiff_t`

通常没有好的选择大整数的办法，那就选这俩，size_t无符号，ptrdiff_t有符号。足够用

size_t可是operator new的参数，也是sizeof的返回值，大小足够用了，ptrdiif_t是算两个指针举例的，也算是够用

进一步，考虑flat c++ memory model，sizeof(size_t)和指针大小是一样的。（无论什么平台）

考虑下面这个类

```c++
template <int N>
struct A{
    char data[N];
};
```

sizeof(A\<N\>)最起码N，所以size_t不会小于int，同理可证ptrdiff_f

`void T::swap(T&)`

需要T提供T::swap(T&)，性能不能比传统的三次复制差（最次应该相同），理论上是可行的，调用成员的swap就可以了

std::swap/std::container<\T\>::swap针对trivial类型已经做了足够的优化，对于用户实现的T，保证T::swap的实现能用上std::swap/std::container<\T\>::swap 应该就够用 （std::swap调用的就是成员的swap，各类容器会提供std::swap的特化版本，无缝结合）

效率完全取决于这个T是不是swapable，std::array<T,N> 的swap调用的是swap_range，效率会差一些，但是string实现决定是swapable的，交换会非常快，利用这种类型的swap会有优势



那首先要考虑的问题就是T未知如何swap

```c++
template <typename T>
class TheClass{
    T theObj_;
    void swap(TheClass<T> & that){
        std::swap(theObj_, that,theObj_);
    }
};
// 去掉std::限制会有问题
using std::swap;
template <typename T>
class TheClass2{
    T theObj_;
    void swap(TheClass<T> & that){
        swap(theObj_, that,theObj_);// compile err: match one...
    }
};
```

名称查找的问题，解决办法是加一层调用，引入adl（或者干脆就加上std::好不好，为了省五个字，多打了五行）

```c++
using std::swap;
template <typename T>
inline void swap_with_adl(T& a,T& b){
    swap(a,b);
}

template <typename T>
class TheClass3{
    T theObj_;
    void swap(TheClass<T> & that){
        swap_with_adl(theObj_, that,theObj_);
    }
};
```

也有可能还有swap重载，本质上都是为了找使用std::swap来保证最佳效率。毕竟大部分T::operator=也是用swap实现的

`bool T::empty() const, void T::clear()`

要求永远是O1，这里有个坑，empty的实现不一定是size()==0，size()也没要求过复杂度，c++98 list的size()就是O(N) 的，后面才改成O1 没什么好说的

clear是一个状态重置，语义上不保证释放资源/内存，所以就有这个swap惯用法

```c++
std::vector<int> x(10000,5);
std::vector<int>().swap(x);
```

`X T::get() const, X T::base() const`

get 是智能指针设计上的小技巧，T封装了一层X ，get就直接返回了，在智能指针实现上，就是返回指针

base返回值，感觉和get很想但是语义不一样。std::reverse_iterator就用了这个。

`X T::property()`

property就是个名字，这个std::iostream在用

`Action(Value), Action(range)`

这个就是没有for-range和std::span的妥协产物, 了解即可

`操作符 manipulators`

这个在iostream这套邪恶的库中，算是个亮点，但是导致stream本身不是stateless，增加了复杂度

就比如， std::endl实际上是什么东西

```c++
class ostream{
public:
    //...
    inline ostream& endl(ostream& os){
        os<<'\n'  ;
        os.flush();
    }
    ostream& operator<<(ostream& (*f)(ostream&)){
        return f(*this)
    }
};
```

再比如setprecision，实现是什么样的

```c++
struct precision_proxy_t{
    int prec;
};
inline ostream& operator<<(ostream&o, precision_proxy_t p){
    o.precision(p.prec);
    return o;
}
precision_proxy_t setprecision(int p){
    precision_proxy_t result = {p};
    return result;
}
cout<<setprecision(12)<<3.14;
```

一个更成熟的实现是会把proxy存个函数指针，然后setprecision返回proxy<int,fp>然后直接就调用fp了。此处略过。写着实在是闹心。

`operators`位置

本质上还是拷贝构造的问题

作者建议实现放在类的外面，帮助抓错

假如实现pair

```c++
template <typename T1, typename T2>
struct pair{
	T1 first;
	T2 second;
	template <typename S1, typename S2>
	pair(const pair<S1, S2>& that): first(that.first), second(that.second)
	{}
};
```



如果在内部实现operator== 类型就不能和T1T2重复，假设你实现了个operator== 模板参数和上面相同

```c++
template <typename T1, typename T2>
struct pair
{
// ...
	inline bool operator== (const pair<T1,T2>& that) const{
		return (first == that.first) && (second == that.second);
	}
};
pair<int, std::string> P(1,"abcdefghijklmnop");
pair<const int, std::string> Q(1,"qrstuvwxyz");
if (P == Q) { ... }
```

问题来了！比较的类型不一致，就会调用默认拷贝构造来调用一个满足条件的参数来比较

如果你把实现放在外面，这种场景会直接报错。

```c++
template <typename T1, typename T2>
bool operator== (const pair<T1,T2>& x, const pair<T1,T2>& y) {
	return (x.first == y.first) && (x.second == y.second);
}
//正确的实现
template <typename T1, typename T2 >
struct pair {
	// ...
	template <typename S1, typename S2>
	inline bool operator== (const pair<S1, S2>& that) const {
		return (first == that.first) && (second == that.second);
	}
};
```

`无声无息的继承  Secret Inheritance`

如果父类组件比较多，自雷继承父类更像是typedef，相当于一种上层的委托构造，或者是模板typedef

```c++
template <typename T1, typename T2> 
class A{};

template <typename T>
class B :public A<T,T>
{};
```

这种写法，最好要保证A是不可见，使用者拿不到的，不然可能就会a* p=new b；这种用法，就得为a加上析构（因为a本身会有很多数据，很重，而不是仅仅作为一个接口）

一个例子

```c++
template<typename T>
class B :std::map<T,T>{}; //bad

namespace std{
template <...>
class map :public _Tree<...> //good, _Tree一般没人知道，不会拿过来直接用
}
```

还有一个例子，提供相同的接口

```c++
template <typename T, int CAP=16>
class C;

template <typename T>
class H{
  H&operator ==(const H&)  const ;
};
template <typename T, int CAP>
class C :public H<T>
{};
```

因为C 是{T}x{int} operator==要抽离出int，利用这个技巧，可以写一个干净的operator==，只要继承H<T\>, 由H<T\>来实现operator==就好了

`Literal Zero`

就是预防传值错误,但是又可以传0，一个匹配的trick

```c++
class dumy{};
typedef int dummy::*literal_zero_t;
template <typename T>
class match_literal_not_0_err{
    bool operator==(literal_zero_t)const{
        ...
    }
}
```

因为literal_zero_t构造不出来，只能转成0才能过。

`safe bool`

由于类可以实现operator bool，可能就会引入歧义。 实现一个safe operator bool是个很有趣的事儿，引用中列了几个文章

stream是怎么实现的

实现了operator void*

```c++
stream s;
if(s)
{
    int i=s+2;// 转换成this，不会编译
    free(s);// oops
}
```

作者介绍了一个类似上面literal_zero的trick，当然和safe bool idiom差不多

```c++
struct boolean_type_t{
     int true_;
};
typedef int boolean_type_t::*boolean_type;
#define mxt_boolena_true &boolean_type_t::true_
#define mxt_boolean_false 0

class stream{
  ...
  operator boolean_type() const{
      ...return mxt_bool
  }
};
```



`初始化`

初始化可能值是未定义的（POD），也有可能定义了一部分，初始化还有一些坑

```c++
T a(); //err, 函数， T (*a)() 
T b;// ok，有默认构造函数
T c(T());//err, 函数 T(*c)(T (*)())
T d ={};//ok ，对于POD
T e= T();// ok 调用拷贝构造
```

理论上应该有个optional的默认值，作者建议自己实现一个,非常简单（但不是std::optional那种语义，仅仅作为初始化来用）

```c++
template <typename T>
struct initialized_value{
    T result;
    initialized_value():result(){
        
    }
};
```



## 代码安全，编译器约定，预处理器



由于TMP编程，优雅~~(瞎写)~~先行，这就带来了麻烦, 作者举了个unary_function的例子

```c++
class unary_f: public std::unary_function<int, float>{
public:
    //...  
};

int main(){
    unary_f u;
    std::unary_function<int, float>* ptr = &u;
    delete ptr;
}
```

这个例子看的我十分不适，且不说现在基本没什么人知道unary_function, std::bind 都没啥人用，这套binder太硬核了，见识见识std::bind也就足够，现在都是std::function +lambda，况且作者举例的这个写法就是瞎写

剩下的几个例子直接总结就好了，TMP错误实践

- 非虚析构函数基类问题 ~~上面这个例子~~
- 实现operator T()
- 声明非显式的一个参数的构造函数 T(a)

---

#### 编译器假定

这些模板使用背后是编译器的大量工作，不是所有的标准都在编译器上实现了的。一个满足标准(standard-comforming)的编译器应该考虑到所有优化场景，这基本上是不可能的，只能说，编译器不可能比代码表现更差，会有优化点。

但是这些场景也没法避免

- 意外的编译器错误，ICE
- 运行时错误，访问错误，coredump，panic
- 大量的编译链接时间
- 并不令人满意(suboptimal)的运行速度

前两个问题可能是编译器bug，或者用的不对，第三个可能是模板代码引入，第四个问题可能是编译优化效果太差



##### inline，内联

inline是编译器决定的，即使你代码中标注了inline，定义声明在一起的通常默认inline，成员函数默认inline，如果定义声明不在一起，就不inline

代码中的inline对于编译器来说就是个hint，编译器最终决定是否inline

我们通常假定

- 如果函数足够简单，会inline，不管代码片长度

```c++
template <typename T, int N>
class recursive{
    recursive<T,N-1> r_;
public:
    int size() const {
        return 1+ r_.size();
    }
};
template <typename T>
class recursive<T, 0>
{
public:
    int size() const {
        return 0;
    }
};
```

上面这段代码片，调用recursive<T,N>::size()会内联，直接返回N

- 编译器能优化成无状态的，会内联，典型场景，operator(), functor

functor通常会作为容器的成员，还会占用一字节，可以用空基类优化干掉。

```c++
template < typename T, typename less_t = std::less<T> >
class set : private less_t
{
	inline bool less(const T& x, const T& y) const	{
		return static_cast<const less_t&>(*this)(x,y);
	}
public:
	set(const less_t& l = less_t())
	: less_t(l)	{}
	
	void insert(const T& x)	{
	// ...
		if (less(x,y)) // invoking less_t::operator() through *this
		{}
	}
};
```

##### 错误信息

模板编译错误的错误信息很难看懂，作者讲解了点读编译错误日志的技能

- 看长模板堆栈
- 看实现细节， 比如std::_Tree std::map
- 看拓展的typeder ，比如string就是 std::basic_string<char, ...>.
- 类型不全 incompliete types

还有一些编译器小细节

- 别怪编译器
- 开编译警告级别， 别忽略警告 比如什么unsigned signed mismatch，很容易打哈哈就过去了
- 维护一个编译器bug列表
- 避免不规范的行为，或者说不要写未定义行为的代码
- 不要害怕语言特性
- 别人拿你的代码做什么，可能会卵用，预防性接口

---

#### 预处理器

#### macro guard

作者还说了一些库中爱用的技巧，跨平台，版本号定义之类的。not fancy


### ref

- SCARY更多资料 
  - 提到的论文 http://www.open-std.org/Jtc1/sc22/wg21/docs/papers/2009/n2913.pdf
  - <https://devblogs.microsoft.com/cppblog/what-are-scary-iterators/>
  - <http://www.open-std.org/jtc1/sc22/WG21/docs/papers/2009/n2911.pdf>
  - <https://stackoverflow.com/questions/14391705/what-are-scary-iterators>
  - <https://www.boost.org/doc/libs/1_55_0/doc/html/intrusive/scary_iterators.html>
 - get <https://zh.cppreference.com/w/cpp/memory/shared_ptr/get>
  - base <https://zh.cppreference.com/w/cpp/iterator/reverse_iterator/base>
  - safe bool <https://en.wikibooks.org/wiki/More_C%2B%2B_Idioms/Safe_bool>
  - 这个safe bool中文的 <https://zhuanlan.zhihu.com/p/30173442>

  

---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>
