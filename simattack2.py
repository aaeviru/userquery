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
from pythonlib import attack
from pythonlib import sysf
from pythonlib import crand

inputform = "topic-folder,cl-file,cl-floder,zipf,stype[0(tfidf)/1(tfidf2)/2(lsa)/3(lda)],output-floder"

if len(sys.argv) != 7:
    print "input:" + inputform
    sys.exit(1)

outf = sys.argv[6]+'/sim2-'+'-'.join(map(lambda x:x.strip('/').split('/')[-1],sys.argv[2:-1]))
fout = sysf.logger(outf,inputform)

otype = 0
if sys.argv[6] == 'stdout':
    otype = 1

def vecof(lines,a,wtol,kk):
    vec = np.zeros(kk)
    for line in lines:
        line = line.strip('\n')
        vec = vec + a[:,wtol[line]]
    return vec

stype = int(sys.argv[5])
zipf = float(sys.argv[4])
wtola = sm.readwl("/home/ec2-user/git/statresult/wordslist_dsw.txt")
#zipf = crand.zipf_init(len(wtola))
if stype == 3:
    wtolu = sm.readwl("/home/ec2-user/git/statresult/wordslist_top10000_dsw.txt")
else:
    wtolu = wtola
a = np.load('/home/ec2-user/data/classinfo/vt.npy')#lsa result
b = a
ukk = a.shape[0]
s = None
akk = ukk
if stype == 3:
#    b = np.load('/home/ec2-user/git/statresult/lda-30-2000-phi.npy')
#    s = np.load('/home/ec2-user/git/statresult/lda-30-2000-pz.npy')
    b = np.load('/home/ec2-user/git/statresult/lda-32-2000-top10000-phi.npy')
    s = np.load('/home/ec2-user/git/statresult/lda-32-2000-top10000-pz.npy')
    ukk = b.shape[0]
    if type(zipf) == float and zipf < 0:
        fldawl = open('/home/ec2-user/git/statresult/wordslist_top10000_dsw.txt','r')#wordlist for lda
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
srp = 0
usernum = 0
for user in u:
    if len(u[user]) > 10:
        print user
        usernum = usernum + 1
        count = 0
        vec = [np.zeros(akk) for i in range(0,4)]
        vect = [np.zeros(akk) for i in range(0,4)]
        vecu = [np.zeros(ukk) for i in range(0,4)]
        vecut = [np.zeros(ukk) for i in range(0,4)]
        pu = [[] for i in range(4)]
        put = [[] for i in range(4)]
        for name in u[user]:
            if otype == 1:
                fin = open(root+name,'r')
                line = fin.read()
                fin.close()
                title = re.search(r'【発明の名称】(.*?)\(',line,re.DOTALL)
                cl = re.search(r'(【国際特許分類第.*版】.*?)([A-H][0-9]+?[A-Z])',line,re.DOTALL)
                print '@'+root+name
                print title.group(1)
                print cl.group(2)

            count = count + 1
            if count == 1 or type(zipf) == float and zipf < 1:
                if stype == 3 and type(zipf) == float and zipf < 0:
                    result = sm.dg3(root+name,cll,b,s,p,wtolu,ltow,ukk)
                else:
                    result = sm.dg(root+name,cll,sys.argv[3],b,s,wtolu,ukk,zipf,stype)
            else:
                if stype == 3 and type(zipf) == float and zipf < 0:
                    result = sm.dg4(root+name,cll,b,s,p,wtolu,ltow,ukk,vecu)
                else:
                    result = sm.dg2(root+name,cll,sys.argv[3],b,s,wtolu,ukk,zipf,vecu,stype)
            dlu = np.array([10.0 for i in range(0,len(result)-1)])
            sim = np.array([0.0 for i in range(0,len(result)-1)])
            mt = []
            for i in range(0,len(result)-1):
                if count == 1:
                    vect[i] = sm.vecof(result[i],a,wtola,akk)
                    mt.append(vect[i].max())
                    vecut[i] = sm.vecof0(result[i],b,s,wtolu,ukk)
                    put[i].append(result[i][0:-2])
                else:
                    vecr = sm.vecof(result[i],a,wtola,akk)
                    mt.append(vecr.max())
                    vecur = sm.vecof0(result[i],b,s,wtolu,ukk)
                    for j in range(0,len(result)-1):
                        dlt = spatial.distance.cosine(vecur,vecu[j])
                        simt = attack.simatt(result[i],pu[j])
                        if (simt>sim[i]):
                            sim[i] = simt
                            put[i] = pu[j]
                        if(dlt<dlu[i]):
                            dlu[i] = dlt
                            vecut[i] = vecu[j]
                    put[i].append(result[i][0:-2])
                    vecut[i] = (vecur + vecut[i] * count)/(count+1)
            for i in range(0,len(result)-1):
                vecu[i] = vecut[i]
                pu[i] = put[i]
            if count > 1:
                total = total +1
                if np.array(sim).argmax() == int(result[-1]):
                    hit = hit + 1
            if np.array(mt).argmax() == int(result[-1]):
                mthit = mthit + 1
            if np.array(mt).argmin() == int(result[-1]):
                mtls = mtls + 1
            if otype == 1:
                print sim,result[-1],hit

print 'usernum:',usernum
print 'hit:',hit
print 'mthit:',mthit
print 'mthls:',mtls
print 'srp:',srp
print 'total:',total
print 'hit/total:',hit*1.0/total
print 'mthit/(total+usernum):',mthit*1.0/(total+usernum)
print 'mthls/(total+usernum):',mtls*1.0/(total+usernum)
print 'srp/(total+usernum):',srp*1.0/(total+usernum)
