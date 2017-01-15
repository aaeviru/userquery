#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import math
from os import path

sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from pythonlib import semantic as sm


num = 0
tin = 0

wtol = sm.readwl("/home/ec2-user/git/statresult/wordslist_dsw_top1000.txt")

for root, dirs, files in os.walk('/home/ec2-user/data/topics/'):
    for name in files:
        filename = root + '/' + name
        if name.isdigit():
            fin = open(filename+'.txt','r')
            temp = fin.readlines()
            fin.close()
            for i in temp:
                i = i.strip('\n')
                num = num +1
                if i in wtol:
                    tin = tin + 1

print num,tin
print 1.0*tin/num
