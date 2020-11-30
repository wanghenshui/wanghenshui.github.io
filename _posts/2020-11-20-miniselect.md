---
layout: post
title: miniselect 一个选择算法库
categories: [algorithm]
tags: [c++, clickhouse, sort, miniselect]
---


---

> 这个库是作者用在clickhouse上的，抽出来做成公共库了。借着这个库重新复习一下选择/排序算法

选择算法，见图

| Name                                                         | Average                                                      | Best Case                                                    | Worst Case                                                   | Comparisons                                                  | Memory                                                       |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| [pdqselect](https://github.com/danlark1/miniselect/blob/main/include/miniselect/pdqselect.h) | [![\large O(n)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%28n%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(n)) | [![\large O(n)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%28n%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(n)) | [![\large O(n\log n)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%28n%5Clog+n%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(n\log+n)) | At least [![\large 2n](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+2n)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+2n). Random data [![\large 2.5n](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+2.5n)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+2.5n) | [![\large O(1)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%281%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(1)) |
| [Floyd-Rivest](https://github.com/danlark1/miniselect/blob/main/include/miniselect/floyd_rivest_select.h) | [![\large O(n)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%28n%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(n)) | [![\large O(n)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%28n%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(n)) | [![\large O(n^2 )](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%28n%5E2+%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(n^2+)) | Avg: [![\large n + \min(k, n - k) + O(\sqrt{n \log n})](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+n+%2B+%5Cmin%28k%2C+n+-+k%29+%2B+O%28%5Csqrt%7Bn+%5Clog+n%7D%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+n+%2B+\min(k%2C+n+-+k)+%2B+O(\sqrt{n+\log+n})) | [![\large O(\log \log n)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%28%5Clog+%5Clog+n%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(\log+\log+n)) |
| [Median Of Medians](https://github.com/danlark1/miniselect/blob/main/include/miniselect/median_of_medians.h) | [![\large O(n)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%28n%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(n)) | [![\large O(n)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%28n%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(n)) | [![\large O(n)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%28n%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(n)) | Between [![\large 2n](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+2n)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+2n) and [![\large 22n](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+22n)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+22n). Random data  [![\large 2.5n](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+2.5n)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+2.5n) | [![\large O(\log n)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%28%5Clog+n%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(\log+n)) |
| [Median Of Ninthers](https://github.com/danlark1/miniselect/blob/main/include/miniselect/median_of_ninthers.h) | [![\large O(n)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%28n%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(n)) | [![\large O(n)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%28n%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(n)) | [![\large O(n)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%28n%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(n)) | Between [![\large 2n](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+2n)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+2n) and [![\large 21n](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+21n)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+21n). Random data [![\large 2n](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+2n)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+2n) | [![\large O(\log n)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%28%5Clog+n%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(\log+n)) |
| [Median Of 3 Random](https://github.com/danlark1/miniselect/blob/main/include/miniselect/median_of_3_random.h) | [![\large O(n)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%28n%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(n)) | [![\large O(n)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%28n%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(n)) | [![\large O(n^2 )](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%28n%5E2+%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(n^2+)) | At least [![\large 2n](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+2n)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+2n). Random data [![\large 3n](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+3n)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+3n) | [![\large O(\log n)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%28%5Clog+n%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(\log+n)) |
| [HeapSelect](https://github.com/danlark1/miniselect/blob/main/include/miniselect/heap_select.h) | [![\large O(n\log k)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%28n%5Clog+k%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(n\log+k)) | [![\large O(n)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%28n%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(n)) | [![\large O(n\log k)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%28n%5Clog+k%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(n\log+k)) | [![\large n\log k](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+n%5Clog+k)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+n\log+k) on average, for some data patterns might be better | [![\large O(1)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%281%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(1)) |
| [libstdc++ (introselect)](https://github.com/gcc-mirror/gcc/blob/e0af865ab9d9d5b6b3ac7fdde26cf9bbf635b6b4/libstdc%2B%2B-v3/include/bits/stl_algo.h#L4748) | [![\large O(n)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%28n%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(n)) | [![\large O(n)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%28n%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(n)) | [![\large O(n\log n)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%28n%5Clog+n%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(n\log+n)) | At least [![\large 2n](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+2n)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+2n). Random data [![\large 3n](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+3n)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+3n) | [![\large O(1)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%281%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(1)) |
| [libc++ (median of 3)](https://github.com/llvm/llvm-project/blob/3ed89b51da38f081fedb57727076262abb81d149/libcxx/include/algorithm#L5159) | [![\large O(n)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%28n%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(n)) | [![\large O(n)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%28n%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(n)) | [![\large O(n^2 )](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%28n%5E2+%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(n^2+)) | At least [![\large 2n](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+2n)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+2n). Random data [![\large 3n](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+3n)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+3n) | [![\large O(1)](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+O%281%29)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+O(1)) |



作者总结了这些快速选择的使用特点

- pdqselect 改自pdqsort 使用场景 Use it when you need to sort a big chunk so that [![\large k](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+k)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+k) is close to [![\large n](https://render.githubusercontent.com/render/math?math=%5Cdisplaystyle+%5Clarge+n)](https://render.githubusercontent.com/render/math?math=\displaystyle+\large+n).
- FR 快速选择算法，非常牛逼，大部分场景性能都很好，除非重复元素多
- Median Of Medians，别用
- Median Of Ninthers ， AA大作，除非非常悲观，追求保底性能，否则别用
- Median Of 3Random，别用
- introselect ，也就是标准库的nth_select，别用
- Median Of 3 别用
- std::partial_sort or HeapSelect 非常随机的数据，用，否则别用



复习一下各种排序算法 

| 排序算法 | 最好时间     | 平均时间              | 最坏时间   | 辅助空间     |
| -------- | ------------ | --------------------- | ---------- | ------------ |
| 归并排序 | O(nlogn)     | O(nlogn)              | O(nlogn)   | O(n)         |
| 堆排序   | O(nlogn)     | O(nlogn)              | O(n log n) | O(1)         |
| 快速排序 | O(nlogn)     | O(nlogn)              | O(n2)      | O(logn) O(n) |
| 自省排序 | O(nlogn)     | O(nlogn)              | O(n log n) | -            |
| PDQSort  | O(n)         | O(nlogn)              | O(nlogn)   | -            |
| K路归并  | -            | O(nklogk)) or O(nk^2) | -          | -            |
| 并行归并 | O((log n)^2) | O((log n )^2)         | O((logn)3) | -            |

简单原理归纳见参考链接，这里简单说一下

- 归并，两指针比较移动 比较经典
- 堆，构造一个最小堆/最大堆，然后重复构造交换节点等
- 快排，选定一个pivot点，左边小于P右边大于P 子区间重复划分
  - 这个效率取决于P的选取，如果P选的不好，那就是最差的冒泡 
  - 一般有三分采样 Median of three，也可以算个平均值，还有什么好的P选取法？
  - java DualPivotQuickSort，取两个Pivot，实现**快速三向切分**的快速排序，也是个有意思的点子
  - 数据集小，不如插入排序，也就产生了自省排序，也就是快排+插入+堆排序组合

- pdqsort Pattern-defeating Quicksort，这也是主要说的，rust库用的sort_unstable就是这个，也是当前发展上最快的sort，论文关键字 **BlockQuicksort: Avoiding Branch Mispredictions in Quicksort** 实现看参考链接 是快排的优化版，参考链接的实现是std::sort的优化版，其中快排部分采用了论文提到的优化：部分打乱，小范围内交换位置等等避免分支预测

> pdqsort gets a great speedup over the traditional way of implementing quicksort when sorting large arrays (1000+ elements). This is due to a new technique described in "BlockQuicksort: How Branch Mispredictions don't affect Quicksort" by Stefan Edelkamp and Armin Weiss. In short, we bypass the branch predictor by using small buffers (entirely in L1 cache) of the indices of elements that need to be swapped. We fill these buffers in a branch-free way that's quite elegant (in pseudocode):
>
> ```c++
> buffer_num = 0; buffer_max_size = 64;
> for (int i = 0; i < buffer_max_size; ++i) {
>     // With branch:
>     if (elements[i] < pivot) { buffer[buffer_num] = i; buffer_num++; }
>     // Without:
>     buffer[buffer_num] = i; buffer_num += (elements[i] < pivot);
> }
> ```



上文作者介绍原理

> 1. If there are ![n < 24](https://s0.wp.com/latex.php?latex=n+%3C+24&bg=FFFFFF&fg=181818&s=0&c=20201002) elements, use [insertion sort](https://en.wikipedia.org/wiki/Insertion_sort) to partition or even sort them. As insertion sort is really fast for a small amount of elements, it is reasonable
> 2. If it is more, choose pivot:
>    1. If there are less or equal than 128 elements, choose pseudomedian (or  “ninther”, or median of medians which are all them same) of the  following 3 groups:
>       1. begin, mid, end
>       2. begin + 1, mid – 1, end – 1
>       3. begin + 2, mid + 1, end – 2
>    2. If there are more than 128 elements, choose median of 3 from begin, mid, end
> 3. Partition the array by the chosen pivot with avoiding branches
>    1. The partition is called bad if it splits less than ![1/8n](https://s0.wp.com/latex.php?latex=1%2F8n&bg=FFFFFF&fg=181818&s=0&c=20201002) elements
>    2. If the total number of bad partitions exceeds ![\log n](https://s0.wp.com/latex.php?latex=%5Clog+n&bg=FFFFFF&fg=181818&s=0&c=20201002), use `std::nth_element` or any other fallback algorithm and return
>    3. Otherwise, try to defeat some patterns in the partition by (sizes are l_size and r_size respectively):
>       1. Swapping begin, begin + l_size / 4
>       2. Swapping p – 1 and p – l_size / 4
>       3. And if the number of elements is more than 128
>          1. begin + 1, begin + l_size / 4 + 1
>          2. begin + 2, begin + l_size / 4 + 2
>          3. p – 2, p – l_size / 4 + 1
>          4. p – 3, p – l_size / 4 + 2
>       4. Do the same with the right partition
> 4. Choose the right partition part and repeat like in QuickSelect

- k路归并就是归并个数增加，并行归并就是开并发，不表



多提一点，基数排序 Radix Sort在某些场景上要比快排快的。当然，只能用于整数

|           n | `std::sort` | `radix_sort` |
| ----------: | ----------: | -----------: |
|          10 |      3.3 ns |     284.2 ns |
|         100 |      6.1 ns |      91.6 ns |
|       1 000 |     19.3 ns |      59.8 ns |
|      10 000 |     54.8 ns |      46.8 ns |
|     100 000 |     66.9 ns |      40.1 ns |
|   1 000 000 |     81.1 ns |      40.8 ns |
|  10 000 000 |     95.1 ns |      40.7 ns |
| 100 000 000 |    108.4 ns |      40.6 ns |

---

### ref

- https://danlark.org/2020/11/11/miniselect-practical-and-generic-selection-algorithms/
  - 代码仓库 https://github.com/danlark1/miniselect
- 作者还提到了learned sort，机器学习真牛逼啊 https://blog.acolyer.org/2020/10/19/the-case-for-a-learned-sorting-algorithm/ 看不太懂
- FR select https://zhuanlan.zhihu.com/p/109385885
- https://rongyi.blog/fast-sorting
- https://github.com/orlp/pdqsort/blob/master/pdqsort.h
- sound of sorting https://panthema.net/2013/sound-of-sorting/
- 基数排序快过std::sort https://sortingsearching.com/2015/09/26/radix-sort.html
  - 作者提到快过基数排序的 Kirkpatrick-Reisch 排序，感觉是基数排序的优化版https://sortingsearching.com/2020/06/06/kirkpatrick-reisch.html


---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>