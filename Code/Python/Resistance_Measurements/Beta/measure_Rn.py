# -*- coding: utf-8 -*-
"""
Created sometime in the past

@author: Soroush
"""

from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.Point import Point
import pyqtgraph as pg
import random
import sys
import numpy as np
import math
import IV_curve_v3 as iv
import matplotlib.pyplot as plt
import Input_Functions as inpfunc
import measure_Ic as ic
import Live_Plot_Functions as lpf
import time
from pyqtgraph import exporters
import database_v4 as d



#======================
# main Function to collect data and plot
# =====================

def initialization(num_plots):
    global windows, plots, curves
    windows = lpf.create_windows(num_plots)
    plots = lpf.create_plots(windows)
    curves = lpf.create_curves(plots)
    return curves

# save at the end
def get_Rn_Imax(folder, chip, devices):
    global slope_plots, app
    global windows, plots, curves, my_exporters,figures
    '''
     Inputs:
        Folder-Target folder for data to be saved
        Chip-Target Chip
        Devices-Devices on Target Chip
    Outputs:
        return_measurements_Rn-Array of rn measurements
        return_measurements_Imax-array of Imax measurements
        2 graphs for each device, one has Rn, Imax
        s
    Called By: 
        Measurement Functions- MEasure_JJs_Rn
    Calls On:
        sweep_current_live_Rn
        save_Rn_data
    ''' 
    # get variables
    inputs = inpfunc.format_input_Rn_Imax_devices(devices)
    channels = inputs[0]
    num_JJ = inputs[1]
    cards = inputs[2]
    
    # arrays that will be returned
    return_measurements_Rn = []
    return_measurements_Imax = []

    # check instance, so that it doesn't crash on exit (hopefully)
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
    else:
        pass

    num_plots = len(num_JJ)
    # create windows, plots, curves
    curves = initialization(num_plots)
    x, y = lpf.create_data(curves)

    slope_plots = lpf.create_slope_plots(plots)

    # data collection
    counter = 0
    steps = 0.00008
    # create exporters (trying to fix problem of C object being deleted
    my_exporters = []
    for i in range(0, num_plots):
        scene = plots[i].scene()
        exporter = exporters.ImageExporter(scene)
        my_exporters.append(exporter)

    # loop through and plot slope
    # i incremets by 2, counter by 1
     # get current number of JJ and channels
    for i in range (0, len(channels), 2):
        num_j = num_JJ[counter]
        chan1 = channels[i]
        chan2 = channels[i+1]
        card1 = cards[i]
        card2 = cards[i+1]


        dev = devices[counter]
        ic_pred = d.predict_Ic(d.chip_Jc(chip), dev.JJ_radius_nom*1e-06)
        steps = (ic_pred*16)/100
        print("-----------------")
        print(steps)
        
        # bring current window to focus        
        windows[counter].move(-900, 0) # move to other desktop, spyder had been blocking before
        windows[counter].setWindowState(QtCore.Qt.WindowActive)
        windows[counter].raise_()
        
        # this will activate the window (yellow flashing on icon)
        windows[counter].activateWindow()
        
        # plot, from zero, to at least V_max (num_j*2.5e-03) and stop when slope exceeds certain amount
        # see iv.sweep_current_live_Rn
        I, V, R,slope,slope_index = iv.sweep_current_live_Rn(app, curves[counter], 1, 0, num_j*2.5e-03, steps, card1, card2, chan1, chan2,dev)
        if I==0 and V==0 and R==0:
            return 0,0
        
        # plot the slope and get the location it was plotted
        try:
            slope_index, slope = plot_slope(I,V, counter, slope,slope_index)
        except:
            print("\nERROR!\n")
            slope_index = 0
            slope = 1e-09
                
        # set label
        label = pg.TextItem(text=("Slope: " +str(slope)), color=(0, 0, 0), fill=(255, 0, 0), anchor=(-.5, -.5))
        label.setPos(I[slope_index], V[slope_index])
        plots[counter].addItem(label)
  
        # append to total data
        x[counter] = I
        y[counter] = V

        # create name
        name = ic.create_name(chip, devices[counter])
        plots[counter].setTitle(name)
        # new fig
        #fig = plt.figure()
        #figures.append(fig)
       
        # plot differential
        #Rdiff = np.diff(V)/np.diff(I)
        #plt.plot(V[0:-1], Rdiff)
       
        # saving
        filename = (folder + name + "_Rn.png")
        ic.create_dir(filename)
        print(filename)
        iv.save_data_live(I,V,R,(folder+name+"_Rn_raw.dat"))
        plt.savefig(folder + name + '_Rn_Diff.png')
       
        return_measurements_Rn.append(slope/num_JJ[counter])
        return_measurements_Imax.append(I[slope_index+5])
        save_Rn_data((slope/num_JJ[counter]),I[slope_index+5], folder+name)
        
        try:
            my_exporters[counter].export(filename)
        except:
            print("oh noooo, wrapped object was deleted\n")
            
        counter += 1
    return return_measurements_Rn, return_measurements_Imax

