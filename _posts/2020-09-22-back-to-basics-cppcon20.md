---
layout: post
title: (cppcon2020) back to basics
categories: [c++]
tags: [type, cppcon ,cppcon2020]
---


# Algebraic Data Types

指 pair tuple (product type)(结构体) optional variant(sum type) (有index信息)

 `std::any`不行，有类型擦除，丢信息了

**pair tuple 多种信息**

- std::in_place/std::piecewise_construct
- forward_as_tuple
- std::tie
  - 用std::tie来实现比较
- 结构化绑定
- 公共接口还是定义一个类/结构体吧，丢失了名字信息，很可惜

**optional，优雅，不浪费堆空间**

**optional 默认值, 没有值 对于指针场景，没有堆使用。优雅**

```c++
std::unique_ptr<ComplicatedObject> obj_ = nullptr;
void setComplicated(int a, int b) {
	obj_ = std::make_unique<ComplicatedObject>(a, b);
}

std::optional<ComplicatedObject> obj_ = std::nullopt;
void setComplicated(int a, int b) {
	obj_.emplace(a, b);
}
```

- std::optional<int\> o = std::nullopt
- value_or方法，非常优雅，省一个if
  - 必须是constexpr的，不然or不了
- Setter, 用(std::optional<T>) const std::optional<T\>&会拿到个临时对象？

**variant 优雅的union**

index方法 返回下表

`std::get`可以 通过index和类型来访问 类似的`std::get_if`

`std::visit`

**poor man’s Expected<T\>.**

```c++
std::variant<std::string, std::errc> vGetenv(const char *name);
if (auto v = vGetenv("foo"); std::get_if<std::string>(&v)) {
	const auto& value = std::get<std::string>(v);
	std::cout << "Value is: " << value << "\n";
} else {
	std::error_condition error = std::get<std::errc>(v);
	std::cout << "Error was: " << error.message() << "\n";
}
```

---

# Class Layout

- 静态变量，非虚成员函数，静态成员函数，类型成员不会影响类的存储布局

- 空基类，[[no_unique_address]]修饰，强制指定不占用空间

  - 空基类优化暂且不提，因为依赖编译器是否做优化。

- 比较，`auto operator <=>(const Flatland &) const = default;`

  - 别默认内存布局memcmp，可能会失败（什么时候会失败？？？？）

- POD，以及pack

  - is_standard_layout_v

  ```c++
  class NarrowLand {
      unsigned char x;       // offset 0
      unsigned long long y;  // offset 8 (still!)
      unsigned long long z;  // offset 16
      friend bool operator ==(NarrowLand const &lhs, NarrowLand const &rhs);
  };
  bool operator ==(NarrowLand const &lhs, NarrowLand const &rhs) {
  	if constexpr (has_unique_object_representations_v<NarrowLand>)
  		return !memcmp(&lhs, &rhs, sizeof(NarrowLand));
  	else
  		return lhs.x == rhs.x && lhs.y == rhs.y && lhs.z == rhs.z;
  }
  ```

- vptr

  - dynamic_cast 开销大 static_cast有偏移

- 介绍了一波实现。太累了。不看了。这段东西看着就头疼



---

# Concurrency

**What is a data race and how do we fix it?**

- The hardware can reorder accesses 指令重排
- ABA
  -  busy-wait aka spinning
  - std::mutex
    - exception-safety？ RAII
- condition_variable for “wait until” 生产消费
  - produce/consume happen only once, consider std::promise/std::future 实际上内部也是mutex+cv

```c++
struct TokenPool {
	std::vector<Token> tokens_;
	std::mutex mtx_;
	std::condition_variable cv_;
	void returnToken(Token t) {
		std::unique_lock lk(mtx_);
		tokens_.push_back(t);
		lk.unlock();//!
		cv_.notify_one();
	}
	Token getToken() {
		std::unique_lock lk(mtx_);
		while (tokens_.empty()) {
			cv_.wait(lk);
		}
		Token t = std::move(tokens_.back());
		tokens_.pop_back();
		return t;
	}
};
```

**Static initialization and once_flag 多线程的初始化**

```c++
class Logger {
	std::mutex mtx_;
	std::optional<NetworkConnection> conn_;
	NetworkConnection& getConn() {
		std::lock_guard<std::mutex> lk(mtx_);
		if (!conn_.has_value()) {
			conn_ = NetworkConnection(defaultHost);
		}
		return *conn_;
	}
};

class Logger {
	std::once_flag once_;
	std::optional<NetworkConnection> conn_;
	NetworkConnection& getConn() {
		std::call_once(once_, []() {
			conn_ = NetworkConnection(defaultHost);
		});
		return *conn_;
	}
};
```

