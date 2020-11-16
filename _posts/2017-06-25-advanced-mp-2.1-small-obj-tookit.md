---
layout: post
title: (译)advanced metaprogramming in classic c++ 2 小对象工具  small object toolkit
categories: translation
tags: [c++, template]
---

  

比第一章有意思一点，但还没到正文

---

TMP与遍地临时变量相对应的就是帮助类型，auxiliary type

----

### hollow types 空类型

`instance_of`

在元编程中特别有用的一个工具

```c++
template <typename T>
struct instance_of{
    typedef T type;
    instance_of(int =0){}
};
const instance_of<int> I_INT= instance_of<int>();
const instance_of<double> I_DOUBLE = 0;
```

没明白这有啥特别好用的，感觉主要是提取类型吧，作者没说

至于为什么提供一个参数，主要是因为const变量可能会被警告未使用，所以赋值0避免

`selector`

主要是用来实现tag dispatch，也可以用std::integral_constant实现

```c++
template <bool PARA>
struct selector{};
typedef selector<true> true_type;
typedef selector<false> false_type;
template <typename T, bool B>
void f(const T& x, selector<B>)
{
}
```

not fancy，标准库里很多。比如iterator 各种分类以及相关的dispatch

`static value`

实际上还是std::integral_constant的一个实现，没啥值得说的

`大小限制`

实际上就是sizeof trick

```
template <typename T>
class larger_than{
    T body_[2];
};
```

一定满足sizeof(T) < 2*sizeof(T)  < =sizeof(larger_than<T>) 考虑padding

根据这个，可以用来做函数匹配, SFINAE，这个后面会讲，只要记住这个char结合sizeof dummy很好用就行了

```c++
typedef char no_type;
typedef larger_than<no_type> yes_type;
```



### 静态断言 static assertions

其实c++11出了static_assert关键字，下面这些就是个回溯，已经不重要了。

```c++
template <typename T>
void myfunc(){
	typedef typename T::type ERROR_T_DOES_NOT_CONTAIN_type;
	const int ASSERT_T_MUST_HAVE_STATIC_CONSTANT_value(T::value);
};
```

其实也可以理解成一种traits，不存在就报错，编译期拒绝

`boolean assertions`

这个实现基本上也就是c++11 static_assert的实现，`只声明不实现`

```c++
template <bool Statement>
struct static_assertion{};
template<> 
struct static_assertion<false>;// unimpl

int main(){
	static_assertion<sizeof(int)==3144> ASSERT_LARGE_INT;
}
```

或者直接用sizeof求值，进一步用宏封装起来

```c++
#define MXT_ASSERT(statement) sizeof(static_assertion<statement>)
```

但是又有了新问题，如果statement中有逗号，按照宏的处理，就会报错，这种场景就得使用两个括号括起来，或者把带逗号的表达式typedef替换掉。比较难看

```c++
typedef std::map<int, double> map_type;
MXT_ASSERT( is_well_defined<map_type>::value );
MXT_ASSERT(( is_well_defined< std::map<int, double> >::value ));
```



`assert legal`

这也是sizeof的妙用，求值，sizeof求表达式的返回值，所以表达式就得合法



### tagging techniques

作者举的例子就是函数重载+空类tag，上面也讲过tag dispatch。没啥说的

一个著名的例子就是迭代器的tag了，针对不同的tag匹配不同的advance函数



此外，作者还举了几个特殊的例子

tag iteration，使用std::integral_constant来做函数匹配迭代，迭代周期应该是/2而不是-1，这样会生成多余的模板。

不过一般也没人把tag dispatch和递归函数叠加着用，太evil了

tag & inheritance， 这个更邪恶, 直接复制书的原话吧

Suppose you are given a simple allocator class, which, given a fixed size, will allocate one block of
memory of that length.

You now wrap it up in a larger allocator. Assuming for simplicity that most memory requests have a size
equal to a power of two, you can assemble a compound_pool<N> that will contain a fixed_size_allocator<J>
for J=1,2,4,8. It will also resort to ::operator new when no suitable J exists (all at compile-time).
The syntax for this allocation is 11 :
compound_pool<64> A;
double* p = A.allocate<double>();

The sketch of the idea is this. compound_pool<N> contains a fixed_size_allocator<N> and derives
from compound_pool<N/2>. So, it can directly honor the allocation requests of N bytes and dispatch all other
tags to base classes. If the last base, compound_pool<0>, takes the call, no better match exists, so it will call
operator new.

More precisely, every class has a pick function that returns either an allocator reference or a pointer.
The call tag is static_value<size_t, N>, where N is the size of the requested memory block.

```c++

template <size_t SIZE>
struct fixed_size_allocator
{
	void* get_block();
};
template <size_t SIZE>
class compound_pool;

template < >
class compound_pool<0>
{
protected:
	template <size_t N>
	void* pick(static_value<size_t, N>){
		return ::operator new(N);
	}
};

template <size_t SIZE>
class compound_pool : compound_pool<SIZE/2>
{
	fixed_size_allocator<SIZE> p_;
protected:
	using compound_pool<SIZE/2>::pick;
	fixed_size_allocator<SIZE>& pick(static_value<SIZE>){
		return p_;
	}
public:
	template <typename object_t>
	object_t* allocate(){
		typedef static_value<size_t, sizeof(object_t)> selector_t;
		return static_cast<object_t*>(get_pointer(this->pick(selector_t())));
	}
private:
	template <size_t N>
	void* get_pointer(fixed_size_allocator<N>& p){
		return p.get_block();
	}
	void* get_pointer(void* p){
		return p;
	}
};
```

---

### ref

- std::type_identity 应该是instance_of 的对应物<https://en.cppreference.com/w/cpp/types/type_identity>
- selector对应的实现应该是 std::integral_constant <https://en.cppreference.com/w/cpp/types/integral_constant>



看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
![微信转账](https://wanghenshui.github.io/assets/wepay.png)
</details>