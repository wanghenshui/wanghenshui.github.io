---
layout: post
title: lmdb boltdb原理介绍
categories: database
tags: [lmdb. boltdb]
---

lmdb是基于mmap的。还好是嵌入式的小kv，选择mmap可以理解，不过不推荐

boltdb是借鉴lmdb的思想用go重写的，boltdb的资料非常多。



<!-- more -->

这里介绍一下lmdb

```text
┌───────────────────────┐
│       CURD/commit     │
├─────┬─────────┬───────┤
│ COW │   MVCC  │ TXN   │
├─────┴────────┬┴───────┤
│    B+ Tree   │ Locks  │
├──────────────┴────────┤
│    MMAP               │
└───────────────────────┘
```



读 mmap只读

写，write系统调用

> 下面简单的介绍一下该数据库的基本情况：
>
> 1 数据库在运行时需要创建一个环境mdb_env_open()，我们需要传入目录路径，并在目录下产生一个锁文件以及存储文件。
>
> 2 当环境创建完成后，我们便需要创建mdb_txn_begin()来创建事物，而该事物在同一个时间只能有一个线程来执行。
>
> 3 我们可以调用mdb_dbi_open()来打开已有的数据库。
>
> 4 使用mdb_get() 与mdb_put()操作键值对，而该KV通常会被表示为MDB_val结构，该结构有两个域，包括mv_size以及mv_data
>
> 由于LMDB使用0拷贝技术，且直接将数据攻disk映射到Memory中。
>
> 5 为了提升操作的执行效率，LMDB使用了游标机制，其能存储、获取或删除多个值。
>
> 6 LMDB使用了POSIX文件锁，当一个进程多次调用打开函数打开同一个文件的时候会产生问题。所以，LMDB对所有线程共享打开环境。
>
> 7 LMDB必须使用mdb_txn_commit()将事务提交，否则所有的操作均被丢弃。对于读操作来说，所有的游标不会被自动释放而在读写事务中所有游标被自动释放且无法复用。
>
> LMDB允许多个读操作同时进行而只允许一次写。一旦一个读写事务开始时，其他的操作将会被阻塞直到第一个进程完成。
>
> 8 mdb_get()与 mdb_put() 对于一个key对于多个value的情况，只会返回第一个value。
>
> 当需要一个key多值时，那么需要对MDB_DUPSORT进行设置
>
> 9 如果用户频繁开始或者结束读操作，那么LMDB会选择reset而不是清除重建。
>
> 10 对于读操作，结束后必须调用函数关闭游标并清除；

基本的api实现，以及流程

## 创建db流程

主要是这四个

```c
int  mdb_env_create(MDB_env **env);
int  mdb_env_set_mapsize(MDB_env *env, mdb_size_t size);
int  mdb_env_set_maxreaders(MDB_env *env, unsigned int readers);
int  mdb_env_open(MDB_env *env, const char *path, unsigned int flags, mdb_mode_t mode);
```

env创建主要是初始化共享内存相关的东西, 初始化fd，记录页大小之类的

