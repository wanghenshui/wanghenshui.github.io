---
layout: post
category: c++
title: relocation error version GLIBC_PRIVATE not defined in file 
tags: [c++]
---

  

---



拷贝库到某某目录，执行

```bash
 export LD_LIBRARY_PATH=$PWD:$LD_LIBRARY_PATH
```

导入，遇到了一堆类似的错误。做个记录。以后弄清楚

----

### ref

1. https://lists.debian.org/debian-glibc/2016/03/msg00153.html
2. https://askubuntu.com/questions/831592/glibc-private-not-defined-in-file-libc-so-6 貌似是resolv库拷贝引发的不兼容
3. https://unix.stackexchange.com/questions/367597/almost-no-commands-working-relocation-error-symbol-getrlimit-version-glibc 解决办法，`unset LD_LIBRARY_PATH`，没说具体原因
4. 打开vim提示错误`vim: : ATUSHHH-! : Error 43692576`的罪魁祸首 https://stackoverflow.com/questions/31155824/dlopen-in-libc-and-libdl



Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。