|                           `mutex`                            |               `condition_variable`                |                         `once_flag`                          |
| :----------------------------------------------------------: | :-----------------------------------------------: | :----------------------------------------------------------: |
|       `lock` blocks only if someone “owns” the mutex.        |               `wait` always blocks.               |  `call_once` blocks only if the “done” flag isn’t yet set.   |
|             Many threads can queue up on `lock`.             |       Many threads can queue up on `wait`.        |          Many threads can queue up on `call_once`.           |
| Calling `unlock` unblocks exactly one waiter: the new “owner.” | Calling `notify_one` unblocks exactly one waiter. | Failing at the callback unblocks exactly one waiter: the new “owner.” |
|                                                              |    Calling `notify_all` unblocks all waiters.     | Succeeding at the callback unblocks all waiters and sets the “done” flag. |

**New C++17 and C++20 primitives**

- shared_mutex
- counting_semaphore

```c++
using Sem = std::counting_semaphore<256>;
struct SemReleaser {
	bool operator()(Sem *s) const { s->release(); }
};
class AnonymousTokenPool {
	Sem sem_{100};
	using Token = std::unique_ptr<Sem, SemReleaser>;
	Token borrowToken() {
		sem_.acquire(); // may block
		return Token(&sem_);
	}
};
```

- std::latch
- std::barrier<>

