# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 11:50:50 2017

@author: Soroush
"""

import sys
import IV_curve_v3 as iv
import Resistance_curve as rc
import measure_Ic as ic
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from pyqtgraph import exporters
import numpy as np
import Input_Functions as inpfunc
import Live_Plot_Functions as lpf



#===================
# measure functions
#===================

# create live plotting elements 

def initialization(num_plots):
    '''
    Creates all the live plot elements
    '''
    global windows, plots, curves
    windows = lpf.create_windows(num_plots)
    plots = lpf.create_plots(windows)
    curves = lpf.create_curves(plots)
    return curves

# plot a current sweep

def get_resistance_arrays(folder, chip, devices):
    '''
    Takes a sweep from 0 to 3mA and returns the slope
    
    :param Folder: Target folder for data to be saved
  
    :param Chip: Target Chip
   
    :param Devices: Devices on Target Chip
        
    :return: return_measurements_Resistance-I,V,R arrays
    
   
    
    Called By: 
        
        -Measurement Functions
         
            -Measure_PCM_Chip_Cold
        
            -Measure_PCM_Chip_Warm
    
    Calls On:
        
        -plot_Resistance_Array_live
        
        -plot_slope_Resistance_arrays
        
        -save_data_live
        
        -save_resistance_data
        
        -save_JJ_Measurements_Ic
    

    '''
    global slope_plots, app
    global windows, plots, curves, my_exporters
    
    # get variables
    inputs = inpfunc.format_input_resistance(devices)
    cards = inputs[0]
    channels = inputs[1]

    # arrays that will be returned
    return_measurements_Resistance = []


    # check instance, so that it doesn't crash on exit (hopefully)
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
    else:
        pass

    num_plots = int(len(cards)/2)
    
    # create windows, plots, curves
    curves = initialization(num_plots)

    # data collection
    counter = 0

    # create exporters (trying to fix problem of C object being deleted)
    my_exporters = []
    for i in range(0, num_plots):
        scene = plots[i].scene()
        exporter = exporters.ImageExporter(scene)
        my_exporters.append(exporter)

    # loop through and plot slope
    # i incremets by 2, counter by 1
    for i in range (0, len(channels), 2):
        
        slope_plots = lpf.create_slope_plots_resistor_arrays(plots)
        
        # get current number of JJ and channels
        chan1 = channels[i]
        chan2 = channels[i+1]
        card1 = cards[i]
        card2 = cards[i+1]
        
        # bring current window to focus        
        windows[counter].move(-900, 0) # move to other desktop, spyder had been blocking before
        windows[counter].setWindowState(QtCore.Qt.WindowActive)
        windows[counter].raise_()
        
        # this will activate the window (yellow flashing on icon)
        windows[counter].activateWindow()

        # Sweep from 0 to 3 mA
        max_current = 3e-03
       # import pdb;pdb.set_trace()
        I, V, R,_ = rc.plot_Resistance_Array_live(app, curves[counter], card1, card2, chan1, chan2, max_current)
        # plot the slope and get the location it was plotted
        resistances, indicies = plot_slope_Resistor_Arrays(I,V, counter)
        print(resistances)
        
        # set label
        for i in range (0, len(resistances)):
            index = indicies[i]
            label = pg.TextItem(text=("Slope: " +str(resistances[i])), color=(0, 0, 0), fill=(255, 0, 0), anchor=(-.5, -.5))
            label.setPos(I[index], V[index])
            plots[counter].addItem(label)

        # append to total data
        return_measurements_Resistance.append(resistances)

        # create name
        name = ic.create_name(chip, devices[counter])
        plots[counter].setTitle(name)


        # saving

        filename = (folder + name + "_Resistor_Array.png")
        print(filename)
        ic.create_dir(filename)
        
        
        iv.save_data_live(I,V,R,(folder+name+"_Resistor_Array_raw.dat"))
        
        save_resistance_data(resistances, folder+name)
        
        try:
            my_exporters[counter].export(filename)
        except:
            print("oh noooo, wrapped object was deleted\n")
            
        
        counter += 1

    return return_measurements_Resistance



def plot_slope_Resistor_Arrays(I,V, counter):
    '''
    :param I: Current array
    
    :param V: Voltage array
    
    :param Counter: Counter for which graph this data pertains to
   
    :return: final index-6: slope index
   
    :return: slope-measured slope
   
    :Graph: plots 2 points in red and a trendline based on them over the raw data
    
    Called By: 
        
        MeasureRn
        
            -get_resistance_arrays
        
    '''
    global slope_plots, app
    
    slope_x = []
    slope_y = []
    indicies = []
    resistances = []
    
    current_slope_plot = slope_plots[counter]
    
    for i in range(0, len(I)):
        if (I[i] == 0.5e-03):
            indicies.append(i)
        if (I[i] == 1e-03):
            indicies.append(i)
        if (I[i] == 2e-03):
            indicies.append(i)
    
    for i in range(0, len(indicies)):
        index = indicies[i]
        slope_x.append(I[index-1])
        slope_x.append(I[index+1])
        slope_y.append(V[index-1])
        slope_y.append(V[index+1])
        current_slope_plot[i].setData(slope_x, slope_y, symbol='o', symbolBrush ='r', pen='r')
        resistances.append((slope_y[1] - slope_y[0])/(slope_x[1] - slope_x[0]))
        slope_x = []
        slope_y = []
    
    return resistances, indicies

def save_resistance_data(resistances, name):
    '''
    Saves the values found for the resistances in a .dat file
    '''
    column = 3
    data = np.zeros((1, column))
    data[0][0] = resistances[0]
    data[0][1] = resistances[1]
    data[0][2] = resistances[2]
    name = name + "_Resistor_Array.dat"
    np.savetxt(name, data, header = 'row1: @ 0.5 mA, row2: @ 1mA, row3: @ 2mA \n')