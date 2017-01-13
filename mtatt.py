#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import math
import re
import random
from os import path
from scipy import spatial
import numpy as np

sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from pythonlib import semantic as sm
from pythonlib import sysf
from pythonlib import crand
from pythonlib import getapy as gp
from pythonlib import attack

inputform = "topic-folder,cl-file,cl-floder,zipf,stype[0(tfidf)/1(tfidf2)/2(lsa)/3(lda)],dtype[<0(diff*rand)/0(diff)/1(same)/>=2(diff*same)],atype[1(tfidf)/2(lsa)/3(lda)],output-floder"

if len(sys.argv) != 9:
    print "input:" + inputform
    sys.exit(1)

outf = sys.argv[-1]+'/uqc-'+'-'.join(map(lambda x:x.strip('/').split('/')[-1],sys.argv[2:-1]))
fout = sysf.logger(outf,inputform)

def vecof(lines,a,wtol,kk):
    vec = np.zeros(kk)
    for line in lines:
        line = line.strip('\n')
        vec = vec + a[:,wtol[line]]
    return vec

stype = int(sys.argv[5])
dtype = int(sys.argv[6])
atype = int(sys.argv[7])
zipf = float(sys.argv[4])
otype = 0
if sys.argv[-1] == 'stdout':
    otype = 1



if atype == 2:
    wtola = sm.readwl("/home/ec2-user/git/statresult/wordslist_dsw.txt")
    a = np.load('/home/ec2-user/data/classinfo/vt.npy')#lsa result
    sa = None
elif atype == 3:
    wtola = sm.readwl("/home/ec2-user/git/statresult/wordslist_dsw_top1000.txt")
    a = np.load('/home/ec2-user/git/statresult/lda-64-2000-top1000-phi.npy')
    sa = np.load('/home/ec2-user/git/statresult/lda-64-2000-top1000-pz.npy')

akk = a.shape[0]

if stype == 2:
    wtolu = sm.readwl("/home/ec2-user/git/statresult/wordslist_dsw.txt")
    b = np.load('/home/ec2-user/data/classinfo/vt.npy')#lsa result
    s = None
elif stype == 3:
    wtolu = sm.readwl("/home/ec2-user/git/statresult/wordslist_dsw_top1000.txt")
    b = np.load('/home/ec2-user/git/statresult/lda-64-2000-top1000-phi.npy')
    s = np.load('/home/ec2-user/git/statresult/lda-64-2000-top1000-pz.npy')
    if type(zipf) == float and zipf < 0:
        fldawl = open('/home/ec2-user/git/statresult/wordslist_dsw_top1000.txt','r')#wordlist for lda
        i = 0
        ltow = {}
        for line in fldawl:
            line = line.strip('\n')
            ltow[i] = line
            i = i + 1
        fldawl.close()
        p = []
        p.append(b[:,0])
        for i in range(1,b.shape[1]):
            p.append(b[:,i]+p[i-1])
        p = np.array(p)
        p = p.transpose()
if stype in (0,1):
    wtolu = None
    b = None
    ukk = 623
else:
    ukk = b.shape[0]


root = sys.argv[1]

cll = sm.readcll0(sys.argv[2],ukk,stype)

if len(cll) != ukk:
    ukk = len(cll)
    b = b[:ukk]
u = {}
querytot = []

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
                u[user] = []
            u[user].append((name,0))
            querytot.append(name)


total = 0
mthit = 0
mtls = 0
usernum = 0

for user in u:
    if len(u[user]) > 5:
        tmpuser = []
        while len(tmpuser) < -1.0 * dtype * 0.1 * len(u[user]):
            du = random.randint(0,len(querytot)-1)
            if (querytot[du],0) not in u[user]:
                tmpuser.append((querytot[du],1))
        u[user] = u[user] + tmpuser
        random.shuffle(u[user])

dummylen = len(cll.values()[0])

for user in u:
    print user
    usernum = usernum + 1
    count = 0
    for (name,real) in u[user]:
        print '@'+root+name,total
        count = count + 1
        #fin = open(root+name,'r')
        #line = fin.read()
        #title = re.search(r'【発明の名称】(.*?)\(',line,re.DOTALL)
        #cl = re.search(r'(【国際特許分類第.*版】.*?)([A-H][0-9]+?[A-Z])',line,re.DOTALL)
        #print title.group(1)
        #print cl.group(2)
        if dtype == 1:
          result = sm.dg5(root+name,sys.argv[3],None,None,dummylen,b,s,wtolu,ukk,stype)  
        elif stype == 3 and type(zipf) == float and zipf < 0:
            result = sm.dg3(root+name,cll,b,s,p,wtolu,ltow,ukk)
        elif stype == 3:
            result = sm.dg(root+name,cll,sys.argv[3],b,s,wtolu,ukk,zipf,stype)
        else:
            result = sm.dg(root+name,cll,sys.argv[3],b,None,wtolu,ukk,zipf,stype)
        mt = []
        for i in range(0,len(result)-1):
            if atype == 2:
                vec = sm.vecof(result[i],a,wtola,akk)
            elif atype == 3:
                vec = sm.vecof3(result[i],a,sa,wtola,akk)
            mt.append(vec.max())
        total = total +1
        if np.array(mt).argmax() == int(result[-1]):
            mthit = mthit + 1
        if np.array(mt).argmin() == int(result[-1]):
            mtls = mtls + 1
        if otype == 1:
            print "mt:",mt
            print result[-1]
            print "mthit:"+str(mthit)," mtls:"+str(mtls)," total:"+str(total)


print 'usernum:',usernum
print 'mthit:',mthit
print 'mthls:',mtls
print 'total:',total
print 'p:',mthit*1.0/total

sysf.pend()
