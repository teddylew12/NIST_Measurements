# -*- coding: utf-8 -*-
"""
Created on Fri May 26 14:26:21 2017
Purpose of this code is to sweep the current and plot an IV curve
@author: JPulecio
"""

#=================================
#Import libraries
#=================================
import Visa_Functions as vf
import matplotlib.pyplot as plt
import numpy as np
import time
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import math
import sys
from scipy import stats
import Unified_Measurement_GUI_v0 as ug
#=================================
#Global variables
#=================================

address_I_yoko_GS200 = 25
address_I_yoko_GS610 = 24
address_V = 23
address_Switch = 26
short = 40
#TODO move the following to Vf, makes it more global (used by other sweeps)
shorts = [[10,40],0,[10,40],0,0,0,0,0,0,10] # index corresponds to the card #, value is the short on that card
nplc = 1.0
Vrange = 'auto'
VDwellTime = 0.25
Irange = 1e-03
compliance_voltage = 2.
path = 'Z:\JPulecio\Code\Python\Resistance_Measurements\data\\'
I_values = []
V_values = []
R_values = []
title = "Voltage over time"
xlabel = "sample"
ylabel = "V"
#=================================
#Function definitions
#=================================  

def sweep_current_live(app, curve, current_point, number_of_sweeps, I_min, I_max, step, card1, card2, channel1, channel2,extra_res=0):

    """
    Inputs:
    :param app, curve: (both pyqtgraph constructs)
    
    :param current_point: pyqtgraph contruct used to plot current point
   
    :param number_of_sweeps: number of sweeps to complete
    
    :param I_min: current sweep start
   
    :param I_maxcurrent: sweep stop
    
    :param step: increment
   
    :param card1, card2: Target Cards 1 and 2
   
    :param channel1,channel 2: Target Channels
   
    :return: I,V,R arrays
    
    :Graphs: Updates a live plot with current on x axis, voltage on y axis
    
    Called By:
        
      -Measure_Resistance
      
      -Automate_channel_IV_live
    
    Calls On:
        
        All Visa Functions
         
    """
    # current initialization variables
    # lower range has less noise
    Irange = 1e-02
    compliance_voltage = 2.
    
    # get GPIB instruments
    Voltmeter = vf.get_voltage()
    CurrentSource = vf.get_current()
    Switch = vf.get_switch()

    # Initialize the switch matrix
    vf.intialize_switch_all(Switch)
    
    vf.intialize_current_yoko(CurrentSource, Irange, compliance_voltage)
    time.sleep(0.2)

    vf.intialize_voltage(Voltmeter, nplc, Vrange)

    
    vf.close_channel(Switch, card1, channel1) # instead of card, used to be 1
    time.sleep(0.2)

    vf.close_channel(Switch, card2, channel2) # instead of card, used to be 1
    time.sleep(0.2)
    
    vf.turnon_current_yoko(CurrentSource)    
    time.sleep(0.2)    
    vf.open_short(Switch, card1, shorts)    
    
    time.sleep(.2)

    # Going to use lists to start with for flexibility, even though slower than arrays
    I_values = []
    V_values = []
    R_values = []

    # current point array
    current_x = []
    current_y = []
    
    # voltmeter reads non zero when the current is zero
    offset = vf.read_voltage_fast(Voltmeter, VDwellTime)

    print('Offset: %s' %offset)
    
    global go
    go = 1
    #Sweep Current up
    for n in range(0, number_of_sweeps):
        print('\nChannel %d:%d SweepUp Current:'%(channel1,channel2))
        for I in np.arange(I_min, I_max, step):
            try:
                vf.set_current_fast_yoko(CurrentSource, I)
                
                V = vf.read_voltage_fast(Voltmeter, VDwellTime)
                V=V-extra_res*I
                I_values.append(I)
                # For fixing the offset
                V_values.append(V-offset)
                
                # put current point in an array to plot in a different color
                current_x.append(I)
                current_y.append(V-offset)
                #R_Offset accounts for the addition of series resistors to select devices 
                r_offset=0
                
                #Dev_Resistors- Dictionary- key:device with resistor, value-resitance 
                #Dev_resistors={}
                
                
                #check for devices with resistors
                #if device in Dev_resistors:
                #    r_offset = Dev-resistors[device]
                #else:
                #   r_offset=0
                
                if I != 0:
                    R_values.append(float(V)/float(I)-r_offset)
                else:
                    R_values.append(0.0)
                
                
                # live plotting
                curve.setData(I_values,V_values, symbol='o', symbolBrush='w', symbolSize=5)
                current_point.setData(current_x, current_y, symbol='o', symbolBrush='r', symbolSize=7)
                app.processEvents()
                
                # empty the current point array
                current_x = []
                current_y = []
                
                # input from GUI
                if go == 0:
                    exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                    return 0,0,0
                
#                print('%e '%I,end=" ")
            
            # handle keyboard event    
            except KeyboardInterrupt:
                print("\nExiting...\n")
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                return 0,0,0

        #Sweep Current down
        print('\nChannel %d:%d SweepDown Current:'%(channel1,channel2))
        for I in np.arange(I_max-step, I_min, -step):
            try:
                vf.set_current_fast_yoko(CurrentSource, I)
                V = vf.read_voltage_fast(Voltmeter, VDwellTime)
                V=V-extra_res*I
                I_values.append(I)
                V_values.append(V-offset)
                
                current_x.append(I)
                current_y.append(V-offset)
                
                if I != 0:
                    R_values.append(float(V)/float(I))
                else:
                    R_values.append(0.0)
                    
                # live plotting 
                curve.setData(I_values,V_values, symbol='o', symbolBrush='w', symbolSize=5)
                current_point.setData(current_x, current_y, symbol='o', symbolBrush='r', symbolSize=7)
                app.processEvents()
                
                current_x = []
                current_y = []
                
                if go ==0:
                    exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                    return 0,0,0
                
