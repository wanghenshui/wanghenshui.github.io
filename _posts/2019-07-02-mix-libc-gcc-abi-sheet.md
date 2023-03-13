---
layout: post
categories: language
title: libstdc++.so.6 version GLIBCXX_3.4.20 not found
tags: [c++]
---

  

---



> 屡次被stdc++ glibc 符号困扰。
>
> 从4.9开始记录。这个版本算是真正支持c++11的



| gcc版本 | libstdc++版本号     | glibc版本号    | cxxabi版本号  |
| ------- | ------------------- | -------------- | ------------- |
| 4.9     | libstdc++.so.6.0.20 | GLIBCXX_3.4.20 | CXXABI_1.3.8  |
| 5.1     | libstdc++.so.6.0.21 | GLIBCXX_3.4.21 | CXXABI_1.3.9  |
| 6.1     | libstdc++.so.6.0.22 | GLIBCXX_3.4.22 | CXXABI_1.3.10 |
| 7.1     | libstdc++.so.6.0.23 | GLIBCXX_3.4.23 | CXXABI_1.3.11 |
| 7.2     | libstdc++.so.6.0.24 | GLIBCXX_3.4.24 | CXXABI_1.3.11 |
| 8.1     | libstdc++.so.6.0.25 | GLIBCXX_3.4.25 | CXXABI_1.3.11 |
| 9.1     | libstdc++.so.6.0.26 | GLIBCXX_3.4.26 | CXXABI_1.3.12 |
| 9.2     | libstdc++.so.6.0.27 | GLIBCXX_3.4.27 | CXXABI_1.3.12 |
| 9.3     | libstdc++.so.6.0.28 | GLIBCXX_3.4.28 | CXXABI_1.3.12 |
| 10.1    | libstdc++.so.6.0.28 | GLIBCXX_3.4.28 | CXXABI_1.3.12 |



#### why

CI编译机是docker，内置了gcc4.8.5，在上层目录gcc5.4,不能网页端设定gcc版本，要用需要自己脚本适配。这是个踩坑记录



首先编译环境需要引入新的gcc

```bash
export PATH=$WORKSPACE/../buildbox/gcc-5.4.0/bin:$PATH
```

然后注意，gcc对应的libstdc++ abi不同, 不匹配就会遇到标题中的错误，

 ```bash
/lib64/libstdc++.so.6: version `GLIBCXX_3.4.20' not found
/lib64/libstdc++.so.6: version `CXXABI_1.3.8' not found
...
 ```



所以需要调整一下libso,gcc 版本与libstdc++对应关系如下

```
GCC 4.9.0: libstdc++.so.6.0.20
GCC 5.1.0: libstdc++.so.6.0.21
GCC 6.1.0: libstdc++.so.6.0.22
GCC 7.1.0: libstdc++.so.6.0.23
GCC 7.2.0: libstdc++.so.6.0.24
GCC 8.0.0: libstdc++.so.6.0.25
```

解决方法，改软链接
```bash
cp $WORKSPACE/../buildbox/gcc-5.4.0/lib64/libstdc++.so.6.0.21 /lib64/
cd /lib64/
rm -f libstdc++.so.6
ln -s libstdc++.so.6.0.21 libstdc++.so.6
ldconfig
```

到这里，普通makefile编译应该就没有问题了。

注意，此时 lib64下，libstdc++.so.6.0.21和libstdc++.so.6.0.19是共存的，如果依赖cmake的项目是不能删掉19的

对于cmake，cmake会探测到默认的gcc而不使用新的gcc，所以需要指定编译器

 ```bash
cmake . -DCXX_COMPILER_PATH=$WORKSPACE/../buildbox/gcc-5.4.0/bin/g++
 ```

但是，cmake会通过编译来判定工作环境，如果之前删掉了libstdc++.so.6.0.19，gcc4.8.5就不能工作，就会有编译错误

```shell
-- Check for working CXX compiler: /usr/bin/c++ -- broken
  CMake Error at cmake-3.10.3/share/cmake-3.10/Modules/CMakeTestCXXCompiler.cmake:45 (message):
    The C++ compiler  
      "/usr/bin/c++"  
    is not able to compile a simple test program.  
    It fails with the following output:  
      Change Dir: build/CMakeFiles/CMakeTmp      
      Run Build Command:"/usr/bin/gmake" "cmTC_2fb3b/fast"
      /usr/bin/gmake -f CMakeFiles/cmTC_2fb3b.dir/build.make CMakeFiles/cmTC_2fb3b.dir/build
      gmake[1]: Entering directory `build/CMakeFiles/CMakeTmp'
      Building CXX object CMakeFiles/cmTC_2fb3b.dir/testCXXCompiler.cxx.o
      /usr/bin/c++     -o CMakeFiles/cmTC_2fb3b.dir/testCXXCompiler.cxx.o -c /data/fuxi-task/workSpace/5d1b501bdf2fcc0001b69669/DFV-Redis_222652/build/CMakeFiles/CMakeTmp/testCXXCompiler.cxx
      Linking CXX executable cmTC_2fb3b
      cmake-3.10.3/bin/cmake -E cmake_link_script CMakeFiles/cmTC_2fb3b.dir/link.txt --verbose=1
      /usr/bin/c++       -rdynamic CMakeFiles/cmTC_2fb3b.dir/testCXXCompiler.cxx.o  -o cmTC_2fb3b 
      /usr/bin/ld: cannot find -lstdc++
      collect2: error: ld returned 1 exit status
      gmake[1]: *** [cmTC_2fb3b] Error 1
      gmake[1]: Leaving directory `build/CMakeFiles/CMakeTmp'
      gmake: *** [cmTC_2fb3b/fast] Error 2 
    CMake will not be able to correctly generate this project.
  Call Stack (most recent call first):
    CMakeLists.txt:2 (project)  
  -- Configuring incomplete, errors occurred!
```





再或者，`直接静态链接libstdc++就好了` 

```cmake
target_link_libraries(gemini-proxy -static-libgcc -static-libstdc++)
```



### ref

1. https://stackoverflow.com/questions/44773296/libstdc-so-6-version-glibcxx-3-4-20-not-found/46613656
2. https://gcc.gnu.org/onlinedocs/libstdc++/manual/abi.html


### contact

