---
layout: post
category : c++
title: 为啥不用realloc
tags : [c,gcc]
---
{% include JB/setup %}

>只要遇到的问题多，天天都能水博客

主要是这两个题目

https://www.zhihu.com/question/316026652/answer/623343052

https://www.zhihu.com/question/316026215/answer/623342036

和这个提问题的人说了好多条也没说明白（也怪我没说到点子上）



vector不用realloc原因就是realloc只提供memmove但是不提供构造语义，对于not trivial对象是有问题的。和他讨论半天，他还给我举了placement new的例子，提问者不明白realloc和placement new本质区别



realloc这个api是十分邪恶的，为了复用一小块，搞了这个不明不白的api

> 这api ，不填ptr（NULL） 就是malloc ，不填size（0）就是free



realloc为了复用这小块地方能带来的优势十分有限。并且这个邪恶的api很容易用错。

c程序员不是最喜欢纯粹，一眼能看出来c代码背后做了什么，反对c++这种背后隐藏语义，怎么会喜欢realloc ？这个api可能在背后帮你memmove，如果not trivial，复制就是有问题的。这种心智负担放在使用api的人身上肯定有问题，何况这个api真的太烂了，api caller不了解的话就是个深坑。



## 参考

- realloc的代价，别用就好了。 https://stackoverflow.com/questions/5471510/how-much-overhead-do-realloc-calls-introduce
- 还是不建议用https://stackoverflow.com/questions/25807044/can-i-use-stdrealloc-to-prevent-redundant-memory-allocation
- realloc 和free-malloc有啥区别，能有机会复用原来的数据，但是这是心智负担啊 https://stackoverflow.com/questions/1401234/differences-between-using-realloc-vs-free-malloc-functions