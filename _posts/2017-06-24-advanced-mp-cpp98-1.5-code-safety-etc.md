---
layout: post
title: (译)advanced metaprogramming in classic c++ 1.5-1.7 代码安全，编译器约定，预处理器
categories: translation
tags: [c++, template]
---

  

#### 代码安全

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

---

看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。

