#/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
import os

def check_post_format():
    file=sys.argv[1]
    with open(file, "r+") as f:
        l=f.readlines()
        print(l)
        l.insert(6,"  \n")
        print(l)
        f.seek(0,0)
        f.truncate()
        f.writelines(l)
			
def check_img():
#replace img with link
    file=sys.argv[1]
    with open(file) as f1,open("%s.bak" % file, "w") as f2 :
        for line in f1:
            f2.write(re.sub("../../assets/","https://wanghenshui.github.io/assets/",line))

    os.remove(file)
    os.rename("%s.bak" % file, file)
            
if __name__ == '__main__':
	check_img()
	#check_post_format()
