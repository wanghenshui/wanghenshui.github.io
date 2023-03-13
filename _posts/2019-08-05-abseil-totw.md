---
layout: post
categories: language
title: Abseil Tip of the Week
tags: [c++]
---

  

本文是Abseil库 tip of the week的总结。不是翻译，有些点子还是不错的。

---

##### totw #1 string_view

厌烦了const char*到string之间的处理转换？你只是想用一下而已不需要构造一个拷贝？string_view就是为此而生的，它是一个视图，就是一个借用，也是类似go rust胖指针 slice之类的东西。内部有一个指针和一个长度

注意，string_view是没有\0的

##### totw #3 String Concatenation and operator+ vs. StrCat()

简单说，不要用string::operator +() 会有临时变量。absl::StrCat用来解决这个问题

##### totw #10 Splitting Strings, not Hairs

absl提供了string split相关函数

```c++
// Splits on commas. Stores in vector of string_view (no copies).
std::vector<absl::string_view> v = absl::StrSplit("a,b,c", ',');

// Splits on commas. Stores in vector of string (data copied once).
std::vector<std::string> v = absl::StrSplit("a,b,c", ',');

// Splits on literal string "=>" (not either of "=" or ">")
std::vector<absl::string_view> v = absl::StrSplit("a=>b=>c", "=>");

// Splits on any of the given characters (',' or ';')
using absl::ByAnyChar;
std::vector<std::string> v = absl::StrSplit("a,b;c", ByAnyChar(",;"));

// Stores in various containers (also works w/ absl::string_view)
std::set<std::string> s = absl::StrSplit("a,b,c", ',');
std::multiset<std::string> s = absl::StrSplit("a,b,c", ',');
std::list<std::string> li = absl::StrSplit("a,b,c", ',');

// Equiv. to the mythical SplitStringViewToDequeOfStringAllowEmpty()
std::deque<std::string> d = absl::StrSplit("a,b,c", ',');

// Yields "a"->"1", "b"->"2", "c"->"3"
std::map<std::string, std::string> m = absl::StrSplit("a,1,b,2,c,3", ',');
```

要是c++有python那种split就好了。（那种效率比较低）

##### totw #11 RVO  返回值优化。返回局部变量不必考虑多余的拷贝构造等。现代编译器默认功能

##### totw #42: Prefer Factory Functions to Initializer Methods

google是禁止使用异常的。如果初始化会失败，那就用工厂函数来搞，大概这样

```c++
class Foo {
 public:
  // Factory method: creates and returns a Foo.
  // May return null on failure.
  static std::unique_ptr<Foo> Create();

  // Foo is not copyable.
  Foo(const Foo&) = delete;
  Foo& operator=(const Foo&) = delete;

 private:
  // Clients can't invoke the constructor directly.
  Foo();
};

std::unique_ptr<Foo> Foo::Create() {
  // Note that since Foo's constructor is private, we have to use new.
  return absl::WrapUnique(new Foo());
}
```

这里注意，std::unique_ptr不能访问private构造函数，所以absl提供了一个wrapunique的一个wrapper

##### totw #45 不要用全局变量，尤其是库代码

（只能说尽量啦）

##### totw #88: Initialization: =, (), and {}

总结好了

- 简单的构造逻辑，直接用`=`初始化基本类型（结合`{}`），结构体，以及拷贝构造

  ```c++
  int x = 2;
  std::string foo = "Hello World";
  std::vector<int> v = {1, 2, 3};
  std::unique_ptr<Matrix> matrix = NewMatrix(rows, cols);
  MyStruct x = {true, 5.0};
  MyProto copied_proto = original_proto;

  // Bad code
  int x{2};
  std::string foo{"Hello World"};
  std::vector<int> v{1, 2, 3};
  std::unique_ptr<Matrix> matrix{NewMatrix(rows, cols)};
  MyStruct x{true, 5.0};
  MyProto copied_proto{original_proto};
  ```

- 用传统的构造函数语义`()`来调用复杂的构造语义

  ```c++
  Frobber frobber(size, &bazzer_to_duplicate);
  std::vector<double> fifty_pies(50, 3.14);
  // Bad code 
  // Could invoke an intializer list constructor, or a two-argument   constructor.
  Frobber frobber{size, &bazzer_to_duplicate};

  // Makes a vector of two doubles.
  std::vector<double> fifty_pies{50, 3.14};
  ```

- 用`{}`不用`=`这种场景, 只用在上面这两种场景不能编译的情况下

  ```c++
  class Foo {
   public:
    Foo(int a, int b, int c) : array_{a, b, c} {}
  
   private:
    int array_[5];
    // Requires {}s because the constructor is marked explicit
    // and the type is non-copyable.
    EventManager em{EventManager::Options()};
  };
  ```

