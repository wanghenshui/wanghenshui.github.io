---
layout: post
title: (cppcon)一些老的编程规范的反思
categories: [c++, cppcon, cppcon2019]
tags: [c++]
---
  



# goto harmful?

goto更像汇编一点。

感觉是老生长谈了，常用的goto场景还算处理错误码退出，还列了论文，高德纳的

goto 在c++：可能那个跳过构造函数，漏掉初始化(编译不过/编译告警)，注意（setjmp是不是也这样）

循环中提前退出, goto版本更高效 （why??）

switch里用goto c++里没有对应的应用，类似 duff's device????? 手动展开循环
别手写，让编译器干这个活

用switch就算用goto了

讨论了其他语言中的使用套路 pattern, 没记录 只记录c++相关的

- 不能跳过复杂类型初始化?non-vacuous怎么翻译？我大概理解就算没有默认构造的
- 不能跳出/跳入函数
- 不能用在constexpr函数
- 不能跳入try catch，跳出没事儿（都try-catch了还用goto感觉有点分裂）




# 函数退出集中起来。
（确实，多路返回的代码让人痛苦，我也写过那种。。 不清晰）

上面讨论的for循环return 低效，可以把for中间判断限制一下，提前break，起到goto效果


返回值复杂，比如variant 使用overload trick，variant的switch

几种例外，能省构造等等。各取所需


# 成员变量private访问权限

封装
不变量
提前设计 即使你用不到 需要c#那种proprity？
class封装和struct那种透明的语义就不一样了。还是哪句话，用不到不要过度设计


# 声明就初始化

可能写成函数声明了，ecpp有一条
某些场景没必要非得初始化
你不用的，不要多付出

还有在函数开头声明，这是c的习惯，可能用不到，白白浪费构造
其他语言也是一样，什么时候用什么时候声明
两部初始化，工厂模式




## ref

1. https://www.bilibili.com/video/BV1pJ411w7kh?p=12
2. ppt 在这里 https://github.com/CppCon/CppCon2019/blob/master/Presentations/some_programming_myths_revisited/some_programming_myths_revisited__patrice_roy__cppcon_2019.pdf

   

---
看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>
