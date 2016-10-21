#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import math
import re
from os import path
from scipy import spatial

sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from tfidf.dg_lr import *


if len(sys.argv) != 4:
    print "input:topic-folder,cl-file,cl-floder"
    sys.exit(1)


def vecof(lines,a,wtol,kk):
    vec = np.zeros(kk)
    for line in lines:
        line = line.strip('\n')
        vec = vec + a[:,wtol[line]]
    return vec

wtol = readwl("/home/ec2-user/git/statresult/wordslist_dsw.txt")
a = np.load('/home/ec2-user/data/classinfo/vt.npy')#lsa result
kk = a.shape[0]
root = sys.argv[1]

if sys.argv[2] == 'rand':
    cll = {}
    for i in range(0,kk):
	cll[i] = np.random.randint(kk,size=3)

else:
    fcl = open(sys.argv[2],'r')
    cll = {}
    for line in fcl:
	line = line.strip(' \n')
	line = line.split(' ')
	for w in line:
	    ww = int(w)
	    cll[ww] = list(line)
	    cll[ww].remove(w)
    fcl.close()



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
for user in u:
    if len(u[user]) > 5:
        print user
        count = 0
        vec = [np.zeros(kk) for i in range(0,4)]
        vect = [np.zeros(kk) for i in range(0,4)]
        for name in u[user]:
            count = count + 1
            result = dg(root,name,cll,sys.argv[3],1.04,a,wtol,kk)
            dl = np.array([10.0 for i in range(0,len(result)-1)])
	    print '@'+root+name
	    for i in range(0,len(result)-1):
                if count == 1:
                    vect[i] = vecof(result[i],a,wtol,kk)
		else:
                    for j in range(0,len(result)-1):
                        vecr = vecof(result[i],a,wtol,kk)
                        dlt = spatial.distance.cosine(vecr,vec[j])
                        print i,j,vecr.argmax(),dlt
                        if(dlt<dl[i]):
                            dl[i] = dlt
                            vect[i] = vec[j]
                    vect[i] = (vecr + vect[i] * count)/(count+1)
            
            for i in range(0,len(result)-1):
                vec[i] = vect[i]        
            print dl.argmin()
        raw_input()

