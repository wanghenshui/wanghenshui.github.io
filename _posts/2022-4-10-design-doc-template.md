---
layout: post
title: Design Doc Template
categories: [todo]
tags: []
---

内网转载。内容非常不错。去掉隐私信息。非常适合作为一个模板

<!-- more -->

# Design Doc Template



## **目标**

“我们要解决什么问题？”



用几句话说明该设计文档的关键目的，让读者能够一眼得知自己是否对该设计文档感兴趣。

如：

“本文描述 Spanner 的顶层设计"



继而，使用 Bullet Points 描述该设计试图达到的重要目标，如：

- 可扩展性
- 多版本
- 全球分布
- 同步复制



非目标也可能很重要。

非目标并非单纯目标的否定形式，也不是与解决问题无关的其它目标，而是一些可能是读者非预期的、本可作为目标但并没有的目标，如：

- 高可用性
- 高可靠性

如果可能，解释是基于哪些方面的考虑将之作为非目标。如：

- 可维护性： 本服务只是过渡方案，预计寿命三个月，待 XX 上线运行后即可下线



设计不是试图达到完美，而是试图达到平衡。 显式地声明哪些是目标，哪些是非目标，有助于帮助读者理解下文中设计决策的合理性，同时也有助于日后迭代设计时，检查最初的假设是否仍然成立。



## **背景**

“我们为什么要解决这个问题？”



为设计文档的目标读者提供理解详细设计所需的背景信息。

按读者范围来提供背景。见上文关于目标读者的圈定。



设计文档应该是“自足的”（self-contained），即应该为读者提供足够的背景知识，使其无需进一步的查阅资料即可理解后文的设计。

保持简洁，通常以几段为宜，每段简要介绍即可。如果需要向读者提供进一步的信息，最好只提供链接。



