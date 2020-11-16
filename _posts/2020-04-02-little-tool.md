---
layout: post
title: 压缩图片几个命令行小工具
categories: tools
tags: [linux]
---
  

需求，网络限制，超过50k不让上传

压缩图片 

- jpg by `jpegtran`

```bash
apt install libjpeg-progs
jpegtran -optimize image-20200402171439048.jpg
```



- png by  `optipng`

```bash
apt install optipng
optipng -o3 image-20200402172644242.png
```

o1 ~ o7 七个等级压缩

---

### ref

- https://www.zhihu.com/question/19779256

  ytzong的答案不错。我在wsl上可以用上面的工具。对于压缩图片来说他那个cssgaga贼破，没法用

---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>