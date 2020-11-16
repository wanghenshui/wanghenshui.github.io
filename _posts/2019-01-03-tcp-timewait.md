---
layout: post
title: 说说 time_wait
categories: net
tags: [tcp]
---
  

不只是time_wait， 说说tcp关闭状态

![TCP CLOSE_WAIT](http://benohead.com/wp-content/uploads/2013/07/TCP-CLOSE_WAIT.png)

![03130408-930b424bf5384c80b677b6a50f1c6edc](../../assets/03130408-930b424bf5384c80b677b6a50f1c6edc.png)





几个问题

- 主动关闭进入FIN_WAIT_1状态后，被动方没有回ack，主动方回怎样？如果大量堆积FIN_WAIT_1会怎样？怎么避免？
- 主动的一方进入FIN_WAIT_2



####  参考

- 火丁笔记 这两篇博文非常棒。解释了大量FIN_WAIT1和大量TIME_WAIT的问题，就比如说很多解决TIME_WAIT的方案简单说下配置就完了，这几篇文章说了背后的问题，还带了rfc，专业。
  - https://huoding.com/2014/11/06/383
  - https://huoding.com/2013/12/31/316
- https://benohead.com/tcp-about-fin_wait_2-time_wait-and-close_wait/

![TCP CLOSE_WAIT](http://benohead.com/wp-content/uploads/2013/07/TCP-CLOSE_WAIT.png)