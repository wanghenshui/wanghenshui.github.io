---
layout: post
categories: database
title: DeleteRange以及删除范围key
tags: [rocksdb]
---

  

---

#### Why

这是Rocksdb API使用记录。作为一个掌握的过程

---

`DeleteRange`见参考链接1

在5.18.3之前，只能Seek开头结尾，然后遍历调用删除

```c++
Slice start, end;
// set start and end
auto it = db->NewIterator(ReadOptions());

for (it->Seek(start); cmp->Compare(it->key(), end) < 0; it->Next()) {
  db->Delete(WriteOptions(), it->key());
}
```

后面增加了新的API **DeleteRange**，可以一次性搞定，注意，是半开半闭区间，**end**是不删除的

`实现原理`见参考链接23





`如何删除整个CF？`

如果CF名字不是**rocksdb::kDefaultColumnFamilyName**  可以直接调用**Drop CF**，然后重新**Create CF**就行了，如果是的话，直接Drop会报错，最好改掉，或者先**SeekToFirst**，  **SeekToLast**找到范围**[first, end)**，然后DeleteRange，然后在删除**end**.挺繁琐的。最好还是命个名，就可以删Drop了



注意DropCF后需要deletehandle不然会泄露

### ref

1. https://github.com/facebook/rocksdb/wiki/DeleteRange
2. https://github.com/facebook/rocksdb/wiki/DeleteRange-Implementation
3. https://rocksdb.org/blog/2018/11/21/delete-range.html
4. https://stackoverflow.com/questions/54438787/faster-way-to-clear-a-column-family-in-rocksdb


### contact

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
![微信转账](https://wanghenshui.github.io/assets/wepay.png)
</details>