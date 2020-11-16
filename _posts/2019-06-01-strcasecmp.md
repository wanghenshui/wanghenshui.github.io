---
layout: post
categories: c++
title: strcasecmp
tags: [string, c++]

---

  

---

### why

一个常见的比较字符串的需求，不分大小写

在linux上可以用strcasecmp，在windows上可以用stricmp，需要写个宏糊到一起，当然，也有其他办法，参考链接给出了很多种实现

比如下面这个不怎么费力的

```c++
#include <algorithm>
bool iequals(const string& a, const string& b)
{
    return std::equal(a.begin(), a.end(),
                      b.begin(), b.end(),
                      [](char a, char b) {
                          return tolower(a) == tolower(b);
                      });
}
```

或者boost::iequals，这个是怎么实现的？

```c++
        //! 'Equals' predicate ( case insensitive )
        /*!
            This predicate holds when the test container is equal to the
            input container i.e. all elements in both containers are same.
            Elements are compared case insensitively.

            \param Input An input sequence
            \param Test A test sequence
            \param Loc A locale used for case insensitive comparison
            \return The result of the test

            \note This is a two-way version of \c std::equal algorithm

            \note This function provides the strong exception-safety guarantee
        */
        template<typename Range1T, typename Range2T>
        inline bool iequals( 
            const Range1T& Input, 
            const Range2T& Test,
            const std::locale& Loc=std::locale())
        {
            return ::boost::algorithm::equals(Input, Test, is_iequal(Loc));
        }

```





### ref

- <https://stackoverflow.com/questions/11635/case-insensitive-string-comparison-in-c>

### contact

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>