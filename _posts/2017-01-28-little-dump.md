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


用了hexdump，自然有读数据的需求

```bash
#!/bin/bash
echo -n "The decimal value of 0x$@="
echo $((0x$@))
```
hex 转十进制

---