- `{}` 和`auto`不要混用

  ```c++
  // Bad code
  auto x{1};
  auto y = {2}; // This is a std::initializer_list<int>!
  ```



##### totw #93: using absl::Span 也就是std::span ，container_view，更好用。也可以理解成flat pointer

##### totw #117: Copy Elision and Pass-by-value

就是一种吃掉拷贝的优化

```c++
// First constructor version
explicit Widget(const std::string& name) : name_(name) {}

// Second constructor version
explicit Widget(std::string name) : name_(std::move(name)) {}
```

##### totw #120: Return Values are Untouchable

```c++
MyStatus DoSomething() {
  MyStatus status;
  auto log_on_error = RunWhenOutOfScope([&status] {
    if (!status.ok()) LOG(ERROR) << status;
  });
  status = DoA();
  if (!status.ok()) return status;
  status = DoB();
  if (!status.ok()) return status;
  status = DoC();
  if (!status.ok()) return status;
  return status;
}
```

这段代码是有问题的，`lambda`中访问的`status`是在`return`执行完之后才会析构访问的，但是鉴于返回值优化，`return`没有执行，勉强正确，如果最后一行换成`return MyStatus();` 这个`lambda`将永远错误的`status`，行为是未定义的 ，可能是错误的逻辑

解决办法，不用这种`RAII`访问返回值

##### totw #123: `absl::optional` and `std::unique_ptr`

这个表概括的很好了，absl::optional就是std::optional的替代版