#                print('%e'%I,end=" ")
                
            except KeyboardInterrupt:
                print("\nExiting...\n")
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                return 0,0,0
        
        # clear out the different colored current point
        current_point.setData([],[])

    # turn it off and be ready to switch channels
    vf.set_current_fast_yoko(CurrentSource, 0)
    time.sleep(.2)

    vf.close_short(Switch, card1, shorts)
    time.sleep(.2)

    # open channels that were just measured
    # 10 is always sort, is this necessary
    if channel1 != 10:
        vf.open_channel(Switch,card1,channel1)
        vf.open_channel(Switch,card2,channel2)


    return I_values, V_values, R_values

def constantrun(app,curve,card1,card2,channel1,channel2):
    '''
    Inputs:
    :param app, curve: (both pyqtgraph constructs)
    
    :param current_point: pyqtgraph contruct used to plot current point
       
    :param card1, card2: Target Cards 1 and 2
   
    :param channel1,channel 2: Target Channels
     
    :Graphs: Updates a live plot with current on x axis, voltage on y axis
    '''
    global go
    go = 1
    currentlevel=1e-3
    Irange = 1e-02
    compliance_voltage = 2.
    Voltmeter = vf.get_voltage()
    CurrentSource = vf.get_current()
    Switch = vf.get_switch()
    vf.intialize_switch_all(Switch)
    
    vf.intialize_current_yoko(CurrentSource, Irange, compliance_voltage)
    time.sleep(0.2)

    vf.intialize_voltage(Voltmeter, nplc, Vrange)

    
    vf.close_channel(Switch, card1, channel1) # instead of card, used to be 1
    time.sleep(0.2)

    vf.close_channel(Switch, card2, channel2) # instead of card, used to be 1
    time.sleep(0.2)
    
    vf.turnon_current_yoko(CurrentSource)    
    time.sleep(0.2)    
    vf.open_short(Switch, card1, shorts)    
    
    time.sleep(.2)
    
     # Going to use lists to start with for flexibility, even though slower than arrays
    timevals=[0]
    R_values = [0]

    # current point array
 
    # voltmeter reads non zero when the current is zero
    offset = vf.read_voltage_fast(Voltmeter, VDwellTime)

    print('Offset: %s' %offset)
    
   
    stillrunning=True
    passage=0
    count=0
    testing=True
    start_time=time.time()
    while stillrunning and passage<600:
        #print('\nChannel %d:%d Constant Current:'%(channel1,channel2))
        
        
        try:
           # current=currentlevel+np.random.normal(0,1e-3)
            current=currentlevel
            vf.set_current_fast_yoko(CurrentSource,current)
            
            V = vf.read_voltage_fast(Voltmeter, VDwellTime)
            r_offset=0
            passage=time.time()-start_time
            if testing:
                count+=1
                if count%10==0:
                    print(passage)
            if current != 0:
                R_values.append(float(V)/float(current)-r_offset)
                timevals.append(passage)    
            else:
                R_values.append(0.0)
                timevals.append(passage)
              

           # if len(R_values)%10==0:
              #  print("Time is %f, Resistance is %f" %(timevals[-1],R_values[-1]))
            curve.setData(timevals,R_values, symbol='o', symbolBrush='w', symbolSize=5)            
            app.processEvents()
            
           
                
            if go == 0:
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                stillrunning=False
  
        except KeyboardInterrupt:
                print("\nExiting...\n")
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                stillrunning=False

    # turn it off and be ready to switch channels
    vf.set_current_fast_yoko(CurrentSource, 0)
    time.sleep(.2)

    vf.close_short(Switch, card1, shorts)
    time.sleep(.2)

    # open channels that were just measured
    # 10 is always sort, is this necessary
    if channel1 != 10:
        vf.open_channel(Switch,card1,channel1)
        vf.open_channel(Switch,card2,channel2)
        