警惕知识的诅咒。 **知识的诅咒**（Curse of knowledge）是一种[认知偏差](https://zh.wikipedia.org/wiki/認知偏差)，指人在与他人交流的时候，下意识地假设对方拥有理解交流主题所需要的背景知识。



背景通常可以包括：

- 需求动机以及可能的例子。 如，“ xxx微服务模式正在公司内变得流行，但是缺少一个通用的、封装了常用内部工具及服务接口的微服务框架”。

- - 这是放置需求文档的链接的好地方。

- 此前的版本以及它们的问题。 如，“yyy是之前的应用框架， 有以下特点，…………， 但是有以下局限性及历史遗留问题”。

- 其它已有方案， 如公司内其它方案或开源方案， "xxx vs. yyy vs. bbb vs. ccc"

- 相关的项目，如 "xxx 框架中可能会对接的其它  系统"



不要在背景中写你的设计，或对问题的解决思路。 



## **总体设计**

“我们如何解决这个问题？”



用一页描述高层设计。

说明系统的主要组成部分，以及一些关键设计决策。应该说明该系统的模块和决策如何满足前文所列出的目标。

本设计文档的评审人应该能够根据该总体设计理解你的设计思路并做出评价。描述应该对一个新加入的、不在该项目工作的腾讯工程师而言是可以理解的。



推荐使用 [系统关系图](https://zh.wikipedia.org/wiki/系统关系图) 描述设计。它可以使读者清晰地了解文中的新系统和已经熟悉的系统间的关系。它也可以包含新系统内部概要的组成模块。

注意：不要只放一个图而不做任何说明，请根据上面小节的要求用文字描述设计思想。   

不要在这里描述细节，放在下一章节中； 不要在这里描述背景，放在上一章节中。

## **详细设计**

在这一节中，除了介绍设计方案的细节，还应该包括在产生最终方案过程中，主要的设计思想及权衡（tradeoff）。这一节的结构和内容因设计对象（系统，API，流程等）的不同可以自由决定，可以划分一些小节来更好地组织内容，尽可能以简洁明了的结构阐明整个设计。



不要过多写实现细节。就像我们不推荐添加只是为了说明代码做了什么的注释，我们也不推荐在设计文档中只说明你具体要怎么实现该系统。否则，为什么不直接实现呢？

以下内容可能是实现细节例子，不适合在设计文档中讨论：

- API 的所有细节
- 存储系统的 Data Schema
- 具体代码或伪代码
- 该系统各模块代码的存放位置、各模块代码的布局
- 该系统使用的编译器版本
- 开发规范



通常可以包含以下内容（注意，小节的命名可以更改为更清晰体现内容的标题）：

### **各子模块的设计**

阐明一些复杂模块内部的细节，可以包含一些模块图、流程图来帮助读者理解。可以借助时序图进行展现，如一次调用在各子模块中的运行过程。

每个子模块需要说明自己存在的意义。如无必要，勿添模块。

如果没有特殊情况（例如该设计文档是为了描述并实现一个核心算法），不要在系统设计加入代码或者伪代码。



### **API接口**

如果设计的系统会暴露 API 接口，那么简要地描述一下API会帮助读者理解系统的边界。

避免将整个接口复制粘贴到文档中，因为在特定编程语言中的接口通常包含一些语言细节而显得冗长，并且有一些细节也会很快变化。着重表现API接口跟设计最相关的主要部分即可。



### **存储**

介绍系统依赖的存储设计。该部分内容应该回答以下问题，如果答案并非显而易见：

- 该系统对数据/存储有哪些要求？ 

- - 该系统会如何使用数据？
  - 数据是什么类型的？
  - 数据规模有多大？
  - 读写比是多少？读写频率有多高？
  - 对可扩展性是否有要求？
  - 对原子性要求是什么？
  - 对一致性要求是什么？是否需要支持事务？
  - 对可用性要求是什么？
  - 对性能的要求是什么？
  - …………

- 基于上面的事实，数据库应该如何选型？

- - 选用关系型数据库还是非关系型数据库？是否有合适的中间件可以使用？
  - 如何分片？是否需要分库分表？是否需要副本？
  - 是否需要异地容灾？
  - 是否需要冷热分离？
  - …………



数据的抽象以及数据间关系的描述至关重要。可以借助 [ER](https://zh.wikipedia.org/wiki/ER模型)[ ](https://zh.wikipedia.org/wiki/ER模型)[图](https://zh.wikipedia.org/wiki/ER模型)(Entity Relationshiop) 的方式展现数据关系。



回答上述问题时，尽可能提供数据，将数据作为答案或作为辅助。 不要回答“数据规模很大，读写频繁”，而是回答“预计数据规模为 300T， 3M 日读出， 0.3M 日写入， 巅峰 QPS 为 300”。这样才能为下一步的具体数据库造型提供详细的决策依据，并让读者信服。

注意：在选型时也应包括可能会造成显著影响的非技术因素，如费用。



避免将所有数据定义（data schema）复制粘贴到文档中，因为 data schema 更偏实现细节。



## **其他方案**

“我们为什么不这么解决这个问题？”

在介绍了最终方案后，可以有一节介绍一下设计过程中考虑过的其他设计方案（Alternatives Considered）、它们各自的优缺点和权衡点、以及导致选择最终方案的原因等。通常，有经验的读者（尤其是方案的审阅者）会很自然地想到一些其他设计方案，如果这里的介绍描述了没有选择这些方案的原因，就避免读者带着疑问看完整个设计再来询问作者。这一节可以体现设计的严谨性和全面性。



## **交叉关注点**

### **基础设施**

如果基础设施的选用需要特殊考量，则应该列出。

如果该系统的实现需要对基础设施进行增强或变更，也应该在此讨论。



### **可扩展性**

你的系统如何扩展？横向扩展还是纵向扩展？注意数据存储量和流量都可能会需要扩展。



### **安全** **& 隐私**

安全性通常需要在设计初期做设计。不同于其它部分是可选的，安全部分往往是必需的。即使你的系统不需要考虑安全和隐私，也需要显式地在本章说明为何是不必要的。



安全性如何保证？ 

系统如何授权、鉴权和审计(Authorization, Authentication and Auditing, AAA）？

是否需要破窗（break-glass）机制？

有哪些已知漏洞和潜在的不安全依赖关系？

是否应该与专业安全团队讨论安全性设计评审？

……

### **数据完整性**

如何保证数据完整性（Data Integrity）？

如何发现存储数据的损坏或丢失？如何恢复？由数据库保证即可，还是需要额外的安全措施？

为了数据完整性，需要对稳定性、性能、可复用性、可维护性造成哪些影响？



### **延迟**

声明延迟的预期目标。描述预期延迟可能造成的影响，以及相关的应对措施。



### **冗余 & 可靠性**

是否需要容灾？是否需要过载保护、有损降级、接口熔断、轻重分离？

是否需要备份？备份策略是什么？如何修复？在数据丢失和恢复之间会发生什么？



### **稳定性**

SLA 目标是什么？ 如果监控？如何保证？

## 稳定性设计清单（Checklist）

| 检查项目                                                     | 已规划 | 不适用 | 其他 |
| ------------------------------------------------------------ | ------ | ------ | ---- |
| [乐观并发（Optimistic Concurrency）](https://dev.to/harri_etty/what-you-need-to-know-about-optimistic-concurrency-1g3l) |        |        |      |
| [事务失败补偿（Compensate transaction failure）](https://www.simpleorientedarchitecture.com/handling-failure-in-long-running-processes/) |        |        |      |
| [优雅降级（Graceful degrade）](https://blog.newrelic.com/engineering/design-software-for-graceful-degradation/) |        |        |      |
| [减少健谈通信（Reduce chatty communication）](https://thenewstack.io/are-your-microservices-overly-chatty/) |        |        |      |
| [分布式跟踪（Distributed tracing）](https://opentracing.io/docs/overview/what-is-tracing) |        |        |      |
| [卸载至后台（Background offloading）](https://devcenter.heroku.com/articles/background-jobs-queueing) |        |        |      |
| [卸载至网关（Gateway offloading）](https://vukvuk.com/gateway-offloading-pattern/) |        |        |      |
| [命令查询责任分离（CQRS）](https://www.upsolver.com/blog/cqrs-event-sourcing-build-database-architecture) |        |        |      |
| [基础设施即代码（Infra as code）](https://stackify.com/what-is-infrastructure-as-code-how-it-works-best-practices-tutorials/) |        |        |      |
| [处理瞬时故障（Handle transient failure）](https://docs.microsoft.com/en-us/azure/architecture/best-practices/transient-faults) |        |        |      |
| [复制备份（Replication）](https://www.manageengine.com/device-control/data-replication.html) |        |        |      |
| [断路器（Circuit breaker）](https://martinfowler.com/bliki/CircuitBreaker.html) |        |        |      |
| [幂等（Idempotency）](https://nordicapis.com/understanding-idempotency-and-safety-in-api-design/) |        |        |      |
| [异步消息（Async Messaging）](https://www.cloudamqp.com/blog/asynchronous-communication-with-rabbitmq.html) |        |        |      |
| [接口版本控制（API versioning）](https://restfulapi.net/versioning/) |        |        |      |
| [支持混沌工程（Chaos Engineering）](https://github.com/dastergon/awesome-chaos-engineering) |        |        |      |
| [支持独立部署（Independent deployment）](https://devops.com/3-golden-rules-microservices-deployments/) |        |        |      |
| [支持生产环境测试（Test in production）](https://opensource.com/article/19/5/dont-test-production) |        |        |      |
| [故障转移（Failover）](https://www.cloudflare.com/learning/performance/what-is-server-failover/) |        |        |      |
| [数据保留策略（Rentention policy）](https://www.intradyn.com/data-retention-policy/) |        |        |      |
| [最终一致性（Eventual consistency）](https://cloud.google.com/datastore/docs/articles/balancing-strong-and-eventual-consistency-with-google-cloud-datastore) |        |        |      |
| [特性开关（Feature toggles）](https://martinfowler.com/articles/feature-toggles.html) |        |        |      |
| [缓存策略（Caching policy）](https://aws.amazon.com/caching/best-practices/) |        |        |      |
| [舱壁隔离（Bulkhead）](https://akfpartners.com/growth-blog/bulkhead-pattern) |        |        |      |
| [负载均衡（Load balancing）](https://www.nginx.com/resources/glossary/load-balancing/) |        |        |      |
| [负载整形（Load leveling）](https://docs.microsoft.com/en-us/azure/architecture/patterns/queue-based-load-leveling) |        |        |      |
| [避免热点分区（Avoid hotspots）](https://cloud.google.com/spanner/docs/schema-design) |        |        |      |
| [配置即代码（Config as code）](https://www.cloudbees.com/blog/configuration-as-code-everything-need-know/) |        |        |      |
| [限流（Thottling）](https://www.progress.com/blogs/how-to-rate-limit-an-api-query-throttling-made-easy) |        |        |      |
| [领域事件（Domain events）](https://www.innoq.com/en/blog/domain-events-versus-event-sourcing/) |        |        |      |
| [领域封装（Domain encapuslation）](http://www.kamilgrzybek.com/design/domain-model-encapsulation-and-pi-with-entity-framework-2-2/) |        |        |      |
| [高内聚低耦合（HCLC）](https://stackoverflow.com/questions/14000762/what-does-low-in-coupling-and-high-in-cohesion-mean) |        |        |      |
| [黑灰白名单管理（Blacklist/Greylist/Whitelist）](https://techbeacon.com/security/whitelisting-blacklisting-your-security-strategy-its-not-either-or) |        |        |      |



### **外部依赖**

你的外部依赖的可靠性（如 SLA）如何？会对你的系统的可靠性造成何种影响？

如果你的外部依赖不可用，会对你的系统造成何种影响？



除了服务级的依赖外，不要忘记一些隐含的依赖，如 DNS 服务、时间协议服务、运行集群等。



## **实现计划**

描述时间及人力安排（如里程碑）。 这利于相关人员了解预期，调整工作计划。



## **未来计划**

未来可能的计划会方便读者更好地理解该设计以及其定位。

我们确实应该把设计限定在当前问题，但是该设计可能是更高层系统所要解决问题的一部分，或者只是阶段性方案。 读者可能会对方案的完整性有所疑问，会质疑到底问题是否得到完整解决，甚至会质疑该问题在更高层的系统中是否确实值得解决。 “背景（过去）-- 当前方案 -- 未来计划” 三者的结合会为读者提供更好的全景图。

---

