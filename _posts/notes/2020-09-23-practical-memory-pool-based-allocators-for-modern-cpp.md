---
layout: post
title: Practical memory pool based allocators for Modern C++ 
category: [c++]
tags: [c++,cppcon ,cppcon2020]
---
{% include JB/setup %}

---

[toc]

**Practical memory pool based allocators for Modern C++**

又讲内存池实现的，内存池等于块池

bucket为基本单元  bucket has two properties: BlockSize and BlockCount



bucket主要接口，构造析构分配回收

```c++
class bucket {
public:
	const std::size_t BlockSize;
	const std::size_t BlockCount;
	bucket(std::size_t block_size, std::size_t block_count);
	~bucket();
	// Tests if the pointer belongs to this bucket
	bool belongs(void * ptr) const noexcept;
	// Returns nullptr if failed
	[[nodiscard]] void * allocate(std::size_t bytes) noexcept;
	void deallocate(void * ptr, std::size_t bytes) noexcept;
private:
	// Finds n free contiguous blocks in the ledger and returns the first block’s index or BlockCount on failure
	std::size_t find_contiguous_blocks(std::size_t n) const noexcept;
	// Marks n blocks in the ledger as “in-use” starting at ‘index’
	void set_blocks_in_use(std::size_t index, std::size_t n) noexcept;
	// Marks n blocks in the ledger as “free” starting at ‘index’
	void set_blocks_free(std::size_t index, std::size_t n) noexcept;
	// Actual memory for allocations
	std::byte* m_data{nullptr};
	// Reserves one bit per block to indicate whether it is in-use
	std::byte* m_ledger{nullptr};
};

bucket::bucket(std::size_t block_size, std::size_t block_count)
: BlockSize{block_size}
, BlockCount{block_count}
{
	const auto data_size = BlockSize * BlockCount;
	m_data = static_cast<std::byte*>(std::malloc(data_size));
	assert(m_data != nullptr);
	const auto ledger_size = 1 + ((BlockCount - 1) / 8);
	m_ledger = static_cast<std::byte*>(std::malloc(ledger_size));
	assert(m_ledger != nullptr);
	std::memset(m_data, 0, data_size);
	std::memset(m_ledger, 0, ledger_size);
}
bucket::~bucket() {
	std::free(m_ledger);
	std::free(m_data);
}


void * bucket::allocate(std::size_t bytes) noexcept {
	// Calculate the required number of blocks
	const auto n = 1 + ((bytes - 1) / BlockSize);
	const auto index = find_contiguous_blocks(n);
	if (index == BlockCount) {
		return nullptr;
	}
	set_blocks_in_use(index, n);
	return m_data + (index * BlockSize);
}

void bucket::deallocate(void * ptr, std::size_t bytes) noexcept {
	const auto p = static_cast<const std::byte *>(ptr);
	const std::size_t dist = static_cast<std::size_t>(p - m_data);
	// Calculate block index from pointer distance
	const auto index = dist / BlockSize;
	// Calculate the required number of blocks
	const auto n = 1 + ((bytes - 1) / BlockSize);
	// Update the ledger
	set_blocks_free(index, n);
}
```

然后就是由块来构成池子 指定 BlockSize和BlockCount

```c++
// The default implementation defines a pool with no buckets
template<std::size_t id>
struct bucket_descriptors {
	using type = std::tuple<>;
};

struct bucket_cfg16 {
	static constexpr std::size_t BlockSize = 16;
	static constexpr std::size_t BlockCount = 10000;
};
struct bucket_cfg32{
	static constexpr std::size_t BlockSize = 32;
	static constexpr std::size_t BlockCount = 10000;
};
struct bucket_cfg1024 {
	static constexpr std::size_t BlockSize = 1024;
	static constexpr std::size_t BlockCount = 50000;
};
template<>
struct bucket_descriptors<1> {
	using type = std::tuple<bucket_cfg16, bucket_cfg32, bucket_cfg1024>;
};

template<std::size_t id>
using bucket_descriptors_t = typename bucket_descriptors<id>::type;

template<std::size_t id>
static constexpr std::size_t bucket_count = std::tuple_size<bucket_descriptors_t<id>>::value;


template<std::size_t id>
using pool_type = std::array<bucket, bucket_count<id>>;

template<std::size_t id, std::size_t Idx>
struct get_size
    : std::integral_constant<std::size_t, std::tuple_element_t<Idx, bucket_descriptors_t<id>>::BlockSize>{};
    
template<std::size_t id, std::size_t Idx>
struct get_count
: std::integral_constant<std::size_t, std::tuple_element_t<Idx, bucket_descriptors_t<id>>::BlockCount>{};

template<std::size_t id, std::size_t... Idx>
auto & get_instance(std::index_sequence<Idx...>) noexcept {
	static pool_type<id> instance{{{get_size<id, Idx>::value, get_count<id, Idx>::value} ...}};
	return instance;
}
template<std::size_t id>
auto & get_instance() noexcept {
	return get_instance<id>(std::make_index_sequence<bucket_count<id>>());
}
```



涉及到具体的分配策略，怎么找到所需的块呢？