def constantruntemp(app,curve1,curve2,card1,card2,channel1,channel2,target,tempSetpoint,PID,manual):
    '''
    Inputs:
    :param app, curve: (both pyqtgraph constructs)
    
    :param current_point: pyqtgraph contruct used to plot current point
       
    :param card1, card2: Target Cards 1 and 2
   
    :param channel1,channel 2: Target Channels
     
    :Graphs: Updates a live plot with current on x axis, voltage on y axis
    '''
    global go
    go = 1
    currentlevel=1e-4
    Irange = 1e-02
    compliance_voltage = 2.
    
    #Initialize all hardware
    Voltmeter = vf.get_voltage()
    CurrentSource = vf.get_current()
    Switch = vf.get_switch()
    vf.intialize_switch_all(Switch)
    
    vf.intialize_current_yoko(CurrentSource, Irange, compliance_voltage)
    time.sleep(0.2)
    vf.intialize_voltage(Voltmeter, nplc, Vrange)
    vf.close_channel(Switch, card1, channel1) # instead of card, used to be 1
    time.sleep(0.2)
    vf.close_channel(Switch, card2, channel2) # instead of card, used to be 1
    time.sleep(0.2)
    vf.turnon_current_yoko(CurrentSource)    
    time.sleep(0.2)    
    vf.open_short(Switch, card1, shorts)    
    time.sleep(.2)
    
    #Initialize temperature controller
    lake=vf.getLake()
    vf.setManualOutput(lake,manual)
    vf.setTempSetpoint(lake,tempSetpoint)
    vf.setPID(lake,float(PID[0]), float(PID[1]), float(PID[2]))
    
    
    timevals=[]
    R_values = []
    T_values = []
 
    # voltmeter reads non zero when the current is zero
    #offset = vf.read_voltage_fast(Voltmeter, VDwellTime)
   
    stillrunning=True
    passage=0
    count=0
    #testing=True
    start_time=time.time()
    vf.set_current_fast_yoko(CurrentSource,currentlevel) #Set the current initially
    
    while stillrunning: # and abs(T_values[-1] - float(target)) > 0.5:
        try:
            count = count + 1
            V = vf.read_voltage_fast(Voltmeter, VDwellTime)
            #if count % 10 == 5:
             #   print(V)
            T = vf.getTempK(lake)
            #r_offset=0
            passage=time.time()-start_time

            if currentlevel != 0:
                R_values.append(float(V)/float(currentlevel))#-r_offset)
                timevals.append(passage)  
                T_values.append(T)
            else:
                R_values.append(0.0)
                timevals.append(passage)
                T_values.append(T)
              

           # if len(R_values)%10==0:
              #  print("Time is %f, Resistance is %f" %(timevals[-1],R_values[-1]))
            curve1.setData(timevals,R_values, symbol='o', symbolBrush='w', symbolSize=5)
            curve2.setData(timevals,T_values, symbol='o', symbolBrush='g', symbolSize=5)            
            app.processEvents()
            
            if go == 0:
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                vf.safe_temp_controller(lake)
                stillrunning=False
  
        except KeyboardInterrupt:
                print("\nExiting...\n")
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                vf.safe_temp_controller(lake)
                stillrunning=False

    
    #Put the current/voltage sources in a safe configuration    
    vf.set_current_fast_yoko(CurrentSource, 0)
    time.sleep(.2)
    vf.close_short(Switch, card1, shorts)
    time.sleep(.2)

    if channel1 != 10:
        vf.open_channel(Switch,card1,channel1)
        vf.open_channel(Switch,card2,channel2)
        
    vf.safe_temp_controller(lake)
    
    return R_values, T_values
        
def initialization(num_plots):
    import Live_Plot_Functions as lpf
    global windows, plots, curves
    windows = lpf.create_windows(num_plots)
    plots = lpf.create_plots(windows,"Temp")
    curves = lpf.create_curves(plots)
    if num_plots ==1:
        curves=curves[0]
        windows=windows[0]
        plots=plots[0]
    return curves,windows,plots

def temptime(temp):
    global slope_plots,app
    global windows,plots,curves,figures
    global go
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
    else:
        pass
    num_plots=1
    curve,windows,plot=initialization(num_plots)
    windows.move(-900, 0) # move to other desktop, spyder had been blocking before
    windows.setWindowState(QtCore.Qt.WindowActive)
    windows.raise_()
        
        # this will activate the window (yellow flashing on icon)
    windows.activateWindow()
    
    plot.addLine(x=None,y=temp)
    stillrunning=True
    passage=0
    tempvals=[]
    timevals=[]
    start_time=time.time()
    go=1

    lake=vf.getLake()
    while stillrunning and passage<600:
        #print('\nChannel %d:%d Constant Current:'%(channel1,channel2))
        
        
        try:
           # current=currentlevel+np.random.normal(0,1e-3)
            
            '''
            Get Temperature Reading Here
            
            '''
            currenttemp=vf.getTempK(lake)

            passage=time.time()-start_time
            
            
            tempvals.append(currenttemp)
            timevals.append(passage)
           
              

            #if court%10==0:
           #    print("Temp is %f, Resistance is %f" %(tempvals[-1],R_values[-1]))
            curve.setData(timevals,tempvals, symbol='o', symbolBrush='w', symbolSize=5)  
            
            app.processEvents()
            
           
                
            if go == 0:
                stillrunning=False
                vf.safe_temp_controller(lake)
        except KeyboardInterrupt:
                print("\nExiting...\n")
                vf.safe_temp_controller(lake)
                stillrunning=False
    
    
def tempandresrun(app,curve,current_point,card1,card2,channel1,channel2):
    '''
    Written by Nathan
    Inputs:
    :param app, curve: (both pyqtgraph constructs)
    
    :param current_point: pyqtgraph contruct used to plot current point
       
    :param card1, card2: Target Cards 1 and 2
   
    :param channel1,channel 2: Target Channels
     
    :Graphs: Updates a live plot with current on x axis, voltage on y axis
    '''
    global go
    go = 1
    currentlevel=0.1e-3 #We will constantly output 250 uA
    Irange = 1e-02
    compliance_voltage = 2.
    
    #Initialize voltmeter, current source, and switch matrix
    Voltmeter = vf.get_voltage()
    CurrentSource = vf.get_current()
    Switch = vf.get_switch()
    vf.intialize_switch_all(Switch)
    
    vf.intialize_current_yoko(CurrentSource, Irange, compliance_voltage)
    time.sleep(0.2)
    vf.intialize_voltage(Voltmeter, nplc, Vrange)
    vf.close_channel(Switch, card1, channel1) # instead of card, used to be 1
    time.sleep(0.2)
    vf.close_channel(Switch, card2, channel2) # instead of card, used to be 1
    time.sleep(0.2)
    vf.turnon_current_yoko(CurrentSource)    
    time.sleep(0.2)    
    vf.open_short(Switch, card1, shorts)    
    time.sleep(.2)
    
    lake = vf.getLake()
    
    T_values =[]
    R_values =[] 
    
    # current point array
    current_x = []
    current_y = []

    stillrunning = True

    offset = float(vf.read_voltage_fast(Voltmeter, VDwellTime))
    vf.set_current_fast_yoko(CurrentSource,currentlevel) #Set the current source to one constant value initially
    print("Temperature sweep up on channels %d and %d"%(channel1,channel2))    
   
    #manual control
    while stillrunning: 
        try:
            V = vf.read_voltage_fast(Voltmeter, VDwellTime)
            R = (float(V)-offset)/float(currentlevel)   
            T = vf.getTempK(lake)
            R_values.append(R)
            T_values.append(T)
            current_x.append(T)
            current_y.append(R)               
            #empty=False
            curve.setData(T_values,R_values,symbol='o',symbolBrush='w',symbolSize=5)   
            current_point.setData(current_x, current_y, symbol='o', symbolBrush='r', symbolSize=7)
            app.processEvents()
            
            current_x = []
            current_y = []
            
            
            if go == 0: #Asynchronous safe exit
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                vf.closeLake(lake)
                Tc=findTc(R_values,T_values)
                return R_values,T_values,Tc
                stillrunning=False
  
        except KeyboardInterrupt:
                print("\nExiting...\n")
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                stillrunning=False
      
    #Put the voltmeter, switch matrix, and current source back in safe configurations
    vf.set_current_fast_yoko(CurrentSource, 0)
    time.sleep(.2)
    vf.close_short(Switch, card1, shorts)
    time.sleep(.2)
    if channel1 != 10:
        vf.open_channel(Switch,card1,channel1)
        vf.open_channel(Switch,card2,channel2)
        
    vf.closeLake(lake)
    
    Tc=findTc(R_values,T_values)
    return R_values,T_values,Tc
    
