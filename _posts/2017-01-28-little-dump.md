layout: post
title: 一些二进制分析工具记录
categories: tools
tags: []



[toc]

<!-- more -->



## hexdump

测试代码

```c++
#include <string>
#include <cstdint>
#include <cstdio>
#include <cstring>

int main(){
  std::string filename = "test.dat";
  uint64_t x = 0x1234567890abcdef;
  std::FILE *file = std::fopen(filename.c_str(), "wb");
  if (!file) {
    return 1;
  }
  if (std::fwrite(&x, sizeof(x), 1, file) !=
      1) {
    std::fclose(file);
    return 2;
  }
  if (std::fclose(file) != 0) {
    return 3;
  }
  return 0;
}
```

hexdump效果

```bash
hexdump test.dat
0000000 ef cd ab 90 78 56 34 12                        
0000008
```

小端序，反过来，前四个字节是低位，反着读



同理00 00 80 00 00 00 00 00就是8M




---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>
