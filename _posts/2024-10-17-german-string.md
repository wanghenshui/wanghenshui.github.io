---
layout: post
title: german string
categories: [database]
tags: [design,string,prefix]
---

prefix计算，空间换时间


https://cedardb.com/blog/german_strings/

https://cedardb.com/blog/strings_deep_dive/


这里有来源介绍

umbra论文的来的，主要是为了小字符串 12B 做优化

<!-- more -->


## arrow

arrow

```text
* Short strings, length <= 12
  | Bytes 0-3  | Bytes 4-15                            |
  |------------|---------------------------------------|
  | length     | data (padded with 0)                  |

* Long strings, length > 12
  | Bytes 0-3  | Bytes 4-7  | Bytes 8-11 | Bytes 12-15 |
  |------------|------------|------------|-------------|
  | length     | prefix     | buf. index | offset      |
```

buf index表示第几个buffer 
buf内的[offset,offset+length) 表示字符串

https://pola.rs/posts/polars-string-type/

https://arrow.apache.org/docs/format/Columnar.html#variable-size-binary-view-layout


## 常规

还有一种常规设计

```text
* Short strings, length <= 12
  | Bytes 0-3  | Bytes 4-15                            |
  |------------|---------------------------------------|
  | length     | data (padded with 0)                  |

* Long strings, length > 12
  | Bytes 0-3  | Bytes 4-7  | Bytes 8-15 |
  |------------|------------|------------|
  | length     | prefix     |  ptr     |
```

比较直观
```c++
bool isEqual(data128_t a, data128_t b) {
    if (a.v[0] != b.v[0]) return false;
    auto len = (uint32_t) a.v[0];
    if (len <= 12) return a.v[1] == b.v[1];
    return memcmp((char*) a.v[1], (char*) b.v[1], len) == 0;
}
```

对于小字符串 能省非常多

不过std::string也有sso，对于小字符串，但是没有prefix优势/16B传参优势 


duckdb实现 duckdb/blob/main/src/include/duckdb/common/types/string_type.hpp