def findTc(R1,T1):
    #import numpy as np
    '''
    On Sweep up, take all points below 6.5 Kelvin and average the resitance, then create envelope and record when it breaks the envelope
    This needs to be rewritten... sorry Ted
    '''
    '''
    tcs=[]
    index=1
    resistavg=[]
    while T1[index]<6.5:
        resistavg.append(abs(R1[index]))
        index+=1
    resistavg=np.mean(resistavg)
    delta=100
    tcupfound=False
    while not tcupfound:
        if R1[index]>=delta*resistavg:
            tcs.append(T1[index])
            tcupfound=True
        else:
            index+=1
    tcdownfound=False
    index=0
    while not tcdownfound and index<len(R2):
        #import pdb;pdb.set_trace()
        if R2[index]<=delta*resistavg:
            tcs.append(T2[index])
            tcdownfound=True
        else:
            index+=1
    if len(tcs)==1:
        print("Error! One of the Tc's was not found")
        return [0,0]
    return tcs
    '''
    return [0,0]
    
    
def exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2):
    '''
        
    :param Switch: GPIB switch matrix object 
     
    :param CurrentSource: GPIB current source object 
   
    :param card1, card2: Target Cards 1 and 2
    
    :param channel1, channel2: Target Channels 1 and 2
           
    :return: exits sweep cleanly
    
    Called by: 
        
        -Virtually all functions in IV_curve_v3
    '''

    vf.set_current_fast_yoko(CurrentSource, 0)
    time.sleep(.2)
    
    vf.close_short(Switch, card1, shorts)
    time.sleep(.2)

    vf.open_channel(Switch,card1,channel1)
    vf.open_channel(Switch,card2,channel2)

def stop():
    global go
    go = 0
    

def turn_current_off():
    CurrentSource = vf.get_current()
    vf.set_current_fast_yoko(CurrentSource, 0)

def sweep_current_live_Rn(app, curve, number_of_sweeps, I_min, V_max, step, card1, card2, channel1, channel2,dev):
    """
      
    :param app, curve: (both pyqtgraph constructs)
    
    :param number_of_sweeps: number of sweeps to complete
    
    :param I_min: current sweep start
   
    :param I_maxcurrent: sweep stop
    
    :param step: increment
   
    :param card1, card 2: Target Cards
   
    :param channel1,channel 2: Target Channels
   
    :param dev: Target device
   
    
    :return: I,V,R arrays
    
    :Graphs: Updates a live plot with current on x axis, voltage on y axis
    
    Called By:
      -Get Rn Imax 
      
      -Get Rn Imax and save
    
    Calls On:
        
        All Visa Functions
        
    FINDS LINEAR SLOPE:
    First checks for hitting Vmax
    Next checks for expected length based on size of JJ
    then looks for 4 collinear point (using stats.linregress) 
    then looks at most recent sets of points
    if all still linear will exit
    
    """
    # current initialization variabels 
    Irange = 200e-03
    compliance_voltage = 5.
    current_limit = 30e-03 # This is highest possible current in A. Shouldn't get this high
    
    # get GPIB instruments
    Voltmeter = vf.get_voltage()
    CurrentSource = vf.get_current()
    Switch = vf.get_switch()
    

    vf.intialize_switch_all(Switch)

    vf.intialize_current_yoko(CurrentSource, Irange, compliance_voltage)
    time.sleep(0.2)

    vf.intialize_voltage(Voltmeter, nplc, Vrange)

    vf.close_channel(Switch, card1,channel1)
    time.sleep(.2)

    vf.close_channel(Switch,card2,channel2)
    time.sleep(.2)

    vf.turnon_current_yoko(CurrentSource)
    time.sleep(.2)

    vf.open_short(Switch, card1, shorts)

    #Going to use lists to start with for flexibility, even though slower than arrays
    I_values = []
    V_values = []
    R_values = []


    global go
    go = 1
    
    slopevalue=None
    slope_index=None
    printstatement=True
    for n in range(0, number_of_sweeps):
        #Sweep Current up
        print('\nChannel %d:%d SweepUp Current:'%(channel1,channel2))
        V=0
        prev_slope=[]
        #measure of how close the previous and current slopes need to be to break
        sigma=.05
        #how soon to start checking for RN
        alpha=100
        expected_length=int(30 + alpha * dev.JJ_radius_nom)
        print("Expected length: ",expected_length)
        for I in np.arange(I_min, current_limit, step):
            vf.set_current_fast_yoko(CurrentSource, I)
            V = vf.read_voltage_fast(Voltmeter, VDwellTime)
            I_values.append(I)
            print('%e '%I,end=" ")
            V_values.append(V)
            if I==0:
                R_values.append(0.0)
            else:
                R_values.append(float(V)/float(I))
          
            if V >= V_max:
                print("V_max reached")
                break
            #MOST OF THIS WIL GO IF WE SWITCH TO NON REAL TIME
            #Check for negative to positive first r derivative
            if len(I_values)>expected_length:
                #first check for inflection points
                first_deriv=[]
                second_deriv=[]
                first_deriv=np.gradient(V_values)
                second_deriv=np.gradient(first_deriv)
                if np.mean(second_deriv[-6:-3]) <= 0 and np.mean(second_deriv[-3:]) >= 0:
                    if printstatement:
                        print("Break due to inflection")
                        printstatement=False
                    if slopevalue is None:
                        slopevalue=np.mean(R_values[-3:-1])
                    if slope_index is None:
                        slope_index=len(I_values)
                #next check for jumps due to thermal 
                jumptuner=3
                if np.diff(V_values)[-1]>=jumptuner * np.mean(np.diff(V_values)[-4:-1]):
                    if printstatement:
                        print("Break due to thermal jump")
                        printstatement=False
                    if slopevalue is None:
                        slopevalue=np.mean(R_values[-3:-1])
                    if slope_index is None:
                        slope_index=len(I_values)
                
                
            curve.setData(I_values,V_values, symbol='o', symbolBrush='w', symbolSize=5)
            app.processEvents()
            
            if go == 0:
                print("Exiting")
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                return 0,0,0
    vf.set_current_fast_yoko(CurrentSource, 0)
    time.sleep(.2)
    vf.close_short(Switch, card1, shorts)
    vf.open_channel(Switch,card1,channel1)
    vf.open_channel(Switch,card2,channel2)
    print(slopevalue)
    return I_values, V_values, R_values, slopevalue, slope_index