```c
struct MDB_env {
    HANDLE      me_fd;      /**< The main data file */
    HANDLE      me_lfd;     /**< The lock file */
    HANDLE      me_mfd;     /**< For writing and syncing the meta pages */
    /** Failed to update the meta page. Probably an I/O error. */
#define MDB_FATAL_ERROR 0x80000000U
    /** Some fields are initialized. */
#define MDB_ENV_ACTIVE  0x20000000U
    /** me_txkey is set */
#define MDB_ENV_TXKEY   0x10000000U
    /** fdatasync is unreliable */
#define MDB_FSYNCONLY   0x08000000U

    uint32_t    me_flags;       /**< @ref mdb_env */
    unsigned int    me_psize;   /**< DB page size, inited from me_os_psize */
    unsigned int    me_os_psize;    /**< OS page size, from #GET_PAGESIZE */
    unsigned int    me_maxreaders;  /**< size of the reader table */
    /** Max #MDB_txninfo.%mti_numreaders of interest to #mdb_env_close() */
    volatile int    me_close_readers;
    MDB_dbi     me_numdbs;      /**< number of DBs opened */
    MDB_dbi     me_maxdbs;      /**< size of the DB table */
    MDB_PID_T   me_pid;     /**< process ID of this env */
    char        *me_path;       /**< path to the DB files */
    char        *me_map;        /**< the memory map of the data file */
    MDB_meta    *me_metas[NUM_METAS];   /**< pointers to the two meta pages */
    // 元数据列表，lmdb使用两个页面作为meta页面，因此其大小为2. meta页面的一个主要作用是
    // 用于保存B+Tree的root_page指针。其内部采用COW技术
    /*
      root page指针可能会被修改，因此使用两个不同的页面进行切换保存最新页面，
      类似于double-buffer设计。由此可知，虽然lmdb支持一个文件中多个B+Tree，
      由于meta页面的限制，其个数是有限的。
    */
    void        *me_pbuf;       /**< scratch area for DUPSORT put() */
    MDB_txninfo *me_txns;       /**< the memory map of the lock file or NULL */
    MDB_txn     *me_txn;        /**< current write transaction */
    /*
      me_txn，me_txns:目前环境中使用的事务列表，一个env对象归属于一个进程，一个进程
      可能有多个线程使用同一个env，每个线程可以开启一个事务，因此在一
      个进程级的env对象需要维护txn列表以了解目前多少个线程及事务在进行工作。
    */

    MDB_txn     *me_txn0;       /**< prealloc'd write transaction */
    size_t      me_mapsize;     /**< size of the data memory map */
    off_t       me_size;        /**< current file size */
    pgno_t      me_maxpg;       /**< me_mapsize / me_psize */
    MDB_dbx     *me_dbxs;       /**< array of static DB info */
    uint16_t    *me_dbflags;    /**< array of flags from MDB_db.md_flags */
    unsigned int    *me_dbiseqs;    /**< array of dbi sequence numbers */
    pthread_key_t   me_txkey;   /**< thread-key for readers */
    txnid_t     me_pgoldest;    /**< ID of oldest reader last time we looked */
    MDB_pgstate me_pgstate;     /**< state of old pages from freeDB */
#   define      me_pglast   me_pgstate.mf_pglast
#   define      me_pghead   me_pgstate.mf_pghead
    MDB_page    *me_dpages;     /**< list of malloc'd blocks for re-use */
    /** IDL of pages that became unused in a write txn */
    MDB_IDL     me_free_pgs;
    /** ID2L of pages written during a write txn. Length MDB_IDL_UM_SIZE. */
    // 可用页面，可用页面用于控制MVCC导致的文件大小膨胀，
    // 可用页面是指已经没有事务使用但是已经被修改，根据MVCC原理，其已经是旧版本的页面。


    /*
        对于需要查阅历史数据的数据库来说，比如说需要恢复到任意时刻的要求，
        所有的旧版本应该被保存，而对于只需要保持最新一致数据的数据库系统比
        如lmdb来说，这些页面是可以重用的，页面重用就可以有效避免物理文件的
        无限增大。free_pgs为当前写事务导致的可重用页面列表。
    */

    MDB_ID2L    me_dirty_list;
    /** Max number of freelist items that can fit in a single overflow page */
    // 脏页列表，是写事务已经修改过的但没有提交到物理文件中的所有页面列表。
    int         me_maxfree_1pg;
    /** Max size of a node on a page */
    unsigned int    me_nodemax;
#if !(MDB_MAXKEYSIZE)
    unsigned int    me_maxkey;  /**< max size of a key */
#endif
    int     me_live_reader;     /**< have liveness lock in reader table */
#ifdef _WIN32
    int     me_pidquery;        /**< Used in OpenProcess */
#endif
#ifdef MDB_USE_POSIX_MUTEX  /* Posix mutexes reside in shared mem */
#   define      me_rmutex   me_txns->mti_rmutex /**< Shared reader lock */
#   define      me_wmutex   me_txns->mti_wmutex /**< Shared writer lock */
#else
    mdb_mutex_t me_rmutex;
    mdb_mutex_t me_wmutex;
    /*
        锁表互斥所，lmdb可以支持多线程、多进程。多进程之间的同步访问通过系统级的互斥来达到。
        其mutex本身存在于系统的共享内存当中而非进程本身的内存，因此在进行读写页面时，首先访
        问锁表看看对应的资源是否有别的进程、线程在进行，有的话需要根据事务规则要求进行排队等待。
    */
#endif
    void        *me_userctx;     /**< User-settable context */
    // 用户数据，用户上下文数据，主要用于进行key比较时进行辅助。
    MDB_assert_func *me_assert_func; /**< Callback for assertion failures */
};


typedef struct MDB_meta {
        /** Stamp identifying this as an LMDB file. It must be set
         *  to #MDB_MAGIC. */
    uint32_t    mm_magic;
        /** Version number of this file. Must be set to #MDB_DATA_VERSION. */
    uint32_t    mm_version;
    // mm_version: 当前lock文件的version，是实现MVCC的重要成员，必须设置为MDB_DATA_VERSION.
    void        *mm_address;        /**< address for fixed mapping */
    size_t      mm_mapsize;         /**< size of mmap region */
    MDB_db      mm_dbs[CORE_DBS];   /**< first is free space, 2nd is main db */
    // mm_dbs: 数据库B+Tree根，同时保存两个，0为目前使用的可替代的root page指针，1为当前使用的主数据库。
    /** The size of pages used in this DB */
#define mm_psize    mm_dbs[FREE_DBI].md_pad
    /** Any persistent environment flags. @ref mdb_env */
#define mm_flags    mm_dbs[FREE_DBI].md_flags
    /** Last used page in the datafile.
     *  Actually the file may be shorter if the freeDB lists the final pages.
     */
    pgno_t      mm_last_pg;
    volatile txnid_t    mm_txnid;   /**< txnid that committed this page */
} MDB_meta;

typedef struct MDB_page {
#define mp_pgno mp_p.p_pgno
#define mp_next mp_p.p_next
    union {
        pgno_t      p_pgno; /**< page number */
        struct MDB_page *p_next; /**< for in-memory list of freed pages */
    } mp_p;
    uint16_t    mp_pad;         /**< key size if this is a LEAF2 page */
/** @defgroup mdb_page  Page Flags
 *  @ingroup internal
 *  Flags for the page headers.
 *  @{
 */
#define P_BRANCH     0x01       /**< branch page */
#define P_LEAF       0x02       /**< leaf page */
#define P_OVERFLOW   0x04       /**< overflow page */
#define P_META       0x08       /**< meta page */
#define P_DIRTY      0x10       /**< dirty page, also set for #P_SUBP pages */
#define P_LEAF2      0x20       /**< for #MDB_DUPFIXED records */
#define P_SUBP       0x40       /**< for #MDB_DUPSORT sub-pages */
#define P_LOOSE      0x4000     /**< page was dirtied then freed, can be reused */
#define P_KEEP       0x8000     /**< leave this page alone during spill */
/** @} */
    uint16_t    mp_flags;       /**< @ref mdb_page */
#define mp_lower    mp_pb.pb.pb_lower
#define mp_upper    mp_pb.pb.pb_upper
#define mp_pages    mp_pb.pb_pages
    union {
        struct {
            indx_t      pb_lower;       /**< lower bound of free space */
            indx_t      pb_upper;       /**< upper bound of free space */
        } pb;
        uint32_t    pb_pages;   /**< number of overflow pages */
    } mp_pb;
    indx_t      mp_ptrs[1];     /**< dynamic size */
} MDB_page;
```



