# -*- coding: utf-8 -*-
"""
Created on Tue May 28 14:32:10 2019

@author: tkl
"""

import sys
import re
import IV_curve_v3 as iv
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from pyqtgraph import exporters
import os
import time
import database_v4 as d
import numpy as np
import Input_Functions as inpfunc
import Live_Plot_Functions as lpf
import measure_Ic as ic
import Resistance_curve as rc
import measure_Via_Resistance as mvr
import measure_Resistor_Arrays_v2 as mra
import measure_Device_Resistance as mdr


dirname = ("E:/Users/volt.686QVACTEST/National Institute of Standards and Technology (NIST)/SEG - SFQ_Circuits/")
web_link = ("https://nistgov.sharepoint.com/sites/SEG/Shared%20Documents/Forms/AllItems.aspx?newTargetListUrl=%2Fsites%2FSEG%2FShared%20Documents&viewpath=%2Fsites%2FSEG%2FShared%20Documents%2FForms%2FAllItems%2Easpx&id=%2Fsites%2FSEG%2FShared%20Documents%2FSFQ_Circuits_Measurements%2F")
web_link = ("https://nistgov.sharepoint.com/sites/SEG/Shared%20Documents/Forms/AllItems.aspx?newTargetListUrl=%2Fsites%2FSEG%2FShared%20Documents&viewpath=%2Fsites%2FSEG%2FShared%20Documents%2FForms%2FAllItems%2Easpx&id=%2Fsites%2FSEG%2FShared%20Documents%2FSFQ_Circuits_Measurements%2F")

points=[2e-3,1e-3,5e-4]
'''
Measurements to be done:
    
Metal Layers:
    For Both Temperatures:
        For All 5 layers:
            RL and RCross by IV curve 0-3mA
            
    Calculations:
        RL and RC are known from experiment
    For Both Temperatures
        Rsq=RC*pi/ln(2)
        Width=200*Rsq/RL
    RRR=RL(roomtemp)/RL(cold)

    Program that controls Temperature?


RS Arrays:
    For both size arrays:
        IV curve at Room temp
        Iv points at cold temp
            2ma,1ma,.5ma
    Calculations:
        For all current vals
            R/256=R(4k)/256
            R/2.7=(R/256)/2.7 or r(4k)/691.2
        
VIA Arrays:
    All cold:
        Measure resist at 2ma
        sweep IV until discontinuity,record as IMAX
        stop sweep at IMAX or 100mA

'''
def initialization(num_plots):
    global windows, plots, curves, current_point
    windows = lpf.create_windows(num_plots)
    plots = lpf.create_plots(windows)
    curves = lpf.create_curves(plots)
    
    if num_plots ==1:
        curves=curves[0]
    return curves
def measure_PCM3B_Vias(folder,folder_link, chip,Vias):
    
    resistances,Imax = mvr.pcm3b_Via(folder, chip, Vias)
    
    # save the via measurements
    for i in range(0,len(resistances)):
        d.save_Via_Measurements_PCM3B_cold(chip, [resistances[i]], [Imax[i]], folder_link, Vias[i])
    print("Weblink: %s" %folder_link)
    
def continousResistTemp(chip,devices,folder,save):
    global slope_plots,app
    global windows,plots,curves,figures, current_point
    
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
    else:
        pass
    
    num_plots= len(devices)
    #curves = initialization(num_plots)
    windows = lpf.create_windows(num_plots)
    plots = lpf.create_plots(windows,formatt='RvsT')  
    curves = lpf.create_curves(plots)
    current_point = lpf.create_current_point(plots)
   
    windows[0].move(-900, 0) # move to other desktop, spyder had been blocking before
    windows[0].setWindowState(QtCore.Qt.WindowActive)
    windows[0].raise_()
        
        # this will activate the window (yellow flashing on icon)
    windows[0].activateWindow()
    i = 0
    
    for device in devices:
        cards =inpfunc.get_cards(device)
        card1=cards[0]
        card2=cards[1]
        channels = inpfunc.get_channels(device)
        channel1=channels[0]
        channel2=channels[1]
        print("Device name is %s" %device.name)
        R,T,Tc=iv.tempandresrun(app,curves[i],current_point[i],card1,card2,channel1,channel2)
        print("Sweep Up Tc is %f" % Tc[0])
        print("Sweep Down Tc is %f" % Tc[1])
        Tc=np.mean(Tc)
        print("Averaged Tc is %f" % Tc)
        if save: 
            name=ic.create_name(chip,device)
            name=name.replace(" ","_") #For fixing problem in Fix Tc with spaces in device name
            ic.create_dir((folder+name))
            filename=folder+name+"_ResistvsTemp_raw.dat"
            iv.save_rt_data_live(R,T,filename) #Save data to sharepoint
            d.save_Crossbar_Tc(chip, Tc,folder,device) #Save Tc to database
        i = i + 1
        
