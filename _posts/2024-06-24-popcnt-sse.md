---
layout: post
title: popcnt也能向量化？
categories: [language]
tags: []
---
<!-- more -->

popcnt指令本身也支持sse向量化了，但如果序列非常大 popcnt只能处理8B，怎么办

直观的方法就是把序列按照8B拆开，分段popcnt，或者，向量化？大块？

回忆一下上一篇，把count放在这里

```cpp
int count ( uint64_t x) {
    int v = 0;
    while (x != 0) {
        x &= x - 1;
        v ++;
    }
    return v;
}
```
当然编译器会优化成popcnt

## 考虑avx512，这个足够大了吧

chatgpt很快就能帮咱们实现一个

```c++
#include <immintrin.h>
#include <stdint.h>
#include <stdio.h>

// Function to perform popcnt using AVX-512 for 64-bit integers
void avx512_popcnt_epi64(const uint64_t *input, uint64_t *output, size_t size) {
    for (size_t i = 0; i < size; i += 8) { // Process 8 x 64-bit integers at a time
        __m512i data = _mm512_loadu_si512(&input[i]); // Load 512 bits (8 x 64-bit integers)
        __m512i result = _mm512_popcnt_epi64(data);   // Perform popcnt on each 64-bit integer
        _mm512_storeu_si512(&output[i], result);      // Store the results
    }
}
```

但很多硬件是不支持avx512的~~(比如arm)~~, 怎么办？模拟，只需要avx2就行

但数字大于512呢，怎么拆分呢？

## Harley-Seal算法 和 [Faster Population Counts Using AVX2 Instructions](https://arxiv.org/pdf/1611.07612)

如果没有avx512也可以avx2的话类似_mm256_shuffle_epi8也可以利用上

借助 PSHUFB可以多组popcnt 甚至可以自己主动划分组搞流水线 这里引入Harley-Seal算法

核心思想就是 Carry-Save Adder（CSA）：

给定三个数 a b c 那他们和可以分成两部分

```cpp
void CSA (uint64_t * h , uint64_t * l, uint64_t a , uint64_t b , uint64_t c) {
    uint64_t u = a ˆ b;
    *h = (a & b) | (u & c);
    *l = u ˆ c;
}
```

具体实现类似这样

```cpp
uint64_t harley_seal ( uint64_t * d , size_t size ) {
    uint64_t total = 0, ones = 0, twos = 0,
    fours = 0, eights = 0, sixteens = 0;
    uint64_t twosA , twosB , foursA , foursB , eightsA , eightsB ;
    for ( size_t i = 0; i < size - size % 16; i += 16) {
        CSA (& twosA , & ones , ones , d[i +0] , d[i +1]) ;
        CSA (& twosB , & ones , ones , d[i +2] , d[i +3]) ;
        CSA (& foursA , & twos , twos , twosA , twosB );
        CSA (& twosA , & ones , ones , d[i +4] , d[i +5]) ;
        CSA (& twosB , & ones , ones , d[i +6] , d[i +7]) ;
        CSA (& foursB , & twos , twos , twosA , twosB );
        CSA (& eightsA , & fours , fours , foursA , foursB );
        CSA (& twosA , & ones , ones , d[i +8] , d[i +9]) ;
        CSA (& twosB , & ones , ones , d[i +10] , d[i +11]) ;
        CSA (& foursA , & twos , twos , twosA , twosB );
        CSA (& twosA , & ones , ones , d[i +12] , d[i +13]) ;
        CSA (& twosB , & ones , ones , d[i +14] , d[i +15]) ;
        CSA (& foursB , & twos , twos , twosA , twosB );
        CSA (& eightsB , & fours , fours , foursA , foursB );
        CSA (& sixteens , & eights , eights , eightsA , eightsB );
        total += count ( sixteens );
    }
    total = 16 * total + 8 * count ( eights ) + 4 * count ( fours ) + 2 * count ( twos ) + count ( ones );
    for ( size_t i = size - size % 16 ; i < size ; i ++)
    total += count (d[i ]) ;
    return total ;
}
```

这个算法可以三个数驱动，那自然可以pipeline话 另外这个CSA也可以用avx2或者avx512重写

比如 avx2

```cpp
#include <immintrin.h>
#include <stdint.h>
#include <stddef.h>

// Carry-Save Adder (CSA) implementation using AVX2
void CSA(__m256i* h, __m256i* l, __m256i a, __m256i b, __m256i c) {
    __m256i u = _mm256_xor_si256(a, b);
    *h = _mm256_or_si256(_mm256_and_si256(a, b), _mm256_and_si256(u, c));
    *l = _mm256_xor_si256(u, c);
}

__m256i count ( __m256i v) {
    __m256i lookup =
        _mm256_setr_epi8 (0 , 1, 1, 2, 1, 2, 2, 3, 1, 2,
        2, 3, 2, 3, 3, 4, 0, 1, 1, 2, 1, 2, 2, 3,
        1, 2, 2, 3, 2, 3, 3, 4) ;
    __m256i low_mask = _mm256_set1_epi8 (0 x0f );
    __m256i lo = = _mm256_and_si256 (v , low_mask );
    __m256i hi = _mm256_and_si256 ( _mm256_srli_epi32
    (v , 4) , low_mask );
    __m256i popcnt1 = _mm256_shuffle_epi8 ( lookup ,
    lo );
    __m256i popcnt2 = _mm256_shuffle_epi8 ( lookup ,
    hi );
    __m256i total = _mm256_add_epi8 ( popcnt1 , popcnt2
    );
    return _mm256_sad_epu8 ( total ,
        _mm256_setzero_si256 () );
}

```

