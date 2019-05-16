---
layout: post
title:  Declarative Control Flow
category: c++
tags: [c++, cppcon]
---
{% include JB/setup %}

这个讲的是scope_exit和栈回溯异常处理问题，用上了std::uncaught_exceptions

```c++
class UncaughtExceptionCounter {
	int getUncaughtExceptionCount() noexcept;
	int exceptionCount_ ;
public:
	UncaughtExceptionCounter()
	: exceptionCount_ (std::uncaught_exceptions()) {
	}
	bool newUncaughtException() noexcept {
		return std::uncaught_exceptions() > exceptionCount _ ;
	}
};

template <typename FunctionType, bool executeOnException>
class ScopeGuardForNewException {
	FunctionType function_ ;
	UncaughtExceptionCounter ec_ ;
public:
	explicit ScopeGuardForNewException(const FunctionType& fn)
	: function_ (fn) {}
	explicit ScopeGuardForNewException(FunctionType&& fn)
	: function_ (std::move(fn)) {}
	~ScopeGuardForNewException() noexcept(executeOnException) {
		if (executeOnException == ec_.isNewUncaughtException()) {
			function_ ();
		}
	}
};

enum class ScopeGuardOnFail {};

template <typename FunctionType>
ScopeGuardForNewException<typename std::decay<FunctionType>::type, true>
operator+(detail::ScopeGuardOnFail, FunctionType&& fn) {
	return ScopeGuardForNewException<
		typename std::decay<FunctionType>::type, true>(
			std::forward<FunctionType>(fn));
}

#define SCOPE_FAIL \
	auto ANONYMOUS_VARIABLE(SCOPE_ FAIL_STATE) \
		= ::detail::ScopeGuardOnFail() + [&]() noexcept
```



我的疑问，直接用scope_exit不行吗，貌似这个捕获了其他异常也会执行functor，不局限于本身的fail

需求不太一样



### ref

- https://github.com/CppCon/CppCon2015/tree/master/Presentations/Declarative%20Control%20Flow
- <https://isocpp.org/files/papers/N4152.pdf> 
  - 就是他<https://en.cppreference.com/w/cpp/error/uncaught_exception>
  - 提案中提到的一个实现<https://github.com/evgeny-panasyuk/stack_unwinding>
  - folly scope_exit不列了

看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。