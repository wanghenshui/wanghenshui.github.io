---
layout: post
title: blog review 第二期
categories: [review]
tags: [postgresql, sqlite, materialize, mysql, boost, template]
---

准备把blog阅读和paper阅读都归一，而不是看一篇翻译一篇，效率太低了

后面写博客按照 paper review，blog review，cppcon review之类的集合形式来写，不一篇一片写了。太水了

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




---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>