mdb_env_set_mapsize可以重制mmap大小

```c
mdb_env_open
  mdb_fname_init //分配内存存fname，可以destory
  pthread_mutex_init
  env->me_free_pgs = mdb_midl_alloc(MDB_IDL_UM_MAX) //就是个数组/链表
  env->me_dirty_list = calloc(MDB_IDL_UM_SIZE, sizeof(MDB_ID2))
  mdb_env_setup_locks //这个针对readonly和其他场景处理不一样，如果是readonly的要到后面检测文件是否存在再去初始化lock
  mdb_env_open2 //同步meta
  	mdb_env_read_header //读meta，有个METADATA宏去转换buffer
   	  mdb_env_init_meta0 //空的，只赋值就可以了
    mdb_env_init_meta //调pwrite写meta pwrite=write+lseek
    mdb_env_map
      madvise(env->me_map, env->me_mapsize, MADV_RANDOM);//关掉预读,随机读，更快
    //debug mdb_env_pick_meta 
  mdb_fopen
```



>  内存映射的文件io过程（一次数据拷贝）
>
> 1. 调用mmap()（系统调用）分配逻辑地址。
> 2. 逻辑地址转换成物理地址。
> 3. 进程第一次访问ptr指向的内存地址，发生缺页中断。由中断处理函数将数据拷贝到相应的内存地址上。（一次数据拷贝）
> 4. 虚拟地址置换。
>
> - - lmdb使用mmap文件映射,不管这个文件存储实在内存上还是在持久存储上。
>
>   - - lmdb的所有读取操作都是通过mmap将要访问的文件只读的映射到虚拟内存中，直接访问相应的地址。
>
>     - 因为使用了read-only的mmap，同样避免了程序错误将存储结构写坏的风险。
>
>     - 写操作，则是通过write系统调用进行的，这主要是为了利用操作系统的文件系统一致性，避免在被访问的地址上进行同步。
>
>     - lmdb把整个虚拟存储组织成B+Tree存储,索引和值读存储在B+Tree的页面上（聚集索引）。
>
>     - LMDB中使用append-only B+树，其更新操作最终都会转换为B+树的物理存储的append操作，文件不支持内部的修改，只支持append。
>
>     - - append增加了存储开销，因为旧的数据依然存在。带来一个额外的好处就是，旧的链路依然存在，依然可以正常的访问，例如过去有个人持有了过去的root（root9）的指针，那么过去的整棵树都完整的存在



