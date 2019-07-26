# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 15:00:05 2019

@author: tkl
"""

import database_v4 as db
import Plot_Generation_v2 as pg
import pickle
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
import pdb
from scipy.optimize import leastsq
from scipy.stats import linregress
import time

'''
Project Overview:

Author: Theodore Lewitt

Superconductive electronic devices using Jospehson junctions are tested for properties like critical current and normal resistance in determining the success of their manufacturing

Finding normal resistance in an IV curve is challenging because the data is noisy and is usually preformed manually by a researcher.

When the IV curve switches from superconductive behavior to normal resistive behavior, the curve goes from concave down to linear

The challenge is that the data is succeptible to thermal noise, especially with higher current that disguises the point of inflection signifying the change

My summer project is to find an way to automate the finding of normal resistance.

Current Approach:

The current approach I developed last year uses a sliding window average of the second derivative to try to smooth the noise, but it consistently would miss the change



New Approach 1:
    
Going off the work done by Gudkov et al in their paper "Properties of Planar Nb/a-Si/Nb Jospehson Junctions with Various Degrees of Doping of the a-Si layer"

I approached this as modeling the curve with a generalized linear model with an knot at the point of inflection and the constraint that it must be continous at the knot (a linear spline)

On the left side of the knot, Gudkov provides an equation for modeling the concave down part of the curve with equation I=<#Junctions>*<SizeOfJunctions(um)>*(<a>*V + <b>*V^(7/3) with <a>,<b> constants to be determined

The right side is linear and the slope of this side is the normal resistance we are trying to find

The program first tries to fit good constants <a> and <b> to all IV curves, then using those constants it searches for where the values start to deviate from that curve, signifying the change to linear

It then takes the slope of the next ten points (any higher would start to be succeptible to thermal noise)
----This method didnt work, couldn't find similar parameters across the chips and even across devices in the same array line

New Approach 2:

Using the same paper and approach, but this time not requiring the same <a> and <b> parameters, just looking at quality of fit of the two models to determine the ideal knot position 



Dataset and Preprocessing:
    
I manually found the ideal knot placement for 8 chips with 54 devices (excluding the ones with measurement defects) for a total of 425 IV curves

The chips have the same manufacturing, but some are arrays of 40 Junctions and some are Single junctions.

The resistances scales linearly, so all arrays are preprocessed by dividing by the number of junctions

In addition, the resistance depends on the size of the junctions, so all arrays are divided by the size of the junction as well


Thoughts so far:

Definitely no similar parameters between single junctions and arrays so this approach isn't working

what other methods could work??

Delta best of 17 for right side of 50 points and the indexknot method and weighting left accuracy vs right accuracy 7:3

try: less than 50 points??
will it be able to find right point in small region cuz i can find a small region using other methods?

''' 



#Chips with bad IV curves
exceptionlist=["D180802-F3_A1_2.4","D180802-F3_S3_1.5","D180802-F3_A1_2.7","D180802-F3_A1_1.5","D180802-F3_S3_1.5","D180802-J9_A2_3.0","D180802-J9_A3_3.0","D180802-B8_JJ2.7_3.1","D180802-I6_S1_2.7","D180802-E6_A2_1.5","D180802-F3_A3_2.4","D180802-F3_A3_2.7","D180802-F3_A3_3.0","D180802-F3_A3_3.3"]
chipsused= ["I6","E6","K6","F3","J9","F6","B8","G1"]
def tryitout():
    
    options=["datacollect","manualguess","gridsearch","least sq","indexknot"]
    for num,option in enumerate(options,1):
        print(num, option)
    method= int(input("Pick an method: \n"))
    
    if method==1:
        '''
        Collect and saves data in Python Dictionary
        '''
        print("Data successfully saved with filename %s" % collectData())
   
    elif method ==2:
            '''
            Mainly used for data exploration in early stages, allows you to manually tune the <a> and <b> parameters
            '''
            with open('measureRNData.pickle','rb') as handle:
                fulldict=pickle.load(handle)
            chipname="D180802-I6"
            chip=db.find_chip(chipname)
            for i,dev in enumerate(db.show_devices_from_chip(chip)):
                print("%d : %s"%(i,dev.name))
            devnum=int(input("Pick a device to use"))
            #for i in range(len(db.show_devices_from_chip(chip))-1,0,-1):
            happy=False
            device=db.show_devices_from_chip(chip)[devnum]
            if chip.name +"_"+device.name in exceptionlist:
                    pass
            else:
                numjjs=device.num_JJs
                sconst=(device.JJ_radius_nom-.12)/1000
                while not happy:
                    a=int(input("Enter an alpha"))
                    b=int(input("Enter an Beta"))
                    I=fulldict[chip.name][device.name]["Ivals"]
                    index=fulldict[chip.name][device.name]["Index"]
                    I2=I[:index]
                    V=fulldict[chip.name][device.name]["Vvals"]
                    V2=V[:index]
                    mse=0
                    for i in range(0,len(I2)):
                        iguess=numjjs*sconst*(a*np.abs(V2[i])+b*np.power(np.abs(V2[i]),(7/3)))
                        mse+=(I2[i]-iguess)**2
                    mse=mse/len(I2)*100000
       
                    print("Min Mse is %.6f with min b is %d"%(mse,b))
                    plt.figure()
                    plt.plot(V,I,'b')
                    plt.plot(V2,I2,'r')
                    plt.plot(V2,numjjs*sconst*(a*np.abs(V2)+b*np.power(np.abs(V2),(7/3))),'g')
                    plt.show()
                    happy=int(input("1 if happy,0 otherwise"))

    elif method == 3:
            '''
            Naive linear grid search for best parameters for <a> and <b>
            '''
            with open('measureRNData.pickle','rb') as handle:
                fulldict=pickle.load(handle)
            for chipend in chipsused:
                chipname="D180802-" + chipend
                chip=db.find_chip(chipname)
                minchipmse=1000000000000000
                minchipa=0
                minchipb=0
                devname=0
                
                for device in db.show_devices_from_chip(chipname):
                    if chip.name +"_"+device.name in exceptionlist:
                        pass
                    else:
                        numjjs=device.num_JJs
                        sconst=(device.JJ_radius_nom-.12)/1000
                        alpha=np.linspace(1,3,num=40)
                        beta=np.linspace(2000,5000,num=40)
                        index=fulldict[chip.name][device.name]["Index"]
                        I=fulldict[chip.name][device.name]["Ivals"]
                        I=I[:index]
                        V=fulldict[chip.name][device.name]["Vvals"]
                        V=V[:index]
                        fulldict[chip.name][device.name]["Alphabeta"]=[0,0]
                        fulldict[chip.name][device.name]["MSE"]=0
                        fulldict[chip.name][device.name]["r2"]=3
                        minmse=1000000
                        mina=0
                        minb=0
                        
                        for a in alpha:
                            for b in beta:
                                mse=0
                                for i in range(0,len(I)):
                                    iguess=numjjs*sconst*(a*V[i]+b*np.power(V[i],(7/3)))
                                    mse+=(I[i]-iguess)**2
                                mse=mse/len(I)
                                if mse<minmse:
                                    mina=a
                                    minb=b
                                    minmse=mse
                                    fulldict[chip.name][device.name]["Alphabeta"]=[a,b]
                                    fulldict[chip.name][device.name]["MSE"]=minmse
                                    
                                    fulldict[chip.name][device.name]["r2"]=r2_score(I,numjjs*sconst*(a*V+b*np.power(V,(7/3))))
                        if minmse<minchipmse:
                            minchipmse=minmse
                            minchipa=mina
                            minchipb=minb
                            devname=device.name

                print("Minmse for chip %s is %f with a %f and b %f on device %s"%(chipname,minmse,minchipa,minchipb,devname))
            alla=[]
            allb=[]
            allr=[]
            devnames=[]
            for chipend in chipsused:
                chipname="D180802-" + chipend
                chip=db.find_chip(chipname)
                for device in db.show_devices_from_chip(chipname):
                    if chip.name +"_"+device.name in exceptionlist:
                        pass
                    else:
                        if device.device_type!="SingleJunction":
                            devnames.append(device.name)
                            alla.append(fulldict[chip.name][device.name]["Alphabeta"][0])
                            allb.append(fulldict[chip.name][device.name]["Alphabeta"][1])
                            allr.append(fulldict[chip.name][device.name]["r2"])
                            plt.bar(devnames,alla)
            pdb.set_trace()    
            
            
            
    elif method==4:
        '''
        Using Scipy's least squares optimizer to find the best alpha and beta for each graph, both with and without the equality constraint at the knot
        
        Found large deviation in the single junctions but some promise in the arrays
        '''
       
        
        constraint=int(input("1 for index constraint, 0 for no constraint"))
        
        alla=[]
        allb=[]
        allsc=[]

        with open('measureRNData.pickle','rb') as handle:
            fulldict=pickle.load(handle)
        for chipend in chipsused:
            chipname="D180802-" + chipend
            chip=db.find_chip(chipname)
            for device in db.show_devices_from_chip(chipname):
                if chip.name +"_"+device.name in exceptionlist:
                    pass
                else:
                    numjjs=device.num_JJs
                    sconst=(device.JJ_radius_nom-.12)/1000
                    allsc.append(sconst)
                    index=fulldict[chip.name][device.name]["Index"]
                    I=fulldict[chip.name][device.name]["Ivals"]
                    I=I[:index]
                    V=fulldict[chip.name][device.name]["Vvals"]
                    V=V[:index]
                   
                    if  constraint==1:
                        lam=10000
                        '''
                        Least squares objective function with additional constraint that the point passes through the index point
                        '''
                        func=lambda x:numjjs*sconst*(x[0]*V+x[1]*np.power(V,(7/3)))-I + lam*(numjjs*sconst*(x[0]*V[-1]+x[1]*np.power(V[-1],(7/3)))-I[-1])

                    else:
                        func=lambda x:numjjs*sconst*(x[0]*V+x[1]*np.power(V,(7/3)))-I
                    est_a,est_b=leastsq(func,[2,200])[0]
                    
                    if np.isnan(est_a):
                        est_a=0
                    if np.isnan(est_b):
                        est_b=0
                    fulldict[chip.name][device.name]["Alphabeta"]=[est_a,est_b]
                    alla.append(fulldict[chip.name][device.name]["Alphabeta"][0])
                    allb.append(fulldict[chip.name][device.name]["Alphabeta"][1])

        plt.figure()
        xvals=list(range(len(alla)))
        
        #Graph of the <a>'s found for each device and the difference between them
        plt.subplot(1,3,1)
        plt.plot(xvals,alla)
        plt.plot(xvals[:-1],np.diff(alla))
        
        #Graph of the <b>'s found for each device
        plt.subplot(1,3,2)
        plt.plot(xvals,allb)
        plt.subplot(1,3,3)
        plt.plot(xvals,np.array(alla)*np.array(allsc))
        plt.show()
        
    elif method==5:
         with open('measureRNData.pickle','rb') as handle:
                fulldict=pickle.load(handle)
                delta=[]
                delta2=[]
         for chipend in chipsused:
            chipname="D180802-" + chipend
            chip=db.find_chip(chipname)
            for device in db.show_devices_from_chip(chipname):
                guesses=[]
                alla=[]
                allb=[]
                allm=[]
                alli=[]
                if chip.name +"_"+device.name in exceptionlist:
                        pass
                else:
                    numjjs=device.num_JJs
                    sconst=(device.JJ_radius_nom-.12)/1000
                    I=fulldict[chip.name][device.name]["Ivals"]
                    V=fulldict[chip.name][device.name]["Vvals"]
                    index=fulldict[chip.name][device.name]["Index"]
                   # count=1
                    passes=0
                    #plt.figure()
                    if index is None:
                        pass
                    else:
                        offset=20
                        step=2
                        leftcut=6
                        rightcut=50
                        lam=10000
                        rightimp=7
                        leftimp=3
                        for xpos in range(index-offset,index+offset,step):
                            
                            Ileft=I[leftcut:xpos]
                            Iright=I[xpos:xpos+rightcut]
                            Vleft=V[leftcut:xpos]
                            Vright=V[xpos:xpos+rightcut]
                            if len(Vright)>0:
                                Iknot=Ileft[-1]
                                Vknot=Vleft[-1]
                                guess=lambda x:numjjs*sconst*(x[0]*Vleft+x[1]*np.power(Vleft,(7/3)))-Ileft + lam*(numjjs*sconst*(x[0]*Vknot+x[1]*np.power(Vknot,(7/3)))-Iknot)
                                a,b=leastsq(guess,[2,200])[0]
                                
                                if np.isnan(a) or np.isnan(b):# or np.isnan(right_m):
                                    pass
                                    passes+=1
                                    
                                else:
                                    m,intercept,r,_,_=linregress(Vright,Iright)
                                    leftrscore=r2_score(Ileft,numjjs*sconst*(a*Vleft+b*np.power(Vleft,(7/3))))
                                    rightrscore=r**2
                                    fit= rightimp*leftrscore + leftimp*rightrscore
                                    alla.append(a)
                                    allb.append(b)
                                    allm.append(m)
                                    alli.append(intercept)
                                    guesses.append(fit)
                            else:
                                pass
                        
                        '''
                        plt.subplot(5,8,count)
                        count+=1
                        plt.title("%s with xpos %d" %(device.name,xpos))
                        plt.plot(V,I,'b')
                        plt.plot(Vleft,Ileft,'r')
                        plt.plot(Vleft,numjjs*sconst*(a*np.abs(Vleft)+b*np.power(np.abs(Vleft),(7/3))),'g')
                        plt.plot(Vright,intercept+m*Vright)
                        plt.show()
                        '''
                        #pdb.set_trace()
                    if guesses and index is not None:
                        guess=np.argmax(guesses)
                        xbest=index-offset+ step*guess + step*passes
                        
                        print("Guess is %d and ground truth is %d"%(xbest,index))
                        delta.append(abs(xbest-index))
                        delta2.append(xbest-index)
                    else:
                        print("Something is wrong with chip %s,device %s, no guesses" % (chip.name,device.name))
                    '''
                    plt.figure()
                    plt.title("Best found position for %s"%device.name)
                    plt.plot(V,I,'b')
                    plt.plot(V[:xbest],numjjs*sconst*(a*np.abs(V[:xbest])+b*np.power(np.abs(V[:xbest]),(7/3))),'g')
                    plt.plot(V[xbest:],intercept+m*V[xbest:])
                    plt.show()
                    '''
         print("Average is %f"%np.mean(delta))
         plt.figure()
         plt.plot(range(len(delta)),delta2)
         plt.show()
         pdb.set_trace()
    elif method==6:
        '''
        Combinging current method 
        '''
def samedirectory(meas,dictdir):
    '''
    Checks that the directory from the database is the same as the directory from the files
    '''
    if meas.data_directory.split('%2F')[-1]==dictdir.split("/")[3] and meas.chip_name+"_"+meas.device_name ==dictdir.split("/")[5][:len(meas.chip_name+"_"+meas.device_name)]:
        return True
    else:
        return False

def collectData():
    '''
    Creates an Python Dictionary with all data in the format
    
    
    {Chip:{
            Device:{
                    Ivals
                    Vvals
                    DataDirectory
                    CorrectRN
                    Index
                    MSE
                    R^2
                    }}}
    '''
    dictionary={}
    for chip in db.show_chips_from_wafer("D180802-pcms3"):
        if chip.name.split("-")[1]  in ["I6","E6","K6","F3","J9","F6","B8","G1"]:
            dictionary[chip.name]={}      
            for device in db.show_devices_from_chip(chip.name):  
                if pg.get_data_direct(chip.name,device.name)!=-1:
                    try:
                        I,V,dictt=pg.get_data_direct(chip.name,device.name)
                        dictionary[chip.name][device.name]={}    
                        dictionary[chip.name][device.name]["Ivals"]=I
                        dictionary[chip.name][device.name]["Vvals"]=V
                        dictionary[chip.name][device.name]["directory"]=dictt
                        
                        for measurement in db.get_measurements_from_device(chip,device):
                            print(samedirectory(measurement,dictionary[chip.name][device.name]["directory"]))
                            if samedirectory(measurement,dictionary[chip.name][device.name]["directory"]):
                                dictionary[chip.name][device.name]["RN"]=measurement.Rn
                                dictionary[chip.name][device.name]["Index"]=measurement.tedindex
                    except TypeError:
                        pass

    
    filename='measureRNData.pickle'
    with open(filename, 'wb') as handle:
        pickle.dump(dictionary, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return filename
if __name__ == '__main__':
    tryitout()
'''
Need all the raw data, using the correct ones

with open('measureRNData.pickle','rb') as handle:
    fulldict=pickle.load(handle)
    

Approach 1:
Using Measured Chips
--Get Index Where RN begins
--Fit Curve on Left Side of RN using selfmade cosntants according to paper
----Mainly used to perfect those constants    
For New Chips    
Fix Guess of Where the Point Should Be based on Research
Take 5 points on each side of the data
Try to fit the curve on left size and expected rn for the 10 points after it
--Needs new loss function that emphasizes linearlity in top??
Take the best fit of the 11 points and call that inflection point,
Then take that point and make line thru next 5-10 points to get RN  

CONSTANTS and EQNs
Before Index
I=A*V +B*V^7/3
A=s*g^2*a^4*E^2*e^(-L/a)+
L=12.5 nanometers
s=nom_rad_jj-.12 micrometers
'''


             