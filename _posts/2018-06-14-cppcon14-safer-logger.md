---
layout: post
title: (cppcon)用表达式模板实现一个一个简单安全的log
categories: language
tags: [c++, cppcon]
---
  

  传统写法

```c++
#define LOG(msg) \
    if (s_bLoggingEnabled) \
       std::cout<<__FILE__<<"("<<__LINE__<<")"<<msg<<std::endl;
```

汇编长这样

```shell
   0x0000000000400c9d <+53>:    mov    %rax,%rdi
   0x0000000000400ca0 <+56>:    callq  0x400af0 <_ZNSaIcED1Ev@plt>
   0x0000000000400ca5 <+61>:    movzbl 0x201528(%rip),%eax        # 0x6021d4 <s_bLoggingEnabled>
   0x0000000000400cac <+68>:    test   %al,%al
   0x0000000000400cae <+70>:    je     0x400d2c <main()+196>
   0x0000000000400cb0 <+72>:    mov    $0x400e5a,%esi
   0x0000000000400cb5 <+77>:    mov    $0x6020c0,%edi
   0x0000000000400cba <+82>:    callq  0x400ad0 <_ZStlsISt11char_traitsIcEERSt13basic_ostreamIcT_ES5_PKc@plt>
   0x0000000000400cbf <+87>:    mov    $0x400e65,%esi
   0x0000000000400cc4 <+92>:    mov    %rax,%rdi
   0x0000000000400cc7 <+95>:    callq  0x400ad0 <_ZStlsISt11char_traitsIcEERSt13basic_ostreamIcT_ES5_PKc@plt>
   0x0000000000400ccc <+100>:   mov    $0xe,%esi
   0x0000000000400cd1 <+105>:   mov    %rax,%rdi
   0x0000000000400cd4 <+108>:   callq  0x400a70 <_ZNSolsEi@plt>
   0x0000000000400cd9 <+113>:   mov    $0x400e67,%esi
   0x0000000000400cde <+118>:   mov    %rax,%rdi
   0x0000000000400ce1 <+121>:   callq  0x400ad0 <_ZStlsISt11char_traitsIcEERSt13basic_ostreamIcT_ES5_PKc@plt>
   0x0000000000400ce6 <+126>:   mov    $0x400e69,%esi
   0x0000000000400ceb <+131>:   mov    %rax,%rdi
   0x0000000000400cee <+134>:   callq  0x400ad0 <_ZStlsISt11char_traitsIcEERSt13basic_ostreamIcT_ES5_PKc@plt>
   0x0000000000400cf3 <+139>:   mov    %rax,%rdx
   0x0000000000400cf6 <+142>:   lea    -0x40(%rbp),%rax
   0x0000000000400cfa <+146>:   mov    %rax,%rsi
   0x0000000000400cfd <+149>:   mov    %rdx,%rdi
   0x0000000000400d00 <+152>:   callq  0x400b50 <_ZStlsIcSt11char_traitsIcESaIcEERSt13basic_ostreamIT_T0_ES7_RKNSt7__cxx1112basic_stringIS4_S5_T1_EE@plt>
   0x0000000000400d05 <+157>:   mov    $0x37,%esi
   0x0000000000400d0a <+162>:   mov    %rax,%rdi
   0x0000000000400d0d <+165>:   callq  0x400a70 <_ZNSolsEi@plt>
   0x0000000000400d12 <+170>:   mov    $0x400e6d,%esi
   0x0000000000400d17 <+175>:   mov    %rax,%rdi
   0x0000000000400d1a <+178>:   callq  0x400ad0 <_ZStlsISt11char_traitsIcEERSt13basic_ostreamIcT_ES5_PKc@plt>
   0x0000000000400d1f <+183>:   mov    $0x400b10,%esi
   0x0000000000400d24 <+188>:   mov    %rax,%rdi

```

作者说了log相关的指令问题，可能会阻止编译器优化，icache也不友好

针对此，要达到减少指令，保留速度，类型安全还方便，所以就用到表达式模板了，把工作放到编译期

怎么做？把所有打印的参数用表达式墨宝封装一下，typelist登场

拆成两部分，log 和logdata

logdata就是个表达式模板typelist，把所有的参数串起来

```c++
using namespace std;
#define LOG(msg) \
    if (s_bLoggingEnabled) \
       (log(__FILE__,__LINE__,LogData<None>()<<msg));

template <typename List>
struct LogData{
    typedef List type;
    List list;
};
struct None{};

template <typename Begin, typename Value>
LogData<std::pair<Begin&&, Value&&>> operator<<(LogData<Begin>&& begin,
                                                Value&& v) noexcept {
    return {{std::forward<Begin>(begin.list), std::foward<Value>(v)}};
}

template <typename Begin, size_t n >
LogData<std::pair<Begin&&, const char* >> operator<<(LogData<Begin>&& begin,
                                               const char(&sz)[n]) noexcept{
    return {{std::forward<Begin>(begin.list), sz}};
}

template<typename TLogData>
void log(const char* file, int line, TLogData&& data)
noexcept {
    std::cout<< file<<" "<<line<<": ";
    LogRecursive(std::cout, std::forward<typename TLogData::type>(data.list));
    std::cout<<std::endl;
}

template<typename TLogDataPair>
void LogRecursive(std::ostream& os, TLogDataPair&& data) noexcept{
   LogRecursive(os,std::forward<typename TLogDataPair::first_type>(data.first));
   os<<std::forward<typename TLogDataPair::second_type>(data.second);
}
inline void LogRecursive(std::ostream& os, None) noexcept{}

int main()
{
  s_bLoggingEnabled = true;
  string s{"blaa"};
  LOG("sth"<<s<<55<<"!!");
}
```