def continuousResistTemp_Nathan(chip, device, target, tempSetpoint, PID, manual):
    global slope_plots,app
    global windows,plots,curves,figures    
    
    cards =inpfunc.get_cards(device)
    card1=cards[0]
    card2=cards[1]
    channels = inpfunc.get_channels(device)
    channel1=channels[0]
    channel2=channels[1]
    
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
    else:
        pass
    
    windows = lpf.create_windows(1)
    plot = lpf.create_plots(windows,formatt='Nathan')  
    curve1 = plot[0].plot()
    curve2 = plot[0].plot()
   
    windows[0].move(-900, 0) # move to other desktop, spyder had been blocking before
    windows[0].setWindowState(QtCore.Qt.WindowActive)
    windows[0].raise_()
    windows[0].activateWindow()
    
    R,T=iv.constantruntemp(app,curve1,curve2,card1,card2,channel1,channel2,target,tempSetpoint,PID,manual)

    
    
def continousresist(chip,device):
    global slope_plots,app
    global windows,plots,curves,figures
    '''
    Get channels,card
    '''
    cards =inpfunc.get_cards(device)
    card1=cards[0]
    card2=cards[1]
    channels = inpfunc.get_channels(device)
    channel1=channels[0]
    channel2=channels[1]
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
    else:
        pass
    num_plots=1
    curves = initialization(num_plots)
   

   
    windows[0].move(-900, 0) # move to other desktop, spyder had been blocking before
    windows[0].setWindowState(QtCore.Qt.WindowActive)
    windows[0].raise_()
        
        # this will activate the window (yellow flashing on icon)
    windows[0].activateWindow()
    
    iv.constantrun(app,curves,card1,card2,channel1,channel2)
def measure_PCM3b_RS(folder,folder_link,chip,RSs,warm):
   
    if warm:
       
        Resistance_measurements,_ = mdr.get_Resistance(folder, chip, RSs)
        '''
        Saves to Database, one per device

        '''
        for i in range(0,len(RSs)):
            d.save_Resistance_Measurements_PCM3B_warm(chip,[float(Resistance_measurements[i])],folder_link,RSs[i])
        
    else:
        
        
        Resistance_measurements=mra.get_resistance_arrays(folder,chip,RSs)
      #  Resistance_measurements=rc.discretepoints(folder,chip,RSs,points)
        for i in range(0,len(RSs)):
            d.save_Resistance_Measurements_PCM3B_cold(chip,Resistance_measurements[i], folder_link, RSs[i])
def measure_PCMRS(folder,folder_link,chip,RSs,warm):
    if warm:
        Resistance_measurements,funkygraphlist = mdr.get_Resistance(folder, chip, RSs)
        return funkygraphlist
    else:
        Resistance_measurements,_ = mdr.get_Resistance(folder, chip, RSs,OptionalCurrent=1e-03)
        
        for i in range(0,len(RSs)):
            Resistance_measurements[i]=float(Resistance_measurements[i])
            d.save_Resistance_Measurements_PCMRS(chip,Resistance_measurements[i],folder_link, RSs[i])
        return False
def measure_PCM3b_Crossbars(folder,folder_link,chip,Crossbars,warm):
    '''
    Just going 0 to 3Ma and getting resistance
    '''
    

    Resistance_measurements,_ = mdr.get_Resistance(folder, chip, Crossbars)
    
    if warm:
        for i in range(0,len(Crossbars)):
            d.save_Crossbar_Measurements_PCM3B_warm(chip,[Resistance_measurements[i]],folder_link,Crossbars[i])
    else:
        for i in range(0,len(Crossbars)):
            d.save_Crossbar_Measurements_PCM3B_cold(chip,[Resistance_measurements[i]],folder_link,Crossbars[i])

