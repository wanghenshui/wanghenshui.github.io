---
layout: post
title: blog review 第二期
categories: [review]
tags: [postgresql, sqlite,todo, materialize, mysql, boost, template, clang, ast]
---

看tag知内容


<!-- more -->



## [How Materialize and other databases optimize SQL subqueries](https://scattered-thoughts.net/writing/materialize-decorrelation)

非关联子查询

```sql
select posts.id 
from posts 
where posts.user_id in (
    select users.id 
    from users
    where users.country = 'Narnia'
);
```

对应的查询计划

```text
 Hash Join  (cost=17.51..50.23 rows=2 width=4)
   Hash Cond: (posts.user_id = users.id)
   ->  Seq Scan on posts  (cost=0.00..28.60 rows=1560 width=8)
   ->  Hash  (cost=17.50..17.50 rows=1 width=4)
         ->  Seq Scan on users  (cost=0.00..17.50 rows=1 width=4)
               Filter: (country = 'Narnia'::text)
```

关联子查询

```sql
select 
  users.id, 
  (
      select count(*)
      from posts 
      where posts.user_id = users.id
  )
from users;
```

对应的查询计划

```text
Seq Scan on users  (cost=0.00..25550.00 rows=1000 width=12)
   SubPlan 1
     ->  Aggregate  (cost=25.52..25.54 rows=1 width=8)
           ->  Seq Scan on posts  (cost=0.00..25.50 rows=10 width=0)
                 Filter: (user_id = users.id)
```

注意这个subplan scan，这是关联子查询性能差的问题来源。对应这个，不同的数据库有一些列的解决方案



