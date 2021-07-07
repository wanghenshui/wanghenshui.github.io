---
layout: post
title: blog review 第七期
categories: [review]
tags: [shell, abi, tsdb, mrouter, reflect, rocksdb, todo]
---

准备把blog阅读和paper阅读都归一，而不是看一篇翻译一篇，效率太低了

后面写博客按照 paper review，blog review，cppcon review之类的集合形式来写，不一篇一片写了。太水了



<!-- more -->

一点私货：

以前格局小了，服务的概念很单一

上一次被启发是达哥的想法，rocksdb的compaction剥离出去由另一个服务去做。很印象深刻。这个想法的前提是文件底层是虚拟的文件系统(hdfs之类)，可以做这种hack

最近看公司里的各种服务组件，发现和之前的做法不太一样

比如备份，以前的服务非常简单，就是db进程/对象存储/管控平台三方面交互

备份的速度，备份对当前服务的影响，都是不可观测的。完全不能动态可控的。db服务提供一个打快照的接口，文件准备好，随便管控平台来取，然后传到对象存储里

公司里的设计是引入一个backup服务夹在管控平台和对象存储之间

backup感知db服务的状态，另外无法拿磁盘的文件，需要复制，所以db服务提供拷贝接口，这也是没有用户态文件系统的缺陷吧



之前做数据迁移，是有个部门专门转协议接入的。各种解析然后转然后重新写，这种效率是非常低下的。原来是做redis的毕竟大部分在内存，可能没有dump完整的rdb，所以迁移还是在线形式的

现在做迁移工具不是一个部门，是一个组件，留管控面的接入之后，直接传二进制，一般来说，rocksdb的文件，直接覆盖就完事了。如果是别的文件，通过对象存储中转一下，改写成rocksdb的文件，然后再倒入。这样的效率要比转上层协议的导入要快的多，如果是同类集群的迁移，这个逻辑也能完美复用。原来的做法是做个全备，然后再加载。类似上面的backup服务



brpc的bvar是个很有意思的东西，简单的采集metric信息

---

## [minikeyvalue](https://github.com/geohot/minikeyvalue)

用go实现的http kv todo:用c++重写

### [The Cache Replacement Problem](http://alexandrutopliceanu.ro/post/cache-replacement-problem/)

