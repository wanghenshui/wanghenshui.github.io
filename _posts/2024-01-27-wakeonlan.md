---
layout: post
title: 一个wakeonlan实践
categories: [linux]
tags: []
---


需求背景: 内网，机器不想手动按电源开机，如何通过控制来开机？

我首先想到的是买个智能开关，配置机器bios来电启动，然后手机控制智能开关来电

和群友聊天 A神告知了一个我不知道的功能 wake on lan，学吧，都是知识

<!-- more -->

机器是ubuntu 2204，首先确认一下网卡

ubuntu 新版本都是用network manager来控制网络，也就是nmcli

~~用ifconfig会被重置，注意~~

我的网络是这样的

```bash
➜  ~ nmcli
enp2s0：已连接 到 Wired connection 1
        "Intel I225-V"
        ethernet (igc), 70:70:FC:01:02:24, 硬件, mtu 1500
        ip4 默认
        inet4 192.168.3.32/24
        route4 192.168.3.0/24 metric 100
        route4 169.254.0.0/16 metric 1000
        route4 default via 192.168.3.1 metric 100
        inet6 fe80::7cad:3f3b:14b1:f5c2/64
        route6 fe80::/64 metric 1024

wlp4s0：已连接 到 b2708-5G
        "Intel 6 AX200"
        wifi (iwlwifi), 38:7A:0E:E0:A2:EF, 硬件, mtu 1500
        inet4 192.168.3.11/24
        route4 192.168.3.0/24 metric 600
        route4 default via 192.168.3.1 metric 600
        inet6 fe80::757d:2bd6:c4a2:8ff3/64
        route6 fe80::/64 metric 1024

lo：未托管
        "lo"
        loopback (unknown), 00:00:00:00:00:00, 软件, mtu 65536

DNS configuration:
        servers: 192.168.3.1
        domains: router.ctc
        interface: wlp4s0

```

注意得有个有线的网卡，记住这个网卡名字，ip mac信息 

比如我这个机器就是 enp2s0 192.168.3.32 70:70:FC:01:02:24

无线一般不支持wake on lan

然后通过ethtool查看，没有ethtool可以装一个

```bash

➜  ~ sudo ethtool enp2s0
[sudo] gtr6 的密码：
Settings for enp2s0:
	Supported ports: [ TP ]
	Supported link modes:   10baseT/Half 10baseT/Full
	                        100baseT/Half 100baseT/Full
	                        1000baseT/Full
	                        2500baseT/Full
	Supported pause frame use: Symmetric
	Supports auto-negotiation: Yes
	Supported FEC modes: Not reported
	Advertised link modes:  10baseT/Half 10baseT/Full
	                        100baseT/Half 100baseT/Full
	                        1000baseT/Full
	                        2500baseT/Full
	Advertised pause frame use: Symmetric
	Advertised auto-negotiation: Yes
	Advertised FEC modes: Not reported
	Speed: 1000Mb/s
	Duplex: Full
	Auto-negotiation: on
	Port: Twisted Pair
	PHYAD: 0
	Transceiver: internal
	MDI-X: off (auto)
	Supports Wake-on: pumbg
	Wake-on: g
        Current message level: 0x00000007 (7)
                               drv probe link
	Link detected: yes
```

注意wake on这两行 Supports Wake-on: pumbg Wake-on: g

这几个字母的意思

```bash
p 	Wake on PHY activity
u 	Wake on unicast messages
m 	Wake on multicast messages
b 	Wake on broadcast messages
g 	Wake on MagicPacket messages
```

如果是d 就是disable，重点关注是不是d，如果是d要执行一下

```bash
sudo ethtool --change enp2s0 wol g

```

然后再查看一下, 是g

这个配置可能重启就丢了，你可以重启一下重新查看是不是g，是g就可以通过wakeonlan唤醒了

测试一下

被唤醒机器，执行睡眠

```bash

sudo systemctl suspend
```


唤醒触发机器 mac，装一个wakeonlan，ip 192.168.3.2 （需要在同一个内网）

执行唤醒，以下两个命令均可以
```bash
wakeonlan -i 192.168.3.22  70:70:fc:01:02:24
#wakeonlan  70:70:fc:01:02:24
```

唤醒时间很长，一分钟？就可以登陆了

时间感觉长以前是按按钮，开机，现在是唤醒，开机，等待登陆，开机时间给人一种唤醒很慢的错觉

挺好用的，懒狗可以不点开机按钮了