---
layout: post
categories : c++
title:  打印uint64_t以及编译错误
tags : [c,gcc]
---
  

简单说，用PRIu64来打印uint64 有编译错误



```shell
error: expected ')' before 'PRIu64'
   ROCKS_LOG_DEBUG(info_log_, "kAllCommitted ts in commit: #%" PRIu64,
                                                               ^
./util/logging.h:19:74: note: in definition of macro 'PREPEND_FILE_LINE'
 #define PREPEND_FILE_LINE(FMT) ("[" __FILE__ ":" TOSTRING(__LINE__) "] " FMT)
                                                                          ^
utilities/transactions/transaction_db_impl.cc:272:3: note: in expansion of macro 'ROCKS_LOG_DEBUG'
   ROCKS_LOG_DEBUG(info_log_, "kAllCommitted ts in commit: #%" PRIu64,
   ^
utilities/transactions/transaction_db_impl.cc:273:62: error: expected ')' before ';' token
                   TSmgr_.TimeStamps[kAllCommitted].timestamp);

```

 解决办法，头文件前加上宏定义

```c++
#define __STDC_FORMAT_MACROS
#include <inttypes.h>
```



## 参考

<https://stackoverflow.com/questions/14535556/why-doesnt-priu64-work-in-this-code>

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>