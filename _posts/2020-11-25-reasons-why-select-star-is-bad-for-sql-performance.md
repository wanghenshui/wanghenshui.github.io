---
layout: post
title: (译) 为啥select*性能差
categories: [database]
tags: [sql]
---


---

> [原文链接](https://tanelpoder.com/posts/reasons-why-select-star-is-bad-for-sql-performance/)

作者这个经验是放在oracle上的，其他的关系型数据库有类似的判断

### 增加了网络的流量

那肯定啊，不需要的列/行被搜出来丢弃了，没有意义占用带宽影响延迟



### 增加调用方的CPU

计算量上去了



### 可能失去优化器优化的机会



```sql
SQL> @xi f2czqvfz3pj5w 0

SELECT * FROM soe_small.customers

---------------------------------------------------------------------------
| Id | Operation         | Name      | Starts | A-Rows | A-Time   | Reads |
---------------------------------------------------------------------------
|  0 | SELECT STATEMENT  |           |      1 |   1699K| 00:00.57 | 28475 |
|  1 |  TABLE ACCESS FULL| CUSTOMERS |      1 |   1699K| 00:00.57 | 28475 |
---------------------------------------------------------------------------
```



```sql
SQL> @xi 9gwxhcvwngh96 0

SELECT customer_id, dob FROM soe_small.customers

---------------------------------------------------------------------------------------
| Id  | Operation            | Name              | Starts | A-Rows | A-Time   | Reads |
---------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT     |                   |      1 |   1699K| 00:00.21 |  5915 |
|   1 |  INDEX FAST FULL SCAN| IDX_CUSTOMER_DOB2 |      1 |   1699K| 00:00.21 |  5915 |
---------------------------------------------------------------------------------------
```

一个是全表扫一个是索引扫，效率肯定不一样



### 省内存

```sql
SELECT * FROM soe_small.customers ORDER BY customer_since

Plan hash value: 2792773903

----------------------------------------------------------------------------------
| Id  | Operation          | Name      | Starts | A-Rows |   A-Time   | Used-Mem |
----------------------------------------------------------------------------------
|   0 | SELECT STATEMENT   |           |      1 |   1699K|00:00:02.31 |          |
|   1 |  SORT ORDER BY     |           |      1 |   1699K|00:00:02.31 |  232M (0)|
|   2 |   TABLE ACCESS FULL| CUSTOMERS |      1 |   1699K|00:00:00.24 |          |
----------------------------------------------------------------------------------
```



效果显而易见

```sql
SELECT customer_id,dob FROM soe_small.customers ORDER BY customer_since

Plan hash value: 2792773903

----------------------------------------------------------------------------------
| Id  | Operation          | Name      | Starts | A-Rows |   A-Time   | Used-Mem |
----------------------------------------------------------------------------------
|   0 | SELECT STATEMENT   |           |      1 |   1699K|00:00:00.59 |          |
|   1 |  SORT ORDER BY     |           |      1 |   1699K|00:00:00.59 |   67M (0)|
|   2 |   TABLE ACCESS FULL| CUSTOMERS |      1 |   1699K|00:00:00.13 |          |
----------------------------------------------------------------------------------
```



### 增加服务端cpu占用

首先，大量的数据的parse要浪费cpu，优化也要浪费cpu

```sql
SQL> SET AUTOTRACE TRACE STAT

SQL> SELECT * FROM widetable /* test100 */;

100 rows selected.

Statistics
----------------------------------------------------------
       2004  recursive calls
       5267  db block gets
       2458  consistent gets
          9  physical reads
    1110236  redo size
     361858  bytes sent via SQL*Net to client
        363  bytes received via SQL*Net from client
          2  SQL*Net roundtrips to/from client
          0  sorts (memory)
          0  sorts (disk)
        100  rows processed
        
        
SQL> SELECT id,col1 FROM widetable /* test101 */;

100 rows selected.

Statistics
----------------------------------------------------------
          5  recursive calls
         10  db block gets
         51  consistent gets
          0  physical reads
       2056  redo size
       1510  bytes sent via SQL*Net to client
        369  bytes received via SQL*Net from client
          2  SQL*Net roundtrips to/from client
          0  sorts (memory)
          0  sorts (disk)
        100  rows processed
```





作者写了个插件,[Session Snapper](https://tanelpoder.com/snapper/) ，可以抓时间



```sql
SQL> SELECT * FROM widetable /* test1 */;

SQL> @snapper stats,gather=t 5 1 1136
Sampling SID 1136 with interval 5 seconds, taking 1 snapshots...

-- Session Snapper v4.30 - by Tanel Poder ( http://blog.tanelpoder.com/snapper )

-----------------------------------------------------------------------------
    SID, USERNAME  , TYPE, STATISTIC                          ,         DELTA
-----------------------------------------------------------------------------
   1136, SYSTEM    , TIME, hard parse elapsed time            ,         78158
   1136, SYSTEM    , TIME, parse time elapsed                 ,         80912
   1136, SYSTEM    , TIME, PL/SQL execution elapsed time      ,           127
   1136, SYSTEM    , TIME, DB CPU                             ,         89580
   1136, SYSTEM    , TIME, sql execute elapsed time           ,          5659
   1136, SYSTEM    , TIME, DB time                            ,         89616


SQL> SELECT id,col1 FROM widetable /* test2 */;

-----------------------------------------------------------------------------
    SID, USERNAME  , TYPE, STATISTIC                          ,         DELTA
-----------------------------------------------------------------------------
   1136, SYSTEM    , TIME, hard parse elapsed time            ,          1162
   1136, SYSTEM    , TIME, parse time elapsed                 ,          1513
   1136, SYSTEM    , TIME, PL/SQL execution elapsed time      ,           110
   1136, SYSTEM    , TIME, DB CPU                             ,          2281
   1136, SYSTEM    , TIME, sql execute elapsed time           ,           376
   1136, SYSTEM    , TIME, DB time                            ,          2128
```



能看得出来这个parse时间上的节省



### 缓存的cursor 浪费内存

```sql
SQL> SELECT sharable_mem, sql_id, child_number, sql_text FROM v$sql 
     WHERE sql_text LIKE 'SELECT % FROM widetable';

SHARABLE_MEM SQL_ID        CHILD_NUMBER SQL_TEXT
------------ ------------- ------------ -------------------------------------
       19470 b98yvssnnk13p            0 SELECT id,col1 FROM widetable
      886600 c4d3jr3fjfa3t            0 SELECT * FROM widetable
```



作者还有个插件 [sqlmem.sql](https://github.com/tanelpoder/tpt-oracle/blob/master/sqlmem.sql) ，可以看具体的浪费（作者有点东西）



```sql
SQL> @sqlmem c4d3jr3fjfa3t
Show shared pool memory usage of SQL statement with SQL_ID c4d3jr3fjfa3t

CHILD_NUMBER SHARABLE_MEM PERSISTENT_MEM RUNTIME_MEM
------------ ------------ -------------- -----------
           0       886600         324792      219488


TOTAL_SIZE   AVG_SIZE     CHUNKS ALLOC_CL CHUNK_TYPE STRUCTURE            FUNCTION             CHUNK_COM            HEAP_ADDR
---------- ---------- ---------- -------- ---------- -------------------- -------------------- -------------------- ----------------
    272000        272       1000 freeabl           0 kccdef               qkxrMem              kccdef: qkxrMem      000000019FF49290
    128000        128       1000 freeabl           0 opn                  qkexrInitO           opn: qkexrInitO      000000019FF49290
    112568         56       2002 freeabl           0                      qosdInitExprCtx      qosdInitExprCtx      000000019FF49290
     96456         96       1000 freeabl           0                      qosdUpdateExprM      qosdUpdateExprM      000000019FF49290
     57320         57       1000 freeabl           0 idndef*[]            qkex                 idndef*[]: qkex      000000019FF49290
     48304         48       1000 freeabl           0 qeSel                qkxrXfor             qeSel: qkxrXfor      000000019FF49290
     40808         40       1005 freeabl           0 idndef               qcuAll               idndef : qcuAll      000000019FF49290
     40024      40024          1 freeabl           0 kafco                qkacol               kafco : qkacol       000000019FF49290
     37272        591         63 freeabl           0                      237.kggec            237.kggec            000000019FF49290
     16080       8040          2 freeabl           0 qeeRwo               qeeCrea              qeeRwo: qeeCrea      000000019FF49290
      8032       8032          1 freeabl           0 kggac                kggacCre             kggac: kggacCre      000000019FF49290
      8024       8024          1 freeabl           0 kksoff               opitca               kksoff : opitca      000000019FF49290
      3392         64         53 freeabl           0 kksol                kksnsg               kksol : kksnsg       000000019FF49290
      2880       2880          1 free              0                      free memory          free memory          000000019FF49290
      1152        576          2 freeabl           0                      16751.kgght          16751.kgght          000000019FF49290
      1040       1040          1 freeabl           0 ctxdef               kksLoadC             ctxdef:kksLoadC      000000019FF49290
       640        320          2 freeabl           0                      615.kggec            615.kggec            000000019FF49290
       624        624          1 recr           4095                      237.kggec            237.kggec            000000019FF49290
       472        472          1 freeabl           0 qertbs               qertbIAl             qertbs:qertbIAl      000000019FF49290
...

53 rows selected.
```

对比

```sql
SQL> @sqlmem b98yvssnnk13p
Show shared pool memory usage of SQL statement with SQL_ID b98yvssnnk13p

CHILD_NUMBER SHARABLE_MEM PERSISTENT_MEM RUNTIME_MEM
------------ ------------ -------------- -----------
           0        19470           7072        5560


TOTAL_SIZE   AVG_SIZE     CHUNKS ALLOC_CL CHUNK_TYPE STRUCTURE            FUNCTION             CHUNK_COM            HEAP_ADDR
---------- ---------- ---------- -------- ---------- -------------------- -------------------- -------------------- ----------------
      1640       1640          1 free              0                      free memory          free memory          00000001AF2B75D0
      1152        576          2 freeabl           0                      16751.kgght          16751.kgght          00000001AF2B75D0
      1040       1040          1 freeabl           0 ctxdef               kksLoadC             ctxdef:kksLoadC      00000001AF2B75D0
       640        320          2 freeabl           0                      615.kggec            615.kggec            00000001AF2B75D0
       624        624          1 recr           4095                      237.kggec            237.kggec            00000001AF2B75D0
       544        272          2 freeabl           0 kccdef               qkxrMem              kccdef: qkxrMem      00000001AF2B75D0
       472        472          1 freeabl           0 qertbs               qertbIAl             qertbs:qertbIAl      00000001AF2B75D0
       456        456          1 freeabl           0 opixpop              kctdef               opixpop:kctdef       00000001AF2B75D0
       456        456          1 freeabl           0 kctdef               qcdlgo               kctdef : qcdlgo      00000001AF2B75D0
       328         54          6 freeabl           0                      qosdInitExprCtx      qosdInitExprCtx      00000001AF2B75D0
       312        312          1 freeabl           0 pqctx                kkfdParal            pqctx:kkfdParal      00000001AF2B75D0
       296        296          1 freeabl           0                      unmdef in opipr      unmdef in opipr      00000001AF2B75D0
       256        128          2 freeabl           0 opn                  qkexrInitO           opn: qkexrInitO      00000001AF2B75D0
       256         42          6 freeabl           0 idndef               qcuAll               idndef : qcuAll      00000001AF2B75D0
       208         41          5 freeabl           0                      kggsmInitCompac      kggsmInitCompac      00000001AF2B75D0
       192         96          2 freeabl           0                      qosdUpdateExprM      qosdUpdateExprM      00000001AF2B75D0
       184        184          1 freeabl           0                      237.kggec            237.kggec            00000001AF2B75D0
...
```



1000:2



### 大对象LOB

浪费更多，（延迟上，带宽上，cpu上等等）



### 另外，不要在select *上select

❌

```sql
SELECT
    id, a 
FROM (
    SELECT * FROM tl
)
```

✅

```sql
SELECT * FROM (
    SELECT id, a FROM tl
)
```



PS作者还有很多工具 https://tanelpoder.com/psnapper/ https://0x.tools/ 有点意思，定位问题专家了学习关注一波



---