```cpp
uint64_t avx_hs ( __m256i * d , uint64_t size ) {
    __m256i total = _mm256_setzero_si256 () ;
    __m256i ones = _mm256_setzero_si256 () ;
    __m256i twos = _mm256_setzero_si256 () ;
    __m256i fours = _mm256_setzero_si256 () ;
    __m256i eights = _mm256_setzero_si256 () ;
    __m256i sixteens = _mm256_setzero_si256 () ;
    __m256i twosA , twosB , foursA , foursB ,
    eightsA , eightsB ;
    for ( uint64_t i = 0; i < size ; i += 16) {
        CSA (& twosA , & ones , ones , d[i], d[i +1]) ;
        CSA (& twosB , & ones , ones , d[i +2] , d[i +3]) ;
        CSA (& foursA , & twos , twos , twosA , twosB );
        CSA (& twosA , & ones , ones , d[i +4] , d[i +5]) ;
        CSA (& twosB , & ones , ones , d[i +6] , d[i +7]) ;
        CSA (& foursB ,& twos , twos , twosA , twosB );
        CSA (& eightsA ,& fours , fours , foursA , foursB );
        CSA (& twosA , & ones , ones , d[i +8] , d[i +9]) ;
        CSA (& twosB , & ones , ones , d[i +10] , d[i +11]) ;
        CSA (& foursA , & twos , twos , twosA , twosB );
        CSA (& twosA , & ones , ones , d[i +12] , d[i +13]) ;
        CSA (& twosB , & ones , ones , d[i +14] , d[i +15]) ;
        CSA (& foursB , & twos , twos , twosA , twosB );
        CSA (& eightsB , & fours , fours , foursA , foursB );
        CSA (& sixteens , & eights , eights , eightsA , eightsB );
        total = _mm256_add_epi64 ( total , count ( sixteens ));
    }
    total = _mm256_slli_epi64 ( total , 4) ;
    total = _mm256_add_epi64 ( total ,
        _mm256_slli_epi64 ( count ( eights ) , 3) );
    total = _mm256_add_epi64 ( total ,
        _mm256_slli_epi64 ( count ( fours ) , 2) );
    total = _mm256_add_epi64 ( total ,
        _mm256_slli_epi64 ( count ( twos ) , 1) );
    total = _mm256_add_epi64 ( total , count ( ones ));
    return _mm256_extract_epi64 ( total , 0)
        + _mm256_extract_epi64 ( total , 1)
        + _mm256_extract_epi64 ( total , 2)
        + _mm256_extract_epi64 ( total , 3) ;
}
```

好了，你大概已经明白这个算法了，avx512版本就不贴了，可以看libpopcnt代码

## 性能数据

[libpopcnt](https://github.com/kimwalisch/libpopcnt)

直接贴性能数据吧

<table>
  <tr align="center">
    <td><b>Algorithm</b></td>
    <td><b>32 B</b></td>
    <td><b>64 B</b></td>
    <td><b>128 B</b></td>
    <td><b>256 B</b></td>
    <td><b>512 B</b></td>
    <td><b>1024 B</b></td>
    <td><b>2048 B</b></td>
    <td><b>4096 B</b></td>
  </tr>
  <tr>
    <td>lookup-8</td> 
    <td>1.00</td>
    <td>1.00</td>
    <td>1.00</td>
    <td>1.00</td>
    <td>1.00</td>
    <td>1.00</td>
    <td>1.00</td>
    <td>1.00</td>
  </tr>
  <tr>
    <td>bit-parallel-mul</td>
    <td>1.41</td>
    <td>1.54</td>
    <td>1.63</td>
    <td>1.78</td>
    <td>1.60</td>
    <td>1.62</td>
    <td>1.63</td>
    <td>1.64</td>
  </tr>
  <tr>
    <td>builtin-popcnt</td> 
    <td><b>4.75</b></td>
    <td><b>6.36</b></td>
    <td><b>8.58</b></td>
    <td><b>8.55</b></td>
    <td>6.72</td>
    <td>7.60</td>
    <td>7.88</td>
    <td>7.94</td>
  </tr>
  <tr>
    <td>avx2-harley-seal</td> 
    <td>1.15</td>
    <td>1.85</td>
    <td>3.22</td>
    <td>4.17</td>
    <td><b>8.46</b></td>
    <td>10.74</td>
    <td>12.52</td>
    <td>13.66</td>
  </tr>
  <tr>
    <td>avx512-harley-seal</td> 
    <td>0.35</td>
    <td>1.49</td>
    <td>2.54</td>
    <td>3.83</td>
    <td>5.63</td>
    <td><b>15.12</b></td>
    <td><b>22.18</b></td>
    <td><b>25.60</b></td>
  </tr>
</table>

显然 avx512-harley-seal 非常快

[sse-popcnt](https://github.com/WojciechMula/sse-popcount/blob/master/results/cannonlake/cannonlake-i3-8121U-gcc-8.3.1.rst)的结论差不多，就不贴数据了

## 算法厉害，但是用的上吗？

bitmap是经典场景了，但是bitmap不方便管理特长数据

roaringbitmap方案就是截断，优化思路和上面的论文思路相同

另外就是压缩了 [bitmagic 压缩bit](https://github.com/tlk00/BitMagic)

吸收了harley-seal的思想