def open_data(filename):
    """
    Returns the values of I, V, R and plots data
    
    if newplot == 1 it will plot the file in new plot window otherwise it will plot it on same window
    """
    I, V, R = np.loadtxt(filename, unpack=True)
    fig = plt.figure() #opens new plot
    plt.xlabel('I')
    plt.ylabel('V') 
    plt.ticklabel_format(style='sci', axis='both', scilimits=(0,0))
    plt.title(filename)
    plt.plot(I,V,'-o', label=filename, alpha = 0.7, markerfacecolor="None")
    plt.legend(loc='best')
    plt.show()
    return I, V, R


def find_max_y_change(x, y, num_JJ,envelope=0):
  '''
  Uses an envelope around zero based on num_JJ
 
  :param x,y: I,V arrays
  
  :param num_JJ: number of JJs
       
  :return: Critical Currents-First point to enter bounds and last point to exit
  
  '''
  if envelope != 0:
      bound = envelope
  elif num_JJ == 2:
      bound = num_JJ * 0.25e-06
  else:
      bound = num_JJ * 10e-06

  sweep_up = int((len(x)/2)-1)
  sweep_down = int(len(x)-1)

  critical_currents = [] #holds the critical currents found in graph
  
  #find minumim in list
  min_x = min(float(s) for s in x) # min of a generator
  
  
  if (min_x) == (0.0 or -0.0):
      print("\n\nPostive half sweep")
      
  else:
      print("\n\nNegative number found Full sweep")
     

  n1 = 0


  enter_index =[]
  leave_index = []
  
  for n1 in range(0,sweep_up): 
      
      if y[n1]>=-bound:
          enter_index.append(n1)
      if len(enter_index) != 0:
          if y[n1] >= bound:
              leave_index.append(n1-1)

  if len(enter_index)>0 and len(leave_index)>0: # critical currents were found
      critical_currents.append(enter_index[0])
      critical_currents.append(leave_index[0])
  else: # critical currents were not found, append the middle point
  # should probably change this to not append anything, then error catch in measure_Ic
      critical_currents.append(abs(sweep_up - sweep_down))
      critical_currents.append(abs(sweep_up - sweep_down)) 
          
  n2 = sweep_up +1 

  enter_index = []
  leave_index = []
  
  #Find max change in y for the second half of data
  for n2 in range(sweep_up, sweep_down):
      if y[n2]<=bound:
          enter_index.append(n2)
      if len(enter_index) != 0:
          if y[n2] <= -bound:
              leave_index.append(n2-1)
              
  if len(enter_index)>0 and len(leave_index)>0: # critical currents were found
      critical_currents.append(enter_index[0])
      critical_currents.append(leave_index[0])
  else: # critical currents were not found, append the middle point
  # should probably change this to not append anything, then error catch in measure_Ic
      critical_currents.append(abs(sweep_up - sweep_down))
      critical_currents.append(abs(sweep_up - sweep_down))
  
  return critical_currents

