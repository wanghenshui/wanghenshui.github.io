---
layout: post
title: MongoDB中的装饰器模式
category: cpp
tags: c++,mongodb,design pattern
---



实现在util/Decorable.h中 本质是[CRTP](https://en.wikipedia.org/wiki/Curiously_recurring_template_pattern)的一个使用

子类继承Decorable<T> 就可以了。能保证每个实例在不同的装饰器实例上有不同的表现，完全正交。



## 装饰的原理：

先定义装饰器实例DecorableInstance，“被装饰的类”

通过DecorableInstance::declareDecoration<T>调用获得若干“装饰”实例

用DecorableInstance的生成若干实例，每个Decoration在DecorableInstance的表现都是分开的。

每个组件都是个加强版的单例，可以直接通过declareDecoration<T>()实例来访问，对应每个被装饰的类都不一样



简单示例在util/decorable_test.cpp中

具体在MongoDB中

比如ServiceContext 本身应用了这个装饰

```
class ServiceContext : public Decorable<ServiceContext>// service_context.h
```

通过ServiceContext::declareDecoration来为ServiceContext添加“装饰”组件，简单grep

```
...
mongo/src/mongo/util/net/listen.cpp:const auto getListener = ServiceContext::declareDecoration<Listener*>();
```

直接通过getListener(ser)来访问当前service_context的Listener组件的相关信息。



类似还有许多类是这么实现的

```
mongo/src/mongo/db/client.h:class Client: public Decorable<Client> {
mongo/src/mongo/db/operation_context.h:class OperationContext : public Decorable<OperationContext> {
mongo/src/mongo/db/service_context.h:class ServiceContext : public Decorable<ServiceContext> {
mongo/src/mongo/transport/session.h:class Session : public std::enable_shared_from_this<Session>, public Decorable<Session> {
```





在MongoDB中的 类图



![img](https://pic2.zhimg.com/v2-866bbb71139e696c0f98dae75a750141_b.png)







实现原理

Decorable有DecorationRegistry和DecorationContainer成员

其中

- DecorationRegistry内部持有DecorationInfoVector和totalsize，将数组偏移信息用DecorationDescriptorWithType<T> 抛出来
- DecorationContainer内部持有DecorationRegistry（Decorable的）和一个字符数组，间接通过DecorationContainer来访问DecorationRegistry  
- DecorationContainer构造函数会构造DecorationRegistry中的DecorationInfo对象
- 字符数组就当一块内存使用，连续排放各种装饰对象实例T，placement new
- 每个DecorationInfo会记录自己的index，index是std::alignment_of<T>::value算出来的。



- DecorationDescriptorWithType<T>是DecorationDescriptor的封装，DecorationDescriptor内部就记录一个index，通过调用一层一层的把index抛出来



调用declareDecoration会间接调用DecorationRegistry->declareDecoration，底层调用栈是DecorationContainer构造 ->返回DecorationDescriptor -> 返回DecorationDescriptorWithType<T> ->返回到Decoration

当使用declareDecoration生成的实例的时候，实际上调用的是T& Decoration::operator(),

该函数会调用把Decorable内部的DecorationContainer传进去，结合该Decoration自身记录的index来定位到具体的DecorationInfo的T



挺复杂的。没能理解为啥实现的这么复杂



## PS1: CRTP常见用法

singleton

```
template <class T>

class singleton{

public:

singleton()=delete;

static void release(){  delete p;   p=nullptr;}

static T* get(){

    if (!p)p=   new T();    

    return p;

}

static T * p;

};
```

然后单例类就继承singleton<T>就可以了

还有比较常见的是std::enable_shared_from_this 

[其他用法见WIKI](https://en.wikipedia.org/wiki/Curiously_recurring_template_pattern)



## PS2: plantUML

```
@startuml
class Decorable {
 -_decorations:DecorationContainer 

 ~static DecorationRegistry* getRegistry()
 +static Decoration<T> declareDecoration()
}


class Decoration{
 -_raw:DecorationContainer::DecorationDescriptorWithType<T>
 +explicit Decoration(DecorationContainer::DecorationDescriptorWithType<T> raw)
 +T&:operator()
}

class DecorationRegistry{
 -_decorationInfo:std::vector<DecorationInfo>
 -_totalSizeBytes:size_t
 +DecorationContainer::DecorationDescriptorWithType<T> declareDecoration()
 +size_t getDecorationBufferSizeBytes()
 +void construct(DecorationContainer* decorable) const
 +void destruct(DecorationContainer* decorable) const
 ~DecorationContainer::DecorationDescriptor declareDecoration(size_t sizeBytes, 
size_t alignBytes, 
function<void(void*)>constructor, 
function<void(void*)>destructor)
}

class DecorationInfo {
 -descriptor:DecorationContainer::DecorationDescriptor 
 -constructor :function<void(void*)>
 -destructor :function<void(void*)>
 +DecorationInfo(DecorationContainer::DecorationDescriptor descriptor,
                       function<void(void*)>constructor,
                       function<void(void*)>destructor)
}

class DecorationContainer {
 -const DecorationRegistry* const _registry
 -const std::unique_ptr<unsigned char[]> _decorationData
 +explicit DecorationContainer(const DecorationRegistry* registry)
 +~DecorationContainer()
 +T& getDecoration(DecorationDescriptorWithType<T> descriptor)
 +void* getDecoration(DecorationDescriptor descriptor)

}

class DecorationDescriptorWithType<T> {
 - _raw: DecorationDescriptor
 -friend class DecorationContainer
 -friend class DecorationRegistry
 +explicit DecorationDescriptorWithType(DecorationDescriptor raw)
}

class DecorationDescriptor {
 -_index:size_t
 -friend class DecorationContainer;
 -friend class DecorationRegistry;
 +explicit DecorationDescriptor(size_t index)
 
}

Decorable *- DecorationContainer
DecorationContainer *- DecorationRegistry
DecorationContainer +- DecorationDescriptor 
DecorationContainer +- DecorationDescriptorWithType
DecorationRegistry *- DecorationInfo 
DecorationInfo *- DecorationDescriptor 
Decoration *- DecorationDescriptorWithType
DecorationDescriptorWithType *- DecorationDescriptor

Decorable --> Decoration 
Decorable --> DecorationRegistry
DecorationRegistry -->DecorationDescriptorWithType
@enduml
```