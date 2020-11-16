---
layout: post
title: 遇到的两个jenkins问题
categories: [tools]
tags: [debug,linux]
---
  

---

 

> 傻逼jenkins



不知道平台的人把jenkins怎么了，可能是升级了。~~能用内置CI还是不要用第三方组件，真是闹心~~



- 乱码

![image-20200422170106071](https://wanghenshui.github.io/assets/image-20200422170106071.png)

不止这一个命令，git rm都会乱码，我还以为是脚本隐藏了不可见字符，改了半天啊不好使

然后猜测是有中文注释的原因，去掉，依旧不行

最后发现参考链接1 在脚本前加一行

```bash
export LANG="en_US.UTF-8"  
```



-  找不到命令

![image-20200422170524986](https://wanghenshui.github.io/assets/image-20200422170524986.png)

PATH被清空了。在脚本前加上PATH定义即可

```bash
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin"
```





### ref

1. https://blog.csdn.net/qq_35732831/article/details/85236562
2. https://www.cnblogs.com/weifeng1463/p/9419358.html
3. https://testerhome.com/topics/15136



---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
![微信转账](https://wanghenshui.github.io/assets/wepay.png)
</details>