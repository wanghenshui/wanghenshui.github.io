---
layout: post
title: cmake cheatchart
category: tools
tags: [cmake]
---
{% include JB/setup %}

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

看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。

### 参考

- <https://stackoverflow.com/questions/18615451/cmake-missing-modules-directory>







