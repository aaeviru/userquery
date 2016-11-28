#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import math
import re
from os import path
import numpy as np

sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from pythonlib import semantic as sm
from pythonlib import sysf


def coef(a,b):
    tmp = len([val for val in a if val in b])
    return 2.0*tmp/(len(a)+len(b))

def sim(q,P,alpha):
    a = []
    for p in P:
        a.append(coef(q,p))
    a = sorted(a)
    sim = a[0]
    for i in range(1,len(a)):
        sim = alpha * a[i] + (1-alpha) * sim
    return sim


