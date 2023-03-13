---
layout: post
categories: language
title: 使用gsl::not_null封装raw pointer
tags: [gcc, c++]

---

  

---

### why

这篇文章是参考链接的总结，主要是讲替代原生指针，使用not_null封装

----

如果是原生指针，就会有很多if

```cpp
if (pMyData)
    pMyData->Process();
```

or:

```cpp
auto result = pObj ? pObj->Compute() : InvalidVal;
```

or

```cpp
void Foo(Object* pObj)
{
    if (!pObj)
        return;

    // Do stuff...
}
```



多余的if判断,使代码复杂等等等等



一个使用not_null的例子

```c++
// { autofold
// not_null playground
// bfilipek.com


#include <iostream>
#include <string_view>
#include <string>
#include <memory>
// }

#include "gsl/gsl"

// { autofold
class App
{
public:
	App(const std::string& str) : m_name(str) { }

	void Run() { std::cout << "Running " << m_name << "\n"; }
	void Shutdown() { std::cout << "App " << m_name << " is closing...\n"; }
	void Diagnose() { std::cout << "Diagnosing...\n"; }

private:
	std::string m_name;
};
// }


void RunApp(gsl::not_null<App *> pApp)
{
	pApp->Run();
	pApp->Shutdown();
}

void DiagnoseApp(gsl::not_null<App *> pApp)
{
	pApp->Diagnose();
}

int main()
{
    // first case: deleting and marking as null:
	{
		gsl::not_null<App *> myApp = new App("Poker");

		// we can delete it, but cannot assign null
		delete myApp;
		//myApp = nullptr;
	}

    // second case: breaking the contract
	{
		// cannot invoke such function, contract violation
		//RunApp(nullptr);
	}

    // assigning a null on initilization
	{
		//gsl::not_null<App *> myApp = nullptr;
	}
	
	std::cout << "Finished...\n";
}
```

接口语义保证不会null，更清晰，并且编译期就能确保不是null



另外，参考链接二提到，既然有not_null，就应该有optional_ptr, 保证默认null，这个实际上也是observer_ptr的加强版，observer_ptr是对原生ptr的封装，也是通过一个接口语义来清晰`观测`或者对应`rust` 的 `borrow`





### 拓展阅读

在not_null的实现里，get指针是这样的

```c++
    template <typename U, typename = std::enable_if_t<std::is_convertible<U, T>::value>>
    constexpr not_null(U&& u) : ptr_(std::forward<U>(u))
    {
        Expects(ptr_ != nullptr);
    }

    template <typename = std::enable_if_t<!std::is_same<std::nullptr_t, T>::value>>
    constexpr not_null(T u) : ptr_(std::move(u))
    {
        Expects(ptr_ != nullptr);
    }

    constexpr std::conditional_t<std::is_copy_constructible<T>::value, T, const T&> get() const
    {
        Ensures(ptr_ != nullptr);
        return ptr_;
    }
```



其中expects和ensures定义是这样的

```c++
#if defined(__clang__) || defined(__GNUC__)
#define GSL_LIKELY(x) __builtin_expect(!!(x), 1)
#define GSL_UNLIKELY(x) __builtin_expect(!!(x), 0)

#else

#define GSL_LIKELY(x) (!!(x))
#define GSL_UNLIKELY(x) (!!(x))
#endif // defined(__clang__) || defined(__GNUC__)

#define GSL_CONTRACT_CHECK(type, cond)                                                             \
    (GSL_LIKELY(cond) ? static_cast<void>(0) : gsl::details::terminate())

#define Expects(cond) GSL_CONTRACT_CHECK("Precondition", cond)
#define Ensures(cond) GSL_CONTRACT_CHECK("Postcondition", cond)
```



为啥get需要Ensures校验？本身都非空了，这样不是多此一举吗？

考虑只能指针的move，比如gsl::not_null\<unique_ptr\<T> >发生了move行为，那旧的not_null就是是空指针了

这里是为了留这么一手 至于运行时的消耗，就让编译期优化吧，编译器能判定出来分支走到static_cast\<void>(0) 整个分支都没有任何作用，应该就会优化掉



### ref

- <https://www.bfilipek.com/2017/10/notnull.html>
- 讲optional_ptr，顺便给了个实现 <https://a4z.bitbucket.io/blog/2017/03/02/Adding-optional_ptr-to-my-toolbox.html> 
- GSL中not_null的实现<https://github.com/microsoft/GSL/blob/6418b5f4de2204cd5a335b00d2f8754301b8b382/include/gsl/pointers>
- 这条也是cpp core guidelines 推荐的用法，GSL库也是为此而生的 <https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#Ri-nullptr>
- 关于get里的Ensures SO上的讨论https://stackoverflow.com/questions/51157916/why-gslnot-null-ensures-ptr-is-not-null-on-get
- 关于get里的Ensures  gsl作者们的讨论https://github.com/Microsoft/GSL/pull/449

### contact

