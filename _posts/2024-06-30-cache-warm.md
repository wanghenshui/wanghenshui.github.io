---
layout: post
title: cache warm一例
categories:[database]
tags: [multi,database]
---

原文


https://johnnysswlab.com/latency-sensitive-applications-and-the-memory-subsystem-keeping-the-data-in-the-cache/

<!-- more -->


while循环，没干活，干活逻辑是数据访问，那没干活分支应该可以热数据

比如原来的逻辑

```cpp
td::unordered_map<int32_t, order> my_orders;
...
packet_t* p;
while(!exit) {
    p = get_packet();
    // If packet arrived
    if (p) {
        // Check if the identifier is known to us
        auto it = my_orders.find(p->id);
        if (it != my_orders.end()) {
            send_answer(p->origin, it->second);
        }
    }
}
```

while里是个干活逻辑，但是有个大的if，我们可以把这个if拆出来分成干活不干活两个逻辑

```cpp
std::unordered_map<int32_t, order> my_orders;
...
packet_t* p;
int64_t total_random_found = 0;
while(!exit) {
    // 增加个检查header 然后再判断packet，不满足就去warm
    // 如果header没满足，packet必不满足
    if (packet_header_arrived()) {
        p = get_packet();
        // If packet arrived
        if (p) {
            // Check if the identifier is known to us
            auto it = my_orders.find(p->id);
            if (it != my_orders.end()) {
                send_answer(p->origin, it->second);
            }
        }
    } else {
        // 不干活就Cache warming 
        auto random_id = get_random_id();
        auto it = my_orders.find(random_id);
        // 随便干点啥避免被编译器优化掉
        total_random_found += (it != my_orders.end());
    }
}
std::cout << "Total random found " << total_random_found << "\n";
```

当然这种cache warm不一定非得随机，有可能副作用

可以从历史值来用，有个词怎么说来着，启发式

硬件层也有cache warm 比如 [intel](https://johnnysswlab.com/wp-content/uploads/Introducing-Cache-Pseudo-Locking-to-Reduce-Memory-Access-Latency-Reinette-Chatre-Intel.pdf)

其实就是prefetch clflush那套，如果你知道具体访问哪个，那prefetch确实是比较高效的

amd也有 L3 Cache Range Reservation 不过没例子

作者测试了软件模拟cache warm，随机访问

数据，迭代多次的延迟，越小越好

| hashmap数据量 | 正常访问hashmap   | 没有访问的时候只warm 0| 没有访问的时候随机warm   |
| ----------------- | ---------------- | ----------------- | ----------------- |
| 1 K               | 226.1 (219.0)    | 213.3 (205.1)     | 132.5 (67.3)      |
| 4 K               | 324.7 (296.3)    | 350.7 (331.3)     | 140.1 (95.4)      |
| 16 K              | 396.8 (341.1)    | 389.1 (354.5)     | 208.7 (134.5)     |
| 64 K              | 425.5 (376.1)    | 416.0 (360.6)     | 232.1 (152.6)     |
| 256 K             | 514.2 (451.5)    | 473.3 (480.6)     | 338.8 (317.6)     |
| 1 M               | 599.8 (550.2)    | 615.1 (573.6)     | 466.3 (429.8)     |
| 4 M               | 702.1 (647.0)    | 619.7 (649.2)     | 531.3 (508.3)     |
| 16 M              | 756.7 (677.6)    | 668.8 (707.4)     | 543.2 (499.9)     |
| 64 M              | 769.1 (702.3)    | 735.9 (734.2)     | 641.0 (774.4)     |


能看到随机访问 随机warm效果显著


和群友讨论

yangbowen认为没用，prefetch有用，手动warm当cpu傻逼(我感觉他没看懂这个例子)

mwish给了一些prefetch的资料 https://www.cs.cmu.edu/~chensm/papers/hashjoin_tods_preliminary.pdf

大家接触的多的例子就是prefetch，这种模拟cache warm还是比较少见的