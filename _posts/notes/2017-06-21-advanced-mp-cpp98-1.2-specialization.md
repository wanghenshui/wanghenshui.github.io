---
layout: post
title: advanced metaprogramming in classic c++ 1.2 特化和参数推导
category: translation
tags: [c++, template]
---

{% include JB/setup %}

### why

填坑，学习tmp

---

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
    std:;cout<<"i am f(reference)";
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



---

看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。

### ref

- SCARY更多资料 
  - 提到的论文 http://www.open-std.org/Jtc1/sc22/wg21/docs/papers/2009/n2913.pdf
  - <https://devblogs.microsoft.com/cppblog/what-are-scary-iterators/>
  - <http://www.open-std.org/jtc1/sc22/WG21/docs/papers/2009/n2911.pdf>
  - <https://stackoverflow.com/questions/14391705/what-are-scary-iterators>
  - <https://www.boost.org/doc/libs/1_55_0/doc/html/intrusive/scary_iterators.html>