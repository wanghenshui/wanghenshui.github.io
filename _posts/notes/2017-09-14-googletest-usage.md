---
layout: post
category : c++
title: googletest使用记录
tags : [rocksdb,c++]
---
{% include JB/setup %}



有一个玩转GoogleTest的文章讲的不错，值得花点时间看下

最近使用googletest，新加了单元测试，就需要判定开关单元测试对原来测试的影响，做个记录

```c++
./db_iterator_test --gtest_filter=-DBIteratorTestInstance/DBIteratorTest.IterSeekBeforePrevWithTimestamp/*
```



gdb调试googletest 

```c++
 gdb --args  db_iterator_test --gtest_filter=-DBIteratorTestInstance/DBIteratorTest.IterSeekBeforePrevWithTimestamp/1

```

打断点有点麻烦，得nm抓符号名，一般都是类名/单元测试类名字_TestBody

测试案例集合

| **命令行参数**                  | **说明**                                                     |
| ------------------------------- | ------------------------------------------------------------ |
| --gtest_list_tests              | 使用这个参数时，将不会执行里面的测试案例，而是输出一个案例的列表。 |
| --gtest_filter                  | 对执行的测试案例进行过滤，支持通配符?    单个字符*    任意字符-    排除，如，-a 表示除了a :    取或，如，a:b 表示a或b 比如下面的例子：./foo_test 没有指定过滤条件，运行所有案例 ./foo_test --gtest_filter=* 使用通配符*，表示运行所有案例 ./foo_test --gtest_filter=FooTest.* 运行所有“测试案例名称(testcase_name)”为FooTest的案例 ./foo_test --gtest_filter=*Null*:*Constructor* 运行所有“测试案例名称(testcase_name)”或“测试名称(test_name)”包含Null或Constructor的案例。 ./foo_test --gtest_filter=-*DeathTest.* 运行所有非死亡测试案例。 ./foo_test --gtest_filter=FooTest.*-FooTest.Bar 运行所有“测试案例名称(testcase_name)”为FooTest的案例，但是除了FooTest.Bar这个案例 |
| --gtest_also_run_disabled_tests | 执行案例时，同时也执行被置为无效的测试案例。关于设置测试案例无效的方法为：在测试案例名称或测试名称中添加DISABLED前缀，比如：[![复制代码](http://common.cnblogs.com/images/copycode.gif)](javascript:void(0);)// Tests that Foo does Abc. TEST(FooTest, DISABLED_DoesAbc) { ![img](https://www.cnblogs.com/Images/dot.gif) }  class DISABLED_BarTest : public testing::Test { ![img](https://www.cnblogs.com/Images/dot.gif) };  // Tests that Bar does Xyz. TEST_F(DISABLED_BarTest, DoesXyz) { ![img](https://www.cnblogs.com/Images/dot.gif) }[![复制代码](http://common.cnblogs.com/images/copycode.gif)](javascript:void(0);) |
| --gtest_repeat=[COUNT]          | 设置案例重复运行次数，非常棒的功能！比如：--gtest_repeat=1000      重复执行1000次，即使中途出现错误。 --gtest_repeat=-1          无限次数执行。。。。 --gtest_repeat=1000 --gtest_break_on_failure     重复执行1000次，并且在第一个错误发生时立即停止。这个功能对调试非常有用。 --gtest_repeat=1000 --gtest_filter=FooBar     重复执行1000次测试案例名称为FooBar的案例。 |

 

测试案例输出

| **命令行参数**                                  | **说明**                                                     |
| ----------------------------------------------- | ------------------------------------------------------------ |
| --gtest_color=(yes\|no\|auto)                   | 输出命令行时是否使用一些五颜六色的颜色。默认是auto。         |
| --gtest_print_time                              | 输出命令行时是否打印每个测试案例的执行时间。默认是不打印的。 |
| --gtest_output=xml[:DIRECTORY_PATH\|:FILE_PATH] | 将测试结果输出到一个xml中。1.--gtest_output=xml:    不指定输出路径时，默认为案例当前路径。 2.--gtest_output=xml:d:\ 指定输出到某个目录  3.--gtest_output=xml:d:\foo.xml 指定输出到d:\foo.xml 如果不是指定了特定的文件路径，gtest每次输出的报告不会覆盖，而会以数字后缀的方式创建。xml的输出内容后面介绍吧。 |

 

\3. 对案例的异常处理

| **命令行参数**           | **说明**                                                     |
| ------------------------ | ------------------------------------------------------------ |
| --gtest_break_on_failure | 调试模式下，当案例失败时停止，方便调试                       |
| --gtest_throw_on_failure | 当案例失败时以C++异常的方式抛出                              |
| --gtest_catch_exceptions | 是否捕捉异常。gtest默认是不捕捉异常的，因此假如你的测试案例抛了一个异常，很可能会弹出一个对话框，这非常的不友好，同时也阻碍了测试案例的运行。如果想不弹这个框，可以通过设置这个参数来实现。如将--gtest_catch_exceptions设置为一个非零的数。注意：这个参数只在Windows下有效。 |

### reference

1. <http://www.cnblogs.com/coderzh/archive/2009/04/10/1432789.html>



看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。





