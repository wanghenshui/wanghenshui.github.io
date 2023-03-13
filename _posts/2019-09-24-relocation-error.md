---
layout: post
categories: language
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