|                                 | `Bar`                   | `absl::optional<Bar>`                                        | `std::unique_ptr<Bar>`                                       |
| :------------------------------ | :---------------------- | :----------------------------------------------------------- | ------------------------------------------------------------ |
| Supports delayed construction   |                         | ✓                                                            | ✓                                                            |
| Always safe to access           | ✓                       |                                                              |                                                              |
| Can transfer ownership of `Bar` |                         |                                                              | ✓                                                            |
| Can store subclasses of `Bar`   |                         |                                                              | ✓                                                            |
| Movable                         | If `Bar` is movable     | If `Bar` is movable                                          | ✓                                                            |
| Copyable                        | If `Bar` is copyable    | If `Bar` is copyable                                         |                                                              |
| Friendly to CPU caches          | ✓                       | ✓                                                            |                                                              |
| No heap allocation overhead     | ✓                       | ✓                                                            |                                                              |
| Memory usage                    | `sizeof(Bar)`           | `sizeof(Bar) + sizeof(bool)`[2](https://abseil.io/tips/123#fn:padding) | `sizeof(Bar*)` when null, `sizeof(Bar*) + sizeof(Bar)` otherwise |
| Object lifetime                 | Same as enclosing scope | Restricted to enclosing scope                                | Unrestricted                                                 |
| Call `f(Bar*)`                  | `f(&val_)`              | `f(&opt_.value())` or `f(&*opt_)`                            | `f(ptr_.get())` or `f(&*ptr_)`                               |
| Remove value                    | N/A                     | `opt_.reset();` or `opt_ = absl::nullopt;`                   | `ptr_.reset();` or `ptr_ = nullptr;`                         |

##### totw#126: `make_unique` is the new `new`

###### How Should We Choose Which to Use?

1. By default, use `absl::make_unique()` (or `std::make_shared()` for the rare cases where shared ownership is appropriate) for dynamic allocation. For example, instead of: `std::unique_ptr<T> bar(new T());` write `auto bar = absl::make_unique<T>();` and instead of `bar.reset(new T());` write `bar = absl::make_unique<T>();`
2. In a factory function that uses a non-public constructor, return a `std::unique_ptr<T>` and use `absl::WrapUnique(new T(...))` in the implementation.
3. When dynamically allocating an object that requires brace initialization (typically a struct, an array, or a container), use `absl::WrapUnique(new T{...})`.
4. When calling a legacy API that accepts ownership via a `T*`, either allocate the object in advance with `absl::make_unique` and call `ptr.release()` in the call, or use `new` directly in the function argument.
5. When calling a legacy API that returns ownership via a `T*`, immediately construct a smart pointer with `WrapUnique` (unless you’re immediately passing the pointer to another legacy API that accepts ownership via a `T*`).

###### Summary

Prefer `absl::make_unique()` over `absl::WrapUnique()`, and prefer `absl::WrapUnique()` over raw `new`.

##### totw #131: Special Member Functions and `= default`

Prefer `=default` over writing an equivalent implementation by hand, even if that implementation is just `{}`

##### totw#134: make_unique and private constructors

和42条一样场景，make_unique不能直接创建private 构造函数，几个办法

声明成友元函数，或者用个wrapunique，或者替换成shared_ptr

##### totw #141: Beware Implicit Conversions to bool

bool转换的问题。属于老生常谈了。特定类型就需要实现safe bool，一般类型用`option<T>`包装一层 `absl::optional<T>::has_value()`判断

**Tote #144** : Heterogeneous Lookup in Associative Containers

看代码

```c++
struct StringCmp {
  using is_transparent = void;
  bool operator()(absl::string_view a, absl::string_view b) const {
    return a < b;
  }
};

std::map<std::string, int, StringCmp> m = ...;
absl::string_view some_key = ...;
// The comparator `StringCmp` will accept any type that is implicitly
// convertible to `absl::string_view` and says so by declaring the
// `is_transparent` tag.
// We can pass `some_key` to `find()` without converting it first to
// `std::string`. In this case, that avoids the unnecessary memory allocation
// required to construct the `std::string` instance.
auto it = m.find(some_key);
```

省一个拷贝

再比如

```c++
struct ThreadCmp {
  using is_transparent = void;
  // Regular overload.
  bool operator()(const std::thread& a, const std::thread& b) const {
    return a.get_id() < b.get_id();
  }
  // Transparent overloads
  bool operator()(const std::thread& a, std::thread::id b) const {
    return a.get_id() < b;
  }
  bool operator()(std::thread::id a, const std::thread& b) const {
    return a < b.get_id();
  }
  bool operator()(std::thread::id a, std::thread::id b) const {
    return a < b;
  }
};

std::set<std::thread, ThreadCmp> threads = ...;
// Can't construct an instance of `std::thread` with the same id, just to do the lookup.
// But we can look up by id instead.
std::thread::id id = ...;
auto it = threads.find(id);
```



##### totw #149 Object Lifetimes vs. `=delete`

不只是构造函数析构函数可以标记为delete，普通成员函数也可以标记delete。这就引入了复杂性问题，是让类更完备还是更复杂

###### `=delete` for Lifetimes

假如你标记为delete就是为了限制参数的生存周期

```c++
class Request {
  ...

  // The provided Context must live as long as the current Request.
  void SetContext(const Context& context);
  void SetContext(Context&& context) = delete;
```

但是报错并不能告诉你正确的做法，只会告诉你因为什么错了

```shell
error: call to deleted function 'SetContext'

  SetContext(Context{});
  ^~~~~~~~~~

<source>:4:6: note: candidate function has been explicitly deleted

void SetContext(Context&& context) = delete;
```



你看了看报错，决定改一下，但是为什么这样改，不知道

这种设计会避免bug，但是也需要完善注释，不然不知所以

要是编译时报错能够定制错误信息，就牛逼了。

###### `=delete` for “Optimization”

这个场景是上面的反面，假如只接受右值，不接受拷贝，这样所有调用的时候都得显式加上std::move，显然更麻烦

这样做实际上是复杂化了，totw不建议使用，keep it simple



**Tip of the Week #152** : `AbslHashValue` and You

把内部用的hash算法暴露出来了，可以这么用

```c++
struct Song {
  std::string name;
  std::string artist;
  absl::Duration duration;

  template <typename H>
  friend H AbslHashValue(H h, const Song& s) {
    return H::combine(std::move(h), s.name, s.artist, s.duration);
  }

  // operator == and != omitted for brevity.
};
```

**Tip of the Week #161**: Good Locals and Bad Locals

Good

```c++
auto& subsubmessage = *myproto.mutable_submessage()->mutable_subsubmessage();
subsubmessage.set_foo(21);
subsubmessage.set_bar(42);
subsubmessage.set_baz(63);
```

Bad

```c++
MyType value = SomeExpression(args);
return value;
```

**Tip of the Week #171**: Avoid Sentinel Values

返回值不清晰，建议用optional或者status

**Tip of the Week #173**: Wrapping Arguments in Option Structs

多参数构造抽象成option，不然难维护，构造指定不合理

**Tip of the Week #175**: Changes to Literal Constants in C++14 and C++17.

尽可能用1'000'000'000

以及chrono的ms min

**Tip of the Week #176**: Prefer Return Values to Output Parameters

尽可能用返回值。如果出参需要非常灵活，返回值控制不了，就用出参

**Tip of the Week #181**: Accessing the value of a `StatusOr<T>`

就是rocksdb status那种东西

```c++
// The same pattern used when handling a unique_ptr...
std::unique_ptr<Foo> foo = TryAllocateFoo();
if (foo != nullptr) {
  foo->DoBar();  // use the value object
}

// ...or an optional value...
absl::optional<Foo> foo = MaybeFindFoo();
if (foo.has_value()) {
  foo->DoBar();
}

// ...is also ideal for handling a StatusOr.
absl::StatusOr<Foo> foo = TryCreateFoo();
if (foo.ok()) {
  foo->DoBar();
}
```

表达能力比option和expect要好一些



此外，abseil还支持解析参数，支持gflags，可以说是把gflags迁移到这个库了，header only更友好一些

----

### ref

1. https://abseil.io/tips/



