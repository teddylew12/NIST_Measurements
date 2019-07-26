# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 14:23:53 2017

@author: Soroush
"""

from pyqtgraph import QtGui, QtCore
import Live_Plot_Functions as lpf
import math
import numpy as np
import sys
import pyqtgraph as pg
import re
import database_v4 as d3
import sqlalchemy as sa
import imp
from pyqtgraph import exporters

def initialization():
    '''
    Initialize plotting elements
    '''
    global windows, plots, curves
    windows = lpf.create_windows(1)
    plots = lpf.create_plots(windows)
    curves = lpf.create_curves(plots)
    return curves

#====================
# Funtion that allows user to select new Rn, I_max values
#====================

def open_data(filename):
    '''
    
    User selects values for rn and I max using the mouse and the database is 
    updated
    
    :param filename: full filename of _Rn_raw data
    
    
    '''
    # globals needed to communicate with mouse move fcn
    global count, slope_x, slope_y, steps
    global vLines, hLines, slope_plots, x, y, vbs, plots, I_max_plots
    global I_max_x, I_max_y
    global num_JJ, chip_info, chip_name, dev_name, dev_size
    global filename_to_save, web_info, web_link
    global windows, plots, curves
    
    web_link = ("https://nistgov.sharepoint.com/sites/SEG/Shared%20Documents/Forms/AllItems.aspx?viewpath=%2Fsites%2FSEG%2FShared%20Documents%2FForms%2FAllItems%2Easpx&id=%2Fsites%2FSEG%2FShared%20Documents%2FSFQ_circuits%2FMeasurements%2F")
    filename_to_save = filename[0:-8]
    
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
    else:
        pass
    
    # same set up as live plot, create all aspects
    curves = initialization()

    x, y = lpf.create_data(curves)
    vbs = lpf.create_vb(plots) # this is new, need to use viewbox to convert coordinates
    
    # set up window correctly
    windows[0].move(0, 0) # move to other desktop, spyder had been blocking before
    
    windows[0].setWindowState(QtCore.Qt.WindowActive)
    windows[0].raise_()
    
    # this will activate the window (yellow flashing on icon)
    windows[0].activateWindow()

    # find the number of junctions based on the filename
    dev_is_sj = re.findall('SJ', filename)
    # is it a single junction?
    if len(dev_is_sj) ==1:
        # yes
        num_JJ = 1
    else:
        # no
        num_JJ = 400
    
    # get the chip name
    filename_split_up = re.split('/', filename) #first, split by components
    web_info = filename_split_up[-2]
    filename_split_up = filename_split_up[-1] # get the last section
    chip_info = re.split('_Rn_raw', filename_split_up) # split the descrtiption
    chip_info = chip_info[0]
    chip_info_split = re.split('_', chip_info)
    chip_name = chip_info_split[0]
    dev_name = chip_info_split[1]
    dev_size = chip_info_split[2]
    
    print("name: " + chip_name)
    print("dev: " + dev_name)
    print("size: " + dev_size)
    print("num JJ: %s" % num_JJ)
    
    
    # get the data 
    # input file name must use '/', not '\'
    
    filename = re.sub('/', '\\\\', filename) # numPy likes double backslashes
    vals = np.loadtxt(filename) # raw
    I_np = vals[:,0] # in format of np.array
    V_np = vals[:,1]
    I = []
    V = []
    
    
    # convert to python array and plot
    for i in range(0,len(I_np)):
        I.append(I_np[i])
        V.append(V_np[i])
        curves[0].setData(I,V, symbolSize = 5, symbolBrush = 'w')

    # set global vars, to send to mouse click function
    x[0] = I
    y[0] = V
    
    #detect the spacing
    steps = I[1] - I[0]

    # create the cross hairs
    vLines, hLines = lpf.create_lines(plots)

    # initialize count and placeholders
    count = 0
    slope_x = []
    slope_y = []
    I_max_x = []
    I_max_y = []

    # connect the mouse functions
    for i in range(0, len(plots)):
        plots[i].scene().sigMouseClicked.connect(onClick)
    for i in range (0, len(plots)):
        plots[i].scene().sigMouseMoved.connect(MouseMoved)

    # create the blank data to be added to
    slope_plots = lpf.create_slope_plots(plots)
    I_max_plots = lpf.create_slope_plots(plots)
    
    # use title as instructions
    plots[0].setTitle("Select two points to find the Rn")

#====================
# function for movement of mouse, called anytime mouse is moved
#===================
def MouseMoved(evt):
    '''
    Function to track the mouse movement, redraws crosshairs
    '''
    global vbs, curves
    global vLines, hLines
    # get position of mouse
    pos=evt

    # find which window is active
    active_window = 0
    for i in range(0,len(curves)):
        if(curves[i].isActive()):
            active_window = i
            break

    # convert to the scene in widget
    mousePoint = vbs[active_window].mapSceneToView(pos)


    # move the lines 
    vLines[active_window].setPos(mousePoint.x())
    hLines[active_window].setPos(mousePoint.y())

#==================
# function for clicking the mouse, called whenevr the mouse is clicked
#==================
def onClick(event):
    '''
    Response to a mouse click. 
    
    Draws red point on first and second click and slope between them for RN
   
    Third click is a green point for the Imax  
   
    After the third click, the new data is written into the database if the measurement is unique. 
    
    Otherwise, a function to manually select the measurement is printed
   
    Fourth Click clears and resets
    '''
    global count, slope_x, slope_y, steps, slope_labels
    global curves, vbs, x, y, slope_plots, plots
    global I_max_plots, I_max_x, I_max_y, label, label1, label2
    global num_JJ, chip_info, chip_name, dev_name, dev_size, Rn
    global filename_to_save, web_info, web_link

    # finds which window is active
    active_window = 0
    for i in range(0, len(curves)):
        if (curves[i].isActive()):
            active_window = i
            break

    # get position and convert to scene in widget
    pos = event.pos()
    mousePoint = vbs[active_window].mapSceneToView(pos)
    
    index = mousePoint.x()

    # index in the data correspoding to x of click
    index = math.ceil(index /steps) - 1
    index = index + 10
    # Now, do stuff with the clicks
    if index>0 and index<len(y[active_window]): # make sure it's in the range
        count += 1
        if count==4: # fourth click, clear all and reset
            count = 0
            slope_x = []
            slope_y = []
            I_max_x = []
            I_max_y = []
            slope_plots[active_window].clear()
            I_max_plots[active_window].clear()
            plots[active_window].removeItem(label)
            plots[active_window].removeItem(label1)
            plots[active_window].removeItem(label2)
            
            
        elif count==1: # first click, append to slope calc
            slope_x.append(x[active_window][index])
            slope_y.append(y[active_window][index])
            slope_plots[active_window].setData(slope_x, slope_y, symbol='o', symbolBrush='r', pen='r')   
            
        elif count==2: # second click, append and then calc slope
            slope_x.append(x[active_window][index])
            slope_y.append(y[active_window][index])
            slope = (slope_y[1] - slope_y[0])/(slope_x[1] - slope_x[0])
            Rn = slope/num_JJ
            # add red line top visualize
            slope_plots[active_window].setData(slope_x, slope_y, symbol='o', symbolBrush ='r', pen='r')
            
            # add labels
            label = pg.TextItem(text=("Slope: " +str(slope)), color=(0, 0, 0), fill=(255, 0, 0), anchor=(-.5, -.5))
            label1 = pg.TextItem(text=("Rn: " +str(Rn)), color=(0, 0, 0), fill=(255, 0, 0), anchor=(-.5, -2))
            label.setPos(x[active_window][index], y[active_window][index])
            label1.setPos(x[active_window][index], y[active_window][index])
            plots[active_window].addItem(label)
            plots[active_window].addItem(label1)
            
            # set instructions
            plots[active_window].setTitle("Select a point for I_max")

       
        elif count==3: # third click, append to I_max, and save all to database
            I_max_x.append(x[active_window][index])
            I_max_y.append(y[active_window][index])
            Imax = I_max_x[0]
            # add green point to visualize
            I_max_plots[active_window].setData(I_max_x, I_max_y, symbol='o', symbolBrush='g')
            
            # add label
            label2 = pg.TextItem(text=("I max: " +str(Imax)), color=(0, 0, 0), fill=(0, 255, 0), anchor=(-.5, -.5))
            label2.setPos(x[active_window][index], y[active_window][index])
            plots[active_window].addItem(label2)
            plots[active_window].setTitle(chip_info)
            
            # Save Data Here
            # Overwrite the data
            overwrite_Rn_Imax(chip_name, dev_name, Rn, Imax)
            
            # save image

            # if name has already been taken, i.e after first save
            if re.search('.png', filename_to_save) is None:
                filename_to_save = filename_to_save + "_Revised.png"
            print(filename_to_save)
            web_link= web_link + web_info
            print("\n")
            print(web_link)
            exporter = exporters.ImageExporter(plots[active_window].scene())
            exporter.export(filename_to_save)
            print("\nImage Saved")

#=======================
# function to overwrite the values in the database
#=======================
def overwrite_Rn_Imax(chipname, devicename, new_Rn, new_Imax):
    '''
     Sets the Rn and Imax in the database to the new values passed
    
    :param chipname: Target Chip
        
    :param devicename: Target Device
            
    :param new_Rn: New Rn to be Saved
                
    :param new_Imax: New Imax to be Saved
   
    '''
    # connect to database
    imp.reload(d3)
    s = d3.session
    s.commit()
    
    # if there is one result
    try:
        # get the existing measurement
        measurement = s.query(d3.JJ_Measurement).filter_by(chip_name=chipname, device_name=devicename).one()
    
        # get relevant info
        chip = measurement.chip_name
        device = measurement.device_name
        date = measurement.date
        time = measurement.time
        meas_id = measurement.id
        
        print("\nFound device %s on chip %s measured on %s at %s" %(device, chip, date, time))
        
        # tell the user the change 
        old_Rn = measurement.Rn
        old_Imax = measurement.Imax
        print("\nOld Rn: %s"%old_Rn)
        print("\nOld Imax: %s"%old_Imax)
        print("\n")
        print("\nNew Rn: %s"%new_Rn)
        print("\nNew Imax: %s"%new_Imax)

        print("\n")     
        print("Overwriting....")
        
        d3.save_JJ_Measurements_Rn(chip, new_Rn, new_Imax, meas_id, device)

        # commit changes
        s.commit()
        print("Success")
          
    # if more than chip, occur, User input the id
    except sa.orm.exc.MultipleResultsFound:
        measurements = s.query(d3.JJ_Measurement).filter_by(chip_name=chipname, device_name=devicename).all()
        print("\nMultiple results found, use the following function to manually set new data:")
        print("\nCopy and Paste the following, then run:\n")
        print("OR.manual_data_overwrite(\'%s\', \'%s\', %s, %s)\n"%(chipname, devicename, new_Rn, new_Imax))

#=======================
# function to overwrite the database when multiple measurements are found
#=======================
