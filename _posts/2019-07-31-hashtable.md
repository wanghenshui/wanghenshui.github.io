---
layout: post
title: (转)Lockfree Hashtable
categories: [language]
tags: [hashtable]
---

> 转自 http://spiritsaway.info/lockfree-hashtable.html



对于让hashtable变成无锁，主要要解决如下几个问题：

1. hash表的核心就是探查方法，开链法在插入节点的时候会引入动态内存分配的问题，这个是在无锁里面很棘手的问题，所以没有采取开链法，同时二次探查在无锁和缓存上面很不友好，所以使用的就是线性探查。因此我们首先要使得线性探查无锁化。
2. hash表插入的时候可能会导致过载。在STL的实现中是发现map内部装载率大于一定值时将map扩容。由于扩容的时候会出现迭代器失效的问题，所以这种方法在无锁的时候压根不可行。所以很多实现是直接开一个新的当前表大小的干净副本，通过指针将所有副本链接起来。查询和插入的时候需要遍历所有的副本

## lockfree linear search

在preshing的[一篇文章](http://preshing.com/20130529/a-lock-free-linear-search/)里面谈到了无锁线性扫描的实现，这里定义了一个基本的`Entry`:

```
struct Entry
{
    mint_atomic32_t key;
    mint_atomic32_t value;
};
Entry *m_entries;
```

在这个`Entry`里，我们规定如果`key`的值为0，则代表这个`entry`还没有被使用，所以插入的时候禁止传入为0的`key`。

在此结构之下，定义的`setItem`操作如下：

```
void ArrayOfItems::SetItem(uint32_t key, uint32_t value)
{
    for (uint32_t idx = 0;; idx++)
    {
        uint32_t prevKey = mint_compare_exchange_strong_32_relaxed(&m_entries[idx].key, 0, key);
        if ((prevKey == 0) || (prevKey == key))
        {
            mint_store_32_relaxed(&m_entries[idx].value, value);
            return;
        }
    }
}
```

类似的`getItem`的操作如下：

```
uint32_t ArrayOfItems::GetItem(uint32_t key)
{
    for (uint32_t idx = 0;; idx++)
    {
        uint32_t probedKey = mint_load_32_relaxed(&m_entries[idx].key);
        if (probedKey == key)
            return mint_load_32_relaxed(&m_entries[idx].value);
        if (probedKey == 0)
            return 0;          
    }
}
```

现在的疑问在于，这里的原子操作使用的都是`relaxed`语义，这个语义在`x86`上基本等于没有任何作用，如何在使得`SetItem`里的第8行能够被`GetItem`的第7行可见。事实上这压根做不到，因为一个线程在执行到`SetItem`的第8行之前被换出， 然后另外一个线程执行到了`GetItem`的第7行，这里读取的还是老的值。除了这种情况之外，还可能出现`SetItem`里的`CAS`操作并没有将数据更新的通知发放到其他的`core`上去，然而第8行的`store`操作已经被另外一个执行`GetItem`的线程可见的情况，此时`GetItem`会返回0。这两种情况都是合法的，因为在多线程中读取数据的时机是不确定的，因此读取老数据也是正常的。甚至可以说在没有通知机制的情况下，是不是最新根本没有意义。如果要实现`publish-listen`的机制，则需要在`SetItem`的时候将一个原子的`bool`变量设置为`True`，同时这个`Store`操作要使用`Release`语义，同时另外一个线程在`CAS`这个值的时候，要使用`Acquire`语义。

```
// Shared variables
char message[256];
ArrayOfItems collection;

void PublishMessage()
{
    // Write to shared memory non-atomically.
    strcpy(message, "I pity the fool!");

    // Release fence: The only way to safely pass non-atomic data between threads using Mintomic.
    mint_thread_fence_release();

    // Set a flag to indicate to other threads that the message is ready.
    collection.SetItem(SHARED_FLAG_KEY, 1)
}
```

这样才能使得数据更改完并通知完之后，另外一方能够得到最新数据。因此，当前设计的无锁`hashtable`在多线程上唯一做的事情就是防止了多个线程对同一个`entry`同时做`SetItem`操作。

preshing对`SetItem`有一个优化：减少不必要的`CAS`操作。在原来的实现中会遍历所有的元素去执行`CAS`操作，其实只有`key == 0 or key == my_key`的时候我们才需要去做`CAS`。所以这里的优化就是预先作一次`load`，发现可以去`set`的时候才去`CAS`。

```
void ArrayOfItems::SetItem(uint32_t key, uint32_t value)
{
    for (uint32_t idx = 0;; idx++)
    {
        // Load the key that was there.
        uint32_t probedKey = mint_load_32_relaxed(&m_entries[idx].key);
        if (probedKey != key)
        {
            // The entry was either free, or contains another key.
            if (probedKey != 0)
                continue;           // Usually, it contains another key. Keep probing.

            // The entry was free. Now let's try to take it using a CAS.
            uint32_t prevKey = mint_compare_exchange_strong_32_relaxed(&m_entries[idx].key, 0, key);
            if ((prevKey != 0) && (prevKey != key))
                continue;       // Another thread just stole it from underneath us.

            // Either we just added the key, or another thread did.
        }

        // Store the value in this array entry.
        mint_store_32_relaxed(&m_entries[idx].value, value);
        return;
    }
}
```

## naive lockfree hashtable

在上面的`lockfree linear scan`的基础上，做一个`lockfree hashtable`还是比较简单的。这里定义了三个函数`intergerHash, SetItem, GetItem`：

```
inline static uint32_t integerHash(uint32_t h)
{
    h ^= h >> 16;
    h *= 0x85ebca6b;
    h ^= h >> 13;
    h *= 0xc2b2ae35;
    h ^= h >> 16;
    return h;
}
```

这个`hash`函数的来源是[MurmurHash3’s integer finalizer](https://code.google.com/p/smhasher/wiki/MurmurHash3) ， 据说这样可以让每一位都起到差不多的作用。

```
void HashTable1::SetItem(uint32_t key, uint32_t value)
{
    for (uint32_t idx = integerHash(key);; idx++)
    {
        idx &= m_arraySize - 1;

        // Load the key that was there.
        uint32_t probedKey = mint_load_32_relaxed(&m_entries[idx].key);
        if (probedKey != key)
        {
            // The entry was either free, or contains another key.
            if (probedKey != 0)
                continue;           // Usually, it contains another key. Keep probing.

            // The entry was free. Now let's try to take it using a CAS.
            uint32_t prevKey = mint_compare_exchange_strong_32_relaxed(&m_entries[idx].key, 0, key);
            if ((prevKey != 0) && (prevKey != key))
                continue;       // Another thread just stole it from underneath us.

            // Either we just added the key, or another thread did.
        }

        // Store the value in this array entry.
        mint_store_32_relaxed(&m_entries[idx].value, value);
        return;
    }
}
```

这里的`SetItem`正确工作有一个前提：整个`hashtable`不是满的，是满的一定会出错。

`GetItem`还是老样子：

```
uint32_t HashTable1::GetItem(uint32_t key)
{
    for (uint32_t idx = integerHash(key);; idx++)
    {
        idx &= m_arraySize - 1;

        uint32_t probedKey = mint_load_32_relaxed(&m_entries[idx].key);
        if (probedKey == key)
            return mint_load_32_relaxed(&m_entries[idx].value);
        if (probedKey == 0)
            return 0;          
    }
}
```

所谓的`publish`函数也是一样:

```
// Shared variables
char message[256];
HashTable1 collection;

void PublishMessage()
{
    // Write to shared memory non-atomically.
    strcpy(message, "I pity the fool!");

    // Release fence: The only way to safely pass non-atomic data between threads using Mintomic.
    mint_thread_fence_release();

    // Set a flag to indicate to other threads that the message is ready.
    collection.SetItem(SHARED_FLAG_KEY, 1)
}
```

至于`delete`操作，我们可以规定`value`是某个值的时候代表当前`entry`是被删除的，这样就可以用`SetItem(key, 0)`来模拟`delete`操作了。

## what about full

上面的无锁`hashtable`有一个致命缺陷，他没有处理整个`hashtable`满了的情况。为了处理满的情况，我们需要设置最大探查数量为当前`hashtable`的容量, 同时维护多个独立的`hashtable`，用一个无锁的链表将所有的`hashtable`的指针串联起来。如果最大探查数量达到上限，且当前`hashtable`没有下一个`hashtable`的指针，且则先建立一个新的`hashtable`，并挂载到无锁链表上，回到了有下一个`hashtable`的情况，然后对下一个`hashtable`做递归遍历。

这样做的确解决了扩容的问题，但是会出现性能下降的问题。后面过来的`key`在查询的时候会变得越来越慢，因为经常需要查询多层的`hashtable`。为了避免这个问题，出现了一种新的设计：每次添加一层`hashtable`的时候，都将容量扩大一倍，然后将上一个`hashtable`的内容拷贝到新的`hashtable`里。这个新的`hashtable`也叫做`main_hashtable`，由于我们无法在无锁的情况下把整个`hashtable`拷贝过去，所以采用`lazy`的方式，这个方式的步骤如下:

1. 维持一个`hashtable`的无锁链表，链表的头节点就叫做`main_hashtable`，所有的`hashtable`通过一个`next`指针相连；
2. 插入的时候如果发现当前的`main_hashtable`的装载因子（这个装载因子考虑了所有的`key`）已经大于0.5，则新建一个`hashtable`，然后插入到新的`hashtable`里；
3. 扩容的时候设置一个标志位，表明当前正在扩容，避免多个线程同时扩容，浪费资源，扩容期间所有等待扩容的线程都忙等待，扩容完成之后清除正在扩容的标记；
4. 新建立的`hashtable`是空的，大小为当前`main_hashtable`的两倍，每次新加入一个`hashtable`的时候都插入到头部，使之成为新的`main_hashtable`；
5. 查询的时候，根据这些`next`指针一直查询，直到最后一个`hashtable`；
6. 如果查询返回结果的时候发现返回结果的那个`hashtable`并不是`main_hashtable`，则把当前的`key value`对插入到`main_hashtable`里，这就是核心的`lazy copy`的过程

这个`lazy`的过程代码如下：

```
auto id = details::thread_id();
        auto hashedId = details::hash_thread_id(id);

        auto mainHash = implicitProducerHash.load(std::memory_order_acquire);
        for (auto hash = mainHash; hash != nullptr; hash = hash->prev) {
            // Look for the id in this hash
            auto index = hashedId;
            while (true) {      // Not an infinite loop because at least one slot is free in the hash table
                index &= hash->capacity - 1;

                auto probedKey = hash->entries[index].key.load(std::memory_order_relaxed);
                if (probedKey == id) {
                    // Found it! If we had to search several hashes deep, though, we should lazily add it
                    // to the current main hash table to avoid the extended search next time.
                    // Note there's guaranteed to be room in the current hash table since every subsequent
                    // table implicitly reserves space for all previous tables (there's only one
                    // implicitProducerHashCount).
                    auto value = hash->entries[index].value;
                    if (hash != mainHash) {
                        index = hashedId;
                        while (true) {
                            index &= mainHash->capacity - 1;
                            probedKey = mainHash->entries[index].key.load(std::memory_order_relaxed);
                            auto empty = details::invalid_thread_id;
#ifdef MOODYCAMEL_CPP11_THREAD_LOCAL_SUPPORTED
                            auto reusable = details::invalid_thread_id2;
                            if ((probedKey == empty    && mainHash->entries[index].key.compare_exchange_strong(empty,    id, std::memory_order_relaxed)) ||
                                (probedKey == reusable && mainHash->entries[index].key.compare_exchange_strong(reusable, id, std::memory_order_acquire))) {
#else
                            if ((probedKey == empty    && mainHash->entries[index].key.compare_exchange_strong(empty,    id, std::memory_order_relaxed))) {
#endif
                                mainHash->entries[index].value = value;
                                break;
                            }
                            ++index;
                        }
                    }

                    return value;
                }
                if (probedKey == details::invalid_thread_id) {
                    break;      // Not in this hash table
                }
                ++index;
            }
        }
```

现在的核心则转移到了扩容的过程，扩容涉及到了动态内存分配和初始内容的填充，是比较耗的操作，所以要避免多个线程在争抢扩容的控制权。在moodycamel的设计里，是这样处理扩容的。

```
// Insert!
            auto newCount = 1 + implicitProducerHashCount.fetch_add(1, std::memory_order_relaxed);
            while (true)
            {
                if (newCount >= (mainHash->capacity >> 1) && !implicitProducerHashResizeInProgress.test_and_set(std::memory_order_acquire))
                {
                    // We've acquired the resize lock, try to allocate a bigger hash table.
                    // Note the acquire fence synchronizes with the release fence at the end of this block, and hence when
                    // we reload implicitProducerHash it must be the most recent version (it only gets changed within this
                    // locked block).
                    mainHash = implicitProducerHash.load(std::memory_order_acquire);
                    if (newCount >= (mainHash->capacity >> 1))
                    {
                        auto newCapacity = mainHash->capacity << 1;
                        while (newCount >= (newCapacity >> 1))
                        {
                            newCapacity <<= 1;
                        }
                        auto raw = static_cast<char*>((Traits::malloc)(sizeof(ImplicitProducerHash) + std::alignment_of<ImplicitProducerKVP>::value - 1 + sizeof(ImplicitProducerKVP) * newCapacity));
                        if (raw == nullptr)
                        {
                            // Allocation failed
                            implicitProducerHashCount.fetch_add(-1, std::memory_order_relaxed);
                            implicitProducerHashResizeInProgress.clear(std::memory_order_relaxed);
                            return nullptr;
                        }

                        auto newHash = new (raw) ImplicitProducerHash;
                        newHash->capacity = newCapacity;
                        newHash->entries = reinterpret_cast<ImplicitProducerKVP*>(details::align_for<ImplicitProducerKVP>(raw + sizeof(ImplicitProducerHash)));
                        for (size_t i = 0; i != newCapacity; ++i)
                        {
                            new (newHash->entries + i) ImplicitProducerKVP;
                            newHash->entries[i].key.store(details::invalid_thread_id, std::memory_order_relaxed);
                        }
                        newHash->prev = mainHash;
                        implicitProducerHash.store(newHash, std::memory_order_release);
                        implicitProducerHashResizeInProgress.clear(std::memory_order_release);
                        mainHash = newHash;
                    }
                    else
                    {
                        implicitProducerHashResizeInProgress.clear(std::memory_order_release);
                    }
                }

                // If it's < three-quarters full, add to the old one anyway so that we don't have to wait for the next table
                // to finish being allocated by another thread (and if we just finished allocating above, the condition will
                // always be true)
                if (newCount < (mainHash->capacity >> 1) + (mainHash->capacity >> 2))
                {
                    bool recycled;
                    auto producer = static_cast<ImplicitProducer*>(recycle_or_create_producer(false, recycled));
                    if (producer == nullptr)
                    {
                        implicitProducerHashCount.fetch_add(-1, std::memory_order_relaxed);
                        return nullptr;
                    }
                    if (recycled)
                    {
                        implicitProducerHashCount.fetch_add(-1, std::memory_order_relaxed);
                    }

#ifdef MOODYCAMEL_CPP11_THREAD_LOCAL_SUPPORTED
                    producer->threadExitListener.callback = &ConcurrentQueue::implicit_producer_thread_exited_callback;
                    producer->threadExitListener.userData = producer;
                    details::ThreadExitNotifier::subscribe(&producer->threadExitListener);
#endif

                    auto index = hashedId;
                    while (true)
                    {
                        index &= mainHash->capacity - 1;
                        auto probedKey = mainHash->entries[index].key.load(std::memory_order_relaxed);

                        auto empty = details::invalid_thread_id;
#ifdef MOODYCAMEL_CPP11_THREAD_LOCAL_SUPPORTED
                        auto reusable = details::invalid_thread_id2;
                        if ((probedKey == empty    && mainHash->entries[index].key.compare_exchange_strong(empty, id, std::memory_order_relaxed)) ||
                            (probedKey == reusable && mainHash->entries[index].key.compare_exchange_strong(reusable, id, std::memory_order_acquire)))
                        {
#else
                        if ((probedKey == empty    && mainHash->entries[index].key.compare_exchange_strong(empty, id, std::memory_order_relaxed)))
                        {
#endif
                            mainHash->entries[index].value = producer;
                            break;
                        }
                        ++index;
                    }
                    return producer;
                }

                // Hmm, the old hash is quite full and somebody else is busy allocating a new one.
                // We need to wait for the allocating thread to finish (if it succeeds, we add, if not,
                // we try to allocate ourselves).
                mainHash = implicitProducerHash.load(std::memory_order_acquire);
            }
```

上面的第五行就是抢夺控制权的过程，进入扩容的条件就是当前装载因子已经大于0.5，且扩容标志位没有设置。

```
newCount >= (mainHash->capacity >> 1) && !implicitProducerHashResizeInProgress.test_and_set(std::memory_order_acquire)
```

扩容的时候设置一个标志位，相当于一个锁，扩容完成之后清空标志位。但是由于线程换出的存在，这个标志位可能导致其他线程永远抢不到控制权，进入无限死循环。所以这里又对没有抢夺到扩容控制权的线程，还有另外的一个判断，如果装载因子小于0.75，则直接尝试插入，不用管。

```
newCount < (mainHash->capacity >> 1) + (mainHash->capacity >> 2)
```

这个分支里还做了一些事情，就是当真正的获得了一个`implicit producer`之后，注册一个线程退出的`callback`，这个`callback`会把当前`producer`销毁，并在`hashtable`里删除对应的`key`。

最后剩下的一种情况就是：拿不到扩容所有权，且当前装载因子已经上了0.75，此时除了死循环没有办法，约等于死锁。这种情况很罕见，但是仍然可以构造出来：正在扩容的线程被换出。不知原作者如何处理这个情况。








---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>
