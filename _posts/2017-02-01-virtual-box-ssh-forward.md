---
layout: post
title: 使用ssh访问 virtualbox，端口转发
categories: linux
tags: [virtualbox, ssh]
---
  

###  使用ssh访问 virtualbox，端口转发

前提环境 ubuntu 1804

#### 安装并开启sshd

apt install openssh-server

service start sshd



设置端口转发

<img src="https://wanghenshui.github.io/assets/vmportfoward.png" alt=""  width="100%">


使用ssh  -p 12345 root@localhost 访问即可

---

到此为止下面是牢骚

本来WSL都能搞定大部分场景，但是会把环境搞乱，虽说重装wsl也不麻烦

决定用docker来做实验环境，但发现业界都转k8s了？

不过docker确实很好用，准备用一用，但是wsl仅在hyper-v条件下才支持docker server daemon，基于这个条件，可以server命令启动，也可以安装docker for windows来导入，连接有很多就不列举了

有个[issue](https://github.com/Microsoft/WSL/issues/2291#issuecomment-383698720) 解释了半天也没说（或者我没看明白）不用hyper-v能不能用docker，所以只能搞虚拟机，还要在开个窗口麻烦，所以搞个转发wsl访问

---



