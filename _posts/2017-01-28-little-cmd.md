---
layout: post
title: 常用快捷键/命令的整理/系统设定
categories: tools
tags: [linux]
---


整理一下常用的命令行，不分平台，tmux和vim不在此列



- grep

  - grep取反 grep -v ”ect“”
  
- Linux 

  - Ctrl + L清屏
  - mv filename(/*) -t directory 也有重命名功能
  
- du -a du -h
    - du -h --max-depth=1 常用，看一个目录
  - file libvswrtp.so 查询文件信息（查链接库版本一个小经验）ldd
  
- win

  - wslconfig /l  wslconfig /s ubuntu-18.04
  - win shirl S win10 截图
  - compmgmt.msc 计算机 管理
  - devmgmt.msc 设备管理器
  - win + break 直接调出系统设置
  - eventvwr
  - ie 卸载程序
  - Ctrl + Shift + Esc 任务管理器
  - alt space n
  - alt f4/alt space c
  - snipingtool
  - mspaint
  - ctrl + win +d /F4 虚拟桌面
  - ctrl + win + →
  - win + L 锁屏
  - 磁盘格式转换 convert h: /fs:ntfs
  - windows查看端口占用 `netstat -aon|findstr 25340` 最后一行就是进程id
  - windows 杀死进程，在任务管理找不到的前提下 taskkill /f /pid 13656
  
- bazel

    - 编译 bazel build //redis:* --copt="-g" --strip="never"

        - ```bash
            ## 参数项一次只能指定一个
            bazel build --copt="-O3" --copt="-fpic" --cxxopt="-std=c++11"
            ```

        - http://zhulao.gitee.io/blog/2019/04/05/%E7%BC%96%E8%AF%91%E6%9E%84%E5%BB%BA%E5%B7%A5%E5%85%B7-bazel/index.html 这个文档不错 什么时候用什么时候再看

        - 换编译器 --repo_env=CC=clang

- MAC
    - 截图 command shift 4
    - 截图且复制到剪贴板 Shift+Control+Command+4
    - 截屏command shift 3
    - 截屏且复制到剪贴板 Shift+Control+Command+3
    - 打开新终端 comand + T
    - 回到桌面 fn + f11 或者五个手指缩放(比较反人类，算了)
      - 设置触发角，我设置到了右下角，这样和windows行为一致
    - 终端分屏 cmd + d 取消 cmd + shift + d
    - 设置 /使用习惯
      - 鼠标 滚轮 去掉自然
      - sudo spctl --master-disable 设置信任
      - 邮件要按住ctrl
    
- VS

  - Ctrl+k Ctrl+f 对齐(format)
  - Ctrl+k Ctrl+c注释
  - Ctrl+k Ctrl+U 取消注释
  - F5 F9断点 F10 F11
  
- EverNote 

  - F10标签 F11笔记本列表 F9同步

  - 结合enter esc与方向键使用
  
- cmder

  - cmder /register all
  
- gdb
  - thread apply all bt
  - pstack
    - pstack在chroot下执行的进程，可能找不到符号，要到chroot下面的目录去执行pstack
      - https://nanxiao.me/linux-pstack/
  
- tar 
  
  - 对于xz文件 **tar xvJf  \**\*.tar.xz**
  
- mount
  
  - mount /dev/vdb target_dir
  
- scp 
  
  - scp local_file root@xx.xx.xx.xx:/root
  
- rpm -ivh xx.rpm

- 特殊场景
  - 查找体积较大的十个文件
    - du -hsx * | sort -rh | head -10
  - 端口占用 netstat|grep 11221
    - lsof -i :11221抓到对应的进程
  
- putty
  - alt enter退出全屏 在window behaviour里，勾选最后一个
    - [x] full screen on alt-enter
  - 小键盘设置，在terminal features 勾选 
    - [x] disable application keypad mode
  - 记得保存设置
  
- telnet 
  
  - 退出 ctrl  ]
  
- iptables
  
    - 查看端口 **cat  /etc/sysconfig/iptables**

- tex 

  ```tex
  \tiny
  \scriptsize
  \footnotesize
  \small
  \normalsize
  \large
  \Large
  \LARGE
  \huge
  \Huge
  ```

特殊需求

git统计提交行数

```bash
git log --author="name"  --since=2019–01-01 --until=2020-01-01  --pretty=tformat: --numstat | awk '{ add += $1; subs += $2; loc += $1 -  $2 } END { printf "added lines: %s, removed lines: %s, total lines:  %s\n", add, subs, loc }'
```
比较两个文件夹

```bash
 diff -Nrq a b
```



列出目录几层的文件

```bash
tree -L 1
```

拆分 合并文件

```shell
split -b 10M data
cat x* > data & #加个&是因为输出可能把tmux标签污染，干脆就后台运行
```



## top命令 一图流

![](https://wanghenshui.github.io/assets/top.png)





---



### 参考

- mount <https://www.runoob.com/linux/linux-comm-mount.html>
- tar <https://blog.csdn.net/silvervi/article/details/6325698>
- <https://my.oschina.net/huxuanhui/blog/58119>
- scp <https://linuxtools-rst.readthedocs.io/zh_CN/latest/tool/scp.html>
- putty 保存设置<https://blog.csdn.net/tianlesoftware/article/details/5831605>
- tree https://www.jianshu.com/p/f117be185c6f
  - tree在markdown中格式会乱的解决办法，用`````` https://stackoverflow.com/questions/19699059/representing-directory-file-structure-in-markdown-syntax
- diff https://blog.csdn.net/longxj04/article/details/7033744





---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>
 