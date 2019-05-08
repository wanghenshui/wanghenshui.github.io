---
layout: post
title: 怀旧系列 boost fusion
category: c++
tags: [c++, boost]
---

{% include JB/setup %}

### why

最近看了一堆ppt，boost::fusion和boost::proto  出现频率太高，不得不仔细看一遍官网教程总结一下。

boost::fusion 是一套元编程工具，结合编译期与运行时的异构容器和算法组件，在c++0x时代比较有名，现在有了boost::hana这种牛逼的替代品，以后再研究，这个帖主要是总结学习fusion

---

Heterogeneous computing

boost::fusion::vector std::tuple boost::hana::tuple都是类似的东西，不过std::tuple光秃秃的，只有get，没有相关短发，boost::fusion和boost::hana都是在trick上做了算法加强

std::get\<N> 和at_c\<N>是一样的

```c++
#include <boost/fusion/sequence.hpp>
#include <boost/fusion/include/sequence.hpp>
vector<int, char, std::string> stuff(1, 'x', "howdy");
int i = at_c<0>(stuff);
char ch = at_c<1>(stuff);
std::string s = at_c<2>(stuff);
```

---

把Vector打印成XML

```c++
struct print_xml
{
    template <typename T>
    void operator()(T const& x) const
    {
        std::cout
            << '<' << typeid(x).name() << '>'
            << x
            << "</" << typeid(x).name() << '>'
            ;
    }
};
for_each(stuff, print_xml());
```

这个例子有个具体的推导的ppt fusion by example。以后有机会在水一贴



组织

Tuple <- iterator + Sequence + Algorithm <- Support

- tuple
- algorithm
  - auxiliary
  - iteration
  - query
  - transformation
- adapted
  - adt
  - array
  - boost::array
  - boost::tuple
  - mpl
  - std_pair
  - std_tuple
  - struct
- view
  - filter_view
  - flatten_view
  - iterator_range
  - joint_view
  - nview
  - repetitive_view
  - reverse_view
  - single_view
  - transform_view
  - zip_view
- container
  - deque
  - list
  - map
  - set
  - vector
  - generation
- mpl
- functional
  - adapter
  - generation
  - invocation
- sequence
  - comparison
  - intrinsic
  - io
- iterator
- support
  - [is_sequence](https://www.boost.org/doc/libs/1_70_0/libs/fusion/doc/html/fusion/support/is_sequence.html)
  - [is_view](https://www.boost.org/doc/libs/1_70_0/libs/fusion/doc/html/fusion/support/is_view.html)
  - [tag_of](https://www.boost.org/doc/libs/1_70_0/libs/fusion/doc/html/fusion/support/tag_of.html)
  - [category_of](https://www.boost.org/doc/libs/1_70_0/libs/fusion/doc/html/fusion/support/category_of.html)
  - [deduce](https://www.boost.org/doc/libs/1_70_0/libs/fusion/doc/html/fusion/support/deduce.html)
  - [deduce_sequence](https://www.boost.org/doc/libs/1_70_0/libs/fusion/doc/html/fusion/support/deduce_sequence.html)
  - pair

### ref

- <https://www.boost.org/doc/libs/1_70_0/libs/fusion>
- boost hana wiki<https://github.com/freezestudio/hana.zh>

看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。