# save throughout
def get_Rn_Imax_and_save(folder, folder_link, chip, devices, meas_ids):
    global slope_plots, app
    global windows, plots, curves
    global my_exporters
    '''
    
    :param folder: Target folder for data to be saved
    
    :param folder_link: Web Link to Folder
    
    :param chip: Target Chip
   
    :param devices: Array of Target devices
   
    :param  Meas_IDs: Array of Measurement Ids
   
    :return: return_measurements_Rn- Array of rn measurements
        
    :return: return_measurements_Imax-array of Imax measurements
      
    :Graphs: 1 Rn, 1 Imax for each device
    
    Saves in database after every run
   
    Called By: 
      
        -Measurement Functions- Measure_PCM_chip_cold
    
    Calls On:
       
        -sweep_current_live_Rn
        
        -save_Rn_data
    '''
    
    # get variables
    inputs = inpfunc.format_input_Rn_Imax_devices(devices)
    channels = inputs[0]
    num_JJ = inputs[1]
    cards = inputs[2]
    
    # arrays that will be returned
    return_measurements_Rn = []
    return_measurements_Imax = []

    # check instance, so that it doesn't crash on exit
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
    else:
        pass

    num_plots = len(num_JJ)
    
    # create windows, plots, curves
    curves = initialization(num_plots)
    x, y = lpf.create_data(curves)

    slope_plots = lpf.create_slope_plots(plots)

    # data collection
    counter = 0
    
    # create exporters (trying to fix problem of C object being deleted
    my_exporters = []
    for i in range(0, num_plots):
        scene = plots[i].scene()
        exporter = exporters.ImageExporter(scene)
        my_exporters.append(exporter)

    # loop through and plot slope
    # i incremets by 2, counter by 1
    for i in range (0, len(channels), 2):
        # get current number of JJ and channels
        num_j = num_JJ[counter]
        chan1 = channels[i]
        chan2 = channels[i+1]
        card1=cards[i]
        card2=cards[i+1]
        # create steps based on device, method: Ic*16/100
        dev = devices[counter]
        ic_pred = d.predict_Ic(d.chip_Jc(chip), dev.JJ_radius_nom*1e-06)
        steps = (ic_pred*16)/100
        print("-----------------")
        print(steps)
        
        # bring current window to focus        
        windows[counter].move(-900, 0) # move to other desktop, spyder had been blocking before
        windows[counter].setWindowState(QtCore.Qt.WindowActive)
        windows[counter].raise_()
        
        # this will activate the window (yellow flashing on icon)
        windows[counter].activateWindow()
        
        # plot, from zero, to at least V_max (num_j*2.5e-03) and stop when slope exceeds certain amount
        # see iv.sweep_current_live_Rn
      
        I, V, R, slope, slope_index = iv.sweep_current_live_Rn(app, curves[counter], 1, 0, num_j*4e-03, steps,card1,card2, chan1, chan2,dev)
        if slope is None:
            slope = 1e-09
            
        if I==0 and V==0 and R==0:
            return 0,0
        
        # plot the slope and get the location it was plotted
        try:
            slope_index_old, slope_old = plot_slope(I,V, counter,slope,slope_index)
        except:
            print("\nERROR!\n")
            slope_index = 0
            slope = 1e-09
        # set label
        label = pg.TextItem(text=("Slope: " +str(slope)), color=(0, 0, 0), fill=(255, 0, 0), anchor=(-.5, -.5))
        label.setPos(I[slope_index], V[slope_index])
        plots[counter].addItem(label)
        
        # append to total data
        x[counter] = I
        y[counter] = V

        # create name
        name = ic.create_name(chip, devices[counter])
        plots[counter].setTitle(name)

        # new fig
