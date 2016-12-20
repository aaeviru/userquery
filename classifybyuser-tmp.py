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
from pythonlib import sysf
from pythonlib import crand
from pythonlib import getapy as gp
from pythonlib import attack

inputform = "topic-folder,cl-file,cl-floder,zipf,stype[num of lsa classes][0(tfidf)/1(tfidf2)/2(lsa)/3(lda)],dtype[0(diff)/1(same)],output-floder"

if len(sys.argv) != 8:
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

stype = sys.argv[5]
a = np.load('/home/ec2-user/data/classinfo/vt.npy')#lsa result
b = a
ukk = a.shape[0]
s = None
if len(stype) > 1:
    ukk = int(stype[1:])
    stype = int(stype[0])
    a = a[0:ukk]
else:
    stype = int(stype)
akk = ukk
dtype = int(sys.argv[6])
otype = 0
if sys.argv[-1] == 'stdout':
    otype = 1
zipf = float(sys.argv[4])
wtola = sm.readwl("/home/ec2-user/git/statresult/wordslist_dsw.txt")
#zipf = crand.zipf_init(len(wtola))
if stype == 3:
    wtolu = sm.readwl("/home/ec2-user/git/statresult/wordslist_top10000_dsw.txt")
else:
    wtolu = wtola
if stype == 3:
#   b = np.load('/home/ec2-user/git/statresult/lda-30-2000-phi.npy')
#   s = np.load('/home/ec2-user/git/statresult/lda-30-2000-pz.npy')
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
querytot = set()

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
            querytot.add(name)


total = 0
hit = 0
simhit = 0
mthit = 0
mtls = 0
srp = 0
srp20 = 0
srp100 = 0
srp500 = 0
usernum = 0
simmax = 0
simmin = 10
simavg = 0
dlmax = 0
dlmin = 10
dlavg = 0

