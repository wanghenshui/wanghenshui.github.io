---
layout: post
title: 常用命令的整理
category: tools
tags: []
---
{% include JB/setup %}

整理一下常用的命令行，不分平台，tex和vim和tex不在此列



- grep

  - grep取反 grep -v ”ect“”
- Linux 

  - Ctrl + L清屏
  - mv filename(/*) -t directory 也有重命名功能

  - du -a du -h
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
- tar 
  - 对于xz文件 **tar xvJf  \**\*.tar.xz**
- mount
  - mount /dev/vdb target_dir
- scp 
  - scp local_file root@xx.xx.xx.xx:/root
- 特殊场景
  - 查找体积较大的十个文件
    - du -hsx * | sort -rh | head -10
  - 端口占用 netstat|grep 11221
    - lsof -i :11221抓到对应的进程

---

看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。

### 参考

- mount <https://www.runoob.com/linux/linux-comm-mount.html>
- tar <https://blog.csdn.net/silvervi/article/details/6325698>
- <https://my.oschina.net/huxuanhui/blog/58119>
- scp <https://linuxtools-rst.readthedocs.io/zh_CN/latest/tool/scp.html>







