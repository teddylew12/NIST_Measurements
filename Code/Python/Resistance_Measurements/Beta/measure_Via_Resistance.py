# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 13:52:59 2017

@author: Soroush
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


def initialization(num_plots):
    '''
    Create live plotting elements
    '''
    global windows, plots, curves
    windows = lpf.create_windows(num_plots)
    plots = lpf.create_plots(windows)
    curves = lpf.create_curves(plots)
    return curves

def get_Resistance_Via(folder, chip, devices):
    '''
    Sweeps from 0 to 3mA and returns the slope
    
    :param folder: folder name of where data will be saved
        
    :param chip: Target chip
    
    :param devices: Array of target devices
   
    :return:   return_measurements: I,V,R arrays
    
    Called By:
        
        Measurement_Functions
            
            -measure pcm cold and warm
   
    Calls On:
        
        -plot_Resistance_Array_live
        
        -save_data_live
        
        -save_Resistance_data_Via
    '''
    # globals- necesarry to avoid automatic deletion of objects
    global app
    global windows, plots, curves, my_exporters
    # get variables
    inputs = inpfunc.format_input_resistance(devices)
    cards = inputs[0]
    channels = inputs[1]

    
    # create instance of the app
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
    else:
        pass
    
    # detect the number of plots need based on the cards, since there is a 1:1 ratio
    # between devices and cards (%use devices?)
    num_plots = len(cards)
    print("num plots: %d" %num_plots)

    # initialize by opening correct number of windows
    # each window contains a plot, each plot a curve and they are all stored in arrays
    curves = initialization(num_plots)

    # we need two indexes, one for pairs, one for normal
    index_pairs = 0
    index = 0

    my_exporters = [] # array to hold exporters
    
    # create exporters
    for i in range(0, num_plots):
        exporter = exporters.ImageExporter(plots[i].scene())
        my_exporters.append(exporter)
    
    
    return_measurements = []
    # take all the sweeps
    for i in range(0,num_plots):
        print("Begin Device %s sweep" %(i))
        # get two channels and two current limits that are needed
        my_channels = []
        my_channels.append(channels[index_pairs])
        my_channels.append(channels[index_pairs+1])


        name = ic.create_name(chip, devices[i]) # create the name
        plots[i].setTitle(name) # set title to name

        # bring current window to focus        
        windows[i].move(-900, 0) # move to other desktop, spyder had been blocking before
        windows[i].setWindowState(QtCore.Qt.WindowActive)
        windows[i].raise_()
        
        # this will activate the window (yellow flashing on icon)
        windows[i].activateWindow()
        
        # sweep the current device
        max_current = .6e-03
        
        I, V, R = rc.plot_Resistance_Array_live(app, curves[i], cards[i], my_channels[0], my_channels[1], max_current)

        # find the slope
        slope = (V[-1]-V[0])/(I[-1]- I[0])

        # Plotting Critical Currents #

        # arrays that will be returned
        return_measurements.append(slope)

        # setting labels
        label = pg.TextItem(text="", color=(0, 0, 0), fill=(255, 0, 0), anchor=(0, -1))
            
        # label text
        label_text = ("Resistance: %s"%slope)
        label.setText(label_text)
        label.setPos(I[int(len(I)/2)], V[int(len(V)/2)])
        graph = plots[i]
        graph.addItem(label)
        
        # add red line to represent slope
        new_curve = plots[i].plot()
        new_curve.setData([I[0], I[-1]], [V[0], V[-1]], symbol='o', symbolBrush='r', pen='r', symbolSize=10)
       
        #Saving 
        filename = (folder + name + "_Via.png")
        print(filename)
        ic.create_dir(filename) # function to create dir if doesn't exist
      
        iv.save_data_live(I,V,R,(folder+name+"_Via_Raw.dat")) # save the raw data
        save_Resistance_data_Via(slope,(folder+name)) # save the important data
    
        try:
            my_exporters[i].export(filename) # export the graph
        except:
            print("Oh no wrapped object was deleted!!!!!")
        
        # repeat
        index = index + 1
        index_pairs = index_pairs + 2

        app.processEvents()
        print("End Device %s sweep\n" %(i))

    return return_measurements