dummylen = len(cll.values()[0])
wam = gp.init("NTCIR")
getar = gp.intp(1000)
for user in u:
    if len(u[user]) > 5:
        print user
        usernum = usernum + 1
        count = 0
        vec = [np.zeros(akk) for i in range(dummylen+1)]
        vect = [np.zeros(akk) for i in range(dummylen+1)]
        vecu = [np.zeros(ukk) for i in range(dummylen+1)]
        vecut = [np.zeros(ukk) for i in range(dummylen+1)]
        pu = [[] for i in range(dummylen+1)]
        put = [[] for i in range(dummylen+1)]
        for name in u[user]:
	    print '@'+root+name,total
            count = count + 1
            #fin = open(root+name,'r')
            #line = fin.read()
            #title = re.search(r'【発明の名称】(.*?)\(',line,re.DOTALL)
            #cl = re.search(r'(【国際特許分類第.*版】.*?)([A-H][0-9]+?[A-Z])',line,re.DOTALL)
            #print title.group(1)
            #print cl.group(2)
            if dtype == 1:
              result = sm.dg5(root+name,sys.argv[3],dummylen,b,s,wtolu,ukk,stype)  
            elif count == 1 or type(zipf) == float and zipf < 1:
                if stype == 3 and type(zipf) == float and zipf < 0:
                    result = sm.dg3(root+name,cll,b,s,p,wtolu,ltow,ukk)
                else:
                    result = sm.dg(root+name,cll,sys.argv[3],b,s,wtolu,ukk,zipf,stype)
            else:
                if stype == 3 and type(zipf) == float and zipf < 0:
                    result = sm.dg4(root+name,cll,b,s,p,wtolu,ltow,ukk,vecu)
                else:
                    result = sm.dg2(root+name,cll,sys.argv[3],b,s,wtolu,ukk,zipf,vecu,stype)
            #print result[-1]
            srlen = gp.search(wam,list(result[int(result[-1])]),getar,1000)
            rqn = np.array([getar[i] for i in range(srlen)])
            for i in range(len(result)-1):
                if i != int(result[-1]):
                    srlen = gp.search(wam,list(result[i]),getar,1000)
                    dqn = np.array([getar[i] for i in range(srlen)])
                    srp20 = srp20 + len(np.intersect1d(rqn[0:20],dqn[2:20]))*1.0/20.0
                    srp100 = srp100 + len(np.intersect1d(rqn[0:100],dqn[0:100]))*1.0/100.0
                    srp500 = srp500 + len(np.intersect1d(rqn[0:500],dqn[0:500]))*1.0/500.0
                    srp = srp + len(np.intersect1d(rqn,dqn))*1.0/len(rqn)

            dl = np.array([10.0 for i in range(0,len(result)-1)])
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
                        dlt = spatial.distance.cosine(vecr,vec[j])
                        simt = attack.simatt(result[i],pu[j])
                        if (simt>sim[i]):
                            sim[i] = simt
                            put[i] = pu[j]
                        #print i,j,vecr.argmax(),dlt
                        if(dlt<dl[i]):
                            dl[i] = dlt
                            vect[i] = vec[j]
                        dlt = spatial.distance.cosine(vecur,vecu[j])

                        #print vecur,vecu[j]
                        #print i,j,vecur.argmax(),dlt
                        if(dlt<dlu[i]):
                            dlu[i] = dlt
                            vecut[i] = vecu[j]
                    vecut[i] = (vecur + vecut[i] * count)/(count+1)
                    vect[i] = (vecr + vect[i] * count)/(count+1)
                    put[i].append(result[i][0:-2])
            for i in range(0,len(result)-1):
                pu[i] = put[i]
                vec[i] = vect[i]        
                vecu[i] = vecut[i]
            if count > 1:
                total = total +1
                if dl.argmin() == int(result[-1]):
                    hit = hit + 1
                if np.array(sim).argmax() == int(result[-1]):
                    simhit = simhit + 1
                simr = sim[int(result[-1])]
                dlr = dl[int(result[-1])]
                if simr > simmax:
                    simmax = simr
                if simr < simmin:
                    simmin = simr
                if dlr > dlmax:
                    dlmax = dlr
                if dlr < dlmin:
                    dlmin = dlr
                simavg = simavg + simr
                dlavg = dlavg + dlr
            if np.array(mt).argmax() == int(result[-1]):
                mthit = mthit + 1
            if np.array(mt).argmin() == int(result[-1]):
                mtls = mtls + 1
            if otype == 1:
                print "mt:",mt
                print "dl:",dl
                print "sim:",sim
                print result[-1]
                print "hit:"+str(hit)," simhit:"+str(simhit)," mthit:"+str(mthit)," mtls:"+str(mtls)," total:"+str(total)
                if total > 0:
                    print "srp:"+str(srp/3.0/total),"srp20:"+str(srp20/3.0/total),"srp100:"+str(srp100/3.0/total),"srp500:"+str(srp500/3.0/total)


print 'usernum:',usernum
print 'hit:',hit
print 'simhit:',simhit
print 'simmax:',simmax
print 'simmin:',simmin
print 'simavg:',simavg / total
print 'dlmax:',dlmax
print 'dlmin:',dlmin
print 'dlavg:',dlavg / total
print 'mthit:',mthit
print 'mthls:',mtls
print 'srp:',srp
print 'total:',total
print 'hit/total:',hit*1.0/total
print 'simhit/total:',simhit*1.0/total
print 'mthit/(total+usernum):',mthit*1.0/(total+usernum)
print 'mthls/(total+usernum):',mtls*1.0/(total+usernum)
print 'srp/(total+usernum):',srp*1.0/(total+usernum)/dummylen
print 'srp20/(total+usernum):',srp20*1.0/(total+usernum)/dummylen
print 'srp100/(total+usernum):',srp100*1.0/(total+usernum)/dummylen
print 'srp500/(total+usernum):',srp500*1.0/(total+usernum)/dummylen