![image-20200923190229383](https://wanghenshui.github.io/assets/image-20200923190229383.png)

**Patterns for sharing data**

- Remember: Protect shared data with a mutex.
  -  You must protect every access, both reads and writes, to avoid UB.
  -  Maybe use a reader-writer lock (std::shared_mutex) for perf.

- Remember: Producer/consumer? Use mutex + condition_variable.

- Best of all, though: Avoid sharing mutable data between threads.
  -  Make the data immutable.
  -  Clone a “working copy” for yourself, mutate that copy, and then quickly “merge” your changes back into the original when you’re done



**In conclusion**

- Unprotected data races are UB
  -  Use std::mutex to protect all accesses (both reads and writes)

- Thread-safe static initialization is your friend
  -  Use std::once_flag only when the initializee is non-static

- mutex + condition_variable are best friends 

- C++20 gives us “counting” primitives like semaphore and latch

- But if your program is fundamentally multithreaded, look for higher-level facilities: promise/future, coroutines, ASIO, TBB

- std::atomic_ref<T\>
- std::jthread

----

# Exceptions

- 异常带来的开销大于错误的影响
  - 解决方案 std::expected<T, E\>

- 异常使得函数难以理解
- 异常依赖动态库
- 异常加大二进制大小
- 什么时候使用/不用异常
  - 不经常发生的错误 
    - 经常出错，出错属于正常场景，别用
  - 异常不能处理的场景
    - IO错误
  - 构造函数等等不应该出错的场景
    - 引用空指针，越界等等应该保证不出错
- 异常安全保证
  - - All functions should at least provide the basic exception safety guarantee, if possible and reasonable the strong guarantee.
    - Consider the no-throw guarantee, but only provide it if you can guarantee it even for possible future changes.
  - 基本的异常安全保证
    - 没有资源泄漏
    - Invariants are preserved ？
  - 强异常安全保证
    - Invariants are preserved
    - 没有资源泄漏
    - 状态未改变 commit-or-rollback
  - 不抛异常
    - 操作不能失败
    - noexcept
- RAII  **RAII*is the single most important idiom of the C++ programming language. Use it!**
-  不能失败
  - 析构函数
    - stack unwinding
    - 失败就terminate了
    - 默认`noexcept`
    - 清理必须安全
  - move 操作符
    - Core Guideline C.66: Make move operations noexcept
  - swap操作符，由基本的操作实现，不会失败

---

# Lambda Expressions

c++20

```c++
[capture clause] <template parameters\> (parameter list)
specifier exception attribute -> return type requires { body }
```

- specifier
  - mutable
  - constexpr（能推导出来，所以这个非必须）
  - consteval
- exception
  - noexcept
  - throw 别用
- requires 
  - capture clause
  - template parameters
  -  arguments passed in the parameter list
  -  anything which can be checked at compile time

- capture std::unique_ptr

```c++
std::unique_ptr<Widget> myPtr = std::make_unique<Widget>();
auto myLamb = [ capturedPtr = std::move(myPtr) ] ( )
{ return capturedPtr->computeSize(); };
```

---

# Move Semantics

再谈右值

- No rvalue reference as function return type

```c++
int&& func() { return 42; }
void test() {
	int a = func();//返回之前已经销毁
}
```

std::move

```c++
template <class T>
constexpr remove_reference_t<T>&& move(T&& t) noexcept
{
	return static_cast<remove_reference_t<T>&&>(t);
}
```

- Next operation after std::move is destruction or assignment move完只能销毁或者重新赋值，其他操作会引入问题
-  Don’t  std::move the return of a local variable 别move返回值

move ctor

- Move constructor / assignment should be explicitly noexcept
- Use t =default when possible
- Moved-from object must be left in a valid state
- Make move assignment safe for self-assignment

```c++
struct S {
	double* data;
	S( S&& other ) noexcept
		: data(std::exchange(other.data, nullptr))
	{ }
    
    S& operator=( S&& other ) noexcept {
        if (this == &other) return *this;
		
        delete[] data;
		data = std::exchange(other.data, nullptr);
		return *this;
	}
};
```



完美转发

```c++
template <class T> void f(T&& value)
{
	g(std::forward<T>(value));
}
```

有些类型只能move不能copy

---

# Smart Pointers

- std::unique_ptr
  - 没有copy语义
  - 比raw pointer无劣势
  - 定制deleter（需要可见）
  - 数组的特化std::unique_ptr<T[]>
  - std::make_unique 要比std::unique_ptr构造要快

- std::shared_ptr
  - 有count原子计数。有消耗
    - 本身线程安全但是不保证引用的资源是线程安全
  - 定制deleter
  - std::make_shared 要比std::shared_ptr构造要快
  - std::shared_ptr\<void>
    -  https://www.cnblogs.com/imjustice/p/how_shared_ptr_void_works.html
    - https://stackoverflow.com/questions/5913396/why-do-stdshared-ptrvoid-work
- std::weak_ptr
  - 借，生成shared_ptr

使用建议，最好别用share or

-  std::atomic_shared_ptr/std::atomic_weak_ptr -> std::atomic\<std::shared_ptr<T\>> std::atomic\<std::weak_ptr<T\>>

---

# C++ Templates

- c++17引入CTAD 没啥说的

- using

```c++
template<size_t N>
using CharArray = std::array<char, N>;
```

- std::array受限于NTTP这种参数难受，不如std::span

- 变参模板

- SFINAE
  - 其他套路
    - tag dispatch
    - if constexpr
  - c++20 用concept代替

---

# Abstract Machines/The Structure of a Program

讲了一遍编译原理

- ODR 

- ABI

- name-mangling 

- 变量存储在哪
  - 注意static和thread_local

---

### ref

- https://github.com/CppCon/CppCon2020/blob/main/Presentations/back_to_basics_algebraic_data_types/back_to_basics_algebraic_data_types__arthur_odwyer__cppcon_2020.pdf
- https://github.com/CppCon/CppCon2020/blob/main/Presentations/back_to_basics_class_layout/back_to_basics_class_layout__steve_dewhurst__cppcon_2020.pdf
- https://github.com/CppCon/CppCon2020/blob/main/Presentations/back_to_basics_concurrency/back_to_basics_concurrency__arthur_odwyer__cppcon_2020.pdf
- https://github.com/CppCon/CppCon2020/blob/main/Presentations/back_to_basics_exceptions/back_to_basics_exceptions__klaus_iglberger__cppcon_2020.pdf
- https://github.com/CppCon/CppCon2020/blob/main/Presentations/back_to_basics_lambda_expressions/back_to_basics_lambda_expressions__barbara_geller__ansel_sermersheim__cppcon_2020.pdf
- https://github.com/CppCon/CppCon2020/blob/main/Presentations/back_to_basics_move_semantics/back_to_basics_move_semantics__david_olsen__cppcon_2020.pdf
  - Nicolai M. Josuttis, C++ Move Semantics: The Complete Guide,http://www.cppmove.com/
  - C++ Core Guidelineshttps://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines.html
  - Nicolai Josuttis, “The Hidden Secrets of Move Semantics”, CppCon 2020
  - Nicolai Josuttis, “The Nightmare of Move Semantics for Trivial Classes”, CppCon 2017 https://www.youtube.com/watch?v=PNRju6_yn3o
- https://github.com/CppCon/CppCon2020/blob/main/Presentations/back_to_basics_smart_pointers/back_to_basics_smart_pointers__rainer_grimm__cppcon_2020.pdf
- https://github.com/CppCon/CppCon2020/blob/main/Presentations/back_to_basics_templates_part_1/back_to_basics_templates_part_1__andreas_fertig__cppcon_2020.pdf
- https://github.com/CppCon/CppCon2020/blob/main/Presentations/back_to_basics_templates_part_2/back_to_basics_templates_part_2__andreas_fertig__cppcon_2020.pdf
- https://github.com/CppCon/CppCon2020/blob/main/Presentations/back_to_basics_the_abstract_machine/back_to_basics_the_abstract_machine__bob_steagall__cppcon_2020.pdf
- https://github.com/CppCon/CppCon2020/blob/main/Presentations/back_to_basics_the_structure_of_a_program/back_to_basics_the_structure_of_a_program__bob_steagall__cppcon_2020.pdf

---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>