sqlite有个[文档说明，比较没有规律](https://www.sqlite.org/optoverview.html#subquery_flattening), 对于文章中的两条sql并没有优化作用

mysql/mariadb 的[处理规则](https://mariadb.com/kb/en/subquery-optimizations-map/)见下图，对于文章中的sql，优化了第一种

<img src="https://mariadb.com/kb/en/subquery-optimizations-map/+image/subquery-map-2013" alt=""  width="100%">

postgresql没找到关于子查询优化的文档，文中的示例就是pg跑出来的

**Oracle**, 有个 [文档](https://oracle.readthedocs.io/en/latest/sql/subqueries/inline-views-ctes.html) 和 [论文](https://www.researchgate.net/profile/Rafi_Ahmed4/publication/220538535_Enhanced_Subquery_Optimizations_in_Oracle/links/56eaee0808ae9dcdd82a5c93/Enhanced-Subquery-Optimizations-in-Oracle.pdf), 看起来并没有什么优化。作者没验证

**SQL Server** 有两篇论文 [2001](https://www.comp.nus.edu.sg/~cs5226/papers/subqueries-sigmod01.pdf)  [2007](https://www.cse.iitb.ac.in/infolab/Data/Courses/CS632/2014/2009/Papers/subquery-proc-elhemali-sigmod07.pdf) 能优化这两种场景

**CockroachDB** 引用了sql server的论文 [decorrelation rules](https://github.com/cockroachdb/cockroach/blob/master/pkg/sql/opt/norm/rules/decorrelate.opt) 也用了同样的优化手段

能把这个关联子查询转化

```text
  project
   ├── group-by
   │    ├── left-join (hash)
   │    │    ├── scan users
   │    │    ├── scan posts
   │    │    └── filters
   │    │         └── user_id = users.id
   │    └── aggregations
   │         └── count
   │              └── user_id
   └── projections
        └── count_rows
```

sql server的子查询优化，其实就是apply算子下推 具体可以看这篇文章 https://zhuanlan.zhihu.com/p/60380557

Materialize作为一个流式数据库不能直接下推apply算子，可能数据丢失，所以参考hyper论文，把input数据保留(flink sql应该类似)

[materialize](https://github.com/MaterializeInc/materialize) 代码值得看一看

对flink也有点好奇。不过flink java味太重了不想碰



## [PostgreSQL: What is a checkpoint?](https://www.cybertec-postgresql.com/en/postgresql-what-is-a-checkpoint/)

正常来说数据库写入流程是数据写入WAL，刷新buffer， buffer写回到磁盘

问题在于buffer不一定击中，可能已经回收了，这就导致WAL不是立即写入，这就导致这段时间可能出现问题，引入checkpoint manager来管理buffer，当WAL写到这个脏buffer的时候再回收，回收也不用立即回收，慢慢来，可以降低io占用

wal有两个参数MAX_WAL_SIZE(决定buffer大小)和MIN_WAL_SIZE(机器空闲，主动把WAL减小到这个程度)



## [ARCHITECTURE.md](https://matklad.github.io//2021/02/06/ARCHITECTURE.md.html)

建议大家都写architecture.md尤其点名夸奖rust-analyzer的[architecture.md](https://github.com/rust-analyzer/rust-analyzer/blob/d7c99931d05e3723d878bea5dc26766791fa4e69/docs/dev/architecture.md).



## [Speeding up SQL queries by orders of magnitude using UNION](https://www.foxhound.systems/blog/sql-performance-with-union/)

教你写sql



## 	[How to Read Assembly Language](https://wolchok.org/posts/how-to-read-assembly-language/)

教你读汇编

几个点

```c++
struct Vec2 {
    int64_t x;
    int64_t y;
    void debugPrint() const;
};

int64_t normSquared(Vec2 v) {
    v.debugPrint();
    return v.x * v.x + v.y * v.y;
}
```

对应的asm

```asm
        subq    $24, %rsp
        movq    %rdi, 8(%rsp)
        movq    %rsi, 16(%rsp)
        leaq    8(%rsp), %rdi
        callq   Vec2::debugPrint() const
        movq    8(%rsp), %rcx
        movq    16(%rsp), %rax
        imulq   %rcx, %rcx
        imulq   %rax, %rax
        addq    %rcx, %rax
        addq    $24, %rsp
        retq
```

为什么是24，多出来的8是什么？[frame pointer](https://en.wikipedia.org/wiki/Call_stack#FRAME-POINTER),可以通过-fno-omit-frame-pointer消除，但不建议，会丢调试信息



## [Debugging production: the LIAR method](https://www.linux.it/~ema/posts/production-debugging-liar-method/)

介绍bpftrace抓信息

```bash
#抓list信息
sudo bpftrace -l '*tcp*send*'
tracepoint:tcp:tcp_send_reset
kprobe:__traceiter_tcp_send_reset
kprobe:tcp_send_mss
kprobe:do_tcp_sendpages
kprobe:tcp_sendpage_locked
kprobe:tcp_sendpage
kprobe:tcp_sendmsg_locked
kprobe:tcp_sendmsg
[...]
#	指令，抓具体字段
sudo bpftrace -e 'kprobe:tcp_sendmsg {
    printf("pid=%d: size=%d\n", pid, arg2)
}'
Attaching 1 probe...
pid=764374: size=36
pid=764374: size=36
pid=633506: size=43
pid=633506: size=566
pid=633506: size=600
pid=633506: size=58
pid=633506: size=819
^C
#聚合
sudo bpftrace -e 'kprobe:tcp_sendmsg {
    @bytes[pid] = stats(arg2);
    print(@bytes);
}'
Attaching 1 probe...
@bytes[770234]: count 1, average 77, total 77

@bytes[770234]: count 1, average 77, total 77
@bytes[770237]: count 1, average 77, total 77
# 报告
 sudo bpftrace -e 'kprobe:tcp_sendmsg {
    @bytes[pid] = stats(arg2);
}'
Attaching 1 probe...
^C

@bytes[769042]: count 1, average 75, total 75
@bytes[769047]: count 1, average 75, total 75
@bytes[769052]: count 1, average 75, total 75
@bytes[769057]: count 1, average 75, total 75
@bytes[633506]: count 13, average 378, total 4915

#报告，十秒一抓
sudo bpftrace -e 'kprobe:tcp_sendmsg {
    @bytes[pid] = stats(arg2);
}

interval:s:10 {
    exit();
}'
```



## [系统设计](https://github.com/donnemartin/system-design-primer)

这得猴年马月才能看完，这么多

这里也有个系统面试 https://wizardforcel.gitbooks.io/gainlo-interview-guide/content/6.html

## [It’s not always obvious when tail-call optimization is allowed](https://quuxplusone.github.io/blog/2021/01/09/tail-call-optimization/)

讲尾递归调用优化(TCO)

尾递归调用优化的汇编是直接jmp到函数上，普通的调用是callq，可以看这个[例子](https://godbolt.org/z/vcY3v9)

为什么有时候会TCO有时候不会呢？

首先 C++ guarantees that every variable (within its lifetime) has a unique address

TCO是否优化取决于函数附近的变量用的栈能不能复用，变量能不能消除

这里的escape不可见，所以不能确定变量能不能优化，如果替换成这个

```c++
const int *addr_of_i;
void escape(const int& i) {
    addr_of_i = &i;
}
void bar() {
    int j;
    assert(&j != addr_of_i);
}
```

立刻全部优化掉。

不要期待TCO，如果可以，自己手写

```c++
int gcd(int x, int y) {
    if (x == 0) return y;
    return gcd(y % x, x);
}

int gcd(int x, int y) {
    while (x != 0) {
        std::tie(x, y) = std::tuple(y % x, x);
    }
    return y;
}
```



## TODO

- https://steveire.wordpress.com/2019/04/30/the-future-of-ast-matching-refactoring-tools-eurollvm-and-accu/
- https://steveire.wordpress.com/2021/02/14/ast-matchmaking-made-easy/




---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>