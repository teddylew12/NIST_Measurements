# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 08:39:21 2018

@author: volt
"""

#taken from Anna Fox's gpib_commands.py file

import sys, time, visa, pylab, datetime, errno, os, random
import numpy as np
import matplotlib.pyplot as plt

from numpy import linspace
# from scipy.signal import *
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
# from scipy.optimize import curve_fit
from datetime import date
from matplotlib import pyplot as plt
import pylab

import pyqtgraph as pg

import csv





GPIB_34420=23
GPIB_6220=10
GPIB_7011=10  #PV10 7001
GPIB_CW = 12 
GPIB_3458A=24 
GPIB_GS200=1
  
debug=0

#colors=['crimson','darksalmon','darkorchid','forestgreen','lavender','lightpink','hotpink','cyan','navy','peru','saddlebrown','plum','teal','tomato','fuchsia','goldenrod','coral']
#channel=[7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22]
#celllist = ['Cell 1-2','Cell 3-4','Cell 5-6','Cell 7-8','Cell 9-10','Cell 11-12','Cell 13-14','Cell 15-16','Cell 17-18','Cell 19-20','Cell 21-22','Cell 23-24','Cell 25-26','Cell 27-28','Cell 29-30','Cell 31-32']
#tenvmatrix = dict(zip(channel,celllist))

#def writefile(filename,col1,col2):
#    
#    fields=[col1,col2]    
#    with open('%s' %filename, 'ab') as csvfile:
#        writeline=csv.writer(csvfile,dialect='excel-tab',delimiter=' ')
#        writeline.writerow(fields)   
    
def initialize6220(address,comp,range_in_mA):

    global currentsource6220
    currentsource6220=visa.ResourceManager().open_resource('GPIB0::%d::INSTR' % address)
    ident = currentsource6220.query('*IDN?')    
    if (debug): 
        print('ID=%s\n' % ident )
    currentsource6220.write('sour:cle:imm')
    currentsource6220.write('sour:curr:comp %f' %comp)
    #print(currentsource6220.query('source:curr:comp?')
    
    #Could also try simply calling setCurrentRange, however this will mean the drop down menu doesn't actually do anything
    if (range_in_mA == "100 mA"):
        currentsource6220.write('sour:curr:range %f' % (100/1000.0))
    elif (range_in_mA == "20 mA"):
        currentsource6220.write('sour:curr:range %f' % (20/1000.0))
    elif (range_in_mA == "2 mA"):
        currentsource6220.write('sour:curr:range %f' % (2/1000.0))
    else:
        currentsource6220.write('sour:curr:range %s' % range_in_mA) #might not work
    

def readCurrent():
    global currentsource6220
    return(1e3*float(currentsource6220.query('curr?'))) # in mA
        

def setCurrent(current_in_mA):
    global currentsource6220
    currentsource6220.write('sour:curr %f' % (current_in_mA/1000.0))
    return(1e3*float(currentsource6220.query('curr?'))) # in mA


def setCurrentRange(stop_current_in_mA):   
    setCurrent(0)
    stop=stop_current_in_mA
    if 0.02< stop <= 0.2:
        range_in_mA=0.2                 #200uA range
    elif 0.2< stop <= 2:
        range_in_mA=2.0                 #2mA range
    elif 2.0< stop <= 20:
        range_in_mA=20.0                #20mA range
    else:
        range_in_mA=100
    time.sleep(.25)
    currentsource6220.write('sour:curr:range %f' % (range_in_mA/1000.0))
    if debug:
        print('current range set to %f mA' %(range_in_mA)) 
    return range_in_mA

       
def enableCurrent():
    currentsource6220.write('outp:stat on')
    print('Current source enabled')

    
def disableCurrent():
    currentsource6220.write('outp:stat off')
    print('Current source disabled')   

    

