---
layout: post
categories: tools
title: 一个 Valgrind Address is on Thread's 1 stack 搞笑场景
tags: [valgrind]
---

  

---

用valgrind扫了一遍模块，有个函数附近报错 ，简单说这个函数是读取配置文件，解析配置文件保存，提示Address is on Thread's 1 stack，各种string越界

搜索了好几个案例，见参考链接，我仔细检查了这一系列函数，最后发现了问题。比较搞笑，就记录下来了

```c++
bool Config::Load()
{ 
  if (!FileExists(path_)) {
    return -1;
  }
  // read conf items

  char line[CONFLEN];
  char name[CONFLEN], value[CONFLEN];
  int line_len = 0;
  int name_len = 0, value_len = 0;
  int sep_sign = 0;
...
}
```

 这个CONFLEN的长度是

```c++
static const int CONFLEN = 1024 * 1024;
```

也就是说是物理意义上的栈溢出。。我还以为代码有bug写穿了。。改小，改成一半，告警就消失了

案例中的第四个链接有点类似

### ref

- 案例
  - https://stackoverflow.com/questions/18746774/valgrind-address-is-on-threads-1-stack
  - <https://sourceforge.net/p/valgrind/mailman/message/7842865/>
  - <http://valgrind.10908.n7.nabble.com/quot-Address-is-on-thread-1-s-stack-quot-td40864.html>
  - <https://ubuntuforums.org/showthread.php?t=2061965>


### contact

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>