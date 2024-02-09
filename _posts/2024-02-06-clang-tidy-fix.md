---
layout: post
title: clang-tidy auto fix 折腾记录
categories: [language]
tags: []
---



<!-- more -->

生成compile_database.json ，cmake / bazel有内置命令，如果是blade，就得借助其他工具生成

这里使用bear，用起来比较简单，编译折腾记录


gcc 8.3.1 低版本坑  undefined reference to `std::filesystem::__cxx11::path::_M_split_cmpts()'

默认不是c++17，没带上-lstdc++fs

https://github.com/rizsotto/Bear/issues/305

作者知道，但是不改，很好

我用的是Bear-3.1.3，改动类似上面说的 具体是

   vim source/bear/CMakeLists.txt

```cmake
target_link_libraries(bear
        bear_a)

+ target_link_libraries(bear stdc++fs)

```

   vim source/citnames/CMakeLists.txt

```cmake
target_link_libraries(citnames_a PUBLIC
        main_a
        citnames_json_a
        events_db_a
        domain_a
        result_a
        flags_a
        sys_a
        exec_a
        fmt::fmt
+        stdc++fs
        spdlog::spdlog)

```
   vim source/intercept/CMakeLists.txt

```cmake
target_link_libraries(intercept_a PUBLIC
        domain_a
        main_a
        events_db_a
        exec_a
        flags_a
        rpc_a
        sys_a
        result_a
+        stdc++fs
        spdlog::spdlog)
```
   vim source/libsys/CMakeLists.txt
```cmake
target_link_libraries(sys_a PUBLIC
        ${CMAKE_DL_LIBS}
        result_a
+        stdc++fs
        fmt::fmt
        spdlog::spdlog)

```

这四个文件


cmake需要3.15以上的，cmake有sh可以自己装一个

编译

cmake -DENABLE_UNIT_TESTS=OFF -DENABLE_FUNC_TESTS=OFF .
make all
make install
bear -- build_cmd 即可


装clang-tools-extra折腾记录

下载的linux ubuntu二进制不能使用，提示tinfo6找不到，版本低，只能从源码编译

SO上的答案都不准哈，一切以 https://llvm.org/docs/GettingStarted.html#getting-the-source-code-and-building-llvm 为准

编译

cmake -S llvm -B build -DLLVM_ENABLE_PROJECTS='clang-tools-extra‘

产物有200G，注意空间。其实我就想编译个clang-tools-extra中的clang-apply而已，没有直接编译的办法