---
layout: post
title: 生成memtier 验证数据
categories: [database]
tags: [python, memtier,redis]
---

用chatgpt生成的代码改的，chatgpt太强了

<!-- more -->

生成的格式在这里
https://github.com/RedisLabs/memtier_benchmark/blob/master/README.import


直接贴代码了

```python

import csv
import time
import random
import string
import argparse
from typing import Generator, Dict

class RecordGenerator:
    """记录生成器类"""
    def __init__(self):
        self.current_time = int(time.time())

    def generate_random_string(self, min_length: int = 5, max_length: int = 20) -> str:
        """
        生成随机字符串
        """
        length = random.randint(min_length, max_length)
        res = ''.join(random.choices(string.ascii_lowercase, k=length))
        return "'" + res + "'"

    def generate_record(self) -> Dict:
        """
        生成单条记录
        """
        # 生成随机key和data
        key = self.generate_random_string(20, 50)
        data = self.generate_random_string(60, 200)
        
        # 计算实际长度
        actual_key_length = len(key)
        actual_data_length = len(data)
        #   To avoid unnecessary error while passing file 
        #     1. Add extra 4 bytes in nbytes
        #     2. Add extra 2 bytes in nkey
        # 我们生成的数据是多引号的，已经+2了
        return {
            'dumpflags': '0',
            ' time': ' 0', #self.current_time,
            ' exptime': ' 60', #self.current_time + random.randint(60, 3600),
            ' nbytes': f' {actual_data_length +2}',
            ' nsuffix': f' {random.randint(100, 300)}',
            ' it_flags': ' 0',
            ' clsid': ' 1',
            ' nkey': f' {actual_key_length}', ## 已经加2了
            ' key': f' {key}', 
            ' data': f' {data}'  
        }

    def records(self, num_records: int) -> Generator[Dict, None, None]:
        """
        生成记录的生成器
        """
        for _ in range(num_records):
            yield self.generate_record()

class CSVWriter:
    """CSV文件写入器类"""
    def __init__(self, filename: str):
        self.filename = filename
        self.fieldnames = [
            'dumpflags', ' time', ' exptime', ' nbytes', ' nsuffix',
            ' it_flags', ' clsid', ' nkey', ' key', ' data'
        ]

    def write_records(self, records_generator: Generator[Dict, None, None]) -> int:
        """
        将记录写入CSV文件
        返回写入的记录数量
        """
        count = 0
        try:
            with open(self.filename, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                writer.writeheader()
                
                for record in records_generator:
                    writer.writerow(record)
                    count += 1
                    # 每1000条记录显示一次进度
                    if count % 1000 == 0:
                        print(f"已生成 {count} 条记录...")
            
            return count
        except Exception as e:
            print(f"写入文件时发生错误：{e}")
            return count

def parse_arguments() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='memtierbenchmark data load CSV文件')
    parser.add_argument('-n', '--number', 
                       type=int, 
                       default=10,
                       help='要生成的记录数量（默认：10）')
    parser.add_argument('-o', '--output',
                       type=str,
                       default='output.csv',
                       help='output.csv）')
    return parser.parse_args()

def main():
    # 解析命令行参数
    args = parse_arguments()
    
    try:
        # 验证输入参数
        if args.number <= 0:
            raise ValueError("记录数量必须大于0")
        
        print(f"开始生成 {args.number} 条记录...")
        start_time = time.time()

        # 创建生成器和写入器
        generator = RecordGenerator()
        writer = CSVWriter(args.output)
        
        # 生成并写入记录
        records_count = writer.write_records(generator.records(args.number))
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 输出统计信息
        print(f"\n完成！")
        print(f"生成文件：{args.output}")
        print(f"记录数量：{records_count}")
        print(f"耗时：{duration:.2f} 秒")
        print(f"平均速度：{records_count/duration:.2f} 记录/秒")
        
    except ValueError as ve:
        print(f"参数错误：{ve}")
    except Exception as e:
        print(f"程序执行出错：{e}")

if __name__ == "__main__":
    main()

# python3 gen.py -n 10000000 -o output.csv
```
