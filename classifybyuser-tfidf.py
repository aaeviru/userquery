#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import math
import re
from os import path
import numpy as np
from scipy import spatial

sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from pythonlib import semantic as sm

if len(sys.argv) != 4:
    print "input:topic-folder,cl-file,cl-floder"
    sys.exit(1)


def vecof(lines,a,wtol,kk):
    vec = np.zeros(kk)
    for line in lines:
        line = line.strip('\n')
        vec = vec + a[:,wtol[line]]
    return vec

root = sys.argv[1]
cll = sm.readcll2(sys.argv[2])
clpath = sys.argv[3]

wtol = sm.readwl("/home/ec2-user/git/statresult/wordslist_dsw.txt")
a = np.load('/home/ec2-user/data/classinfo/vt.npy')#lsa result
kk = a.shape[0]

u = {}

for root, dirs, files in os.walk(root):
    for name in files:
        filename = root + '/' + name
        if name.isdigit():
            fin = open(filename,'r')
            temp = fin.read()
            fin.close()
            cl = re.search(r'【出願人】.【識別番号】.*?【氏名又は名称】(.*?)【',temp,re.DOTALL)
            user = cl.group(1)
            if user not in u:
                u[user] = set()
            u[user].add(name)

total = 0
hit = 0
usernum = 0
for user in u:
    if len(u[user]) > 5:
        print user
        usernum = usernum + 1
        count = 0
        vec = [np.zeros(kk) for i in range(0,4)]
        vect = [np.zeros(kk) for i in range(0,4)]
        for name in u[user]:
            count = count + 1
            fin = open(root+name,'r')
            line = fin.read()
            title = re.search(r'【発明の名称】(.*?)\(',line,re.DOTALL)
            cl = re.search(r'(【国際特許分類第.*版】.*?)([A-H][0-9]+?[A-Z])',line,re.DOTALL)
            #print title.group(1)
            #print cl.group(2)
            result = sm.dg2(root+name,cll,clpath,1.04,2)
            if result == None:
                continue
            dl = np.array([10.0 for i in range(0,len(result)-1)])
	    print '@'+root+name
	    for i in range(0,len(result)-1):
                if count == 1:
                    vect[i] = vecof(result[i],a,wtol,kk)
		else:
                    for j in range(0,len(result)-1):
                        vecr = vecof(result[i],a,wtol,kk)
                        dlt = spatial.distance.cosine(vecr,vec[j])
                        #print i,j,vecr.argmax(),dlt
                        if(dlt<dl[i]):
                            dl[i] = dlt
                            vect[i] = vec[j]
                    vect[i] = (vecr + vect[i] * count)/(count+1)
            
            for i in range(0,len(result)-1):
                vec[i] = vect[i]        
            if count > 1:
                total = total +1
                if dl.argmin() == 3:
                    hit = hit + 1


print 'usernum:',usernum
print 'hit:',hit
print 'total:',total
print 'hit/total:',hit*1.0/total
