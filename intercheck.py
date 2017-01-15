#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import math
import re
import operator
from os import path
from scipy import spatial
import numpy as np

sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from pythonlib import semantic as sm
from pythonlib import attack
from pythonlib import sysf
from pythonlib import crand
from pythonlib import getapy as gp

inputform = "topic-folder,cl-file,cl-floder,zipf,stype[0(tfidf)/1(tfidf2)/2(lsa)/3(lda)],output-floder"

if len(sys.argv) != 7:
    print "input:" + inputform
    sys.exit(1)

outf = sys.argv[6]+'/sim-'+'-'.join(map(lambda x:x.strip('/').split('/')[-1],sys.argv[2:-1]))
fout = sysf.logger(outf,inputform)
otype = 0
if sys.argv[6] == 'stdout':
    otype = 1
otype = 0

stype = int(sys.argv[5])
zipf = float(sys.argv[4])

if stype == 3:
    b = np.load('/home/ec2-user/git/statresult/lda-64-2000-top1000-phi.npy')
    s = np.load('/home/ec2-user/git/statresult/lda-64-2000-top1000-pz.npy')
    wtolu = sm.readwl("/home/ec2-user/git/statresult/wordslist_dsw_top1000.txt")
    ukk = b.shape[0]
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
mthit = 0
mtls = 0
usernum = 0
intersetsize = 0.0
dummylen = len(cll.values()[0])
wam = gp.init("NTCIR")
getar = gp.intp(1000)
srp20 = 0
srp100 = 0
srp500 = 0
srp1000 = 0



for user in u:
    if len(u[user]) > 10:
        print user
        usernum = usernum + 1
        count = 0
        pu = []
        inter = {}
        for name in u[user]:
	    print '@'+root+name
            count = count + 1
            fin  = open(root+name+'.txt','r')
            lines = fin.readlines()
            fin.close()
            for line in lines:
                line = line.strip('\n')
                if line in inter:
                    inter[line] = inter[line] + 1
                else:
                    inter[line] = 1
            si = sorted(inter.items(), key=operator.itemgetter(1))
            si.reverse()
            nn = 0
            mm = si[0][1]
            ti = []
            for i in si:
                if i[1] == mm:
                    ti.append(i[0])
                elif i[1] < mm:
                    ti.append(i[0])
                    mm = i[1]
                    nn = nn + 1
                    if nn >= 3:
                        break
            if count < 4:
                pu.append([line.strip('\n') for line in lines])
            else:
                #result = sm.dg5(root+name,sys.argv[3],None,None,dummylen,b,s,wtolu,ukk,stype)
                result = sm.dg6(root+name,sys.argv[3],None,None,ti,dummylen,b,s,wtolu,ukk,stype)
                sim = []
                for i in range(0,len(result)-1):
                    sim.append(attack.simatt(result[i],pu))
                total = total +1
                if np.array(sim).argmax() == int(result[-1]):
                    hit = hit + 1
                srlen = gp.search(wam,list(result[int(result[-1])]),getar,1000)
                rqn = np.array([getar[i] for i in range(srlen)])
		srlen = gp.search(wam,list(attack.sis(result[int(result[-1])],pu)),getar,1000)
                dqn = np.array([getar[i] for i in range(srlen)])
                srp20 = srp20 + len(np.intersect1d(rqn[0:20],dqn[2:20]))*1.0/20.0
		srp100 = srp100 + len(np.intersect1d(rqn[0:100],dqn[0:100]))*1.0/100.0
		srp500 = srp500 + len(np.intersect1d(rqn[0:500],dqn[0:500]))*1.0/500.0
		srp1000 = srp1000 + len(np.intersect1d(rqn,dqn))*1.0/len(rqn)
                print srp20/total,srp100/total,srp500/total,srp1000/total



                intersetsize = intersetsize + len(attack.sis(result[int(result[-1])],pu))/1.0/len(result[1])

print 'usernum:',usernum
print 'hit:',hit
print 'total:',total
print 'hit/total:',hit*1.0/total
print 'intersetsize/total',intersetsize/total

sysf.pend()
