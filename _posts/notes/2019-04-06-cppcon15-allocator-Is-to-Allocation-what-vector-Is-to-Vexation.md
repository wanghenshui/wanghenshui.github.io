---
layout: post
category: c++
title: allocator Is to Allocation what vector Is to Vexation
tags: [cppcon, c++]
---
{% include JB/setup %}

演讲主题 Allocator的设计历史，AA主讲，标题也是够讽刺哈哈，其实概括的说allocator是设计错误（当初对virtual引入标准库还有抵触，觉得不够zero cost），才有c++17的 std::pmr

---

从malloc讲起

```c
void* malloc(size_t size);
void free(void* p);
```

调用malloc需要记住size，free不需要，但是内部是有trick记住size的 -> allocator必须知道size

改进方案 0.1

```c
struct blk {void* ptr; size_t length;};
struct blk malloc(size_t size);
void free(struct blk block);
```

新方案 operator new api多种多样，可以带size

问题

- 无法和malloc结合使用
- 指定类型
- 有奇怪的语法(指的placement new？)
- 和构造函数没通信
- 数组new带来的分歧(也可以算到奇怪语法里)

提案N3536（problem小节）还提到 delete 不带size的，对于一些allocator可能存在的性能问题(不提供size，可能就需要allocator存size，或者按块存储的，就得搜一遍块)，以及新增 fix



然后引入std::allocator，之所以不是个好的allocator主要还是设计问题

- 类型参数T引入的麻烦
  - 对标准的理解分歧
  - allocator成了了factory
  - 实际上还是void*
  - allocator应该以block为单位
  - `rebind<U>::other`邪恶到家了
- 无状态
  - 甚至是个全局单例 monostate
- 复杂问题：组合
  - 通常allocator都是各种size块组合的，结合着各种list tree，freelist。如何组合，以及调试，观察状态都是问题

重新设计

- 效率
  - 给调用方size信息
  - scoped allocation patterns
  - Thread-Local allocation patterns
- 特性
  - 更好的配置(debug/stat)
  - 特化，适配
  - no legacy, no nonsense

```c++
template <class Primary, class Fallback>
class FallbackAllocator
	: private Primary
	, private Fallback {
public:
	blk allocate(size_t);
	void deallocate(blk);
};
```

Primary和Fallback都是allocator，Fallback保底，这就有个区分问题，需要各自实现owns 函数方便Allocator调用, 当然，最起码需要定义一个，依赖**MDFINAE : Method Definitions Failure Is Not an Error**

```c++
template <class P, class F>
blk FallbackAllocator<P, F>::allocate(size_t n) {
	blk r = P::allocate(n);
	if (!r.ptr) r = F::allocate(n);
	return r;
}
template <class P, class F>
void FallbackAllocator<P, F>::deallocate(blk b) {
	if (P::owns(b)) P::deallocate(b);
	else F::deallocate(b);
}
template <class P, class F>
bool FallbackAllocator::owns(blk b) {
	return P::owns(b) || F::owns(b);
}
```



手把手教你写stackallocator

```c++
template <size_t s> class StackAllocator {
	char d_[s];
	char* p_;
	StackAllocator() : p_(d_) {}
	nlk allocate(size_t n) {
		auto n1 = roundToAligned(n);
		if (n1 > (d_ + s) - p_ ) {
			return { nullptr, 0 };
		}
		blk result = { p_ , n };
		p_ += n1;
		return result;
	}
	
    void deallocate(blk b) {
		if (b.ptr + roundToAligned(n) == p_ ) {
			p_ = b.ptr;
		}
	}
	bool owns(blk b) {
		return b.ptr >= d_ && b.ptr < d_ + s;
	}
	// NEW: deallocate everything in O(1)
	void deallocateAll() {
		p_ = d_ ;
	}
...
};
```

 

手把手教你写freelist

```c++
template <class A, size_t s> class Freelist {
	A parent_ ;
	struct Node { Node * next; };
    Node* root_ ;
public:
	blk allocate(size_t n) {
		if (n == s && root_ ) {
			blk b = { root_ , n };
			root_ = root_.next;
			return b;
		}
		return parent_.allocate(n);
	}
	bool owns(blk b) {
		return b.length == s || parent_.owns(b);
	}
	void deallocate(blk b) {
		if (b.length != s) return parent_.deallocate(b);
		auto p = (Node * )b.ptr;
		p.next = root_ ;
		root_ = p;
	}
...
};
```

还可以改进，比如min max范文，allocate in batch等



添加调试信息

```c++
template <class A, class Prefix, class Suffix = void>
class AffixAllocator;
```

添加适当的前后缀参数，相当于模板装饰器了

类似的

```c++
template <class A, ulong flags>
class AllocatorWithStats;
```

手机各种原语调用，错误信息，内存使用信息，调用（时间行数文件等等）等



Bitmapped block

相当于全是静态的块

```c++
template <class A, size _ t blockSize>
class BitmappedBlock;
```

- 已经定义好的块大小
- 比malloc简单
- 多线程不友好



CascadingAllocator

```c++
template <class Creator>
class CascadingAllocator;
...
auto a = cascadingAllocator([]{
return Heap<...>();
});
```

- 一堆分配器，涨的慢
- 粒度大
- 线性查找



Segregator

分离，感觉像是多个freelist组合的感觉

```c++
template <size_t threshold, class SmallAllocator, class LargeAllocator>
struct Segregator;
```

• 以 threshold作为分界，派发给SmallAllocator或者LargeAllocator



甚至可以自组合，控制粒度 

```c++
typedef Segregator<4096,
	Segregator<128,
		Freelist<Mallocator, 0, 128>,
		MediumAllocator>,
	Mallocator>
Allocator;
```

也可以组合各种搜索策略，但是被size限制住了



Bucketizer

这个单纯就是size桶了

```c++
template <class Allocator,	size_t min, size_t max, size_t step>
struct Bucketizer;
```

• [min, min + step), [min + step, min + 2*step)...
• 个数有限



上面就是主流allocator 策略了



allocator的复制策略

- allocator独立 无状态，可复制，移动
- 不可复制 &移动，比如StackAllocator
- 可移动不可复制，没有存堆的成员就行了
- 可移动，引用计数



还有其他粒度上的控制，比如类型控制，工厂函数，设计，block设计等。不在列举



```c++
using FList = Freelist<Mallocator, 0, -1>;
using A = Segregator<
	8, Freelist<Mallocator, 0, 8>,
	128, Bucketizer<FList, 1, 128, 16>,
	256, Bucketizer<FList, 129, 256, 32>,
	512, Bucketizer<FList, 257, 512, 64>,
	1024, Bucketizer<FList, 513, 1024, 128>,
	2048, Bucketizer<FList, 1025, 2048, 256>,
	3584, Bucketizer<FList, 2049, 3584, 512>,
	4072*1024, CascadingAllocator<decltype(newHeapBlock)>,
	Mallocator
>;
```



---

总结

- Fresh approach from first principles
- Understanding history
  - Otherwise: "...**doomed to repeat it**".
- Composability is key

---

### reference

1. https://github.com/CppCon/CppCon2015/tree/master/Presentations/allocator%20Is%20to%20Allocation%20what%20vector%20Is%20to%20Vexation

2. 提到了cppcon2014 Making Allocators Work 需要翻出来看一下

3. <http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2013/n3536.html>

4. 也是神奇，搜monostate搜出来这个<https://en.cppreference.com/w/cpp/utility/variant/monostate>

   



看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。

