---
layout: post
title: cmake cheatchart
categories: tools
tags: [cmake]
---
  

整理一下cmake遇到的问题

- could not found CMAKE_ROOT

  ```shell
  [root@host-192-168-1-36 cmake-3.14.4]# cmake --version
  CMake Error: Could not find CMAKE_ROOT !!!
  CMake has most likely not been installed correctly.
  Modules directory not found in
  /usr/local/bin
  Segmentation fault
  ```

  

解决办法，执行`hash -r` 原因见参考链接



---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。

### 参考

- <https://stackoverflow.com/questions/18615451/cmake-missing-modules-directory>







