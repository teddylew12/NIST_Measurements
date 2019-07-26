# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 10:49:37 2019

@author: tkl
"""

import matplotlib.pyplot as plt
import numpy as np
import pdb
filename1="D190516-A-G6_S1_1.5_0.75_Ic_raw.dat"
filename2="D190716-G6_S1_1.5_0.75_Ic_raw.dat"
filename3="D190201-G6_S1_1.5_0.75_Ic_raw.dat"
filename4="D190429-B-K6_S1_1.5_0.75_Ic_raw.dat"
filename5="D190321-A-K6_S1_1.5_0.75_Ic_raw.dat"
files=["D190516-A-G6_S1_1.5_0.75_Ic_raw.dat","D190716-G6_S1_1.5_0.75_Ic_raw.dat","D190201-G6_S1_1.5_0.75_Ic_raw.dat","D190429-B-K6_S1_1.5_0.75_Ic_raw.dat","D190321-A-K6_S1_1.5_0.75_Ic_raw.dat"]
files2=["D190429-B-K6_A3_3.9_1.95_Ic_raw.dat","D190204-K6_A3_3.9_1.95_Ic_raw.dat","D190516-E-G6_A3_3.9_1.95_Ic_raw.dat"]

'''
try:
    I,V=np.loadtxt(urlopen(filename,timeout=5))
except:
    print("Hmm")
    pdb.set_trace()
'''
bigR=[]
for i,file in enumerate(files2):
    data=np.loadtxt(file)
    #pdb.set_trace()
    I=data[:,0]
    I=I[:int((len(I)+1)/2)]
    V=data[:,1]
    V=V[:int((len(V)+1)/2)]
   # if i>2:
    #    pdb.set_trace()
    import numpy.ma as ma
    
    maskarr=ma.masked_inside(I,.0005,-.0005)
    subI=maskarr.data[maskarr.mask]
    subV=V[maskarr.mask]
    R=subV/subI
    mask=R>-100000
    R=R[mask]
    mask2=R<100000
    R=R[mask2]
    print("Stdev of %f and mean of %f"%(np.std(R),np.mean(R)))

    for l in R:
        bigR.append(l)
    offset=np.mean(R)*I
    '''
    #mask=.0001>I>-.0001
    #subI=I[mask]
    #subV=V[mask]
    #pdb.set_trace()
    plt.figure()
    plt.plot(I,V)
    plt.plot(subI,subV,color='r')
    plt.plot(I,V-offset,color='g')
    plt.show()
    '''
pdb.set_trace()