直接找空闲的 有点像hash_map 开放地址法实现。浪费

```c++
// Assuming buckets are sorted by their block sizes
template<std::size_t id>
[[nodiscard]] void * allocate(std::size_t bytes) {
	auto & pool = get_instance<id>();
	for (auto & bucket : pool) {
		if(bucket.BlockSize >= bytes) {
			if(auto ptr = bucket.allocate(bytes); ptr != nullptr) {
				return ptr;
			}
		}
	}
	throw std::bad_alloc{};
}
```

需要额外的信息

```c++
template<std::size_t id>
[[nodiscard]] void * allocate(std::size_t bytes) {
	auto & pool = get_instance<id>();
	std::array<info, bucket_count<id>> deltas;
	std::size_t index = 0;
	for (const auto & bucket : pool) {
		deltas[index].index = index;
		if (bucket.BlockSize >= bytes) {
			deltas[index].waste = bucket.BlockSize - bytes;
			deltas[index].block_count = 1;
		} else {
			const auto n = 1 + ((bytes - 1) / bucket.BlockSize);
			const auto storage_required = n * bucket.BlockSize;
			deltas[index].waste = storage_required - bytes;
			deltas[index].block_count = n;
		}
		++index;
	}

    sort(deltas.begin(), deltas.end()); // std::sort() is allowed to allocate
    
	for (const auto & d : deltas)
		if (auto ptr = pool[d.index].allocate(bytes); ptr != nullptr)
			return ptr;
	
    throw std::bad_alloc{};
}
```

碎片问题？

实现allocator接口

不讲了。看代码

```c++
	template<typename T = std::uint8_t, std::size_t id = 0>
class static_pool_allocator {
public:
	//rebind不用实现吧，我记得好像废弃了
    template<typename U>
	static_pool_allocator(const static_pool_allocator<U, id> & other) noexcept
		: m_upstream_resource{other.upstream_resource()} {}
	template<typename U>
	static_pool_allocator & operator=(const static_pool_allocator<U, id> & other) noexcept {
		m_upstream_resource = other.upstream_resource();
		return *this;
	}
	static bool initialize_memory_pool() noexcept { return memory_pool::initialize<id>(); }
private:
	pmr::memory_resource * m_upstream_resource;
};
```





后面介绍了个分析allocate的工具

clang

- 转成llvm bitcode  -g -O0 -emit-llvm -DNDEBUG 然后用llvm-link链接pass
- 设定llvm pass
  - 打印调用
- 用llvm opt命令来执行这个pass

pass长这样

```c++
class AllocListPass : public llvm::FunctionPass {
public:
	static char ID;
	AllocListPass() : llvm::FunctionPass(ID) {}

    bool runOnFunction(llvm::Function & f) override {
		const auto pretty_name = boost::core::demangle(f.getName().str().c_str());
		static const std::regex call_regex{R"(void instrument::type_reg<([^,]+),(.+),([^,]+)>\(\))"};
		std::smatch match;
		if (std::regex_match(pretty_name, match, call_regex)) {
			if (match.size() == 4) {
				const auto pool_id = std::atoi(match[1].str().c_str());
				const auto type = match[2].str();
				const auto size = std::atoi(match[3].str().c_str());
				std::cout << "Pool ID: " << pool_id << ", Size: " << size << ", Type: " << type << "\n";
			}
		}
		return false; // does not alter the code, a read-only pass
	}
};
char AllocListPass::ID = 0;
static llvm::RegisterPass<AllocListPass> dummy("alloc-list", "This pass lists memory pool allocations");
```

llvm::ModulePass原理

- dfs找入口 main等

- 找到 type_reg<\>
  - 记录分配信息
  - 打印函数调用
- 检查递归，跳过一些分支

结果这样

```bash
Call graph for: Pool ID: 3, Size: 24, Type: std::__1::__list_node<int, void*>:
1. static_pool_allocator<std::__1::__list_node<int, void*>, 3ul>::allocate(unsigned long, void const*) called at /usr/include/c++/v1/memory:1547
2. std::__1::allocator_traits<static_pool_allocator<std::__1::__list_node<int, void*>, 3ul>>::allocate(static_pool_allocator<std::__1::__list_node<int, void*>, 3ul>&,
unsigned long) called at /usr/include/c++/v1/list:1079
3. std::__1::list<int, static_pool_allocator<int, 3ul>>::__allocate_node(static_pool_allocator<std::__1::__list_node<int, void*>, 3ul>&) called at
/usr/include/c++/v1/list:1569
4. std::__1::list<int, static_pool_allocator<int, 3ul>>::push_back(int const&) called at /home/program.cpp:12
5. x() called at /home/program.cpp:7
6. f() called at /home/program.cpp:2
```



llvm opt

```bash
opt -load alloc-analyzer.so -alloc-analyze -gen-hdr my_defs.hpp -entry-point "main"< home/program.bc -o /dev/null
```



---

### ref

- https://github.com/CppCon/CppCon2020/blob/main/Presentations/practical_memory_pool_based_allocators_for_modern_cpp/practical_memory_pool_based_allocators_for_modern_cpp__misha_shalem__cppcon_2020.pdf
---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。
