---
layout: post
title: 怎么阻止oom killer杀进程
categories: [debug]
tags: [linux, oom]

---

我的场景是gdb加载二进制，加载中直接被kill了。dmesg查看是oom killer干掉的。怎么禁止？

设置overcommit_memory

```bash
echo 2 > /proc/sys/vm/overcommit_memory
```

永远不overcommit，这样oom killer判定也就没啥用了

关于overcommit 解释一下

| vm.overcommit_memory | 含义                                                         |
| -------------------- | ------------------------------------------------------------ |
| 0                    | 表示内核将检查是否有足够的可用内存。如果有足够的可用内存，内存申请通过，否则内存申请失败，并把错误返回给应用进程 |
| 1                    | 表示内核允许超量使用内存直到用完为止                         |
| 2                    | 表示内核决不过量的(“never overcommit”)使用内存，即系统整个内存地址空间不能超过swap+50%的RAM值，50%是overcommit_ratio默认值，此参数同样支持修改 |



一般设置是0 也会影响到redis fork save db

Never commit判定

```bash
~#grep -i commit /proc/meminfo
CommitLimit:    18403480 kB
Committed_AS:   12516276 kB
```









---

### ref

- https://unix.stackexchange.com/questions/432171/completely-disable-oom-killer
- https://serverfault.com/questions/101916/turn-off-the-linux-oom-killer-by-default
- http://linuxperf.com/?p=102


---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>

