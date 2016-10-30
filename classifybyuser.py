#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import math
import re
from os import path
from scipy import spatial
import numpy as np

sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from pythonlib import semantic as sm


if len(sys.argv) != 5:
    print "input:topic-folder,cl-file,cl-floder,type[0(lsa)/1(lda)]"
    sys.exit(1)


def vecof(lines,a,wtol,kk):
    vec = np.zeros(kk)
    for line in lines:
        line = line.strip('\n')
        vec = vec + a[:,wtol[line]]
    return vec

type = int(sys.argv[4])
wtol = sm.readwl("/home/ec2-user/git/statresult/wordslist_dsw.txt")
a = np.load('/home/ec2-user/data/classinfo/vt.npy')#lsa result
ukk = a.shape[0]
akk = ukk
if type == 1:
    b = np.load('/home/ec2-user/git/statresult/lda-30-2000-phi.npy')
    s = np.load('/home/ec2-user/git/statresult/lda-30-2000-pz.npy')
    ukk = b.shape[0]

root = sys.argv[1]

if sys.argv[2] == 'rand':
    cll = {}
    for i in range(0,ukk):
	cll[i] = np.random.randint(ukk,size=3)

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


total = 0
hit = 0
usernum = 0
for user in u:
    if len(u[user]) > 5:
        print user
        usernum = usernum + 1
        count = 0
        vec = [np.zeros(akk) for i in range(0,4)]
        vect = [np.zeros(akk) for i in range(0,4)]
        for name in u[user]:
            count = count + 1
            fin = open(root+name,'r')
            line = fin.read()
            title = re.search(r'【発明の名称】(.*?)\(',line,re.DOTALL)
            cl = re.search(r'(【国際特許分類第.*版】.*?)([A-H][0-9]+?[A-Z])',line,re.DOTALL)
            #print title.group(1)
            #print cl.group(2)
            if type == 0:
                result = sm.dg(root,name,cll,sys.argv[3],1.04,a,wtol,ukk)
            else:
                result = sm.dg3(root,name,cll,sys.argv[3],1.04,b,s,wtol,ukk)
                
            dl = np.array([10.0 for i in range(0,len(result)-1)])
	    print '@'+root+name
	    for i in range(0,len(result)-1):
                if count == 1:
                    vect[i] = sm.vecof(result[i],a,wtol,akk)
		else:
                    for j in range(0,len(result)-1):
                        vecr = sm.vecof(result[i],a,wtol,akk)
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
            #print dl.argmin()


print 'usernum:',usernum
print 'hit:',hit
print 'total:',total
print 'hit/total:',hit*1.0/total
