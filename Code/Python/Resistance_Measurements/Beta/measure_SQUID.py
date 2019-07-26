# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 15:02:16 2019

@author: Nathan Biesterfeld and Ted Lewitt
"""

import sys
import IV_curve_SQUID as iv
import Input_Functions as inpfunc
import Live_Plot_Functions as lpf
import measure_Ic as ic
import database_v4 as d
import numpy as np
import Plot_Generation_v2 as pg
from pyqtgraph.Qt import QtGui, QtCore

def measure_SQUID_IV_no_flux(folder,folder_link,chip,devices, save, manual, min_Ibias, max_Ibias, step_Ibias):
    global slope_plots,app
    global windows,plots,curves,figures
    
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
    else:
        pass
    
    num_plots= len(devices)
    windows = lpf.create_windows(num_plots)
    plots = lpf.create_plots(windows,formatt='IV')  
    curves = lpf.create_curves(plots)
    current_point = lpf.create_current_point(plots)
    ic_curves_all = []
    for i in range(len(plots)):
        ic_curves = []
        for j in range(4):
            ic_curves.append(plots[i].plot())
        ic_curves_all.append(ic_curves)
   
    windows[0].move(-900, 0) # move to other desktop, spyder had been blocking before
    windows[0].setWindowState(QtCore.Qt.WindowActive)
    windows[0].raise_()
    windows[0].activateWindow()
    
    i = 0
    for device in devices:
        cards =inpfunc.get_cards(device)
        card1=cards[0]
        card2=cards[1]
        channels = inpfunc.get_channels(device)
        channel1=channels[0]
        channel2=channels[1]
    
        if manual:
            I, V, Ics = iv.sweep_current(app,curves[i],current_point[i],ic_curves_all[i],plots[i],card1,card2,channel1,channel2,min_Ibias,max_Ibias,step_Ibias)
        else:
            I, V, Ics = iv.sweep_current(app,curves[i],current_point[i],ic_curves_all[i],plots[i],card1,card2,channel1,channel2,-0.4e-03,0.4e-03, 0.005e-03)
            
        if save:
            new, meas = d.save_SQUID_no_flux(chip, Ics, folder, device)
            name=ic.create_name(chip,device)
            if new: #If a new measurement was created, create a new folder         
                ic.create_dir(folder+name)         
            else: #If the data was added to an existing measurement, add to existing folder
                folder = 'E:/Users/volt.686QVACTEST/National Institute of Standards and Technology (NIST)/SEG - SFQ_Circuits' + '/' + meas.data_directory[pg.find_D(meas.data_directory,chip):]     
            iv.save_data(I,V,(folder+name+"_Ic_raw.dat")) #Save data to sharepoint
            
        i = i + 1
    
def measure_SQUID_periodicity(folder,folder_link,chip,devices,save,manual,minIflux,maxIflux,step,Ibias):
    global slope_plots,app
    global windows,plots,curves,figures
    
    number_of_sweeps = 5 #Changes the number of different Ibiases the Iflux sweep is done at
    
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
    else:
        pass
    
    num_plots= len(devices)
    windows = lpf.create_windows(num_plots)
    plots = lpf.create_plots(windows,formatt='VvsIflux')  
    curves = lpf.create_curves(plots)
    current_point = lpf.create_current_point(plots)
   
    windows[0].move(-900, 0) # move to other desktop, spyder had been blocking before
    windows[0].setWindowState(QtCore.Qt.WindowActive)
    windows[0].raise_()
    windows[0].activateWindow()
    
    i = 0
    for device in devices:
        cards =inpfunc.get_cards(device)
        card1=cards[0]
        card2=cards[1]
        channels = inpfunc.get_channels(device)
        channel1=channels[0]
        channel2=channels[1]
    
        if manual:
            period,Iflux_min_Ic,I,V= iv.sweep_current_vphi(app,curves[i],current_point[i],card1,card2,channel1,channel2, minIflux, maxIflux,step,Ibias,Ibias+1,1)
        else:
            measurements = d.show_squid_measurements_from_device(chip, device)
            average_Ic = get_average_Ic(measurements)
            Ibias_step = average_Ic / (number_of_sweeps + 1)
            Ibias_min = Ibias_step
            Ibias_max = average_Ic-Ibias_step
            period,Iflux_min_Ic,I,V= iv.sweep_current_vphi(app,curves[i],current_point[i],card1,card2,channel1,channel2, 0, 3e-03, 0.5e-05, Ibias_min, Ibias_max, Ibias_step)
        
        if save:
            new, meas = d.save_SQUID_periodicity(chip, period, Iflux_min_Ic, folder, device)
            name=ic.create_name(chip,device)
            if new:                
                ic.create_dir(folder+name)
            else:
                folder = 'E:/Users/volt.686QVACTEST/National Institute of Standards and Technology (NIST)/SEG - SFQ_Circuits' + '/' + meas.data_directory[pg.find_D(meas.data_directory,chip):]
            iv.save_data(I,V,(folder+name+"_period_raw.dat")) #Save data to sharepoint
            
        i = i + 1

def measure_SQUID_IV_with_flux(folder,folder_link,chip,device,save,down,manual,min_Iflux,max_Iflux,step_Iflux,min_Ibias,max_Ibias,step_Ibias):
    global slope_plots,app
    global windows,plots,curves,figures
    
    if manual:
        number_of_sweeps = len(np.arange(min_Iflux, max_Iflux, step_Iflux))
    else:
        number_of_sweeps = 5 #Changes the number of different Ifluxes that the I-V curve is taken at
    
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
    else:
        pass
    
    num_plots= 1
    windows = lpf.create_windows(num_plots)
    plots = lpf.create_plots(windows,formatt='VvsIbias')  
    curves_full = []
    for i in range(0, len(plots)):
        curves = []
        for j in range(0, number_of_sweeps):
            curves.append(plots[i].plot())
        curves_full.append(curves)
    current_point = lpf.create_current_point(plots)
   
    windows[0].move(-900, 0) # move to other desktop, spyder had been blocking before
    windows[0].setWindowState(QtCore.Qt.WindowActive)
    windows[0].raise_()
    windows[0].activateWindow()
    
    i = 0
    
    cards =inpfunc.get_cards(device)
    card1=cards[0]
    card2=cards[1]
    channels = inpfunc.get_channels(device)
    channel1=channels[0]
    channel2=channels[1]
        
    if manual:
        I,V,colorsused = iv.sweep_current_flux(app,curves_full[i],current_point[i],card1,card2,channel1,channel2,min_Ibias,max_Ibias,step_Ibias,min_Iflux,max_Iflux,step_Iflux,down)
    else:
        measurements = d.show_squid_measurements_from_device(chip, device)
        period = get_average_period(measurements)
        Iflux_min_Ic = get_average_Iflux_min_Ic(measurements)
        I,V,colorsused = iv.sweep_current_flux(app,curves_full[i],current_point[i],card1,card2,channel1,channel2,-3e-03,3e-03, 0.1e-03,Iflux_min_Ic-(period/12),Iflux_min_Ic+(period/12),(period/6)/(number_of_sweeps-1),True)
    
    return I,V,colorsused,windows[0]

def get_average_Ic(measurements):
    if type(measurements) != list:
        return measurements.Ic_pos
    elif len(measurements) == 0:
        return False
    elif len(measurements) > 0:
        average_Ic = 0
        for meas in measurements:
            average_Ic = average_Ic + meas.Ic_pos
        average_Ic = average_Ic / len(measurements)
        return average_Ic
    
def get_average_period(measurements):
    if type(measurements) != list:
        return measurements.Iflux_period
    elif len(measurements) == 0:
        return False
    elif len(measurements) > 0:
        average_period = 0
        for meas in measurements:
            average_period = average_period + meas.Iflux_period
        average_period = average_period / len(measurements)
        return average_period
    
def get_average_Iflux_min_Ic(measurements):
    if type(measurements) != list:
        return measurements.Iflux_min_Ic
    elif len(measurements) == 0:
        return False
    elif len(measurements) > 0:
        average_Iflux_min_Ic = 0
        for meas in measurements:
            average_Iflux_min_Ic = average_Iflux_min_Ic + meas.Iflux_min_Ic
        average_Iflux_min_Ic = average_Iflux_min_Ic / len(measurements)
        return average_Iflux_min_Ic


##################
#Failed LC Step Functions
#################
'''
def manual_get_big_step(allI,allV,colors):
    import Unified_Measurement_GUI_v0 as ug

    
    message="Pick the color of the curve with the best LC step to be saved"
    color, okPressed = ug.dropdown("Color:", message,colors, 0, False)
    index=colors.index(color)
    return allI[index],allV[index]
def getbigstep(allI,allV):
    
    Finds biggest LC step of all different Ifluxvals
    
    Get Sweep Up
    Get values greater than 0
    Find first jump
    Find second jump
    take differnce between each
   
    bigstep=-1
    bigstepind=-1

    import numpy as np
    for index,ivsweep in enumerate(allI):
       
        Assumes full sweep, needs to be corrected for sweeps starting at zero or sweeps that also dont go back down
        
        #sweepupI=np.array(ivsweep[:int((len(ivsweep)+1)/2)])
        #sweepupV=np.array(allV[index][:int((len(ivsweep)+1)/2)])
        #Boolean mask for the positive half of the sweep
        #mask=sweepupI>=0
        #Get the data from the upper half of the sweep
        #halfI=sweepupI[mask]
        #halfV=sweepupV[mask]
        halfI=ivsweep
        halfV=allV[index]
        #Gets average difference of first 3 points, then looks for big deviations
        avgchange=np.mean(np.diff(halfV)[:3])
        delta=50
        firststep=-1
        import pdb;pdb.set_trace()
        for I in range(0,len(halfI)-1):
            #Find the first step
            if halfI[I+1]-halfI[I]>=delta*avgchange:
                firststep=I
                break
        secstep=-1
        stepI=halfI[firststep:]
        stepavgchange=np.mean(np.diff(stepI)[:4])
        for I in range(0,len(halfI)-1):
            #Find the first step
            if stepI[I+1]-stepI[I]>=delta*stepavgchange:
                secstep=I
                break
        diff=halfV[secstep]-halfV[firststep]
        if diff>bigstep:
            bigstep=diff
            bigstepind=index
    return allI[bigstepind],allV[bigstepind]
'''