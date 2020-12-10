---
layout: post
title: (译)socket in your shell
categories: [language]
tags: [bash, socket]
---


---

>  整理自这篇[博客](https://who23.github.io/2020/12/03/sockets-in-your-shell.html)



简单说，就是基本工具shell也可以用socket来做服务/客户端（尤其是在没有nc/telnet的场景下）

作者列了普通bash和zsh下两种用法



### bash

```bash
echo "text!" > /dev/$PROTO/$HOST/$PORT
```

一个检测例子

```bash
#!/bin/bash
if exec 3>/dev/tcp/localhost/4000 ; then
	echo "server up!"
else
	echo "server down."
fi
```

我以前都用netcat检测



也可以用exec检测

samplecurl

```bash
#!/bin/bash
exec 3<>/dev/tcp/"$1"/80
echo -e "GET / HTTP/1.1\n" >&3
cat <&3
```



使用

```bash
$ ./simplecurl www.google.com
HTTP/1.1 200 OK
Date: Thu, 03 Dec 2020 00:57:30 GMT
Expires: -1
....
<google website>
```



### zsh

有内建模块支持

```bash
zmodload zsh/net/tcp
```

这行放到`.zshrc` ,或者shell里执行，就加载了ztcp



```bash
# host machine:
lfd=$(ztcp -l 7128)
talkfd=$(ztcp -a $lfd)

# client machine
talkfd=$(ztcp HOST 7128)
```



这样客户端服务端的fd有了，就可以通话了

```bash
# host machine
echo -e "hello!" >&$talkfd

# client machine
read -r line <&$talkfd; print -r - $line
> hello!
```




---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>