-  COW(Copy-on-write)写时复制

- - 如果有多个调用者（callers）同时要求相同资源（如内存或磁盘上的数据存储），他们会共同获取相同的指针指向相同的资源，直到某个调用者试图修改资源的内容时，系统才会真正复制一份专用副本（private copy）给该调用者，而其他调用者所见到的最初的资源仍然保持不变。

  - 因此多个调用者只是读取操作时可以共享同一份资源。

  - 优点

  - - 如果调用者没有修改该资源，就不会有副本（private copy）被创建。

-  当前读

- - 读取的是记录的最新版本，读取时还要保证其他并发事务不能修改当前记录，会对读取的记录进行加锁。

  - - 例如select lock in share mode(共享锁), select for update ; update, insert ,delete(排他锁)这些操作都是一种当前读

-  快照读

- - 快照读的实现是基于多版本并发控制，即MVCC，避免了加锁操作，降低了开销。 

-  MVCC(Multiversion concurrency control )多版并发本控制

- - 当MVCC数据库需要更新数据项时，它不会用新数据覆盖旧数据，而是将旧数据标记为已过时并在其他位置添加新版本。

  - - 因此存储了多个版本，但只有一个是最新版本。

  - MVCC通过保存数据的历史版本，根据比较版本号来处理数据的是否显示，从而达到读取数据的时候不需要加锁就可以保证事务隔离性的效果。

  - 数据库系统维护当前活跃的事务ID列表m_ids，其中最小值up_limit_id和最大值low_limit_id，被访问的事务ID：trx_id。

  - - 如果trx_id< up_limit_id，说明trx_id对应的事务在生成可读视图前已经被提交了，可以被当前事务访问
    - 如果trx_id> low_limit_id，说明事务trx_id生成可读视图后才生成的，所以不可以被当前事务访问到。
    - 如果up_limit_id <=trx_id<=  low_limit_id，判断trx_id是否在m_ids中，若在，则说明trix_id在生成可读视图时还处于活跃，不可以被访问到；弱国不在m_ids中，说明在生成可读视图时该事务已经被提交了，故可以被访问到。

-  MVCC/COW在LMDB中的实现

- - LMDB对MVCC加了一个限制，即只允许一个写线程存在，从根源上避免了写写冲突，当然代价就是写入的并发性能下降。

  - - 因为只有一个写线程，所以不会不需要wait日志、读写依赖队列、锁队列等一系列控制并发、事务回滚、数据恢复的基础工具。

  - MVCC的基础就是COW，对于不同的用户来说，若其在整个操作过程中不进行任何的数据改变，其就使用同一份数据即可。若需要进行改变，比如增加、删除、修改等，就需要在私有数据版本上进行，修改完成提交之后才给其他事务可见。

