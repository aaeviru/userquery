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
from pythonlib import attack

inputform = "topic-folder,cl-file,cl-floder,zipf,stype[0(tfidf)/1(tfidf2)/2(lsa)/3(lda)],dtype[<0(diff*rand)/0(diff)/1(same)/>=2(diff*same)],output-floder"

if len(sys.argv) != 8:
    print "input:" + inputform
    sys.exit(1)

outf = sys.argv[-1]+'/sim2-'+'-'.join(map(lambda x:x.strip('/').split('/')[-1],sys.argv[2:-1]))
fout = sysf.logger(outf,inputform)

stype = int(sys.argv[5])
dtype = int(sys.argv[6])
otype = 0
if sys.argv[-1] == 'stdout':
    otype = 1
zipf = float(sys.argv[4])

if stype == 3:
    b = np.load('/home/ec2-user/git/statresult/lda-64-2000-top1000-phi.npy')
    s = np.load('/home/ec2-user/git/statresult/lda-64-2000-top1000-pz.npy')
    ukk = b.shape[0]
    wtolu = sm.readwl("/home/ec2-user/git/statresult/wordslist_dsw_top1000.txt")
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
elif stype == 2:
    b = np.load('/home/ec2-user/data/classinfo/vt.npy')#lsa result
    ukk = b.shape[0]
    s = None
    wtolu = sm.readwl("/home/ec2-user/git/statresult/wordslist_dsw.txt")
else:
    b = None
    s = None
    wtolu = None
    ukk = 623


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
simhit = 0
usernum = 0
simmax = 0
simmin = 10
simavg = 0

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
    if len(u[user]) > 5:
        print user
        usernum = usernum + 1
        count = 0
        pu = [[] for i in range(dummylen+1)]
        put = [[] for i in range(dummylen+1)]
        for (name,real) in u[user]:
	    print '@'+root+name,total
            count = count + 1
	    if stype == 3 and zipf < 0:
		result = sm.dg3(root+name,cll,b,s,p,wtolu,ltow,ukk)
	    else:
		result = sm.dg(root+name,cll,sys.argv[3],b,s,wtolu,ukk,zipf,stype)

            sim = np.array([0.0 for i in range(0,len(result)-1)])
	    for i in range(0,len(result)-1):
                if count == 1:
                    put[i].append(result[i][0:-2])
		else:
                    for j in range(0,len(result)-1):
                        simt = attack.simatt(result[i],pu[j])
                        if (simt>sim[i]):
                            sim[i] = simt
                            put[i] = pu[j]
                    put[i].append(result[i][0:-2])
            for i in range(0,len(result)-1):
                pu[i] = put[i]
            if real == 0:
                if count > 1:
                    total = total +1
                    if np.array(sim).argmax() == int(result[-1]):
                        simhit = simhit + 1
                    simr = sim[int(result[-1])]
                    if simr > simmax:
                        simmax = simr
                    if simr < simmin:
                        simmin = simr
                    simavg = simavg + simr
            if otype == 1:
                print "real",real
                print "sim:",sim
                print result[-1]
                print "simhit:"+str(simhit)," total:"+str(total)

print 'usernum:',usernum
print 'simhit:',simhit
print 'simmax:',simmax
print 'simmin:',simmin
print 'simavg:',simavg / total
print 'total:',total
print 'simhit/total:',simhit*1.0/total

sysf.pend()
