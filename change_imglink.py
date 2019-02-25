#/bin/env python

'''
![图4](https://wanghenshui.github.io/assets/img/rof-f-4.png)
https://wanghenshui.github.io/assets/xx.[png/jpg]
../../assets/vmportfoward.[png/jpg]
'''
import re
import sys
import os

def run():
    file=sys.argv[1]
    with open(file) as f1,open("%s.bak" % file, "w") as f2 :
        for line in f1:
            f2.write(re.sub("../../assets/","https://wanghenshui.github.io/assets/",line))

    os.remove(file)
    os.rename("%s.bak" % file, file)
            
if __name__ == '__main__':
	run()
