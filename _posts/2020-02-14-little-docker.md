---
layout: post
title: docker cheatsheet
categories: tools
tags: [docker]
---
  

官网做好了图，挺好

https://www.docker.com/sites/default/files/d8/2019-09/docker-cheat-sheet.pdf



我经常用的就几个

`清理`

```bash
docker system prune
# -a 能把所有的都删掉，包括overlay里头的。太大了
```

`pull`

```shell
docker pull _linkxx_
```

`run`

```shell
docker run -it --privileged -d  _linkxx_
```

`exec`

```shell
docker exec -it commitid/_container_name_ bash
```

`stop`

```shell
docker container stop _container_name_
```

 `commit`

```bash
docker commit _container_name_ linkxx
```

拷贝文件

```shell
docker cp /root/xx _container_name_:/root/
```

hardcore_varahamihira是docker名字

`登陆`

```bash
docker login -u username -p password registry.xx.com
```



---


### 参考

- https://blog.csdn.net/fandroid/article/details/46817567
- https://www.cnblogs.com/sparkdev/p/9177283.html
---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
![微信转账](https://wanghenshui.github.io/assets/wepay.png)
</details>