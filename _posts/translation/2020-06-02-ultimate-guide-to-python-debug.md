---
layout: post
title: (译)终极python调试指南 Ultimate Guide to Python Debugging
category: [python, debug]
tags: [python]
---
{% include JB/setup %}

---

# 必须打日志

不打日志必后悔，python设置日志非常简单

```python
import logging
logging.basicConfig(
    filename='application.log',
    level=logging.WARNING,
    format= '[%(asctime)s] %(pathname)s:%(lineno)d %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

logging.error("Some serious error occurred.")
logging.warning('Function you are using is deprecated.')
```

有了日志logger能加上配置文件扩展（ini/yaml）就更好了（译者注：really？有点浮夸）

```yaml
version: 1
disable_existing_loggers: true

formatters:
  standard:
    format: "[%(asctime)s] (pathname)s:%(lineno)d %(levelname)s - %(message)s"
    datefmt: '%H:%M:%S'

handlers:
  console:  # handler which will log into stdout
    class: logging.StreamHandler
    level: DEBUG
    formatter: standard  # Use formatter defined above
    stream: ext://sys.stdout
  file:  # handler which will log into file
    class: logging.handlers.RotatingFileHandler
    level: WARNING
    formatter: standard  # Use formatter defined above
    filename: /tmp/warnings.log
    maxBytes: 10485760 # 10MB
    backupCount: 10
    encoding: utf8

root:  # Loggers are organized in hierarchy - this is the root logger config
  level: ERROR
  handlers: [console, file]  # Attaches both handler defined above

loggers:  # Defines descendants of root logger
  mymodule:  # Logger for "mymodule"
    level: INFO
    handlers: [file]  # Will only use "file" handler defined above
    propagate: no  # Will not propagate logs to "root" logger
```

```python
import yaml
from logging import config

with open("config.yaml", 'rt') as f:
    config_data = yaml.safe_load(f.read())
    config.dictConfig(config_data)
```

logger不直接支持yaml，但是可以把yaml转成dict，然后就可以用了



# 日志装饰器

有了日志还不够，发现了有问题的代码片，想看内部细节调用，直接上日志装饰器，这样要比直接在日志内加要方便的多 ，具体的细节就调节配置文件中的日志级别就可以了

```python
from functools import wraps, partial
import logging

def attach_wrapper(obj, func=None):  # Helper function that attaches function as attribute of an object
    if func is None:
        return partial(attach_wrapper, obj)
    setattr(obj, func.__name__, func)
    return func

def log(level, message):  # Actual decorator
    def decorate(func):
        logger = logging.getLogger(func.__module__)  # Setup logger
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        log_message = f"{func.__name__} - {message}"

        @wraps(func)
        def wrapper(*args, **kwargs):  # Logs the message and before executing the decorated function
            logger.log(level, log_message)
            return func(*args, **kwargs)

        @attach_wrapper(wrapper)  # Attaches "set_level" to "wrapper" as attribute
        def set_level(new_level):  # Function that allows us to set log level
            nonlocal level
            level = new_level

        @attach_wrapper(wrapper)  # Attaches "set_message" to "wrapper" as attribute
        def set_message(new_message):  # Function that allows us to set message
            nonlocal log_message
            log_message = f"{func.__name__} - {new_message}"

        return wrapper
    return decorate

# Example Usage
@log(logging.WARN, "example-param")
def somefunc(args):
    return args

somefunc("some args")

somefunc.set_level(logging.CRITICAL)  # Change log level by accessing internal decorator function
somefunc.set_message("new-message")  # Change log message by accessing internal decorator function
somefunc("some args")
```





# 实现_\_repr__ 方便打印

老生常谈了,实现\__str__也行

```python
class Circle:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def __repr__(self):
        return f"Rectangle({self.x}, {self.y}, {self.radius})"

...
c = Circle(100, 80, 30)
repr(c)
# Circle(100, 80, 30)
```



# 实现\__missing__  避免KeyError异常

如果实现了自己的dict(译者注：用到dict作为自己的内部成员，可以封装一层dict) 可以实现\__missing__ 如果访问key key不存在，就会触发missing调用，帮助捕捉bug



# 调试崩溃的程序

过快崩溃来不及看日志？ -i进入细节调用模式 `python -i xx.py` 如果这个细节还是不够用，可以调用pdb

```python
# crashing_app.py
SOME_VAR = 42

class SomeError(Exception):
    pass

def func():
    raise SomeError("Something went wrong...")

func()
```

```shell
~ $ python3 -i crashing_app.py
Traceback (most recent call last):
  File "crashing_app.py", line 9, in <module>
    func()
  File "crashing_app.py", line 7, in func
    raise SomeError("Something went wrong...")
__main__.SomeError: Something went wrong...
>>> # We are interactive shell
>>> import pdb
>>> pdb.pm()  # start Post-Mortem debugger
> .../crashing_app.py(7)func()
-> raise SomeError("Something went wrong...")
(Pdb) # Now we are in debugger and can poke around and run some commands:
(Pdb) p SOME_VAR  # Print value of variable
42
(Pdb) l  # List surrounding code we are working with
  2
  3   class SomeError(Exception):
  4       pass
  5
  6   def func():
  7  ->     raise SomeError("Something went wrong...")
  8
  9   func()
[EOF]
(Pdb)  # Continue debugging... set breakpoints, step through the code, etc.
```



# 抓调用栈

```python
import traceback
import sys

def func():
    try:
        raise SomeError("Something went wrong...")
    except:
        traceback.print_exc(file=sys.stderr)
```

# 重新加载模块，不用开启新shell

```python
>>> import func from module
>>> func()
"This is result..."

# Make some changes to "func"
>>> func()
"This is result..."  # Outdated result
>>> from importlib import reload; reload(module)  # Reload "module" after changes made to "func"
>>> func()
"New result...
```

不必陷入编辑临时文件，执行，再改，再执行的循环



## ref

1. https://martinheinz.dev/blog/24
2. 日志装饰器这个是装饰器典型用法了，但是却没真正用到代码里，真是惭愧啊
3. 作者还推荐 https://remysharp.com/2015/10/14/the-art-of-debugging，不过我打不开这个网址，改天看吧

---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。

1. 

   

---

Any advice mailto:wanghenshui@qq.com, thanks! 

Pulling a [issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) is fine! I can get noticed from email.

看到这里或许你有建议或者疑问或者指出我的错误，我的邮箱wanghenshui@qq.com 先谢指教。或者到博客上提[issue](https://github.com/wanghenshui/wanghenshui.github.io/issues/new) 我能收到邮件提醒。