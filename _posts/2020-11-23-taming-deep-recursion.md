---
layout: post
title: (译)搞定深度递归
categories: [database, debug,translation]
tags: [c++, boost, stack]
---


---

> [原文链接](http://databasearchitects.blogspot.com/2020/11/taming-deep-recursion.html)

简单来说，作者写sql parse代码，可能需要分析表达式，但是表达式特别多，parse代码一半都是遍历二叉树，有递归的，这样递归深度就上去了

```c++
unique_ptr<Expression> analyzeExpression(AST* astNode) {  
   switch (astNode->getType()) {  
    case AST::BinaryExpression: return analyzeBinaryExpression(astNode->as<BinaryExpAST>());  
    case AST::CaseExpression: return analyzeCaseExpression(astNode->as<CaseExpAST>());  
    ...  
   }  
 }  
 unique_ptr<Expression> analyzeBinaryExpression(BinaryExpAST* astNode) {  
   auto left = analyzeExpression(astNode->left);  
   auto right = analyzeExpression(astNode->right);  
   auto type = inferBinaryType(astNode->getOp(), left, right);  
   return make_unique<BinaryExpression>(astNode->getOp(), move(left), move(right), type);  
 }  
```

 表达式规模300000个，直接栈溢出了，不得不探索解决办法

###  [__builtin_frame_address(0)](https://gcc.gnu.org/onlinedocs/gcc/Return-Address.html)

抓到堆栈溢出直接抛异常，解决的比较恶心

- 表达式太大，直接这个查询就挂了
- 其次，很多地方都这样遍历，不能确定哪里会有这种较大的场景，
- 在优化的过程中，树的结构可能会调整，说不定更深了，表达式更大了，为了优化作出的努力反而因为栈溢出停了

指定堆栈？更恶心了



### [-fsplit-stack](https://gcc.gnu.org/wiki/SplitStacks)

编译器帮忙维护堆栈吧，这个flag就相当于编译器自动的分堆栈，但是实际测试中，编译器直接内部错误(ICE) ，也没有别人使用过的案例，放弃

### [boost.context](https://www.boost.org/doc/libs/1_74_0/libs/context/doc/html/index.html) 

最终解决方案，用户态堆栈，且不用自己维护，代码改成这个样子

```c++
 unique_ptr<Expression> analyzeExpression(AST* astNode) {  
   if (StackGuard::needsNewStack())  
    return StackGuard::newStack([=]() { return analyzeExpression(astNode); });  
   ... // unchanged  
 }  
```

靠boost.context来切换堆栈，降低心智负担，代码也没有那么丑陋，可维护

---

### ref

- 他们还发了论文 https://db.in.tum.de/~radke/papers/hugejoins.pdf 这个论文内容说优化的，不是上面的工程实践内容


---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>