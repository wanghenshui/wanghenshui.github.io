---
layout: post
title: 数据库压缩到底怎么做？
categories: [database]
tags: [redis, rocksdb, compression]
---

[toc]

<!-- more -->

# redis

redis的压缩是针对key的压缩

只针对string和list的value

所有的压缩最终都会调用lzf_compress/lzf_decompress

需要配置文件配置rdb_compression rdb压缩才会生效

lzf压缩限制长度要大于20，即使是aaaaaaaaaaaaaaaaaaaa也压不了，大于20才能压。原因没有深究

## rdb内部的压缩

- 如何确认这个record是被压缩/解压的？

rdb解析每条数据，都有标识字段，压缩的record自然是单独的类型



```c
ssize_t rdbSaveLzfStringObject(rio *rdb, unsigned char *s, size_t len) {
...
    comprlen = lzf_compress(s, len, out, outlen);
    if (comprlen == 0) {
        zfree(out);
        return 0;
    }
    ssize_t nwritten = rdbSaveLzfBlob(rdb, out, comprlen, len);
...
}

ssize_t rdbSaveLzfBlob(rio *rdb, void *data, size_t compress_len,
                       size_t original_len) {
...
    /* Data compressed! Let's save it on disk */
    byte = (RDB_ENCVAL<<6)|RDB_ENC_LZF;
    if ((n = rdbWriteRaw(rdb,&byte,1)) == -1) goto writeerr;
    nwritten += n;
...
}
```

解压缩

```c
void *rdbGenericLoadStringObject(rio *rdb, int flags, size_t *lenptr) {
...
    if (isencoded) {
        switch(len) {
        case RDB_ENC_INT8:
        case RDB_ENC_INT16:
        case RDB_ENC_INT32:
            return rdbLoadIntegerObject(rdb,len,flags,lenptr);
        case RDB_ENC_LZF:
            return rdbLoadLzfStringObject(rdb,flags,lenptr);
        default:
            rdbReportCorruptRDB("Unknown RDB string encoding type %llu",len);
            return NULL;
        }
    }
 ...
 
 void *rdbLoadLzfStringObject(rio *rdb, int flags, size_t *lenptr) {
...

    /* Load the compressed representation and uncompress it to target. */
    if (rioRead(rdb,c,clen) == 0) goto err;
    if (lzf_decompress(c,clen,val,len) != len) {
        rdbReportCorruptRDB("Invalid LZF compressed string");
...
}
```

接口简单容易定位



所有的类型string/hash具体到底层，都是string，就会走这个压缩的过程rdbSaveRawString,内部来调用rdbSaveLzfStringObject

```c
ssize_t rdbSaveObject(rio *rdb, robj *o, robj *key, int dbid) {
    ssize_t n = 0, nwritten = 0;

    if (o->type == OBJ_STRING) {
        /* Save a string value */
        if ((n = rdbSaveStringObject(rdb,o)) == -1) return -1;
        nwritten += n;
    } else if (o->type == OBJ_LIST) {

                if (quicklistNodeIsCompressed(node)) {
                    void *data;
                    size_t compress_len = quicklistGetLzf(node, &data);
                    if ((n = rdbSaveLzfBlob(rdb,data,compress_len,node->sz)) == -1) return -1;
                    nwritten += n;
                } else {
                    if ((n = rdbSaveRawString(rdb,node->zl,node->sz)) == -1) return -1;
                    nwritten += n;
                }
                node = node->next;
            }
        } else {
            serverPanic("Unknown list encoding");
        }
。。。
}
```



## quicklist的压缩

链表压缩可以选择深度，quicklist是redis list的底层数据结构

什么时候做压缩？

```c
/* Insert 'new_node' after 'old_node' if 'after' is 1.
 * Insert 'new_node' before 'old_node' if 'after' is 0.
 * Note: 'new_node' is *always* uncompressed, so if we assign it to
 *       head or tail, we do not need to uncompress it. */
REDIS_STATIC void __quicklistInsertNode(quicklist *quicklist,
                                        quicklistNode *old_node,
                                        quicklistNode *new_node, int after) {
    if (after) {
        new_node->prev = old_node;
        if (old_node) {
            new_node->next = old_node->next;
            if (old_node->next)
                old_node->next->prev = new_node;
            old_node->next = new_node;
        }
        if (quicklist->tail == old_node)
            quicklist->tail = new_node;
    } else {
        new_node->next = old_node;
        if (old_node) {
            new_node->prev = old_node->prev;
            if (old_node->prev)
                old_node->prev->next = new_node;
            old_node->prev = new_node;
        }
        if (quicklist->head == old_node)
            quicklist->head = new_node;
    }
    /* If this insert creates the only element so far, initialize head/tail. */
    if (quicklist->len == 0) {
        quicklist->head = quicklist->tail = new_node;
    }

    /* Update len first, so in __quicklistCompress we know exactly len */
    quicklist->len++;

    if (old_node)
        quicklistCompress(quicklist, old_node);
}
```

也就是说，头尾不会压缩，其他的节点会压缩，在修改的时候同事把旧的节点给压缩了

这里有个问题，这里的节点压缩了，rdb存储的时候还要特别处理一下，判定已经压缩过，走rdbSaveLzfBlob

需要有个record头来记录一个compression的标记



# rocksdb

类似redis，还是很好找的，UncompressData/CompressData

## 针对sst的压缩

调用关系 

UncompressBlockContentsForCompressionType -> UncompressData

WriteBlock/BGWorkCompression -> CompressAndVerifyBlock -> CompressBlock -> CompressData

block本身有信息标记是否是压缩

写入的时候才压缩

## blobdb

CompressBlobIfNeeded -> CompressData

GetCompressedSlice -> CompressData



# 总结

- 需要文件本身知道自己是压缩的，有元信息记录
- 在内存中是否压缩要考虑业务场景，比如redis这个quicklist 压缩，因为list最近访问的就是头尾，其他不重要



# PS

压缩在哪里做？redis这相当于在数据应用层面做，rocksdb这相当于在底层引擎做

做一个数据库，在上层做简单，在引擎做复杂，但是控制的精细，也可以提供额外的接口

我最近做一个引擎层的压缩，做完了发现完全没必要这么精细，可以放到上层来做，白白浪费时间




---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢!  你的评论非常重要！

<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>
