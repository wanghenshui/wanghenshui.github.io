---
layout: post
title: (转)可扩展服务设计原则checklist
categories: [todo]
tags: [checklist]
---
> 转自 http://sunisdown.me/ke-kuo-zhan-fu-wu-she-ji-yuan-ze-checklist.html
>
> 考虑一下

## 基本原则

- [ ] Expect failures 硬盘可能会坏，网络会不稳定，系统设计的时候是不是能够优雅的处理各种异常？
- [ ] Keep things simple 复杂会导致更多的问题，简单的系统更容易正确的运行。去掉不必要的依赖等
- [ ] Automate everything 使人都会犯错，把所有能够自动化的都自动化。

## 整体设计

- [ ] 发生故障的时候，系统能否在没有人工干预的情况下自动恢复
- [ ] 故障恢复的路径需要经常被测试
- [ ] 把各个不同的组件都文档化，而不是每次了解某一个部分都需要看代码
- [ ] 是否只提供一个版本给用户（单一版本迭代成本更低
- [ ] 多租户，是否需要在没有物理隔离的情况下提供多租户功能
- [ ] health check 是否实现了自动且快速的故障检测
- [ ] 当你依赖的系统有问题的时候，能否服务降级
- [ ] 相同那个的功能，只需要在一个应用里面实现，没有必要实现多次，会增加维护成本。
- [ ] 服务需要能够单独运行，而不是必须要依赖于某个其他的服务才可以正常运行。
- [ ] 针对少数需要人工干预的情况，需要准备好文档，脚本，测试方案等。
- [ ] 保持系统简单的架构，如果是为了优化性能而增加复杂度，则需要这个性能上的改进超过一个数量级，只有几个百分点的改进不值得增加系统复杂成都。
- [ ] 所有层级的入口都应该有准入机制，比如 rate limit，防止量过大导致服务不可用
- [ ] 能否拆分服务，拆分的是否合理
- [ ] 分布式环境下，我们是否了解里面的网络拓扑，这个是否找网络方面专家 review 过
- [ ] 是否分析过吞吐量与延迟，是否有对应的扩容方案
- [ ] 对于这个服务给数据库/数据服务带来的流量是否有一个明确的理解，是否验证过。
- [ ] 是否所有的系统，都是在同一套工具链下完成的，比如相同的 code review，测试环境等
- [ ] 版本化，保留之前的版本，测试用例，万一需要回滚呢
- [ ] 单点故障是不可接受的

## 自动化管理

- [ ] 所有的服务都需要支持重启
- [ ] 所有持久化的数据都需要备份
- [ ] 设计上需要支持跨数据中心部署（如果设计是不做，后面要实现就会比较麻烦）
- [ ] 部署/配置自动化
- [ ] 配置与代码需要一起交付，不要 version A的代码用了 version B 的配置。
- [ ] 线上的更改，需要有记录，what，when，whom，which servers ，定时扫描线上版本，以免出现不一致的情况。
- [ ] 按照角色来来管理服务，而不是面向服务来管理。
- [ ] 系统出现多种故障的时候，服务是否能够正常工作
- [ ] 重要的数据不要依赖于本地存储，很容易丢数据。
- [ ] 部署过程是否简单？
- [ ] chaos monkey 是个好东西

## 依赖管理

- [ ] 能否容忍 latency 比较高的情况
- [ ] 服务调用是否有超时机制
- [ ] 超时重试是否有限制次数
- [ ] 是否有CB 机制
- [ ] 是否有快速失败机制
- [ ] 依赖的组件是否可靠，验证过？
- [ ] 跨服务的监控告警有吗
- [ ] 依赖双方要有一直的设计目标
- [ ] 模块解耦，依赖的组件挂了，也要能够服务（服务降级）

## 发布周期与测试

- [ ] 是否频繁发布，发布频繁可以减少出错的机会，发布周期太长是很危险的（3个月）
- [ ] 是否对用户体验定义了标准，是否有测试这些标准
- [ ] 能否回滚到某一个指定版本
- [ ] 可以在单节点上部署测试嘛？
- [ ] 有压测嘛
- [ ] 新版本发布之前的测试（性能，吞吐量，latency）
- [ ] 可以使用 production 来测试嘛
- [ ] 是否有跟生成环境完全一直的环境，并用相同的数据进行大规模测试
- [ ] 有监控系统吗
- [ ] 监控系统能明显的看出系统的各种重要指标嘛
- [ ] 能否减少误报

## 硬件选择与标准化

这个老哥在论文里面教了怎么购买硬件，怎么搞机柜。Google 有一本更专业的书来说这个事儿，这里不总结了。

## 运维与容量规划。

- [ ] devops, 谁开发，谁治理。
- [ ] 只做软删除，要能够恢复被误删的数据
- [ ] 跟踪资源分配
- [ ] 一次只做一项更改（排查问题是，一次只对应用做一次更改，方便溯源问题）
- [ ] 配置一切，如果可以通过更新配置来完成，而不是更改代码，这样会方便很多

## 审计，监控与告警

- [ ] 监控一切
- [ ] 统计有问题但是没有告警的情况，把这个比例降低到0
- [ ] 分析数据，理解那些是正常的行为，避免误报。
- [ ] 数据是最有价值的资源，帮助我们追溯问题。
- [ ] 日志 Level是否可以配置，而不是重启，可配置的日志 Level 可以在需要的时候，输出更详细的日志帮助排问题。
- [ ] 所有发现的错误都要及时处理，如果有错误但是没有处理手段，那这个错误就可能会被长期忽略，最终导致灾难发生
- [ ] 快速定位线上问题
- [ ] 能否镜像一个线上的系统，在镜像系统调试问题

## 优雅的降级与准入机制

- [ ] 是否有 红按钮 机制，支持拒绝不重要的请求
- [ ] 准入控制，拒绝部分请求
- [ ] 渐入式准入控制，慢慢放开流量，以便系统能够优化恢复

## 客户沟通计划

- [ ] 针对大规模系统不可用，数据丢失或损坏，安全漏洞等，是否制定了沟通计划，想之前腾讯云那种情况，就是缺乏沟通导致的

## 客户自助

- [ ] 客户自行配置可以降低成本，并提高满意度，支持客户自助也相对重要。


---