-  LMDB的事务实现

- - Atom（A）原子性：LMDB中通过txn数据结构和cursor数据结构的控制，通过将脏页列表放入  dirtylist中，当txn进行提交时再一次性统一刷新到磁盘中或者abort时都不提交保证事务要不全成功、要不全失败。对于长事务，若页面spill到磁盘，因为COW技术，这些页面未与整棵B-Tree的rootpage产生关联，因此后续的事务还是不能访问到这些页面，同样保证了事务的原子性。

  - Consistency(C)一致性： 有如上的操作,保证其数据就是一致的，不存在因为多线程同时写数据导致数据产生错误的情况。

  - Isolation（I）隔离性：事务隔离通过锁控制（MUTEX），LMDB支持的锁互斥是进程级别/线程级别，支持的隔离方式为锁表支持，读读之间不锁，写等待读完成之后开始，读等待写完成后开始。

  - Duration（D）持久性：，没有使用WAL、undo/redo log等技术来保证系统崩溃时数据库的可用性，其保证数据持续可用的技术是**COW技术和只有一线程写技术**。

  - - 假如LMDB或者系统崩溃时，只有读操作，那么数据本来就没有发生变化，因此数据将不可能遭到破坏。假如崩溃时，有一个线程在进行写操作，则只需要判断最后的页面号与成功提交到数据库中的页面号是否一致，若不一致则说明写操作没有完成，则最后一个事务写失败，数据在最后一个成功的页面前的是正确的，后续的属于崩溃事务的，不能用，这样就保证了数据只要序列化到磁盘则一定可用，要不其就是还没有遵循ACI原则序列化到磁盘。

  - 

## 增删查改

所有的CURD必须在txn之下,通过cursor穿起来

### 写

```c
mdb_put(MDB_txn *txn, MDB_dbi dbi, MDB_val *key, MDB_val *data, unsigned int flags)
  mdb_cursor_init(&mc, txn, dbi, &mx)
    mdb_xcursor_init0
    mdb_page_search
      mdb_node_search //MDB_page *mp = mc->mc_pg[mc->mc_top];拿到page 在page里二分找key
        mdb_node_read
          overflow mdb_page_get
      mdb_page_get //根据pgno查具体的page
      mdb_page_touch //标记脏页更新pgno插入b树
    mdb_page_search_root
      mdb_node_search
        mdb_page_get
          mdb_page_touch &&top移动
  mdb_cursor_put
```





## 杂项

valgrind的深入用法

```c
#ifdef USE_VALGRIND
#include <valgrind/memcheck.h>
#define VGMEMP_CREATE(h,r,z)    VALGRIND_CREATE_MEMPOOL(h,r,z)
#define VGMEMP_ALLOC(h,a,s) VALGRIND_MEMPOOL_ALLOC(h,a,s)
#define VGMEMP_FREE(h,a) VALGRIND_MEMPOOL_FREE(h,a)
#define VGMEMP_DESTROY(h)	VALGRIND_DESTROY_MEMPOOL(h)
#define VGMEMP_DEFINED(a,s)	VALGRIND_MAKE_MEM_DEFINED(a,s)
#else
#define VGMEMP_CREATE(h,r,z)
#define VGMEMP_ALLOC(h,a,s)
#define VGMEMP_FREE(h,a)
#define VGMEMP_DESTROY(h)
#define VGMEMP_DEFINED(a,s)
#endif
```

页大小？

```c
	/** Get the size of a memory page for the system.
	 *	This is the basic size that the platform's memory manager uses, and is
	 *	fundamental to the use of memory-mapped files.
	 */
#define	GET_PAGESIZE(x)	((x) = sysconf(_SC_PAGE_SIZE))
```



## 参考

1. https://github.com/LMDB/lmdb 代码
2. https://www.jianshu.com/p/6378082987ec
3. https://zhuanlan.zhihu.com/p/350141066


---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>

