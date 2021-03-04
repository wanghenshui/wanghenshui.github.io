---
layout: post
title: 常用快捷键/命令的整理/系统设定
categories: tools
tags: [linux, macos, windows, vscode, vim, shell, docker]
---


整理一下常用的命令行，不分平台，



## VIM

- G 跳到最后
- set foldmethod=indent "set default foldmethod
- zi 打开关闭折叠 "zv 查看此行 zm 关闭折叠 zM 关闭所有 zr 打开 zR 打开所有 zc 折叠当前行 zo 打开当前折叠 zd 删除折叠 zD 删除所有折叠
- / 查找 n下一个
  - 正则表达式，例如/vim$匹配行尾的"vim"
  - \c表示大小写不敏感查找，\C表示大小写敏感查找。/foo\c
  - set ignorecase  ~/.vimrc
- 替换 :{作用范围}s/{目标}/{替换}/{替换标志} %s/foo/bar/g会在全局范围(%)查找foo并替换为bar，所有出现都会被替换（g）
  - 作用范围
    - :s/foo/bar/g
    - :%s/foo/bar/g
    - :5,12s/foo/bar/g :.,+2s/foo/bar/g
  - 替换标志
    - 目标的第一次出现：:%s/foo/bar
    - i表示大小写不敏感查找，I表示大小写敏感 :%s/foo/bar/i
    - \#等效于模式中的\c（不敏感）或\C（敏感）:%s/foo\c/bar
    - c表示需要确认，例如全局查找"foo"替换为"bar"并且需要确 :%s/foo/bar/gc
    - 参考： [Vim中如何快速进行光标移](http://harttle.com/2015/11/07/vim-cursor.html)
- 1y lh 粘贴
- v模式 e选中 
- b w 前后走动
- 命令行 补全 ctrl l
- 插入模式补全 ctrl p

- grep

  - grep取反 grep -v ”ect“”
  
- Linux 

  - Ctrl + L清屏
  - mv filename(/*) -t directory 也有重命名功能
  
- du -a du -h
    - du -h --max-depth=1 常用，看一个目录
  - file libvswrtp.so 查询文件信息（查链接库版本一个小经验）ldd
  
- win

  - wslconfig /l  wslconfig /s ubuntu-18.04
  - win shirl S win10 截图
  - compmgmt.msc 计算机 管理
  - devmgmt.msc 设备管理器
  - win + break 直接调出系统设置
  - eventvwr
  - ie 卸载程序
  - Ctrl + Shift + Esc 任务管理器
  - alt space n
  - alt f4/alt space c
  - snipingtool
  - mspaint
  - ctrl + win +d /F4 虚拟桌面
  - ctrl + win + →
  - win + L 锁屏
  - 磁盘格式转换 convert h: /fs:ntfs
  - windows查看端口占用 `netstat -aon|findstr 25340` 最后一行就是进程id
  - windows 杀死进程，在任务管理找不到的前提下 taskkill /f /pid 13656
  
- bazel

    - 编译 bazel build //redis:* --copt="-g" --strip="never"

        - ```bash
            ## 参数项一次只能指定一个
            bazel build --copt="-O3" --copt="-fpic" --cxxopt="-std=c++11"
            ```

        - http://zhulao.gitee.io/blog/2019/04/05/%E7%BC%96%E8%AF%91%E6%9E%84%E5%BB%BA%E5%B7%A5%E5%85%B7-bazel/index.html 这个文档不错 什么时候用什么时候再看

        - 换编译器 --repo_env=CC=clang
        
        - 编译所有 bazel build ...
        
    - 测试 bazel test ...

         * `--nocache_test_results` may be required if you are trying to re-run a test without changing
           anything.
         * `--test_filter=<TestName>` to run a specific test (when test splits are not already in use)
         
    - 遇到bazel错误先看看路径是不是错了，或者文件名是不是错了

- MAC
    - 截图 command shift 4
    - 截图且复制到剪贴板 Shift+Control+Command+4
    - 截屏command shift 3
    - 截屏且复制到剪贴板 Shift+Control+Command+3
    - 打开新终端 command + T
    - 回到桌面 fn + f11 或者五个手指缩放(比较反人类，算了)
      - 设置触发角，我设置到了右下角，这样和windows行为一致
    - 终端分屏 cmd + d 取消 cmd + shift + d
    - 终端切换标签页 command + shift  + 左右箭头
    - 设置 /使用习惯
      - 鼠标 滚轮 去掉自然
      - sudo spctl --master-disable 设置信任
      - 邮件要按住ctrl
    
- VS

  - Ctrl+k Ctrl+f 对齐(format)
  - Ctrl+k Ctrl+c注释
  - Ctrl+k Ctrl+U 取消注释
  - F5 F9断点 F10 F11
  
- vscode 

    - 格式化代码 shift + alt + f 
    - 配置clang-format

- EverNote 

  - F10标签 F11笔记本列表 F9同步

  - 结合enter esc与方向键使用
  
- cmder

  - cmder /register all
  
- gdb
  - thread apply all bt
  - pstack
    - pstack在chroot下执行的进程，可能找不到符号，要到chroot下面的目录去执行pstack
      - https://nanxiao.me/linux-pstack/
  
- tar 
  
  - 对于xz文件 **tar xvJf  \**\*.tar.xz**
  
- mount
  
  - mount /dev/vdb target_dir
  
- scp 
  
  - scp local_file root@xx.xx.xx.xx:/root
  
- rpm -ivh xx.rpm

- 特殊场景
  - 查找体积较大的十个文件
    - du -hsx * | sort -rh | head -10
  - 端口占用 netstat|grep 11221
    - lsof -i :11221抓到对应的进程
  
- putty
  - alt enter退出全屏 在window behaviour里，勾选最后一个
    - [x] full screen on alt-enter
  - 小键盘设置，在terminal features 勾选 
    - [x] disable application keypad mode
  - 记得保存设置
  
- telnet 
  
  - 退出 ctrl  ]
  
- iptables
  
    - 查看端口 **cat  /etc/sysconfig/iptables**

- tex 

  ```tex
  \tiny
  \scriptsize
  \footnotesize
  \small
  \normalsize
  \large
  \Large
  \LARGE
  \huge
  \Huge
  ```

- git
  
  - git统计提交行数

```bash
git log --author="name"  --since=2019–01-01 --until=2020-01-01  --pretty=tformat: --numstat | awk '{ add += $1; subs += $2; loc += $1 -  $2 } END { printf "added lines: %s, removed lines: %s, total lines:  %s\n", add, subs, loc }'
```
-  整理commit git rebase -i HEAD~3

- 修改提交人 git commit --amend --author="NewAuthor <NewEmail@address.com>"

- ```shell
  git push <远程主机名> <本地分支名>:<远程分支名>
  git pull <远程主机名> <远程分支名>:<本地分支名> 
  ```
分支丢了或者head detached了或者错误覆盖了，不要慌，`git reflog`能找回来

  mac要装lfs brew install git-lfs
  
  设置拉取为变基 git config pull.rebase true
  
  git推送分支一定要设定 git config --global push.default current
  
  git设置保存密码 git config credential.helper store
  
  建议写个init脚本 https://github.com/wanghenshui/lazy-scripts/blob/master/scripts/git_config.sh
  
  比较两个文件夹

```bash
 diff -Nrq a b
```



列出目录几层的文件

```bash
tree -L 1
```

拆分 合并文件

```shell
split -b 10M data
cat x* > data & #加个&是因为输出可能把tmux标签污染，干脆就后台运行
```



## top命令 一图流

<p><img src="https://wanghenshui.github.io/assets/top.png" alt="" width="60%"></p>



## docker

官网做好了图，挺好

https://www.docker.com/sites/default/files/d8/2019-09/docker-cheat-sheet.pdf



我经常用的就几个

`清理`

```bash
docker system prune
# -a 能把所有的都删掉，包括overlay里头的。太大了
```

`pull`

```shell
docker pull _linkxx_
```

`run`

```shell
docker run -it --privileged -d  _linkxx_
docker run -it --privileged -d  _linkxx_ /bin/bash #run + exec 
```

有的镜像会在run的时候做一些动作，这个镜像不能通过run+exec分开使用，会报错

> docker: Error response from daemon: OCI runtime create failed: container_linux.go:345: starting container process caused "exec: \"nginx\": executable file not found in $PATH": unknown.

如果不能使用gdb,  命令行要加上`--cap-add=SYS_PTRACE --security-opt seccomp=unconfined` 

`exec`

```shell
docker exec -it commitid/_container_name_ bash
```

`stop`

```shell
docker container stop _container_name_
```

 `commit`

```bash
docker commit _container_name_ linkxx
```

拷贝文件

```shell
docker cp /root/xx _container_name_:/root/
```

hardcore_varahamihira是docker名字

`登陆`

```bash
docker login -u username -p password registry.xx.com
```



## 小工具 推荐

- 同步github gitee仓库 https://github.com/ShixiangWang/sync2gitee
- git diff工具，delta https://github.com/dandavison/delta 非常好用！为啥没有rust的时候没人做这个工具呢，是因为用c++写太麻烦吗？我要写一个！

- 图片压缩需求，网络限制，超过50k不让上传

- jpg by `jpegtran`

```bash
apt install libjpeg-progs
jpegtran -optimize image-20200402171439048.jpg
```



- png by  `optipng`

```bash
apt install optipng
optipng -o3 image-20200402172644242.png
```

o1 ~ o7 七个等级压缩





软件安装清单

|                | windows     | MacOS       | Ubuntu |
| -------------- | ----------- | ----------- | ------ |
| markdown       | typora      | typora      | typora |
| sftp可视化工具 | winscp      | transmit    |        |
| git管理工具    | tortoisegit | sourcetree  |        |
| 终端           | putty       |             |        |
| 画图           | drawio      | OmniGraffle |        |
| 写代码         | vscode      | vscode      |        |





## Tmux 快捷键 & 速查表

本文内容适用于 Tmux 2.3 及以上的版本，但是绝大部分的特性低版本也都适用，鼠标支持、VI 模式、插件管理在低版本可能会与本文不兼容。

启动新会话：

    tmux [new -s 会话名 -n 窗口名]

恢复会话：

```bash
tmux at [-t 会话名]
tmux a #恢复上一个回话
```

列出所有会话：

    tmux ls

关闭会话：

    tmux kill-session -t 会话名

关闭所有会话：

    tmux ls | grep : | cut -d. -f1 | awk '{print substr($1, 0, length($1)-1)}' | xargs kill

在 Tmux 中，按下 Tmux 前缀 `ctrl+b`，然后：

### 会话

    :new<回车>  启动新会话
    s           列出所有会话
    $           重命名当前会话

### 窗口 (标签页)

    c  创建新窗口
    w  列出所有窗口
    n  后一个窗口
    p  前一个窗口
    f  查找窗口
    ,  重命名当前窗口
    &  关闭当前窗口 **这个真的太难记了**

### 调整窗口排序

    swap-window -s 3 -t 1  交换 3 号和 1 号窗口
    swap-window -t 1       交换当前和 1 号窗口
    move-window -t 1       移动当前窗口到 1 号

### 窗格（分割窗口）

注意这个很常用，尤其是 o 可以和命令键一起连按，十分爽快

    %  垂直分割
    "  水平分割
    o  交换窗格
    x  关闭窗格
    ⍽  左边这个符号代表空格键 - 切换布局
    q 显示每个窗格是第几个，当数字出现的时候按数字几就选中第几个窗格
    { 与上一个窗格交换位置
    } 与下一个窗格交换位置
    z 切换窗格最大化/最小化

### 同步窗格

这么做可以切换到想要的窗口，输入 Tmux 前缀和一个冒号呼出命令提示行，然后输入：

```
:setw synchronize-panes
```

你可以指定开或关，否则重复执行命令会在两者间切换。
这个选项值针对某个窗口有效，不会影响别的会话和窗口。
完事儿之后再次执行命令来关闭。[帮助](http://blog.sanctum.geek.nz/sync-tmux-panes/)

### 调整窗格尺寸

如果你不喜欢默认布局，可以重调窗格的尺寸。虽然这很容易实现，但一般不需要这么干。这几个命令用来调整窗格：

    PREFIX : resize-pane -D          当前窗格向下扩大 1 格
    PREFIX : resize-pane -U          当前窗格向上扩大 1 格
    PREFIX : resize-pane -L          当前窗格向左扩大 1 格
    PREFIX : resize-pane -R          当前窗格向右扩大 1 格
    PREFIX : resize-pane -D 20       当前窗格向下扩大 20 格
    PREFIX : resize-pane -t 2 -L 20  编号为 2 的窗格向左扩大 20 格


​    
### 文本复制模式：

按下 `PREFIX-[` 进入文本复制模式。可以使用方向键在屏幕中移动光标。默认情况下，方向键是启用的。在配置文件中启用 Vim 键盘布局来切换窗口、调整窗格大小。Tmux 也支持 Vi 模式。要是想启用 Vi 模式，只需要把下面这一行添加到 .tmux.conf 中：

    setw -g mode-keys vi

启用这条配置后，就可以使用 h、j、k、l 来移动光标了。

想要退出文本复制模式的话，按下回车键就可以了。然后按下 `PREFIX-]` 粘贴刚才复制的文本。

一次移动一格效率低下，在 Vi 模式启用的情况下，可以辅助一些别的快捷键高效工作。

例如，可以使用 w 键逐词移动，使用 b 键逐词回退。使用 f 键加上任意字符跳转到当前行第一次出现该字符的位置，使用 F 键达到相反的效果。

    vi             emacs        功能
    ^              M-m          反缩进
    Escape         C-g          清除选定内容
    Enter          M-w          复制选定内容
    j              Down         光标下移
    h              Left         光标左移
    l              Right        光标右移
    L                           光标移到尾行
    M              M-r          光标移到中间行
    H              M-R          光标移到首行
    k              Up           光标上移
    d              C-u          删除整行
    D              C-k          删除到行末
    $              C-e          移到行尾
    :              g            前往指定行
    C-d            M-Down       向下滚动半屏
    C-u            M-Up         向上滚动半屏
    C-f            Page down    下一页
    w              M-f          下一个词
    p              C-y          粘贴
    C-b            Page up      上一页
    b              M-b          上一个词
    q              Escape       退出
    C-Down or J    C-Down       向下翻
    C-Up or K      C-Up         向下翻
    n              n            继续搜索
    ?              C-r          向前搜索
    /              C-s          向后搜索
    0              C-a          移到行首
    Space          C-Space      开始选中
                   C-t          字符调序

滚屏

``` 
C-b PageUp/PageDown
q退出滚屏
```





### 杂项：

    d  退出 tmux（tmux 仍在后台运行）
    t  窗口中央显示一个数字时钟
    ?  列出所有快捷键
    :  命令提示符

### 配置选项：

    # 鼠标支持 - 设置为 on 来启用鼠标(与 2.1 之前的版本有区别，请自行查阅 man page)
    * set -g mouse on
    
    # 设置默认终端模式为 256color
    set -g default-terminal "screen-256color"
    
    # 启用活动警告
    setw -g monitor-activity on
    set -g visual-activity on
    
    # 居中窗口列表
    set -g status-justify centre
    
    # 最大化/恢复窗格
    unbind Up bind Up new-window -d -n tmp \; swap-pane -s tmp.1 \; select-window -t tmp
    unbind Down
    bind Down last-window \; swap-pane -s tmp.1 \; kill-window -t tmp

### 参考配置文件（~/.tmux.conf）：

下面这份配置是我使用 Tmux 几年来逐渐精简后的配置，请自取。

```bash
# -----------------------------------------------------------------------------
# Tmux 基本配置 - 要求 Tmux >= 2.3
# 如果不想使用插件，只需要将此节的内容写入 ~/.tmux.conf 即可
# -----------------------------------------------------------------------------

# C-b 和 VIM 冲突，修改 Prefix 组合键为 Control-Z，按键距离近
set -g prefix C-z

set -g base-index         1     # 窗口编号从 1 开始计数
set -g display-panes-time 10000 # PREFIX-Q 显示编号的驻留时长，单位 ms
set -g mouse              on    # 开启鼠标
set -g pane-base-index    1     # 窗格编号从 1 开始计数
set -g renumber-windows   on    # 关掉某个窗口后，编号重排

setw -g allow-rename      off   # 禁止活动进程修改窗口名
setw -g automatic-rename  off   # 禁止自动命名新窗口
setw -g mode-keys         vi    # 进入复制模式的时候使用 vi 键位（默认是 EMACS）

# -----------------------------------------------------------------------------
# 使用插件 - via tpm
#   1. 执行 git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
#   2. 执行 bash ~/.tmux/plugins/tpm/bin/install_plugins
# -----------------------------------------------------------------------------

setenv -g TMUX_PLUGIN_MANAGER_PATH '~/.tmux/plugins'

# 推荐的插件（请去每个插件的仓库下读一读使用教程）
set -g @plugin 'seebi/tmux-colors-solarized'
set -g @plugin 'tmux-plugins/tmux-pain-control'
set -g @plugin 'tmux-plugins/tmux-prefix-highlight'
set -g @plugin 'tmux-plugins/tmux-resurrect'
set -g @plugin 'tmux-plugins/tmux-sensible'
set -g @plugin 'tmux-plugins/tmux-yank'
set -g @plugin 'tmux-plugins/tpm'

# tmux-resurrect
set -g @resurrect-dir '~/.tmux/resurrect'

# tmux-prefix-highlight
set -g status-right '#{prefix_highlight} #H | %a %Y-%m-%d %H:%M'
set -g @prefix_highlight_show_copy_mode 'on'
set -g @prefix_highlight_copy_mode_attr 'fg=white,bg=blue'

# 初始化 TPM 插件管理器 (放在配置文件的最后)
run '~/.tmux/plugins/tpm/tpm'

# -----------------------------------------------------------------------------
# 结束
# -----------------------------------------------------------------------------

```


---



### 参考

- mount <https://www.runoob.com/linux/linux-comm-mount.html>
- tar <https://blog.csdn.net/silvervi/article/details/6325698>
- <https://my.oschina.net/huxuanhui/blog/58119>
- scp <https://linuxtools-rst.readthedocs.io/zh_CN/latest/tool/scp.html>
- putty 保存设置<https://blog.csdn.net/tianlesoftware/article/details/5831605>
- tree https://www.jianshu.com/p/f117be185c6f
  - tree在markdown中格式会乱的解决办法，用 https://stackoverflow.com/questions/19699059/representing-directory-file-structure-in-markdown-syntax
- diff https://blog.csdn.net/longxj04/article/details/7033744
- Docker 
  - https://blog.csdn.net/fandroid/article/details/46817567
  - https://www.cnblogs.com/sparkdev/p/9177283.html
- https://www.zhihu.com/question/19779256  ytzong的答案不错。我在wsl上可以用上面的工具。对于压缩图片来说他那个cssgaga贼破，没法用
- 转自这里<https://gist.github.com/ryerh/14b7c24dfd623ef8edc7>
- 这里有个详细版教程<http://louiszhai.github.io/2017/09/30/tmux/>






---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>

```

```