def pcm3b_Via(folder, chip, devices):
    '''
    Looks for discontinuity and finds IMAX
    
    :param folder: folder name of where data will be saved
        
    :param chip: Target chip
    
    :param devices: Array of target devices
   
    :return:   return_measurements: I,V,R arrays
    
    Called By:
        
       Measure_Pcm3b
   
    Calls On:
        
        -plot_Resistance_Array_live
        
        -save_data_live
        
        -save_Resistance_data_Via
    '''
    # globals- necesarry to avoid automatic deletion of objects
    global app
    global windows, plots, curves, my_exporters
    # get variables
    inputs = inpfunc.format_input_resistance(devices)
    cards = inputs[0]
    channels = inputs[1]

    
    # create instance of the app
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
    else:
        pass
    
    # detect the number of plots need based on the cards, since there is a 1:1 ratio
    # between devices and cards (%use devices?)
    num_plots = int(len(cards)/2)
    print("num plots: %d" %num_plots)

    # initialize by opening correct number of windows
    # each window contains a plot, each plot a curve and they are all stored in arrays
    curves = initialization(num_plots)

    # we need two indexes, one for pairs, one for normal
    index_pairs = 0
    index = 0

    my_exporters = [] # array to hold exporters
    
    # create exporters
    for i in range(0, num_plots):
        exporter = exporters.ImageExporter(plots[i].scene())
        my_exporters.append(exporter)
    
    
    resistances = []
    Imaxs=[]
    # take all the sweeps
    for i in range(0,num_plots):
        print("Begin Device %s sweep" %(i))
        # get two channels and two current limits that are needed
        my_channels = []
        my_channels.append(channels[index_pairs])
        my_channels.append(channels[index_pairs+1])


        name = ic.create_name(chip, devices[i]) # create the name
        plots[i].setTitle(name) # set title to name

        # bring current window to focus        
        windows[i].move(-900, 0) # move to other desktop, spyder had been blocking before
        windows[i].setWindowState(QtCore.Qt.WindowActive)
        windows[i].raise_()
        
        # this will activate the window (yellow flashing on icon)
        windows[i].activateWindow()
        
        # sweep the current device
        max_current = 100e-03
        
       # I, V, R = rc.plot_Resistance_Array_live(app, curves[i], cards[i], my_channels[0], my_channels[1], max_current)
        I,V,R,Imax,slope=rc.plot_pcm3b(app,curves[i],cards[0],cards[1],my_channels[0],my_channels[1],max_current)
        # find the slope
        slope=float(slope)

        # Plotting Critical Currents #

        # arrays that will be returned
        resistances.append(slope)
        Imaxs.append(Imax)

        # setting labels
        label = pg.TextItem(text="", color=(0, 0, 0), fill=(255, 0, 0), anchor=(0, -1))
            
        # label text
        label_text = ("Resistance: %s"%slope)
        label.setText(label_text)
        label.setPos(I[int(len(I)/2)], V[int(len(V)/2)])
        graph = plots[i]
        graph.addItem(label)
        
        # add red line to represent slope
        new_curve = plots[i].plot()
        new_curve.setData([I[0], I[5]], [V[0], V[5]], symbol='o', symbolBrush='r', pen='r', symbolSize=10)
       
        #Saving 
        filename = (folder + name + "_Via.png")
        print(filename)
        ic.create_dir(filename) # function to create dir if doesn't exist
    
        iv.save_data_live(I,V,R,(folder+name+"_Via_Raw.dat")) # save the raw data
        save_Resistance_data_Via(slope,Imax,(folder+name)) # save the important data
    
        try:
            my_exporters[i].export(filename) # export the graph
        except:
            print("Oh no wrapped object was deleted!!!!!")
        print("Got here!")
        # repeat
        index = index + 1
        index_pairs = index_pairs + 2

        app.processEvents()
        print("End Device %s sweep\n" %(i))
    return resistances, Imaxs
def save_Resistance_data_Via(R,I, name):
    '''
    Saves the resistance in a text file to the name passed in
    '''
    column = 2
    data = np.zeros((1, column))
    data[0,0] = R
    data[0,1]= I

    name = name + "_Via_Resistance.dat"
    np.savetxt(name, data, header = 'Room Temp Resistance')