import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from tfidf.dg_lr import *


wtol = readwl("/home/ec2-user/git/statresult/wordslist_dsw.txt")
a = np.load('/home/ec2-user/data/classinfo/vt.npy')#lsa result
kk = a.shape[0]
root = "/home/ec2-user/data/topics/"
name = "2112"
cll = {}
for i in range(0,kk):
    cll[i] = np.random.randint(kk,size=3)

result = dg(root,name,cll,"/home/ec2-user/data/lsaclass/",1.04,a,wtol,kk)
print '@'+root+name
for i in range(0,len(result)-1):
    for j in result[i]:
	print j
    print
print result[-1]