def find_max_y_change_half_sweep(x, y, num_JJ):
  '''
   Uses an envelope around zero based on num_JJ
 
  :param x,y: I,V arrays
  
  :param num_JJ: number of JJs
       
  :return: Critical Currents-First point to enter bounds and last point to exit
  
  Ineg,Ipos,Iretpos,Iretneg
  
  '''
  if num_JJ == 2:
      bound = num_JJ * 0.25e-06
  else:
      bound = num_JJ * 2e-06
  y_change = 0
  max_y_change = 0
  sweep_up = int((len(x)/2)-1)
  sweep_down = int(len(x)-1)
  step = x[1]-x[0]
  critical_currents = [] #holds the critical currents found in graph
  
  

  position1 = 0
  c = 0
  n1 = 0
  avg_y_change = 0
  
  #find avg change in y
  for n0 in range(0,len(x)):
      y_change = abs(y[n1+1] - y[n1])
      avg_y_change = (avg_y_change + y_change)/(n0+1)

  enter_index =[]
  leave_index = []
  
  for n1 in range(0,sweep_up): 
      
      if y[n1]>=-bound:
          enter_index.append(n1)
      if len(enter_index) != 0:
          if y[n1] >= bound:
              leave_index.append(n1-1)

  if len(leave_index)>0: # critical currents were found
      critical_currents.append(leave_index[0])
  else: # critical currents were not found, append the middle point
  # should probably change this to not append anything, then error catch in measure_Ic
      critical_currents.append(abs(sweep_up - sweep_down))
      
          
  n2 = sweep_up +1 

  enter_index = []
  leave_index = []

  #Find max change in y for the second half of data
  for n2 in range(sweep_up, sweep_down):
      if y[n2]<=bound:
          enter_index.append(n2)
      if len(enter_index) != 0:
          if y[n2] <= -bound:
              leave_index.append(n2-1)
              
  if len(enter_index)>0: # critical currents were found
      critical_currents.append(enter_index[0])
  else: # critical currents were not found, append the middle point
  # should probably change this to not append anything, then error catch in measure_Ic
      critical_currents.append(abs(sweep_up - sweep_down))
  
  return critical_currents


def sweep_current_live_variable_points(app, curve, current_point, number_of_sweeps, I_min, I_max, step, card1, card2, channel1, channel2, optionalic=0,extra_res=0):
    """
    This plot will be very dense in points around the estimated ic
    
    :param app, curve: (both pyqtgraph constructs)
    
    :param number_of_sweeps: number of sweeps to complete
    
    :param current_point: pyqtgraph contruct used to plot current point
    
    :param I_min: current sweep start
   
    :param I_maxcurrent: sweep stop
    
    :param step: increment
   
    :param card1, card2: Target Cards
   
    :param channel1, channel2: Target Channels
   
    :param dev: Target device
   
    
    :return: I,V,R arrays
    
    :Graphs: Updates a live plot with current on x axis, voltage on y axis
    
    Called By:
      -Get Rn Imax 
      
      -Get Rn Imax and save
    
    Calls On:
        
        All Visa Functions


    """
    # current initialization variables
    # lower range has less noise
    Irange = 1e-03
    compliance_voltage = 2.
    
    # get GPIB instruments
    Voltmeter = vf.get_voltage()
    CurrentSource = vf.get_current()
    Switch = vf.get_switch()

    vf.intialize_switch_all(Switch)
    
    vf.intialize_current_yoko(CurrentSource, Irange, compliance_voltage)
    time.sleep(0.2)

    vf.intialize_voltage(Voltmeter, nplc, Vrange)

    vf.close_channel(Switch, card1,channel1) # instead of card, used to be 1
    time.sleep(0.2)

    vf.close_channel(Switch,card2,channel2) # instead of card, used to be 1
    time.sleep(0.2)
    
    vf.turnon_current_yoko(CurrentSource)    
    time.sleep(0.2)

    vf.open_short(Switch, card1, shorts)
    
    time.sleep(.2)

    #Going to use lists to start with for flexibility, even though slower than arrays
    I_values = []
    V_values = []
    R_values = []
    
    # array to hold current point
    current_x = []
    current_y = []
    

    # offset
    offset = vf.read_voltage_fast(Voltmeter, VDwellTime)
    
    global go
    go = 1
    
    if optionalic !=0:
        estimated_Ic = optionalic
    else:
    # ** location for hard-coded estimated Ic ** 
        estimated_Ic = 200e-6

    # set up the ranges
    range1 = estimated_Ic * 0.8
    range2 = estimated_Ic * 1.2
    range3 = estimated_Ic * 3.7
    
    # different density of points
    step_less_points = (range1)/50
    step_alot_points = (range2-range1)/400
    
    # start with lower density points
    for I in np.arange(0, range1, step_less_points):
        try:
            vf.set_current_fast_yoko(CurrentSource, I)

            V = vf.read_voltage_fast(Voltmeter, VDwellTime)
            V=V-extra_res*I
            I_values.append(I)
            # for fixing the offset
            V_values.append(V-offset)
            
            # current point
            current_x.append(I)
            current_y.append(V-offset)
            
            if I != 0:
                R_values.append(float(V)/float(I))
            else:
                R_values.append(0.0)

            # live plotting
            curve.setData(I_values,V_values, symbol='o', symbolBrush='w', symbolSize=5)
            current_point.setData(current_x, current_y, symbol='o', symbolBrush ='r', symbolSize=7)
            app.processEvents()
            
            current_x = []
            current_y = []
            
            if go == 0:
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)    
                return 0,0,0
    
        except KeyboardInterrupt:
            print("\nExiting...\n")
            exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
            return 0,0,0

    # step with alot of points
    for I in np.arange(range1, range2, step_alot_points):
        try:
            vf.set_current_fast_yoko(CurrentSource, I)

            V = vf.read_voltage_fast(Voltmeter, VDwellTime)
            I_values.append(I)
    
            # for fixing the offset
            V_values.append(V-offset)
            
            # current point
            current_x.append(I)
            current_y.append(V-offset)
            
            if I != 0:
                R_values.append(float(V)/float(I))
            else:
                R_values.append(0.0)

            # live plotting
            curve.setData(I_values,V_values, symbol='o', symbolBrush='w', symbolSize=5)
            current_point.setData(current_x, current_y, symbol='o', symbolBrush='r', symbolSize=7)
            app.processEvents()
            
            current_x = []
            current_y = []
            
            if go == 0:
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                return 0,0,0
            
        except KeyboardInterrupt:
            print("\nExiting...\n")
            exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
            return 0,0,0

    # Less points for rest of sweep
    for I in np.arange(range2, range3, step_less_points):
        try:
            vf.set_current_fast_yoko(CurrentSource, I)

            V = vf.read_voltage_fast(Voltmeter, VDwellTime)
            I_values.append(I)

            # for fixing the offset:
            V_values.append(V-offset)
            
            current_x.append(I)
            current_y.append(V-offset)
            
            if I != 0:
                R_values.append(float(V)/float(I))
            else:
                R_values.append(0.0)

            # live plotting
            curve.setData(I_values,V_values, symbol='o', symbolBrush='w', symbolSize=5)
            current_point.setData(current_x, current_y, symbol='o', symbolBrush='r', symbolSize=7)
            app.processEvents()
            
            current_x = []
            current_y = []
            
            if go == 0:
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                return 0,0,0
    
        except KeyboardInterrupt:
            print("\nExiting...\n")
            exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
            return 0,0,0


    #Sweep Current down less points
    for I in np.arange(range3-step_less_points, range2, -step_less_points):
        try:
            vf.set_current_fast_yoko(CurrentSource, I)
            V = vf.read_voltage_fast(Voltmeter, VDwellTime)
            I_values.append(I)
            V_values.append(V-offset)
            
            current_x.append(I)
            current_y.append(V-offset)
            
            if I != 0:
                R_values.append(float(V)/float(I))
            else:
                R_values.append(0.0)

            # live plotting
            curve.setData(I_values,V_values, symbol='o', symbolBrush='w', symbolSize=5)
            current_point.setData(current_x, current_y, symbol='o', symbolBrush='r', symbolSize=7)
            app.processEvents()
            
            current_x = []
            current_y = []
            
            if go ==0:
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                return 0,0,0

        except KeyboardInterrupt:
            print("\nExiting...\n")
            exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
            return 0,0,0

    # Sweep down with alot of points around the estimated Ic
    for I in np.arange(range2-step_alot_points, range1, -step_alot_points):
        try:
            vf.set_current_fast_yoko(CurrentSource, I)
            V = vf.read_voltage_fast(Voltmeter, VDwellTime)
            I_values.append(I)
            V_values.append(V-offset)
            
            current_x.append(I)
            current_y.append(V-offset)
            
            if I != 0:
                R_values.append(float(V)/float(I))
            else:
                R_values.append(0.0)

            # live plotting
            curve.setData(I_values,V_values, symbol='o', symbolBrush='w', symbolSize=5)
            current_point.setData(current_x, current_y, symbol='o', symbolBrush='r', symbolSize=7)
            app.processEvents()
            
            current_x = []
            current_y = []
            
            if go ==0:
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                return 0,0,0

        except KeyboardInterrupt:
            print("\nExiting...\n")
            exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
            return 0,0,0
    

    # final sweep with less points
    for I in np.arange(range1-step_less_points, 0, -step_less_points):
        try:
            vf.set_current_fast_yoko(CurrentSource, I)
            V = vf.read_voltage_fast(Voltmeter, VDwellTime)
            I_values.append(I)
            V_values.append(V-offset)
            
            current_x.append(I)
            current_y.append(V-offset)
            
            if I != 0:
                R_values.append(float(V)/float(I))
            else:
                R_values.append(0.0)

            # live plotting
            curve.setData(I_values,V_values, symbol='o', symbolBrush='w', symbolSize=5)
            current_point.setData(current_x, current_y, symbol='o', symbolBrush='r', symbolSize=7)
            app.processEvents()
            
            current_x = []
            current_y = []
            
            if go ==0:
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                return 0,0,0
    
        except KeyboardInterrupt:
            print("\nExiting...\n")
            exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
            return 0,0,0

    # turn it all off, ready for next
    exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
    return I_values, V_values, R_values


