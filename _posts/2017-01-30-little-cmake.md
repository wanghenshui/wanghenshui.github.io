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


### 参考

- <https://stackoverflow.com/questions/18615451/cmake-missing-modules-directory>



看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
![微信转账](https://wanghenshui.github.io/assets/wepay.png)
</details>




