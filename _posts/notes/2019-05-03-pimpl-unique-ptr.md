---
layout: post
category: cpp
title: unique_ptr实现pimpl惯用法
tags: [gcc, c++]

---

{% include JB/setup %}

---

### why

这篇文章是参考链接的总结

----

pimpl惯用法，pointer to implementation，就是用指针来拆分实现，这样改动不会导致所有文件都编译一遍，也是一种解耦

以前的实现

```c++
#include "Engine.h"
 
class Fridge
{
public:
   void coolDown();
private:
   Engine engine_;
};
```

 这样改动Engine就会重编Fridge

引入指针分离

```c++
class Fridge
{
public:
   Fridge();
   ~Fridge();
 
   void coolDown();
private:
   class FridgeImpl;
   FridgeImpl* impl_;
};
```

FridgeImpl封装一层Engine，不可见

```c++
#include "Engine.h"
#include "Fridge.h"
 
class FridgeImpl
{
public:
   void coolDown()
   {
      /* ... */
   }
private:
   Engine engine_;
};
 
Fridge::Fridge() : impl_(new FridgeImpl) {}
 
Fridge::~Fridge(){
   delete impl_;
}
 
void Fridge::coolDown(){
   impl_->coolDown();
}
```

这样还是需要管理impl_生命周期，如果用unique_ptr就更好了

改进的代码

```c++
#include <memory>
 
class Fridge
{
public:
   Fridge();
   void coolDown();
private:
   class FridgeImpl;
   std::unique_ptr<FridgeImpl> impl_;
};
```

```c++
#include "Engine.h"
#include "Fridge.h"

class FridgeImpl
{
public:
   void coolDown()
   {
      /* ... */
   }
private:
   Engine engine_;
};

Fridge::Fridge() : impl_(new FridgeImpl) {}
```

这样会有新问题，编译不过

>use of undefined type 'FridgeImpl'
>can't delete an incomplete type

因为unique_ptr需要知道托管对象的析构，最起码要保证可见性

`析构可见性`

c++规则，以下两种情况，delete pointer会有未定义行为

- void* 类型
- 指针的类型不完整，比如这种前向声明类指针

由于unique_ptr检查，会在编译期直接拒绝 同理的还有boost::checked_delete



进一步讨论，Fridge 和FridgeImpl的析构函数都是没定义的，编译器会自动定义并内联，在Fridge的编译单元，就已经见到了Fridge的析构了，但是见不到FridgeImpl的析构，解决办法就是加上Fridge的析构声明，并把实现放到实现文件中，让Fridge和FridgeImpl的析构同时可见

```c++
#include <memory>
 
class Fridge
{
public:
   Fridge();
   +~Fridge();
...
};
```



```c++
#include "Engine.h"
#include "Fridge.h"
 
class FridgeImpl
....
Fridge::Fridge() : impl_(new FridgeImpl) {}
 
+Fridge::~Fridge() = default;
```



### ref

- [How to implement the pimpl idiom by using unique_ptr](https://www.fluentcpp.com/2017/09/22/make-pimpl-using-unique_ptr/)
- <https://www.boost.org/doc/libs/1_64_0/libs/core/doc/html/core/checked_delete.html#core.checked_delete.checked_delete>
- 这条也是effective modern c++提到的一条 <https://blog.csdn.net/big_yellow_duck/article/details/52351729>

### contact

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。