def automate_channel_IV_live(app, curve, current_point, cards, channels, currents, step, number_of_sweeps, optionalic=0,extra_res=0):
    """
    Automates the sweep_current_live function for multiple channels
    
    :param app, curve: (both pyqtgraph constructs)
    
    :param current_point: pyqtgraph contruct used to plot current point
    
    :param card: Target Card
    
    :param channels: Array of Target Channels
    
    :param currents: Array of currents, 0=I_min,1=Imax
    
    :param step: increment
    
    :param number_of_sweeps: number of sweeps to complete
   
    :param optionalic: Optional Ic for sweep_current_live_variable_points
    
    :return: I,V,R arrays
    
    :Graphs: Updates a live plot with current on x axis, voltage on y axis
    
    Called By:
        
        -Get Rn Imax 
      
        -Get Rn Imax and save
    
    Calls On:
        
        -sweep_current_live_variable_points
        
        -sweep_current_live
        
    """
    I_min = currents[0]
    I_max = currents[1]
    channel_pairs = len(channels)
    for n in range(0,channel_pairs, 2):
        channel1 = channels[n]
        channel2 = channels[n+1]
        card1 = cards[n]
        card2 = cards[n+1]
#        print("card1: %s channel1: %s\ncard2: %s channel2: %s"%(card1, channel1, card2, channel2))
        if optionalic ==0:
            I,V,R = sweep_current_live(app, curve, current_point, number_of_sweeps, I_min, I_max, step, card1, card2, channel1, channel2,extra_res=extra_res)
        else:
            I,V,R = sweep_current_live_variable_points(app, curve, current_point, number_of_sweeps, I_min, I_max, step, card1, card2, channel1, channel2, optionalic=optionalic,extra_res=extra_res)
    
    return I,V,R

