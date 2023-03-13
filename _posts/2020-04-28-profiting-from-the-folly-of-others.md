---
layout: post
title: (译)讨论folly的静态注入技术:如何不改接口合法的访问私有成员函数？
categories: [language, translation]
tags: [c++, folly]
---


>  [原文链接](https://accu.org/journals/overload/28/156/harrison%5F2776/)

这段代码是研究 folly发现的 源代码在[这里](https://github.com/facebook/folly/blob/f63a5c31680aaabcc0f9c86709fd4a813db292ce/folly/memory/UninitializedMemoryHacks.h)

前提: 方法

```c++
class Widget {
private:
  void forbidden();
};
```

访问

```c++
void hijack(Widget& w) {
  w.forbidden();  // ERROR!
}
```

```shell
  In function 'void hijack(Widget&)':
  error: 'void Widget::forbidden()' is private
  within this context
        |     w.forbidden();
        |   
```



解决思路

### 类函数可以通过指针来调用！

比如

```c++
class Calculator {
  float current_val = 0.f;
 public:
   void clear_value() { current_val = 0.f; };
   float value() const {
     return current_val;
   };

   void add(float x) { current_val += x; };
   void multiply(float x) { current_val *= x; };
};

using Operation = void (Calculator::*)(float);
Operation op1 = &Calculator::add;
Operation op2 = &Calculator::multiply;
Calculator calc{};
(calc.*op1)(123.0f); // Calls add
(calc.*op2)(10.0f);  // Calls multiply
```



### 私有的函数通过公有函数传指针，绕过

```c++
class Widget {
 public:
  static auto forbidden_fun() {
    return &Widget::forbidden;
  }
 private:
  void forbidden();
};

void hijack(Widget& w) {
  using ForbiddenFun = void (Widget::*)();
  ForbiddenFun const forbidden_fun = Widget::forbidden_fun();

  // Calls a private member function on the Widget
  // instance passed in to the function.
  (w.*forbidden_fun)();
}
```

但是一般函数是不会这么设计API的，太傻逼了，那怎么搞？

### 通过模版实例化绕过！

>  The C++17 standard contains the following paragraph (with the parts of interest to us marked in bold):
>
>    **17.7.2 (item 12)** 
>
>    **The usual access checking rules do not apply to names used to specify explicit instantiations.**  [Note: In particular, the template arguments and names used in the  function declarator (including parameter types, return types and  exception specifications)   **may be private types**  or objects which would normally not be accessible and the template may  be a member template or member function which would not normally be  accessible.]

重点 显式实例化

### 最终方案敲定： 私有成员函数指针做模版的非类型模版参数(NTTP)

```c++
// The first template parameter is the type
// signature of the pointer-to-member-function.
// The second template parameter is the pointer
// itself.
template <
  typename ForbiddenFun,
  ForbiddenFun forbidden_fun
>
struct HijackImpl {
  static void apply(Widget& w) {
    // Calls a private method of Widget
    (w.*forbidden_fun)();
  }
};

// Explicit instantiation is allowed to refer to
// `Widget::forbidden` in a scope where it's not
// normally permissible.
template struct HijackImpl<
  decltype(&Widget::forbidden),
  &Widget::forbidden
>;

void hijack(Widget& w) {
  HijackImpl<decltype(&Widget::forbidden), &Widget::forbidden>::apply(w);
}
```

但是还是报错，理论上可行，但实际上还是会提示私有，原因在于HijackImpl不是`显式实例化`

### freind封装一层调用 + 显式实例化

```c++
// HijackImpl is the mechanism for injecting the
// private member function pointer into the
// hijack function.
template <
  typename ForbiddenFun,
  ForbiddenFun forbidden_fun
>
class HijackImpl {
  // Definition of free function inside the class
  // template to give it access to the
  // forbidden_fun template argument.
  // Marking hijack as a friend prevents it from
  // becoming a member function.
  friend void hijack(Widget& w) {
    (w.*forbidden_fun)();
  }
};
// Declaration in the enclosing namespace to make
// hijack available for name lookup.
void hijack(Widget& w);

// Explicit instantiation of HijackImpl template
// bypasses access controls in the Widget class.
template class
HijackImpl<
  decltype(&Widget::forbidden),
  &Widget::forbidden
>;
```



总结这几条

- 通过显式模版实例化把私有成员函数暴露出来
- 用成员函数的地址指针作为HijackImpl的模版参数
- 定义hijack函数在HijackImpl内部，直接用私有成员函数指针做函数调用
- 通过freind修饰来hijack，这样hijack就可以在外面调用里面的HijackImpl
- 显式实例化，这样调用就可以了

还有一个最终的问题，实现和实例化都在头文件，在所有的编译单元(translation units, TU)里, 显式实例化只能是一个，否则会报mutiple 链接错误，如何保证？

folly的做法，加个匿名tag，这样每个TU的符号名都不一样，最终方案如下



```c++
namespace {
// This is a *different* type in every translation
// unit because of the anonymous namespace.
struct TranslationUnitTag {};
}

void hijack(Widget& w);

template <
  typename Tag,
  typename ForbiddenFun,
  ForbiddenFun forbidden_fun
>
class HijackImpl {
  friend void hijack(Widget& w) {
    (w.*forbidden_fun)();
  }
};

// Every translation unit gets its own unique
// explicit instantiation because of the
// guaranteed-unique tag parameter.
template class HijackImpl<
  TranslationUnitTag,
  decltype(&Widget::forbidden),
  &Widget::forbidden
>;
```



---

### 参考

- The Power of Hidden Friends in C++’ posted 25 June 2019:  https://www.justsoftwaresolutions.co.uk/cplusplus/hidden-friends.html
- Dan Saks ‘Making New Friends’   https://www.youtube.com/watch?v=POa_V15je8Y  ](https://www.youtube.com/watch?v=POa_V15je8Y)
- Johannes Schaub ‘Access to private members. That’s easy!’,http://bloglitb.blogspot.com/2011/12/access-to-private-members-safer.html
-  Johannes Schaub ‘Access to private members: Safer nastiness’, posted 30 December 2011:   http://bloglitb.blogspot.com/2011/12/access-to-private-members-safer.html
- https://dfrib.github.io/a-foliage-of-folly/ 这个文章更进一步，接下来翻译这个

