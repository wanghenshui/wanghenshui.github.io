---
layout: post
title: (译)Data Structures Part 1 Bulk Data 
categories: [c++]
tags: [c++, data structure]
---
  

---

[toc]

作者把数据结构抽象了，不按照传统的什么树跳表堆什么的，根据用途来分类

- Bulk Data，也就是保存大量对象
- 弱引用/handle 对于Bulk Data的引用，即使对象没了也不会访问崩溃
- indices索引，访问特定Bulk Data的索引下表
- 数组的数组，保存一大堆Bulk Data的对象



其实这种和之前提到的index-handle有点像



这里介绍Bulk Data

作者也没有好的术语来概括他们，大概就是一组数据

- 游戏中所有的子弹
- 游戏中所有的树
- 游戏中所有的硬币

更抽象一点

- 所有游戏中的项目
- 所有游戏中的网格物品
- 所有游戏中的声音/音效

并且每种类型都有很多属性来判断，对于音效

- 所有能被播放的声音资源
- 当前播放的声音
- 所有能加到音轨上的音效（淡入淡出，摩擦声等等）

对于bulk data资源，我们假定

- 顺序不重要，当成set
- 每种类型都是POD类型，可以memcpy

可能某些场景顺序也有要求，比如需要渲染的对象，需要从头到尾渲染一遍

作者推荐把需要顺序的捞出来主动排序一下，而不是用个能排序的容器来保存，基数排序O(n) 也能接受（本来数据规模也不大）

至于POD类型，这里假定所有对象都是固定大小的POD，至于有的可能是链表结构这个放到后面数组的数组在讨论



这里还以声音资源来举例

```c
typedef struct {
    resource_t * resource; // 资源 引用
    uint64_t bytes;        // 资源大小
    uint64_t format;       // 资源的格式判断位
} sound_resource_t;

typedef struct {
    sound_resource_t *resource; // 正在播放的资源 引用
    uint64_t samples_played;    // 播放了的个数
    float volume;               // 音量
} playing_sound_t;

typedef struct {
    playing_sound_t *sound;     // 渐入的资源 引用
    float fade_from;            // 音量
    float fade_to;              // 音量
    double fade_from_ts;        // 什么时候开始渐入
    double fade_to_ts;          // 什么时候结束渐入
} playing_fade_t;
```



我们对于保存bulk data有这么几个要求

- 增删对象要快
- 对象的存储布局要cache-friendly，能更快的遍历
- 支持引用 
- allocator-friendly 对于分配器友好？不如说分配器要牛逼一点



最简单的实现bulk data的方法就是用一个静态数组或者一个vector

```c++
#define MAX_PLAYING_SOUNDS 1024
uint32_t num_playing_sounds;
playing_sound_t playing_sounds[MAX_PLAYING_SOUNDS];

// C++ vector
std::vector<playing_sound_t> playing_sounds;
```

如果你知道对象的个数用静态数组非常见到粗暴，如果不确定，可能浪费或者不够用

使用std::vector要注意一些问题

- DEBUG模式下 VS的std::vector非常慢，要注意设置 [_ITERATOR_DEBUG_LEVEL=0](https://docs.microsoft.com/en-us/cpp/standard-library/iterator-debug-level?view=vs-2019)
- std::vector用构造析构创建删除对象，在某些场景要比memcpy慢（应该指的搬迁）
- std::vector更难自省？？要比自己实现一个更难观测(stretchy弹性)

另外两者都不支持对象引用？？？





### 删除策略

如果a[i]被删，几种处理手段

- 搬迁后面的节点，覆盖空的slot 太浪费时间，除非你要保证顺序（尤其是erase）

- 直接搬迁最后面的，swap-and-pop

  ```c++
  std::swap(a[i], a[a.size() - 1]);
  a.pop_back();
  ```

  直接从后面分配，无脑

  - 更紧凑遍历更快
  - index会变，就会类似hashtable重整，属性全丢了

- 留着这个洞，后面直接分配这个 freelist 需要在用slot前检查

  - index信息没变
  - 遍历有洞会慢



作者建议各取所需，除非对遍历有强需求，否则第三种很简单，idindex信息也都在，使用更方便

<img src="https://ourmachinery.com/images/dsp1-bulk-data.jpg" style="zoom:33%;" />

可能最终维护框架长这个样子

```c++
// The objects that we want to store:
typedef struct {...} object_t;

// An item in the free list points to the next one.
typedef struct {
    uint32_t next_free;
} freelist_item_t;

// Each item holds either the object data or the free list pointer.
typedef union {
    object_t;
    freelist_item_t;
} item_t;

typedef struct {
    std::vector<item_t> items;
} bulk_data_t;

void delete_item(bulk_data_t *bd, uint32_t i) {
    // Add to the freelist, which is stored in slot 0.
    bd->items[i].next = bd->items[0].next;
    bd->items[0].next = i;
}

uint32_t allocate_slot(bulk_data_t *bd) {
    const uint32_t slot = bd->items[0].next;
    bd->items[0].next = bd->items[slot].next;
    // If the freelist is empty, slot will be 0, because the header
    // item will point to itself.
    if (slot) return slot;
    bd->items.resize(bd->items.size() + 1);
    return bd->items.size() - 1;
}
```



### weak pointers

直接用索引信息就可以了

加上版本信息就可以了

```c++
typedef struct {
    uint32_t id;         // index
    uint32_t generation; // 引用计数类似物，版本号？
} weak_pointer_t;


typedef struct {
    uint32_t generation;
    union {
        object_t;
        freelist_item_t;
    };
} item_t;
```



### 分配策略

std::vector本身有内存放大问题，如果满了就会扩容搬迁，这导致了一些问题

- 扩容造成的复制开销很大，可能造成延迟，这也是GC在游戏中会造成延迟的问题
- 内存浪费

解决办法

- 多组std::vector(这不是更浪费了么，哦是当内存池用的)
- 分配多组buffer，各种大小，然后选。可以mmap，不用堆内存
- 用 [use the virtual memory system to reserve a huge array](https://ourmachinery.com/post/virtual-memory-tricks/)  内存非常大

<img src="https://ourmachinery.com/images/dsp1-allocation-strategies.jpg" style="zoom:33%;" />

### 结构体数组还是数组结构体？

数组结构体

- 代码复杂
- 分配器压力，分配被迫分散到不同的数组，而不是分配一个大的
- 字段分散，得有index信息分别访问
- 增加了计算量
- cache不友好 但是紧凑起来可以加速simd
- 删除不友好



最终结论 bulk data保存最终方案

There are advantages and drawbacks to everything, but my default recommendation for storing bulk data for a new system would be:

> An array of structures, with “holes” and permanent pointers, either allocated as one single large VM reservation (if possible) or as an array of fixed size blocks (of 16 K or whatever is a good fit for your data).

And for the cases where you need really fast number crunching over the data:

> A structure of arrays of tightly packed objects, grouped 8 at a time for SIMD processing and allocated as one single large VM reservation, or as an array of fixed-size blocks.

结构体数组 方便管理

数组结构体，可以用simd加速，但是不好管理

### ref

- 我是看lobste上的推荐看的这篇文章https://ourmachinery.com/post/data-structures-part-1-bulk-data/ 
- 后面的系列
  - https://ourmachinery.com/post/data-structures-part-2-indices/
  - https://ourmachinery.com/post/data-structures-part-3-arrays-of-arrays/
- 作者自己实现类似vector的容器 值得一看https://ourmachinery.com/post/minimalist-container-library-in-c-part-1/



---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。