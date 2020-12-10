---
layout: post
title: (译)std::any和void*的对比
categories: [language,translation]
tags: [c++,any, shared_ptr]
---

> 翻译整理自这篇[文章](https://www.nextptr.com/tutorial/ta1571648512/stdany-comparison-with-void-and-motivating-examples)

`std::any`不是替代`void*`的产物，但是在某些场景下确实是更安全的替代品，并且 `std::any`也是构建在`void*`之上的

实际上就是记住类型信息的`void*` (type-aware void *)

```c++
struct any {
 void* object;
 type_info tinfo;
};
```

由于不是模版，不能携带类型信息，所以要有额外的绑定信息

![](https://cdn.nextptr.com/images/uimages/0VD9R23XbpWfJMNxfzPVUdj_.jpg)



而且 `std::any`还要做`small object optimization`, `SOO` (也叫`SBO`,` small buffer optimization`), 如果存个int/double指针只有两三个，不需要堆分配，直接`SBO`了

此外，`std::any`还支持移动语义，偷数据

```c++
std::any a = std::string("Hello");

//value cast creates a copy
std::cout << std::any_cast<std::string>(a) << "\n"; //Hello

//reference cast
std::any_cast<std::string&>(a)[0] = 'h'; //cast as reference and change

//value is changed to "hello" now

//cast as const reference and print
std::cout << std::any_cast<const std::string&>(a) << "\n"; //hello

//  --- prints "Wrong Type!" below ---
try {
 std::cout << std::any_cast<double>(a) << "\n";
}catch(const std::bad_any_cast&) {
 std::cout << "Wrong Type!\n";
}

//Pointer cast example
//    ---     prints "hello" below   ---
if(auto* ptr = std::any_cast<std::string>(&a)) {
 std::cout << *ptr << "\n";
} else {
 std::cout << "Wrong Type!\n";
}

//move example
auto str = std::any_cast<std::string&&>(std::move(a));

//std::string in 'a' is moved
std::cout << str << "\n"; //hello

//string in 'a' is moved but it is not destroyed
//therefore 'a' is not empty.
std::cout << std::boolalpha << a.has_value() <<  "\n"; //true

//but should print ""
std::cout << std::any_cast<std::string>(a) << "\n"; //should be ""
```



`std::any`的一个典型应用场景

假设我们要实现一个带TTL的cache， key是string，值可以是任意

```c++
class TTLCache {
public:

 //Initializes with a given ttl (in seconds)
 TTLCache(uint32_t ttl):ttlSeconds(ttl){}

 //Adds an item to the cache along with the current timestamp
 bool add(const std::string& key, const std::any& value);

 //Gets a value from cache if exists
 // - otherwise returns empty std::any
 std::any get(const std::string& key);

 //Erases an item for a given key if exists
 void erase(const std::string& key);

 // Fires periodically in a separate thread and erases the items
 //  - from cache that are older than the ttlSeconds
 void onTimer();

 //...more interfaces...

private:

 //Values stored along with timestamp
 struct Item {
  time_t timestamp;
  std::any value;
 };

 //Expire time (ttl) of items in seconds
 uint32_t ttlSeconds;

 //Items are stored against keys along with timestamp
 std::unordered_map<std::string, Item> items;
};
```

~~暂时不考虑什么O1效率之类的问题~~



`void *`的一个典型应用场景

网络传输数据，user data，用``void *``表达任意二进制/字符串/协议数据

```c++
//Clients send requests to servers
struct Request {
 /*..Request fields..*/

 //User data can be set by clients
 void* userData;
};

//When a response comes to the client, it has
// - same user data that was attached to the Request
struct Response {
 /*..Response fields..*/

 //User data copied from Request
 void* userData;
};


void sendRequest() {
 Request req;
 //Prepare request
 req.userData = new std::string("state data"); //Attach user data
 //Send request to server...
}

//Process response 
void processResponse(Response& res) {
 auto state = (std::string*)(res.userData); //cast not type-safe
 //Process response using state data....
 delete state;  // delete state
}
```

发送数据new出来，处理数据知道数据是new的，处理后删掉

这种场景下，不类型安全且需要堆分配，没有`SBO`优化

可以用`std::any`轻松替换

```c++
//--- Suppose userData is std::any ---

void sendRequest() {
 Request req;
 req.userData = std::string("state data"); //attach user data
 //send request to server
}

void processResponse(Response& res) {
 auto& state = std::any_cast<std::string&>(res.userData); //throws if type does not match
 //Process response using state data....
 //No need to explicitly delete the user data.
}
```

优化也用上了，也不用担心类型的问题，也不用担心释放的问题，一箭三雕



这种user data之前有一种解决方案，`std::shared_ptr<void>`  [这里](https://www.nextptr.com/tutorial/ta1227747841/the-stdshared_ptrvoid-as-arbitrary-userdata-pointer)有文章介绍, 简单说，就是利用shared_ptr构造的时候会记录类型，保证析构

~~译者注: 之前比较无知还反驳过同事不能这么用~~

```c++
std::shared_ptr<void> vps = std::make_shared<std::string>(); //OK 
vps.reset();  //Appropriate destructor is called

auto sps = std::static_pointer_cast<std::string>(vps); //OK with typecast
//sps is std::shared_ptr<std::string>
```

针对user data场景，直接把userdata类型换成`shared_ptr<void>`就行了

缺点在于用不上`SBO`优化，也有多余的记录开销，也没有移动内部对象的能力, 如果用不上c++17，临时用用也可以，最佳方案还是这个`std::any`




---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>