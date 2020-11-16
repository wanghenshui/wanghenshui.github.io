---
layout: post
title: (译)advanced metaprogramming in classic c++ 1.1 templates （2）总结
categories: translation
tags : [c++,template]
---

  

### why

之前还翻译，翻译的吭哧瘪肚的。还是总结比较好。

---

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



看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
![微信转账](https://wanghenshui.github.io/assets/wepay.png)
</details>