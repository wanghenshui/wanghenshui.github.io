---
layout: post
title: (译)写好Pull Requests(PR)
category: translation
tags : [git]
---
  


[原文链接](http://satran.in/2018/12/10/On_Writing_Pull_Requests_Well.html) 

野生翻译，欢迎意见



最近和同事聊了聊关于合入请求（PR）的事儿，进过几个回合的讨论我觉得还是写下我的想法（对我俩都好）

简单介绍一下PR，GitHub术语，是提交请求改变代码库代码的一个方法，在过去（以及现在），内核社区一直用邮件系统。在GitLab这个叫合入请求（Merge Request）。以下原则在任何场景（代码管理方法）都适合使用



### 动机

动机是决定一个PR如何结束的主要因素，当我建了一个PR，我的主要动机是

- 我希望评审员能理解我改动的意图
- 评审员应该能够指出改动中遗漏疏忽的点

当我考虑这些动机，我的意图反应在我创建的PR改动中，当我的首要动机是尽快的解决想解决工单，这个PR在评审员严重可能就是噩梦。我不是贬低修改工单这个需求，尽管这和工资息息相关，单这个动机是次要的，在这片文章中我会列出我认为创建一个PR中至关重要的三条原则



#### 1.PR 改动特别大

当一个PR特别长，这对评审员是个心智负担，改动越长，评审员想要在脑海中记住变更的全貌就越难。我倾向于短的PR，对于我个人可能多点努力，但是能保证我的PR能轻松的审计并及时合入，长的PR带来的长时间的评审



#### 2.如果你非得传大量改动，使用git commits

有时候会遇到这样的场景：很难写出小的改动（PR），要不就功能实现不完整，要不就测试不通过，或者你的啥理由，这种场景我最起码把这些改动拆成小的git commits，这样评审能通过我的git log来看改动过程



#### 3.一个PR里不要提交太多改动

当你改动一个bug的时候，往往也想顺便改个变量名字顺便改个文件结构，请不要这么做。这会使评审走读原本的改动变得困难。本来就是几个小改动，上面这样改可能看起来就是一大堆函数添加删除改动很大。将这种改动和修bug拆开

代码是写出来给别人读的。我认为这在社区中已经说过很多次，PR更应该遵循。它表达出我作为一个作者在项目中改动的意图。这不简单，这需要时间和思考。但利大于弊。如果我希望评审做好工作，那我的工作应该让他更轻松。记住这个动机，它会改变创建PR这个流程



---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。