```shell

   0x0000000000400cab <+67>:    movzbl 0x201522(%rip),%eax        # 0x6021d4 <s_bLoggingEnabled>
   0x0000000000400cb2 <+74>:    test   %al,%al
   0x0000000000400cb4 <+76>:    je     0x400d42 <main()+218>
   0x0000000000400cba <+82>:    movl   $0x37,-0x44(%rbp)
   0x0000000000400cc1 <+89>:    lea    -0x11(%rbp),%rax
   0x0000000000400cc5 <+93>:    mov    $0x40130a,%esi
   0x0000000000400cca <+98>:    mov    %rax,%rdi
   0x0000000000400ccd <+101>:   callq  0x400e24 <operator<< <None, 4ul>(LogData<None>&&, char const (&) [4ul])>
   0x0000000000400cd2 <+106>:   mov    %rax,-0x30(%rbp)
   0x0000000000400cd6 <+110>:   mov    %rdx,-0x28(%rbp)
   0x0000000000400cda <+114>:   lea    -0xa0(%rbp),%rdx
   0x0000000000400ce1 <+121>:   lea    -0x30(%rbp),%rax
   0x0000000000400ce5 <+125>:   mov    %rdx,%rsi
   0x0000000000400ce8 <+128>:   mov    %rax,%rdi
   0x0000000000400ceb <+131>:   callq  0x400ebd <operator<< <std::pair<None&&, char const*>, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >&>(LogData<std::pair<None&&, char const*> >&&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >&)>
   0x0000000000400cf0 <+136>:   mov    %rax,-0x40(%rbp)
   0x0000000000400cf4 <+140>:   mov    %rdx,-0x38(%rbp)
---Type <return> to continue, or q <return> to quit---
   0x0000000000400cf8 <+144>:   lea    -0x44(%rbp),%rdx
   0x0000000000400cfc <+148>:   lea    -0x40(%rbp),%rax
   0x0000000000400d00 <+152>:   mov    %rdx,%rsi
   0x0000000000400d03 <+155>:   mov    %rax,%rdi
   0x0000000000400d06 <+158>:   callq  0x400f6a <operator<< <std::pair<std::pair<None&&, char const*>&&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >&>, int>(LogData<std::pair<std::pair<None&&, char const*>&&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >&> >&&, int&&)>
   0x0000000000400d0b <+163>:   mov    %rax,-0x60(%rbp)
   0x0000000000400d0f <+167>:   mov    %rdx,-0x58(%rbp)
   0x0000000000400d13 <+171>:   lea    -0x60(%rbp),%rax
   0x0000000000400d17 <+175>:   mov    $0x40130e,%esi
   0x0000000000400d1c <+180>:   mov    %rax,%rdi
   0x0000000000400d1f <+183>:   callq  0x401002 <operator<< <std::pair<std::pair<std::pair<None&&, char const*>&&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >&>&&, int&&>, 3ul>(LogData<std::pair<std::pair<std::pair<None&&, char const*>&&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >&>&&, int&&> >&&, char const (&) [3ul])>
   0x0000000000400d24 <+188>:   mov    %rax,-0x70(%rbp)
   0x0000000000400d28 <+192>:   mov    %rdx,-0x68(%rbp)
   0x0000000000400d2c <+196>:   lea    -0x70(%rbp),%rax
   0x0000000000400d30 <+200>:   mov    %rax,%rdx
   0x0000000000400d33 <+203>:   mov    $0x31,%esi
   0x0000000000400d38 <+208>:   mov    $0x401311,%edi
   0x0000000000400d3d <+213>:   callq  0x401054 <log<LogData<std::pair<std::pair<std::pair<std::pair<None&&, char const*>&&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >&>&&, int&&>&&, char const*> > >(char const*, int, LogData<std::pair<std::pair<std::pair<std::pair<None&&, char const*>&&, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >&>&&, int&&>&&, char const*> >&&)>
   0x0000000000400d42 <+218>:   lea    -0xa0(%rbp),%rax

```

我个人测验，感觉并没有好到哪里去。。gcc开O3的话两个长得基本一致了。。就当学一下typelist转发技术好了

### ref

- [https://github.com/CppCon/CppCon2014/blob/master/Lightning%20Talks/Cheap%2C%20Simple%2C%20and%20Safe%20Logging%20Using%20Expression%20Templates/Cheap%2C%20Simple%2C%20and%20Safe%20Logging%20Using%20Expression%20Templates%20-%20Marc%20Eaddy.pdf](https://github.com/CppCon/CppCon2014/blob/master/Lightning Talks/Cheap%2C Simple%2C and Safe Logging Using Expression Templates/Cheap%2C Simple%2C and Safe Logging Using Expression Templates - Marc Eaddy.pdf)

- 看汇编的几种方法 <https://stackoverflow.com/questions/137038/how-do-you-get-assembler-output-from-c-c-source-in-gcc>

  

看到这里或许你有建议或者疑问或者指出我的错误，请留言评论或者邮件mailto:wanghenshui@qq.com, 多谢! 
<details>
<summary>觉得写的不错可以点开扫码赞助几毛</summary>
<img src="https://wanghenshui.github.io/assets/wepay.png" alt="微信转账">
</details>