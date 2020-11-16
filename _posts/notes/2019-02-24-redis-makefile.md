---
layout: post
title: 看redis makefile，重新学习makefile
category: database
tags: [redis, c]
---

  

>曾经我以为我懂makefile，看着网上的一步一步教你写makefile读完，感觉自己啥都会了。makefile不就是个语法诡异的perl吗，都有cmake了谁还有make。那个时候，我既不懂编译原理，也不懂perl，更不懂cmake，现在我也不太懂。



简单概括流程 

- 顶层makefile直接 引导到src目录`$(MAKE) $@` 转发到子目录

- 调用mkrelease.sh 生成release.sh 
  - 这个脚本会手动pull更新代码和submodule
  - 注意权限，否则无法生成release.h，这个文件记录最新的git commit和sha1

- 走%.o: %.c .make-prerequisites，判断依赖make-prerequisites是否存在，然后找persisi-setting, 然后找到make-setting，如果已经存在了，就会直接编译o文件&链接了。
- 生成.make-settings，缓存编译配置。注意该配置不make distclean会一直生效
- make deps   注意有些有文件生成，需要脚本权限(jemalloc说的就是你

  ```
chmod 777 deps/jemalloc/configure
chmod 777 src/mkreleasehdr.sh
chmod 777 deps/jemalloc/include/jemalloc/*
chmod 777 deps/jemalloc/scripts/*
  ```

- 子模块编译注意
  - 同redis编译逻辑，会生成make-setting文件，注意清理要make distclean，不过redis目录也得清理，不然走不进这个分支流程
  - redis编译flag和子模块不一样，比如hiredis子模块是gnu， 本体是c99, 就会重编，按理说这个场景会判断出来。但是有的模块没有判定，比如jemalloc。这里感觉会有坑。已经遇到了一个连接错误的问题，发现jemalloc不知怎么的改成gnu11编译了。保险起见deps目录make distclean， redis src目录 make distclean

- 按照设定和生成的deps编译，然后根据设定链接，然后走all的规则内容，逐个链接
- 最后提示make test 运行测试



这里面好多规则跳跃，有点迷糊。



make流程日志

```
[root@redis]# make
cd src && make all
sh: ./mkreleasehdr.sh: Permission denied #注意这里，需要权限
make[1]: Entering directory `/root/redis/src'
    CC Makefile.dep
make[1]: Leaving directory `/root/redis/src'
sh: ./mkreleasehdr.sh: Permission denied
make[1]: Entering directory `/root/redis/src'
rm -rf redis-server redis-sentinel redis-cli redis-benchmark redis-check-rdb redis-check-aof *.o *.gcda *.gcno *.gcov redis.info lcov-html Makefile.dep dict-benchmark
(cd ../deps && make distclean)
make[2]: Entering directory `/root/redis/deps'
(cd hiredis && make clean) > /dev/null || true
(cd linenoise && make clean) > /dev/null || true
(cd lua && make clean) > /dev/null || true
(cd jemalloc && [ -f Makefile ] && make distclean) > /dev/null || true
(rm -f .make-*)
make[2]: Leaving directory `/root/redis/deps'
(rm -f .make-*)
echo STD=-std=c99 -pedantic -Dredis_STATIC='' >> .make-settings
echo WARN=-Wall -W -Wno-missing-field-initializers >> .make-settings
echo OPT=-O2 >> .make-settings
echo MALLOC=jemalloc >> .make-settings
echo CFLAGS= >> .make-settings
echo LDFLAGS= >> .make-settings
echo redis_CFLAGS= >> .make-settings
echo redis_LDFLAGS= >> .make-settings
echo PREV_FINAL_CFLAGS=-std=c99 -pedantic -Dredis_STATIC='' -Wall -W -Wno-missing-field-initializers -O2 -g -ggdb   -I../deps/hiredis -I../deps/linenoise -I../deps/lua/src -DUSE_JEMALLOC -I../deps/jemalloc/include >> .make-settings
echo PREV_FINAL_LDFLAGS=  -g -ggdb -rdynamic >> .make-settings
(cd ../deps && make hiredis linenoise lua jemalloc)
make[2]: Entering directory `/root/redis/deps'
(cd hiredis && make clean) > /dev/null || true
(cd linenoise && make clean) > /dev/null || true
(cd lua && make clean) > /dev/null || true
(cd jemalloc && [ -f Makefile ] && make distclean) > /dev/null || true
(rm -f .make-*)
(echo "" > .make-cflags)
(echo "" > .make-ldflags)
MAKE hiredis
cd hiredis && make static
make[3]: Entering directory `/root/redis/deps/hiredis'
ar rcs libhiredis.a net.o hiredis.o sds.o async.o read.o
make[3]: Leaving directory `/root/redis/deps/hiredis'
MAKE linenoise
cd linenoise && make
make[3]: Entering directory `/root/redis/deps/linenoise'
cc  -Wall -Os -g  -c linenoise.c
make[3]: Leaving directory `/root/redis/deps/linenoise'
MAKE lua
cd lua/src && make all CFLAGS="-O2 -Wall -DLUA_ANSI -DENABLE_CJSON_GLOBAL -Dredis_STATIC='' " MYLDFLAGS="" AR="ar rcu"
make[3]: Entering directory `/root/redis/deps/lua/src'
cc -o luac  luac.o print.o liblua.a -lm
make[3]: Leaving directory `/root/redis/deps/lua/src'
MAKE jemalloc
cd jemalloc && ./configure --with-version=5.1.0-0-g0 --with-lg-quantum=3 --with-jemalloc-prefix=je_ --enable-cc-silence CFLAGS="-std=gnu99 -Wall -pipe -g3 -O3 -funroll-loops " LDFLAGS=""
///bin/sh: ./configure: Permission denied   注意这里，也需要权限
make[2]: *** [jemalloc] Error 126
make[2]: Leaving directory `/root/redis/deps'
make[1]: [persist-settings] Error 2 (ignored)
```



```
# redis Makefile
# Copyright (C) 2009 Salvatore Sanfilippo <antirez at gmail dot com>
# This file is released under the BSD license, see the COPYING file
#
# The Makefile composes the final FINAL_CFLAGS and FINAL_LDFLAGS using
# what is needed for redis plus the standard CFLAGS and LDFLAGS passed.
# However when building the dependencies (Jemalloc, Lua, Hiredis, ...)
# CFLAGS and LDFLAGS are propagated to the dependencies, so to pass
# flags only to be used when compiling / linking redis itself redis_CFLAGS
# and redis_LDFLAGS are used instead (this is the case of 'make gcov').
#
# Dependencies are stored in the Makefile.dep file. To rebuild this file
# Just use 'make dep', but this is only needed by developers.

#生成 release信息
release_hdr := $(shell sh -c './mkreleasehdr.sh')
#提取Linux
uname_S := $(shell sh -c 'uname -s 2>/dev/null || echo not')
#提取 x85_64
uname_M := $(shell sh -c 'uname -m 2>/dev/null || echo not')
# 优化等级
OPTIMIZATION?=-O2
# 子模块，注意，这里的内容会被转发给make，进入deps层编译，如果加子模块需要改动这里
DEPENDENCY_TARGETS=hiredis linenoise lua
NODEPS:=clean distclean

# Default settings
# 注意这个std=c99
STD=-std=c99 -pedantic -Dredis_STATIC=''
ifneq (,$(findstring clang,$(CC)))
ifneq (,$(findstring FreeBSD,$(uname_S)))
  #不用c11拓展？为了兼容性吧，本身都 c99 l 
  STD+=-Wno-c11-extensions
endif
endif
WARN=-Wall -W -Wno-missing-field-initializers
OPT=$(OPTIMIZATION)

PREFIX?=/usr/local
INSTALL_BIN=$(PREFIX)/bin
INSTALL=install

#设置内存分配器，默认jemalloc
# Default allocator defaults to Jemalloc if it's not an ARM
MALLOC=libc
ifneq ($(uname_M),armv6l)
ifneq ($(uname_M),armv7l)
ifeq ($(uname_S),Linux)
	MALLOC=jemalloc
endif
endif
endif

# To get ARM stack traces if redis crashes we need a special C flag.
ifneq (,$(filter aarch64 armv,$(uname_M)))
        CFLAGS+=-funwind-tables
else
ifneq (,$(findstring armv,$(uname_M)))
        CFLAGS+=-funwind-tables
endif
endif

# Backwards compatibility for selecting an allocator
ifeq ($(USE_TCMALLOC),yes)
	MALLOC=tcmalloc
endif

ifeq ($(USE_TCMALLOC_MINIMAL),yes)
	MALLOC=tcmalloc_minimal
endif

ifeq ($(USE_JEMALLOC),yes)
	MALLOC=jemalloc
endif

ifeq ($(USE_JEMALLOC),no)
	MALLOC=libc
endif

# Override default settings if possible
#注意这行 默认是会生成一个 .make-settings文件的，如果有这个文件
#就不会再生成了，所有编译选线都缓存了，所以光改makefile没用，还得把这个文件删掉(make distclean)
-include .make-settings

#下面是调试符号支持和pthread支持，平台各异
FINAL_CFLAGS=$(STD) $(WARN) $(OPT) $(DEBUG) $(CFLAGS) $(redis_CFLAGS)
FINAL_LDFLAGS=$(LDFLAGS) $(redis_LDFLAGS) $(DEBUG)
FINAL_LIBS=-lm
DEBUG=-g -ggdb

ifeq ($(uname_S),SunOS)
	# SunOS
        ifneq ($(@@),32bit)
		CFLAGS+= -m64
		LDFLAGS+= -m64
	endif
	DEBUG=-g
	DEBUG_FLAGS=-g
	export CFLAGS LDFLAGS DEBUG DEBUG_FLAGS
	INSTALL=cp -pf
	FINAL_CFLAGS+= -D__EXTENSIONS__ -D_XPG6
	FINAL_LIBS+= -ldl -lnsl -lsocket -lresolv -lpthread -lrt
else
ifeq ($(uname_S),Darwin)
	# Darwin
	FINAL_LIBS+= -ldl
else
ifeq ($(uname_S),AIX)
        # AIX
        FINAL_LDFLAGS+= -Wl,-bexpall
        FINAL_LIBS+=-ldl -pthread -lcrypt -lbsd
else
ifeq ($(uname_S),OpenBSD)
	# OpenBSD
	FINAL_LIBS+= -lpthread
	ifeq ($(USE_BACKTRACE),yes)
	    FINAL_CFLAGS+= -DUSE_BACKTRACE -I/usr/local/include
	    FINAL_LDFLAGS+= -L/usr/local/lib
	    FINAL_LIBS+= -lexecinfo
    	endif

else
ifeq ($(uname_S),FreeBSD)
	# FreeBSD
	FINAL_LIBS+= -lpthread -lexecinfo
else
ifeq ($(uname_S),DragonFly)
	# FreeBSD
	FINAL_LIBS+= -lpthread -lexecinfo
else
	# All the other OSes (notably Linux)
	FINAL_LDFLAGS+= -rdynamic
	FINAL_LIBS+=-ldl -pthread -lrt
endif
endif
endif
endif
endif
endif

#这里是deps目录，指定目录放在这
# Include paths to dependencies
FINAL_CFLAGS+= -I../deps/hiredis -I../deps/linenoise -I../deps/lua/src 

ifeq ($(MALLOC),tcmalloc)
	FINAL_CFLAGS+= -DUSE_TCMALLOC
	FINAL_LIBS+= -ltcmalloc
endif

ifeq ($(MALLOC),tcmalloc_minimal)
	FINAL_CFLAGS+= -DUSE_TCMALLOC
	FINAL_LIBS+= -ltcmalloc_minimal
endif

ifeq ($(MALLOC),jemalloc)
	DEPENDENCY_TARGETS+= jemalloc
	FINAL_CFLAGS+= -DUSE_JEMALLOC -I../deps/jemalloc/include
	FINAL_LIBS := ../deps/jemalloc/lib/libjemalloc.a $(FINAL_LIBS)
endif

redis_CC=$(QUIET_CC)$(CC) $(FINAL_CFLAGS)
redis_LD=$(QUIET_LINK)$(CC) $(FINAL_LDFLAGS)
redis_INSTALL=$(QUIET_INSTALL)$(INSTALL)

CCCOLOR="\033[34m"
LINKCOLOR="\033[34;1m"
SRCCOLOR="\033[33m"
BINCOLOR="\033[37;1m"
MAKECOLOR="\033[32;1m"
ENDCOLOR="\033[0m"

ifndef V
QUIET_CC = @printf '    %b %b\n' $(CCCOLOR)CC$(ENDCOLOR) $(SRCCOLOR)$@$(ENDCOLOR) 1>&2;
QUIET_LINK = @printf '    %b %b\n' $(LINKCOLOR)LINK$(ENDCOLOR) $(BINCOLOR)$@$(ENDCOLOR) 1>&2;
QUIET_INSTALL = @printf '    %b %b\n' $(LINKCOLOR)INSTALL$(ENDCOLOR) $(BINCOLOR)$@$(ENDCOLOR) 1>&2;
endif

#所有生成文件的obj文件依赖，手写。见all哪里，指定生成文件，调到相应规则，然后找这里的依赖
redis_SERVER_NAME=redis-server
redis_SENTINEL_NAME=redis-sentinel
redis_SERVER_OBJ=adlist.o quicklist.o ae.o anet.o dict.o server.o sds.o zmalloc.o lzf_c.o lzf_d.o pqsort.o zipmap.o sha1.o ziplist.o release.o networking.o util.o object.o db.o replication.o rdb.o t_string.o t_list.o t_set.o t_zset.o t_hash.o config.o aof.o pubsub.o multi.o debug.o sort.o intset.o syncio.o cluster.o crc16.o endianconv.o slowlog.o scripting.o bio.o rio.o rand.o memtest.o crc64.o bitops.o sentinel.o notify.o setproctitle.o blocked.o hyperloglog.o latency.o sparkline.o redis-check-rdb.o redis-check-aof.o geo.o lazyfree.o module.o evict.o expire.o geohash.o geohash_helper.o childinfo.o defrag.o siphash.o rax.o t_stream.o listpack.o localtime.o lolwut.o lolwut5.o swapdata.o thpool.o sp_queue.o
redis_CLI_NAME=redis-cli
redis_CLI_OBJ=anet.o adlist.o dict.o redis-cli.o zmalloc.o release.o anet.o ae.o crc64.o siphash.o crc16.o
redis_BENCHMARK_NAME=redis-benchmark
redis_BENCHMARK_OBJ=ae.o anet.o redis-benchmark.o adlist.o zmalloc.o redis-benchmark.o
redis_CHECK_RDB_NAME=redis-check-rdb
redis_CHECK_AOF_NAME=redis-check-aof

#这是所有编译入口，逐个编译。之前会生成dep，生成依赖。这里的流程没有搞清楚
all: $(redis_SERVER_NAME) $(redis_SENTINEL_NAME) $(redis_CLI_NAME) $(redis_BENCHMARK_NAME) $(redis_CHECK_RDB_NAME) $(redis_CHECK_AOF_NAME)
	@echo ""
	@echo "Hint: It's a good idea to run 'make test' ;)"
	@echo ""

Makefile.dep:
	-$(redis_CC) -MM *.c > Makefile.dep 2> /dev/null || true

ifeq (0, $(words $(findstring $(MAKECMDGOALS), $(NODEPS))))
-include Makefile.dep
endif

.PHONY: all
#生成 .make-setting，这里都是编译配置
persist-settings: distclean
	echo STD=$(STD) >> .make-settings
	echo WARN=$(WARN) >> .make-settings
	echo OPT=$(OPT) >> .make-settings
	echo MALLOC=$(MALLOC) >> .make-settings
	echo CFLAGS=$(CFLAGS) >> .make-settings
	echo LDFLAGS=$(LDFLAGS) >> .make-settings
	echo redis_CFLAGS=$(redis_CFLAGS) >> .make-settings
	echo redis_LDFLAGS=$(redis_LDFLAGS) >> .make-settings
	echo PREV_FINAL_CFLAGS=$(FINAL_CFLAGS) >> .make-settings
	echo PREV_FINAL_LDFLAGS=$(FINAL_LDFLAGS) >> .make-settings
	#注意这里，生成编译配置后会进入deps编译子模块
	-(cd ../deps && $(MAKE) $(DEPENDENCY_TARGETS))

.PHONY: persist-settings

#检测是否生成make-setting的一个占位符
# Prerequisites target
.make-prerequisites:
	@touch $@

# Clean everything, persist settings and build dependencies if anything changed
ifneq ($(strip $(PREV_FINAL_CFLAGS)), $(strip $(FINAL_CFLAGS)))
.make-prerequisites: persist-settings
endif

ifneq ($(strip $(PREV_FINAL_LDFLAGS)), $(strip $(FINAL_LDFLAGS)))
.make-prerequisites: persist-settings
endif

#所有二进制依赖
# redis-server
$(redis_SERVER_NAME): $(redis_SERVER_OBJ)
	$(redis_LD) -o $@ $^ ../deps/hiredis/libhiredis.a ../deps/lua/src/liblua.a  $(FINAL_LIBS)

# redis-sentinel
$(redis_SENTINEL_NAME): $(redis_SERVER_NAME)
	$(redis_INSTALL) $(redis_SERVER_NAME) $(redis_SENTINEL_NAME)

# redis-check-rdb
$(redis_CHECK_RDB_NAME): $(redis_SERVER_NAME)
	$(redis_INSTALL) $(redis_SERVER_NAME) $(redis_CHECK_RDB_NAME)

# redis-check-aof
$(redis_CHECK_AOF_NAME): $(redis_SERVER_NAME)
	$(redis_INSTALL) $(redis_SERVER_NAME) $(redis_CHECK_AOF_NAME)

# redis-cli
$(redis_CLI_NAME): $(redis_CLI_OBJ)
	$(redis_LD) -o $@ $^ ../deps/hiredis/libhiredis.a ../deps/linenoise/linenoise.o $(FINAL_LIBS)

# redis-benchmark
$(redis_BENCHMARK_NAME): $(redis_BENCHMARK_OBJ)
	$(redis_LD) -o $@ $^ ../deps/hiredis/libhiredis.a $(FINAL_LIBS)

dict-benchmark: dict.c zmalloc.c sds.c siphash.c
	$(redis_CC) $(FINAL_CFLAGS) $^ -D DICT_BENCHMARK_MAIN -o $@ $(FINAL_LIBS)

# Because the jemalloc.h header is generated as a part of the jemalloc build,
# building it should complete before building any other object. Instead of
# depending on a single artifact, build all dependencies first.

#最开始执行这个，编译，检查prerequisites，不满足会跳到
# persis-setting ，跳到到make-setting, 然后执行编译生成obj文件，最后执行all。
%.o: %.c .make-prerequisites 
	$(redis_CC) -c $<

#注意这个清理是不清理 .make*文件的。对于普通用户来说，这加速编译了一下，不用反复编译deps模块，对于开发者要注意。
clean:
	rm -rf $(redis_SERVER_NAME) $(redis_SENTINEL_NAME) $(redis_CLI_NAME) $(redis_BENCHMARK_NAME) $(redis_CHECK_RDB_NAME) $(redis_CHECK_AOF_NAME) *.o *.gcda *.gcno *.gcov redis.info lcov-html Makefile.dep dict-benchmark

.PHONY: clean

distclean: clean
	-(cd ../deps && $(MAKE) distclean)
	-(rm -f .make-*)

.PHONY: distclean

test: $(redis_SERVER_NAME) $(redis_CHECK_AOF_NAME)
	@(cd ..; ./runtest)

test-sentinel: $(redis_SENTINEL_NAME)
	@(cd ..; ./runtest-sentinel)

check: test

lcov:
	$(MAKE) gcov
	@(set -e; cd ..; ./runtest --clients 1)
	@geninfo -o redis.info .
	@genhtml --legend -o lcov-html redis.info

test-sds: sds.c sds.h
	$(redis_CC) sds.c zmalloc.c -DSDS_TEST_MAIN $(FINAL_LIBS) -o /tmp/sds_test
	/tmp/sds_test

.PHONY: lcov

bench: $(redis_BENCHMARK_NAME)
	./$(redis_BENCHMARK_NAME)

32bit:
	@echo ""
	@echo "WARNING: if it fails under Linux you probably need to install libc6-dev-i386"
	@echo ""
	$(MAKE) CFLAGS="-m32" LDFLAGS="-m32"

gcov:
	$(MAKE) redis_CFLAGS="-fprofile-arcs -ftest-coverage -DCOVERAGE_TEST" redis_LDFLAGS="-fprofile-arcs -ftest-coverage"

noopt:
	$(MAKE) OPTIMIZATION="-O0"

valgrind:
	$(MAKE) OPTIMIZATION="-O0" MALLOC="libc"

helgrind:
	$(MAKE) OPTIMIZATION="-O0" MALLOC="libc" CFLAGS="-D__ATOMIC_VAR_FORCE_SYNC_MACROS"

src/help.h:
	@../utils/generate-command-help.rb > help.h

install: all
	@mkdir -p $(INSTALL_BIN)
	$(redis_INSTALL) $(redis_SERVER_NAME) $(INSTALL_BIN)
	$(redis_INSTALL) $(redis_BENCHMARK_NAME) $(INSTALL_BIN)
	$(redis_INSTALL) $(redis_CLI_NAME) $(INSTALL_BIN)
	$(redis_INSTALL) $(redis_CHECK_RDB_NAME) $(INSTALL_BIN)
	$(redis_INSTALL) $(redis_CHECK_AOF_NAME) $(INSTALL_BIN)
	@ln -sf $(redis_SERVER_NAME) $(INSTALL_BIN)/$(redis_SENTINEL_NAME)

```



### 参考

- make 参考文档 https://www.gnu.org/software/make/manual/make.pdf

- 跟我一起写makefile https://seisman.github.io/how-to-write-makefile

看到这里或许你有建议或者疑问，我的邮箱wanghenshui@qq.com 先谢指教。