---
layout: post
categories: language
title: subprocess一次挂死问题
tags: [python, subprocess]
---

  

---

用python脚本拉起后台进程，拉起的代码是这样的

```python
cmds = cmd.split("|")
previous_result, p = None, None
for c in cmds:
    p = subprocess.Popen(shlex.split(c), stdin=previous_result, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    previous_result = p.stdout
result, err = p.communicate()
```



我有两个二进制，一个二进制用的是glog做打印日志，默认输出到stderr，用这个拉起没有问题

另一个二进制使用的print打印日志，默认输出到stdout，用这个拉起会hang住



原因见参考链接<sup>1</sup> 默认是 `shell=True` , 如果调用了communicate，表示和stdout交互，除非显式输入EOF，否则会一直等待输入。解决方法就是加上`shell=False` ，不调用communicate

```python
subprocess.Popen(shlex.split(cmd), stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE, close_fds=True, shell=False)
```

这样输出到stdout的二进制也能拉起。
我考虑过调整日志输出，不输出到stdout, 太麻烦了。作罢



----

### ref

1. https://stackoverflow.com/questions/2408650/why-does-python-subprocess-hang-after-proc-communicate



看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>