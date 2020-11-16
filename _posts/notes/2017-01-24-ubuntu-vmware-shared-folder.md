---
layout: post
title: advanced metaprogramming in classic c++ 1.1 templates （2）总结
category: translation
tags : [c++,template]
---

  

---



这个问题困扰我这工作日最后一天。由于搜索姿势不对怎么也没搜到解决办法。最后琢磨出方法之后，也看到了两个帖子。。

http://blog.csdn.net/cindy_cheng/article/details/50456977

http://blog.csdn.net/kurosakimaon/article/details/53575301

第一个帖子的评论解决了我得问题。

第二个帖子和我的场景一模一样要是早点看见就好了。

两种方法是一样的。

总而言之

安装 `open-vm-tools-dkms` 

使用命令：

```bash
sudo mount -t fuse.vmhgfs-fuse .host:/ /mnt/hgfs -o allow_other
```

或

```bash
vmhgfs-fuse .host:/ /mnt/hgfs
```

如果每次重启之后想让系统自动挂载  修改fstab在最后添加一行：

```bash
vi /etc/fstab
.host:/ /mnt/hgfs fuse.vmhgfs-fuse allow_other 0 0
```

---

看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。