---
layout: post
title: (译)advanced metaprogramming in classic c++ 1.4 典型模式 classic patterns
categories: translation
tags: [c++, template]
---

  

主要是一些典型的用法，或者说old-fashioned 用法

---

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

### ref

- get <https://zh.cppreference.com/w/cpp/memory/shared_ptr/get>
- base <https://zh.cppreference.com/w/cpp/iterator/reverse_iterator/base>
- safe bool <https://en.wikibooks.org/wiki/More_C%2B%2B_Idioms/Safe_bool>
- 这个safe bool中文的 <https://zhuanlan.zhihu.com/p/30173442>

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>