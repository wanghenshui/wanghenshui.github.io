---
layout: post
title: Mixins for C++ PPT 笔记 && sqlpp11简单走读
categories: c++
tags: [c++,cppcon]
---
  

#  Mixins for C++ PPT 笔记 && sqlpp11简单走读

出自 ` cppcon2014 - Mixins for C++ - Roland Bock`   演讲人是sqlpp11的作者

#### 继承

- 有单继承，多重继承，以及变参模板继承
- 以上都可以用CRTP惯用法来实现

#### 组合的缺陷

- 需要事先知道要组合的成员。没有变参组合。
- 组合的名字也得事先起好，没有编译期定义的方法
- 为这些成员提供方法，得事先写好这些函数定义好。



下面就是根据sqlpp11来讲变参模板+CRTP来实现魔法了。。。

```c++
TabFoo foo;
Db db(/* some arguments*/);

// selecting zero or more results, iterating over the results
for (const auto& row : db(select(foo.name, foo.hasFun).from(foo).where(foo.id > 17 and foo.name.like("%bar%"))))
{
    if (row.name.is_null())
        std::cerr << "name is null, will convert to empty string" << std::endl;
    std::string name = row.name;   // string-like fields are implicitly convertible to string
    bool hasFun = row.hasFun;          // bool fields are implicitly convertible to bool
}
```



如何实现select调用链？抽象出sql语句类 statement_t [定义在这里](https://github.com/rbock/sqlpp11/blob/develop/include/sqlpp11/statement.h)

```c++
 template <typename Db, typename... Policies>
  struct statement_t : public Policies::template _base_t<detail::statement_policies_t<Db, Policies...>>...,
                       public expression_operators<statement_t<Db, Policies...>,
                                                   value_type_of<detail::statement_policies_t<Db, Policies...>>>,
                       public detail::statement_policies_t<Db, Policies...>::_result_methods_t
  {...
```



变参模板继承，将policies的属性转发出来，实际上还是元函数转发，变参继承要比之前的手写转发强很多。

policies类都是sql子句或关键字类，比如[select_t](https://github.com/rbock/sqlpp11/blob/develop/include/sqlpp11/select.h) ,serializer_t分别特化藏起字符串。

```c++
  struct select_name_t  { };
  struct select_t : public statement_name_t<select_name_t, tag::is_select>  {};

  template <typename Context>
  struct serializer_t<Context, select_name_t>
  {
    using _serialize_check = consistent_t;
    using T = select_name_t;
    static Context& _(const T& /*unused*/, Context& context)
    {
      context << "SELECT ";
      return context;
    }
  };

  template <typename Database>
  using blank_select_t = statement_t<Database,
                                     no_with_t,
                                     select_t,
                                     no_select_flag_list_t,
                                     no_select_column_list_t,
                                     no_from_t,
                                     no_where_t<true>,
                                     no_group_by_t,
                                     no_having_t,
                                     no_order_by_t,
                                     no_limit_t,
                                     no_offset_t,
                                     no_union_t,
                                     no_for_update_t>;

//一些blank_select_t的特化
```

主要是是这个blank_select_t，这就是select的原型了，所有子句都是空的。但都是全的。

所以select

```c++
  template <typename... Columns>
  auto select(Columns... columns) -> decltype(blank_select_t<void>().columns(columns...))
  {
    return blank_select_t<void>().columns(columns...);
  }
```

这里的blank_select_t会转发给statement_t背后的_base_t  ,然后转发给base_t的columns函数，

由于每个子句类都有base_t，这个匹配会匹配第一个由columns函数的，匹配失败不是错误，直到匹配成功为止，

就会匹配到[no_select_column_list_t](https://github.com/rbock/sqlpp11/blob/ef01958b195e9a8ad7b77780fc53e14fbb8c8bf2/include/sqlpp11/statement.h) 上

```C++
template <typename... Args>
auto columns(Args... args) const
-> _new_statement_t<decltype(_check_args(args...)), detail::make_select_column_list_t<void, Args...>>
{
static_assert(sizeof...(Args), "at least one selectable expression (e.g. a column) required in columns()");
static_assert(decltype(_check_args(args...))::value,
"at least one argument is not a selectable expression in columns()");

return _columns_impl<void>(decltype(_check_args(args...)){}, detail::column_tuple_merge(args...));
}
```

 按照接口，返回的是下一个子句，继续匹配。。假如后面用到了where  [在no_where_t::_base_t中](https://github.com/rbock/sqlpp11/blob/ef01958b195e9a8ad7b77780fc53e14fbb8c8bf2/include/sqlpp11/where.h)

```c++
template <typename Expression>
auto where(Expression expression) const
-> _new_statement_t<check_where_static_t<Expression>, where_t<void, Expression>>
{
using Check = check_where_static_t<Expression>;
return _where_impl<void>(Check{}, expression);
}
```

就会匹配到where函数继续返回新的子句。如果匹配到最后怎么办？什么都匹配不到，临时对象。





这个PPT的主题是多重继承的实现，以及字段字符串的问题

- 多重继承用变参模板，一开始就写好，名字冲突和多重继承类似，（指的匹配失败不是错误？）
- 不要比较字段，直接将字符串作为模板参数，调用内部的方法。



ppt没理解通，代码倒是简单走了一遍，太复杂了。咋想到的。

看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。