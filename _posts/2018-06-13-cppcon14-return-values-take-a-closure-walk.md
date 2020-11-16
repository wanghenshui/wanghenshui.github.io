---
layout: post
title: (cppcon)return values take a closure walk
categories: c++
tags: [c++, cppcon]
---
  

这个ppt讲的是如何把返回值用lambda包起来，让返回值auto，用作者的图来总结这篇内容

![1556158688788](https://wanghenshui.github.io/assets/1556158688788.png)



首先思考在Context下的调用

```c++
void callWithin(const std::function<void()>& fn){
    ScopedContext context;
    try{
        fn();
    } catch (SomeException& e){
        // handle exception here
    }
}

void printLine(const std::string& text){
    std::cout<<text<<'\n';
}
callWithin([](){printLine("Hello, CppCon");});
```

**回调小函数扔到lambda里 接口都操作lambda**



也可以把这个变成模板, 这样 接口可以是任何类型的std::function, lambda

```c++
template <typename Callable>
void callWithin(const Callable& fn){
    ScopedContext context;
    fn();
}
```



进一步，如果想要回调函数的返回值，不需要要变动lambda接口

```c++
double sum(double a,double b){return a+b;}
double res = callWithin([](){return sum(3.14,2.71);})
```

可以在callWithin里改动lambda/function接口，但这降低了灵活性

```
double callWithin(const std::function<double()>&fn)...//如果返回值不是double怎么办？
```

解决办法，**template auto-decltype**

  ```c++
template <typename Callable> 
auto callWithin(const Callable& fn) ->decltype(fn()){
   decltype(fn()) result{};
   auto wrapperFn =[&]()->void
   {
       result = fn();
   }
   callWithImpl(wrapperFn);
   return result;
}
void callWithinImpl(const std::function<void()>& fn);
  ```

注意，这里用局部变量封一层result，弄一个局部的lambda，然后扔进callWithinImpl里，本质是加了一层，把原来的lambda放return的方案内嵌处理

传统方法，context肯定会有context manager，通过manager类接口来搞定, 接口也是固定的

```c++
class Contextmanager{
public:
    virtual void callWithin(const std::function<void()>&fn) = 0;
};
```

然后整合上面的实现，大致这样

```c++
class Contextmanager{
public:
  template <typename Fn>
  void callWithin(const Fn& fn, std::false_type) -> decltype(fn())
  {
    decltype(fn()) result{};
    callWithinImpl([&]{result=fn();});
    return result;
  }
private:
    virtual void callWithinImpl(const std::function<void()>&fn) = 0;
};

double result = manager->CallWithin([]{return sum(3.14, 2/71);});
```



这个方案又有了新问题，原来的直接传void返回的functor不能工作了

特化吧

```c++
template <typename Fn>
auto callWithin(const Fn& fn) -> decltype(fn())
{
    return _callWithin(fn, std::is_same<decltype(fn()),void>());
}
// true就直接调用，没有返回值
template <typename Fn>
void _callWithin(const Fn& fn, std::true_type) -> decltype(fn())
{
    callWithinImpl([&]{fn();});
}

template <typename Fn>
void _callWithin(const Fn& fn, std::false_type) -> decltype(fn())
{
    decltype(fn()) result{};
    callWithinImpl([&]{result=fn();});
    return result;
}
```



 新的挑战，callWithin失败

所以还是需要内部callWithinImpl有个返回值，来设定result，需要std::optional  包装一下

```c++
template <typename Fn>
void callWithin(const Fn& fn) -> std::optional<decltype(fn())>
{
    decltype(fn()) result{};
    bool ok = callWithinImpl([&]{result=fn();});
    if (ok)
    	return result;
    else
        return std::nullopt;
}
```



### ref

- [https://github.com/CppCon/CppCon2014/blob/master/Lightning%20Talks/Return%20values%20take%20a%20closure%20walk/Return%20values%20take%20a%20closure%20walk%20-%20Martin%20Troxler.pdf](https://github.com/CppCon/CppCon2014/blob/master/Lightning Talks/Return values take a closure walk/Return values take a closure walk - Martin Troxler.pdf)
-  ppt2014，那时候还没有 std::optional 和std::nullopt， 使用的是 boost::optional和boost::none 使用上没有差别


看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>