#        fig = plt.figure()

        # plot differential
 #       Rdiff = np.diff(V)/np.diff(I)
  #     plt.plot(V[0:-1], Rdiff)

        #Saving Locally
        filename = (folder + name)
        print(filename)
        ic.create_dir(filename)
       
                
        sub_folder = "/RawData_Rn"
        filename = (folder+sub_folder+name+"_Rn_raw.dat")
        ic.create_dir(filename) # function to create dir if doesn't exist
        print(filename)
        iv.save_data_live(I,V,R,(folder+sub_folder+name+"_Rn_raw.dat")) # save the raw data
        # changed to here 2/15 
        plt.savefig(folder+sub_folder+name+'_Rn_Diff.png')
        

        sub_folder = "/Rn_values"
        filename = (folder+sub_folder+name)
        print(filename)
        ic.create_dir(filename) # function to create dir if doesn't exist
        
        return_measurements_Rn.append(slope/num_JJ[counter])
        try:
            return_measurements_Imax.append(I[slope_index+5])
            save_Rn_data((slope/num_JJ[counter]),I[slope_index+5], filename)
        except:
            return_measurements_Imax.append(1e-09)
            save_Rn_data((slope/num_JJ[counter]),1e-09, folder+name)
        
        
        sub_folder = "/Graphs"
        filename = (folder + sub_folder + name + "_Rn.png")
        print(filename)
        ic.create_dir(filename) # function to create dir if doesn't 
        
        try:
            my_exporters[counter].export(filename)
        except:
            print("oh noooo, wrapped object was deleted\n")
            
        
        # saving to database
        Rn = return_measurements_Rn[counter]
        Imax = return_measurements_Imax[counter]
        device = devices[counter]
        d.save_JJ_Measurements_Rn(chip, Rn, Imax, meas_ids[counter], device)
       
        counter = counter + 1
    return return_measurements_Rn, return_measurements_Imax


def plot_slope(I,V, counter,slope,slope_index):
    '''
    
    :param I: Current array
    
    :param V: Voltage array
    
    :param Counter: Counter for which graph this data pertains to
   
    :return: final index-6: slope index
   
    :return: slope-measured slope
   
    :Graph: plots 2 points in red and a trendline based on them over the raw data
    
    Called By: 
        
        MeasureRn
        
            -get_rn_imax
        
            -get_rn_imax_and_save
    '''
    global slope_plots, app
    
    slope_x = []
    slope_y = []
    
    final_index = slope_index

    slope_x.append(I[final_index-4])
    slope_x.append(I[final_index-6])
    slope_y.append(V[final_index-4])
    slope_y.append(V[final_index-6])
    active_window = counter
    slope_plots[active_window].setData(slope_x, slope_y, symbol='o', symbolBrush ='r', pen='r')
    slope2 = (float(slope_y[1]) - float(slope_y[0]))/(float(slope_x[1]) - float(slope_x[0]))
    if slope>0:
        print("Final slope is: %f" % slope)
    else:
        print("Error: Slope is negative")
        slope=1e-09
    
    app.processEvents()
    return final_index-6, slope

def save_Rn_data(Rn, Imax, name):
    '''
    Saves the Rn and Imax data
    '''
    column = 2
    data = np.zeros((1, column))
    data[0][0] = Rn
    data[0][1] = Imax
    name = name + "_Rn.dat"
    np.savetxt(name, data, header = 'row1: Rn, row2: Imax \nOrder: I0, I1, I2, I3')
