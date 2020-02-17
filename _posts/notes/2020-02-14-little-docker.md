---
layout: post
title: docker cheatsheet
category: tools
tags: [docker]
---
{% include JB/setup %}

官网做好了图，挺好

https://www.docker.com/sites/default/files/d8/2019-09/docker-cheat-sheet.pdf



我经常用的就四个

`pull`

```shell
docker pull _linkxx_
```

`run`

```shell
docker run -it --privileged -d  _linkxx_
```

---

看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。

### 参考

- https://blog.csdn.net/fandroid/article/details/46817567

`exec`

```shell
docker exec -it 8b947752d9d4 bash
```

`stop`

```shell
docker container stop _container_name_
```