实现了各种cache并且压测，代码在[这里](https://github.com/topliceanu/cache/)，后面有机会用c++重写一下

其实现代的cache主要是抗scan污染，比如arc

[这里](https://github.com/anuj-rai-23/Adaptive-Replacement-Cache-ARC-Algorithm)有个arc cache的实现

## [Write a time-series database engine from scratch](https://nakabonne.dev/posts/write-tsdb-from-scratch/)

https://github.com/nakabonne/tstorage

todo

## [Dropping cache didn’t drop cache](https://blog.twitter.com/engineering/en_us/topics/open-source/2021/dropping-cache-didnt-drop-cache)

博主发现了内核最新的bug，一个多线程变量变动的问题，从cache释放入手，找到对应代码。挺细的



## [用 litmus 验证 x86 内存序](https://www.xargin.com/litmus-test/)

简单安装[herdtools](https://github.com/herd/herdtools7/)

```bash
#brew install opam
#opam init
opam install herdtools7
eval $(opam config env) #	执行这个加载到path不然找不到
```

具体操作看这里就行了http://diy.inria.fr/doc/litmus.html

## [高性能队列——Disruptor](https://tech.meituan.com/2016/11/18/disruptor.html)



几个c++实现

https://github.com/fsaintjacques/disruptor--/

https://github.com/Abc-Arbitrage/Disruptor-cpp

原理

https://leiyiming.com/2017/11/01/disruptor/

## [Tales From a Core File - Lessons from the Unix stdio ABI: 40 Years Later](https://fingolfin.org/blog/20200327/stdio-abi.html)

讲了一些可以学习的细节，作者也是写os的

-  APIs and ABIs 	api设计统一，结构体布局兼容保持abi
-  The History of stdio 比如FILE这种不透明指针设计，以及padding的使用，避免false sharing 以及改动数组会破坏ABI，慎重



# [Concurrent programming: Two techniques to avoid shared state](http://vmlens.com/articles/cp/2_techniques_to_avoid_shared_state/)

就是拷贝修改和异步更新，没啥东西



## [Why NOT to Build a Time-Series Database](https://medium.com/dataseries/why-not-to-build-a-time-series-database-e1e63a535357)

他们自己用redis和riak搭了个时序数据库，后来放弃了，很大的维护负担，还需要做迁移维护(S3等)



## [Dijkstra's in Disguise](https://blog.evjang.com/2018/08/dijkstras.html)

很多场景都是Dijkstra算法等延伸 图算法，Q-learning Physically-Based Rendering等等



## [A Flexible Reflection System in C++: Part 1](https://preshing.com/20180116/a-primitive-reflection-system-in-cpp-part-1/)

宏实现反射，具体原理就是注册结构信息

```c++
struct Node {
    std::string key;
    int value;
    std::vector<Node> children;

    REFLECT()      // Enable reflection for this type
};
///
struct TypeDescriptor_Struct : TypeDescriptor {
    struct Member {
        const char* name;
        size_t offset;
        TypeDescriptor* type;
    };

    std::vector<Member> members;

    TypeDescriptor_Struct(void (*init)(TypeDescriptor_Struct*)) : TypeDescriptor{nullptr, 0} {
        init(this);
    }
    TypeDescriptor_Struct(const char* name, size_t size, const std::initializer_list<Member>& init) : TypeDescriptor{nullptr, 0}, members{init} {
    }
    virtual void dump(const void* obj, int indentLevel) const override {
        std::cout << name << " {" << std::endl;
        for (const Member& member : members) {
            std::cout << std::string(4 * (indentLevel + 1), ' ') << member.name << " = ";
            member.type->dump((char*) obj + member.offset, indentLevel + 1);
            std::cout << std::endl;
        }
        std::cout << std::string(4 * indentLevel, ' ') << "}";
    }
};

#define REFLECT() \
    friend struct reflect::DefaultResolver; \
    static reflect::TypeDescriptor_Struct Reflection; \
    static void initReflection(reflect::TypeDescriptor_Struct*);
```



## 一个sparse set实现

```c++
#pragma once

#include <vector>
#include <type_traits>

template <typename T>
class SparseSet
{
	static_assert(std::is_unsigned<T>::value, "SparseSet can only contain unsigned integers");

private:
	std::vector<T> dense;	//Dense set of elements
	std::vector<T> sparse;	//Map of elements to dense set indices

	size_t size_ = 0;	//Current size (number of elements)
	size_t capacity_ = 0;	//Current capacity (maximum value + 1)

public:
	using iterator       = typename std::vector<T>::const_iterator;
	using const_iterator = typename std::vector<T>::const_iterator;
	
	iterator begin() 		{ return dense.begin(); }
	const_iterator begin() const 	{ return dense.begin(); }

	iterator end() 			{ return dense.begin() + size_; }
	const_iterator end() const 	{ return dense.begin() + size_; }

	size_t size() const 		{ return size_; }
	size_t capacity() const		{ return capacity_; }

	bool empty() const 		{ return size_ == 0; }

	void clear() 			{ size_ = 0; }

	void reserve(size_t u)
	{
		if (u > capacity_)
		{
			dense.resize(u, 0);
			sparse.resize(u, 0);
			capacity_ = u;
		}
	}

	bool has(const T &val) const
	{
		return val < capacity_ &&
			sparse[val] < size_ &&
			dense[sparse[val]] == val;
	}

	void insert(const T &val)
	{
		if (!has(val))
		{
			if (val >= capacity_)
				reserve(val + 1);

			dense[size_] = val;
			sparse[val] = size_;
			++size_;
		}
	}

	void erase(const T &val)
	{
		if (has(val))
		{
			dense[sparse[val]] = dense[size_ - 1];
			sparse[dense[size_ - 1]] = sparse[val];
			--size_;
		}
	}
};
```

这有个rust实现 https://github.com/bombela/sparseset

特定场景，key巨量不可接受，序列化其实保存成二进制其实还好



## [Memoize Commands or Bash Functions with Coprocs!      ](https://mbuki-mvuki.org/posts/2021-05-30-memoize-commands-or-bash-functions-with-coprocs/)

其实就是匿名管道小妙招，这种写法有点像go里的channel

这个命令bash4才支持，也就是2009年才支持, 比较新的linux应该都是4.2，应该是都支持的

```bash
#!/bin/bash

function rando-daemon {
    declare -A cache
    declare -a query
    local IFS=$'\t'
    while read -ra query; do
        if ! [[ -v "cache[${query[*]}]" ]]; then
            cache[${query[*]}]=$RANDOM
        fi
        printf '%s\n' "${cache[${query[*]}]}"
    done
}

rando() {
    local IFS=$'\t'
    local resp
    printf '%s\n' "$*" >&"${RANDO[1]}"
    read -r resp <&"${RANDO[0]}"
    printf '%s\n' "$resp"
}

coproc RANDO { rando-daemon; }

printf "%s\n" "$(rando butter bubbles)"
printf "%s\n" "$(rando butter bubbles)"

```

要留意coproc这个命令，对于记忆话shell变量会有点帮助，或者用到worker 模型会有点作用，或者cs模型，channel模型

这里引一下用法

> #### [COPROC基本语法](http://blog.lujun9972.win/blog/2018/04/26/%E5%B0%8F%E8%AE%AEbash%E4%B8%AD%E7%9A%84coproc/)
>
> COPROC的基本语法适用于当只需要有一个coprocess的情况，它的语法为
>
> ```
> coproc cmd [redirections]
> ```
>
> 这时与coprocess的输入/输出管道相连的句柄保存在 `$COPROC` 数组中，分别为 `${COPROC[1]}` 和 `${COPROC[0]}`
>
> 因此，你可以使用 `echo $data >&"${COPROC[1]}"` 来往coprocess中输入数据, 通过使用 `echo $data <&"${COPROC[0]}"` 来读取coprocess的输出数据。
>
> #### COPROC的扩展语法
>
> 当需要创建多个coprocess时，你就需要使用coproc的扩展语法了，因为它允许你为coprocess命名。
>
> ```
> coproc NAME {cmds} [redirections]
> ```
>
> 有没有觉得它跟bash中定义函数的语法 `function NAME {cmds}` 很类似？
>
> 这时与coprocess的输入/输出管道相连的句柄保存在 `$NAME` 数组中，分别为 `${NAME[1]}` 和 `${NAME[0]}`
>
> 对应的，你可以使用 `echo $data >&"${NAME[1]}"` 来往coprocess中输入数据, 通过使用 `echo $data <&"${NAME[0]}"` 来读取coprocess的输出数据。
>
> #### 关闭不需要的管道
>
> 若coprocess只需要输入句柄或输出句柄，则可以使用 `exec` 来关闭不需要的文件句柄
>
> ```
> exec {NAME[0]}>&-
> exec {NAME[1]}>&-
> ```
>
> #### 注意事项
>
> 使用coprocess虽然方便,但要当心coprocess由于输出缓存而导致的卡死。
>
> 比如下面这个例子
>
> ```
> coproc tr a b
> echo a >&"${COPROC[1]}"
> read var<&"${COPROC[0]}"
> ```
>
> 你的期望是第三句能够读出字符 `b` 作为 `var` 的值， 然而实际上执行到第三句话时会卡死。 这是因为 `tr` 命令缓存了输出的内容,而并未将其写到终端上来。
>
> 因此创建coprocess时一定小心，只能使用那些不会缓存输出的命令。 也正因为此，coprocess的使用范围其实也很受限，真要用来跟其他进程做交互的话，还是推荐使用 `expert` 比较好。

## [Scaling Memcache at Facebook](https://www.micahlerner.com/2021/05/31/scaling-memcache-at-facebook.html)

facebook是如何管理memcache集群的

### 降低延迟

mrouter接入+udp转发到memcache 降低tcp cost

memcache 客户端加上slide window 如果有大量的请求，超出的放到queue里，降低竞争进而降低延迟

### 降低压力

引入Lease 解决过期以及惊群，这里的鲸群指的是大量请求请求冷key，对请求加上lease，超过期限直接失败，让客户端重试

还有就是集群级别的管理了故障恢复之类的

## [A Deep dive into (implicit) Thread Local Storage](https://chao-tic.github.io/blog/2018/12/25/tls)



## [BetrFS: A Right-Optimized Write-Optimized File System](https://nan01ab.github.io/2018/08/BetrFS.html)

代码在这里https://github.com/oscarlab/betrfs

## [Analyzing Optimistic Concurrency Control Anomalies and Solutions](https://wangziqi2013.github.io/article/2018/03/21/Analyzing-OCC-Anomalies-and-Solutions.html)

##  待读

https://danilafe.com/blog/00_compiler_intro/ 用c++写函数式语言

https://github.com/VictoriaMetrics/VictoriaMetrics 高性能的时序数据库，技术和clickhouse差不多

https://github.com/DigitalChinaOpenSource/TiDB-for-PostgreSQL

 https://github.com/kelindar/column column存储，go写的

https://github.com/baidu/braft.git braft的文档值得读一下

https://github.com/afiodorov/radixmmap 用c++实现一下

https://github.com/stateright/stateright 一致性教研工具，原理是什么？


---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>
