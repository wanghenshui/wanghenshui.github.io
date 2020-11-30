---
layout: post
title: c++究竟是怎么实现多态的
categories: language
tags: [c++, vtable]
---

  

大家都说虚表虚指针，有虚表虚指针，怎么就能动态的指向虚表呢？

用Compiler Explorer一下就看出来了。这个代码片直接用CE还带颜色，更方便

```c++
#include <cstdio>
class base{
public:
  virtual void p(){printf("base\n");}
  virtual void q(){}
  virtual void r(){}
  virtual ~base(){}
};

class derive : public base{
  public:
  virtual void p(){printf("derive\n");}
};

void f(base*b){
	b->p();
}

int main()
{
  base* b=new base;
  base* d=new derive;
  f(b);
  f(d);
}
```

汇编是这样的

```assembly
base::q():
        ret
base::r():
        ret
base::~base() [base object destructor]:
        ret
derive::~derive() [base object destructor]:
        ret
.LC0:
        .string "derive"
derive::p():
        mov     edi, OFFSET FLAT:.LC0
        jmp     puts
.LC1:
        .string "base"
base::p():
        mov     edi, OFFSET FLAT:.LC1
        jmp     puts
base::~base() [deleting destructor]:
        mov     esi, 8
        jmp     operator delete(void*, unsigned long)
derive::~derive() [deleting destructor]:
        mov     esi, 8
        jmp     operator delete(void*, unsigned long)
f(base*):
        mov     rax, QWORD PTR [rdi]
        jmp     [QWORD PTR [rax]]
main:
        push    r12
        mov     edi, 8
        push    rbp
        sub     rsp, 8
        call    operator new(unsigned long)
        mov     edi, 8
        mov     QWORD PTR [rax], OFFSET FLAT:vtable for base+16
        mov     r12, rax
        call    operator new(unsigned long)
        mov     rdi, r12
        mov     rbp, rax
        mov     QWORD PTR [rax], OFFSET FLAT:vtable for derive+16
        mov     rax, QWORD PTR [r12]
        call    [QWORD PTR [rax]]
        mov     rax, QWORD PTR [rbp+0]
        mov     rdi, rbp
        call    [QWORD PTR [rax]]
        add     rsp, 8
        xor     eax, eax
        pop     rbp
        pop     r12
        ret
typeinfo name for base:
        .string "4base"
typeinfo for base:
        .quad   vtable for __cxxabiv1::__class_type_info+16
        .quad   typeinfo name for base
typeinfo name for derive:
        .string "6derive"
typeinfo for derive:
        .quad   vtable for __cxxabiv1::__si_class_type_info+16
        .quad   typeinfo name for derive
        .quad   typeinfo for base
vtable for base:
        .quad   0
        .quad   typeinfo for base
        .quad   base::p()
        .quad   base::q()
        .quad   base::r()
        .quad   base::~base() [complete object destructor]
        .quad   base::~base() [deleting destructor]
vtable for derive:
        .quad   0
        .quad   typeinfo for derive
        .quad   derive::p()
        .quad   base::q()
        .quad   base::r()
        .quad   derive::~derive() [complete object destructor]
        .quad   derive::~derive() [deleting destructor]
```



 注意两次调用new构造后面，有一个保存指针动作 

```assembly
        mov     QWORD PTR [rax], OFFSET FLAT:vtable for base+16
```

这就是把p函数指针保存起来，vtable+偏移，然后保存到

不理解的地方就是这里了，所谓的动态实际上在代码中也是死的，主要是在构造后多了个存偏移指针，需要额外的开销。

----

#### 参考

- Compiler Explorer https://godbolt.org/
- 这个讲解非常到位 <https://stackoverflow.com/questions/33556511/how-do-objects-work-in-x86-at-the-assembly-level>

---

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>