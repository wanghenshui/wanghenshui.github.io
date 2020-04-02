---
layout: post
title: 几个命令行小工具
category: tools
tags: [linux]
---
{% include JB/setup %}



压缩图片 

- jpg - jpegtran

```bash
apt install libjpeg-progs
jpegtran -optimize image-20200402171439048.jpg
```



- png optipng

```bash
apt install optipng
optipng -o3 image-20200402172644242.png
```



---

### ref

- https://www.zhihu.com/question/19779256

  ytzong的答案不错。我在wsl上可以用上面的工具。对于压缩图片来说他那个cssgaga贼破，没法用

---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。