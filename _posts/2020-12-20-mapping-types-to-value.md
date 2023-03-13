---
layout: post
title: 实现类型为key的map
categories: [language]
tags: [c++, template, map]
---

> 翻译整理自[这篇文章](https://gpfault.net/posts/mapping-types-to-values.txt.html)，加了点自己的理解



类型为key，value不重要，以string举例

其实主要就是解决类型的映射，如何把类型映射成什么东西，肯定离不开模版就是了

## 静态map

先说一种static compile time map的方法，也就是模版偏特化

形状可以是这样的

```c++
template<typename K, typename V>
struct TypeMap { static const V v;}
```

然后根据不同的K来偏特化

这里弱化一下，用string举例，去掉V

```c++
#include <iostream>
#include <string>
template <typename T>
struct StringAnnotationTypeMap { static const std::string annotation; };
//故意不实现，这样没注册的类型会直接link error
//template <typename T>                         
//const std::string StringAnnotationTypeMap<T>::annotation = "default";

#define _TYPE_REGISTER(T, s)                            \
template <>                                                   \
const std::string StringAnnotationTypeMap<T>::annotation = (s);\
template <>                                                   \
const std::string StringAnnotationTypeMap<T&>::annotation = (s)
//这个T&是为了方便从指针推导出类型的特化

#define __STR(x) #x
#define _STR(x) __STR(x)
// 这个宏的目的是拼不同的类型
// 在rpc场景下，rpc函数名， rpc的request response参数都有相同的前缀
// 通过宏帮忙拼接出 参数 < - > rpc函数名字的映射
#define REQ(F) _TYPE_REGISTER(F##Request, _STR(F))
#define RSP(F) _TYPE_REGISTER(F##Response, _STR(F))

struct ARequest{};
struct BResponse{};
REQ(A);
RSP(B);

int p(const std::string & a) {
    std::cout<<a<<'\n';
    return 0;
}

int main() {
  p(StringAnnotationTypeMap<ARequest>::annotation);
  p(StringAnnotationTypeMap<BResponse>::annotation);
  BResponse *p;
  p(StringAnnotationTypeMap<decltype(*p)>::annotation);
}
```



这个方案用用还行，缺点是必须在编译期间就定好。

如果想要runtime方案，如何设计？

## 运行时typemap

考虑ECS设计模式 可以看这个[链接](https://gpp.tkchu.me/component.html)简单了解，不是本文的重点

大概意思就是尽可能的组件化，每个组件有各自的侵入方法，更灵活的组装实现

而不是去操作一个大的数据结构，对数据结构提供N个接口

每个Entity对应一个实例，每个组件是Component



不想让Entity和具体的Component绑定，那就需要一个字符串 <->类型的typemap来辅助，运行时注册



下面举例

```c++
class Entity {
public:
// ...
  AbstractComponent* get (const std::string &component_name) {
    auto it = m_components.find(component_name);
    assert(it != m_components.end());
    return it->second.get();
  }

private:
  std::unordered_map<std::string, std::unique_ptr<AbstractComponent>> m_components;
//...
};
```



至于component，继承基类就可以

```c++
class HitPointComponent : public AbstractComponent {
public:
  void takeHitFrom(const Entity *other_entity);
  void add(int hp);
  void setCurrentCap(int c);
  
private:
  int m_hitPoints;  // amount of hitpoints, can't be greater than m_currentCap
  int m_currentCap; // maximum amount of hitpoints
};
```



调用就这个德行

```c++
dynamic_cast<HitPointComponent>(player->get("HitPointComponent"))->takeHitFrom(projectile)
```

就是看着闹心，犯个错实在太轻松，core给你看

我们需要type map，而不是type-string map

既然有类型type，提供类型模版接口，帮助指针转换, 类似这种用法

```c++
auto e = std::make_unique<Entity>();
e->provideComponent<HitPointComponent>(std::make_unique<HitPointComponent>());
//...
e->get<HitPointComponent>()->takeHitFrom(projectile);
```

增加与调用接口需要指定参数类型，也就是说子类的信息没丢，那么，基类实际上不需要放接口，只需要定义虚析构函数就行了



### 如何实现typemap 之保存类型信息



首先考虑的就是type_info 返回整数

这里要考虑两个问题，1 是type_info的实现是依赖RTTI的，2是type_info是内部调用hash_code，这个实现是不透明的，换言之，这个返回值是不是唯一的，不能保证，只能确定同一个类型肯定返回同一个值



解决方案，自己引入一个getTypeId 保证每个类型的值唯一，一个很简单的唯一方法，自增id

```c++
// In a header file:
#include <atomic>

extern std::atomic_int TypeIdCounter;

template <typename T>
int getTypeId() {
  static int id = ++TypeIdCounter;
  return id;
}

// In a *.cpp file:
std::atomic_int TypeIdCounter(0);
```

当然，如果是单线程，可以用int代替atomic_int

这样，调用一次，就会特化一次，而且每个类型的id是不同的，在不同的翻译单元(TU)里，这就保证了id唯一

有唯一id之后，再保存一个id < - > value 就可以了，当然value是模版，随便是什么都可以

```c++
#include <unordered_map>
#include <atomic>

template <class ValueType>
class TypeMap {
  // Internally, we'll use a hash table to store mapping from type
  // IDs to the values.
  typedef std::unordered_map<int, ValueType> InternalMap;
public:
  typedef typename InternalMap::iterator iterator;
  typedef typename InternalMap::const_iterator const_iterator;
  typedef typename InternalMap::value_type value_type;

  const_iterator begin() const { return m_map.begin(); }
  const_iterator end() const { return m_map.end();  }
  iterator begin() { return m_map.begin();  }
  iterator end() { return m_map.end(); }

  // Finds the value associated with the type "Key" in the type map.
  template <class Key>
  iterator find() { return m_map.find(getTypeId<Key>());  }

  // Same as above, const version
  template <class Key>
  const_iterator find() const { return m_map.find(getTypeId<Key>()); }

  // Associates a value with the type "Key"
  template <class Key>
  void put(ValueType &&value) {
    m_map[getTypeId<Key>()] = std::forward<ValueType>(value);
  }  

private:
  template <class Key>
  inline static int getTypeId() {
    static const int id = LastTypeId++;
    return id;
  }

  static std::atomic_int LastTypeId;
  InternalMap m_map;
};

template <class ValueType>
std::atomic_int TypeMap<ValueType>::LastTypeId(0);
```



这样用起来就是这样的

```c++
TypeMap<std::string> tmap;
tmap.put<int>("integers!");
tmap.put<double>("doubles!");
std::cout << tmap.find<int>()->second << "\n";
```



最终回到ECS模型上来，把Component做Value，问题就解决了



```c++
class Entity {
public:
// ...
  template <typename Component>
  Component* get() {
    auto it = m_components.find<Component>();
    assert(it != m_components.end());
    return static_cast<Component*>(it->second.get());
  }
  
  template <typename Component>
  void provideComponent(std::unique_ptr<Component> &&c) {
    m_components.put<Component>(std::forward<std::unique_ptr<Component>>(c));
  }

private:
  TypeMap<std::unique_ptr<AbstractComponent>> m_components;
//...
};
```



老知识，新复习

---

update 2021-01-10-20-14

其实这种模式，如果是全局的组件，用type_id就够用了，以arangodb为例子，全局server有个addFeature和getFeature接口，思路和上面基本一致，这里把代码贴出来

其中_features就是type map

```c++
class ApplicationServer {
  using FeatureMap =
      std::unordered_map<std::type_index, std::unique_ptr<ApplicationFeature>>;
  ApplicationServer(ApplicationServer const&) = delete;
  ApplicationServer& operator=(ApplicationServer const&) = delete;
////省略一部分代码
 public:
   // adds a feature to the application server. the application server
   // will take ownership of the feature object and destroy it in its
   // destructor
   template <typename Type, typename As = Type, typename... Args,
             typename std::enable_if<std::is_base_of<ApplicationFeature, Type>::value, int>::type = 0,
             typename std::enable_if<std::is_base_of<ApplicationFeature, As>::value, int>::type = 0,
             typename std::enable_if<std::is_base_of<As, Type>::value, int>::type = 0>
   As& addFeature(Args&&... args) {
     TRI_ASSERT(!hasFeature<As>());
     std::pair<FeatureMap::iterator, bool> result =
         _features.try_emplace(std::type_index(typeid(As)),
                           std::make_unique<Type>(*this, std::forward<Args>(args)...));
     TRI_ASSERT(result.second);
     result.first->second->setRegistration(std::type_index(typeid(As)));
#ifdef ARANGODB_ENABLE_MAINTAINER_MODE
     auto obj = dynamic_cast<As*>(result.first->second.get());
     TRI_ASSERT(obj != nullptr);
     return *obj;
#else
     return *static_cast<As*>(result.first->second.get());
#endif
   }

   // checks for the existence of a feature by type. will not throw when used
   // for a non-existing feature
   bool hasFeature(std::type_index type) const noexcept {
     return (_features.find(type) != _features.end());
   }

   // checks for the existence of a feature. will not throw when used for
   // a non-existing feature
   template <typename Type, typename std::enable_if<std::is_base_of<ApplicationFeature, Type>::value, int>::type = 0>
   bool hasFeature() const noexcept {
     return hasFeature(std::type_index(typeid(Type)));
   }

   // returns a reference to a feature given the type. will throw when used for
   // a non-existing feature
   template <typename AsType, typename std::enable_if<std::is_base_of<ApplicationFeature, AsType>::value, int>::type = 0>
   AsType& getFeature(std::type_index type) const {
     auto it = _features.find(type);
     if (it == _features.end()) {
       throwFeatureNotFoundException(type.name());
     }
#ifdef ARANGODB_ENABLE_MAINTAINER_MODE
     auto obj = dynamic_cast<AsType*>(it->second.get());
     TRI_ASSERT(obj != nullptr);
     return *obj;
#else
     return *static_cast<AsType*>(it->second.get());
#endif
   }

   // returns a const reference to a feature. will throw when used for
   // a non-existing feature
   template <typename Type, typename AsType = Type,
             typename std::enable_if<std::is_base_of<ApplicationFeature, Type>::value, int>::type = 0,
             typename std::enable_if<std::is_base_of<Type, AsType>::value || std::is_base_of<AsType, Type>::value, int>::type = 0>
   AsType& getFeature() const {
     auto it = _features.find(std::type_index(typeid(Type)));
     if (it == _features.end()) {
       throwFeatureNotFoundException(typeid(Type).name());
     }
#ifdef ARANGODB_ENABLE_MAINTAINER_MODE
     auto obj = dynamic_cast<AsType*>(it->second.get());
     TRI_ASSERT(obj != nullptr);
     return *obj;
#else
     return *static_cast<AsType*>(it->second.get());
#endif
   }

   // map of feature names to features
   FeatureMap _features;
}
```

其实可以把type_index和type_info隐藏的更深一些，不提供type_index的接口，这样背后替换更轻松一些

使用时这样的

```c++
    ApplicationServer server(options, SBIN_DIRECTORY);
//...
    // Adding the Phases
    server.addFeature<AgencyFeaturePhase>();
    server.addFeature<CommunicationFeaturePhase>();
    server.addFeature<AqlFeaturePhase>();
    server.addFeature<BasicFeaturePhaseServer>();
    server.addFeature<ClusterFeaturePhase>();
//...
```



效果类似

---

### ref

- https://gpp.tkchu.me/ 意外找到了游戏编程模式的中文翻译
- Arangodb 源码 https://github.com/arangodb/arangodb


---