def calc_steps(I_min, I_max, step, number):
    if (number):
        return (I_max-I_min)/step
    else:
        return step

def sweep_current_live_GUI(app,plot, curves, number_of_sweeps, I_min, I_max, step, card1, card2, channel1, channel2,save,chip,device):
    """
     Automates the sweep_current_live function for the older GUI
    
    :param app, curve: (both pyqtgraph constructs)
  
    :param number_of_sweeps: number of sweeps to complete
    
    :param I_min, I_max: Respective max and min current values
    
    :param step: step size
    
    :param card1, card2: Target Cards 1 and 2
    
    :param channel1, channel2: Target Channels 1 and 2
    
    :return: I,V,R arrays
    
    :Graphs: Updates a live plot with current on x axis, voltage on y axis
    
    Called By:
        
        -Get Rn Imax 
      
        -Get Rn Imax and save
    
    Calls On:
        
        -sweep_current_live_variable_points
        
        -sweep_current_live
    
    """
    # current initialization variables
    # lower range has less noise

    Irange = 1.3e-01
    compliance_voltage = 10.

    # get GPIB instruments
    Voltmeter = vf.get_voltage()
    CurrentSource = vf.get_current()
    Switch = vf.get_switch()

    # different init. for squids vs. pcm

    vf.intialize_switch_all(Switch)



    vf.intialize_current_yoko(CurrentSource, Irange, compliance_voltage)
    time.sleep(0.2)

    vf.intialize_voltage(Voltmeter, nplc, Vrange)


    vf.close_channel(Switch, card1,channel1) # instead of card, used to be 1
    time.sleep(0.2)

    vf.close_channel(Switch,card2,channel2) # instead of card, used to be 1
    time.sleep(0.2)

    vf.turnon_current_yoko(CurrentSource)
    time.sleep(0.2)

    vf.open_short(Switch, card1, shorts)

    time.sleep(.2)

    #Going to use lists to start with for flexibility, even though slower than arrays
    # starting 7/24: voltmeter reads non zero when the current is zero
    offset = vf.read_voltage_fast(Voltmeter, VDwellTime)

    print('Offset: %s' %offset)

    global go
    go = 1
    #Sweep Current up
    for n in range(0, number_of_sweeps):
        I_values = []
        V_values = []
        R_values = []

        if n%2==0:
            color = 'w'
        else:
            color = 'b'
        if n>1:
            curves[n-2].setData([],[])

        print('\nChannel %d:%d SweepUp Current:'%(channel1,channel2))
        
        
        for I in np.arange(I_min, I_max, step):
            vf.set_current_fast_yoko(CurrentSource, I)

            V = vf.read_voltage_fast(Voltmeter, VDwellTime)
            I_values.append(I)
            # new, for fixing the offset 7/24:
            V_values.append(V-offset)
            if I != 0:
                R_values.append(float(V)/float(I))
            else:
                R_values.append(0.0)

            # live plotting
            curves[n].setData(I_values,V_values, symbol='o', pen = color,symbolBrush=color, symbolSize=7)
            app.processEvents()
            if go == 0:
                break
            print('%e '%I,end=" ")

        #Sweep Current down
        print('\nChannel %d:%d SweepDown Current:'%(channel1,channel2))
        for I in np.arange(I_max-step, I_min, -step):
            vf.set_current_fast_yoko(CurrentSource, I)
            V = vf.read_voltage_fast(Voltmeter, VDwellTime)
            I_values.append(I)
            V_values.append(V-offset)
            if I != 0:
                R_values.append(float(V)/float(I))
            else:
                R_values.append(0.0)

            # live plotting
            curves[n].setData(I_values,V_values, symbol='o', pen=color,symbolBrush=color, symbolSize=7)
            app.processEvents()
            if go ==0:
                break
            print('%e'%I,end=" ")


    vf.set_current_fast_yoko(CurrentSource, 0)
    time.sleep(.2)

    vf.close_short(Switch, card1, shorts)
    time.sleep(.2)


    vf.open_channel(Switch,card1,channel1)
    vf.open_channel(Switch,card1,channel2)
    
    if save:
        
        current_time = time.strftime("_%Y-%m-%d_%H-%M-%S_IVGUI")
        dirname = ("E:/Users/volt.686QVACTEST/National Institute of Standards and Technology (NIST)/SEG - SFQ_Circuits/")
        import measure_Ic as ic
        folder = dirname+ str(chip.name)+current_time
        name=ic.create_name(chip.name,device)
        filename=folder+name
        ic.create_dir(filename)
        print(filename)
        save_data_live(I_values, V_values, R_values,(folder+name+"_sweep.dat"))
        
        from pyqtgraph import exporters
        exporter = exporters.ImageExporter(plot.scene())
        try:
            exporter.export(filename+"_sweep.png") # export the graph
        except:
            print("Oh no wrapped object was deleted!!!!!")
    
    try:
        return I_values, V_values, R_values
    except:
        return 0,0,0
    
def save_data_live(I_values, V_values, R_values, name):
    """
    Saves the raw data as ASCII seperated by tab
    """
    column = len(I_values)
    data = np.zeros((column, 3))
    data[:,0] = I_values
    data[:,1] = V_values
    data[:,2] = R_values
    np.savetxt(name, data, header = 'col1: I, col2: V, col3: R \n')
def save_rt_data_live(R,T,name):
    column=len(R)
    data = np.zeros((column, 2))
    data[:,0] = R
    data[:,1] = T
    np.savetxt(name, data, header = 'col1: R, col2: T \n') 

