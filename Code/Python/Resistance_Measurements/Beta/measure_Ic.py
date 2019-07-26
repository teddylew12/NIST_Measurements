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


#===================
# measure functions
#===================
# create live plotting elements 

def initialization(num_plots):
    '''
    Creates all the live plot elements
    '''
    global windows, plots, curves, current_point
    windows = lpf.create_windows(num_plots)
    plots = lpf.create_plots(windows)
    curves = lpf.create_curves(plots)
    current_point = lpf.create_current_point(plots)
    return curves
        
# save all the end


# save throughout
def get_Ic_Iret_and_save(folder, folder_link, chip, devices,Jc, optionalic=0):
    '''
    Inputs is in format: [[cards], [channel1,channel2], [Imin,Imax], [steps], 
    [num_sweeps]]
    
    Chip must be the name of the chip. Devices should be in an array
    Folder_link is the web link to the folder
    

    :param Folder: Target folder for data to be saved
  
    :param Chip: Target Chip
   
    :param Devices: Devices on Target Chip
        
    :return: array of Ic(pos/neg) and Iret(pos/neg)
    
    :return: array of measurement ids (to pass to measure_Rn)
    
    :Graph: Overlays critical points in cyan on top of raw IV curve
    
    Called By: 
        
        -Measurement Functions
         
            -Measure_PCM_Chip_Cold
        
            -Measure_JJs_Ic
    
    Calls On:
        -automate_channel_IV_live
        
        -find_max_y_change_half_sweep
        
        -find_max_y_change
        
        -save_data_live
        
        -save_ic_data
        
        -save_JJ_Measurements_Ic
    '''
    global app
    global windows, plots, curves
    global my_exporters, current_point
    # get variables
    print("*******************")
    print(devices)
    inputs = inpfunc.format_input_Ic_Ir_devices(devices, Jc)
    cards = inputs[0]
    channels = inputs[1]
    currents = inputs[2]
    steps = inputs[3]
    sweeps = inputs[4]

    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
    else:
        pass

    num_plots = len(devices)
    print("num plots: %d" %num_plots)

    # create windows, plots, and curves
    curves = initialization(num_plots)

    # we need two indexes, one for pairs, one for normal
    index_pairs = 0
    index = 0
    
    return_measurements = [] # the array that we will return
    meas_ids = [] # the array of measurment ids we will return

    my_exporters = [] # array to hold exporters (hopefully solves problem of C object being deleted)
    # create exporters
    for i in range(0, num_plots):
        exporter = exporters.ImageExporter(plots[i].scene())
        my_exporters.append(exporter)
    
    # take all the sweeps
    for i in range(0,num_plots):
        print("Begin Device %s sweep" %(i))
        # get two channels and two current limits that are needed
        my_channels = []
        my_currents = []
        my_channels.append(channels[index_pairs])
        my_channels.append(channels[index_pairs+1])
        
        # edit 7/19/18
        my_cards = []
        my_cards.append(cards[index_pairs])
        my_cards.append(cards[index_pairs+1])
        
        my_currents.append(currents[index_pairs])
        my_currents.append(currents[index_pairs+1])

        name = create_name(chip, devices[i]) # create the name
        plots[i].setTitle(name) # set title to name
        
        # show the grid
      

        # bring current window to focus        
        windows[i].move(-900, 0) # move to other desktop, spyder had been blocking before
        windows[i].setWindowState(QtCore.Qt.WindowActive)
        windows[i].raise_()
        
        # this will activate the window (yellow flashing on icon)
        windows[i].activateWindow()
        extra_res=0
        if "S1_1.5"  in devices[i].name  and devices[i].design_id[0].name =="PCM3A":
            extra_res=138.19 #originally 137.35
        if "A3_3.9" in devices[i].name and devices[i].design_id[0].name == "PCM3A":
            extra_res=138.37 #originally 138.33

        
        if optionalic !=0: # or design ==4: # higher precision around Ic, design is SingleJJ
            I,V,R = iv.automate_channel_IV_live(app, curves[index], current_point[index], my_cards, my_channels, my_currents, steps[index], sweeps[index], optionalic=optionalic,extra_res=extra_res)
#           
        # sweep the current device
        else: # optional value was not passed in
            I,V,R = iv.automate_channel_IV_live(app, curves[index], current_point[index], my_cards, my_channels, my_currents, steps[index], sweeps[index],extra_res=extra_res)
    
        if I==0 and V==0 and R==0:
            return 0,0

        num_JJ = devices[i].num_JJs # get the number of JJs for this dev
        print("num JJ: %s" %num_JJ)
        
        if optionalic != 0: # or design==4:
            critical_currents = iv.find_max_y_change_half_sweep(I,V, num_JJ)
        elif devices[i].name == 'S1_1.5' or devices[i].name == 'A3_3.9':
            critical_currents = iv.find_max_y_change(I,V, num_JJ,envelope = 50e-06)
        else:
            critical_currents = iv.find_max_y_change(I,V, num_JJ)
            
        # Plotting Critical Currents

        # arrays that will be saved
        critical_currents_save_I = []
        critical_currents_save_V = []

        # setting labels
        for n1 in range(0,len(critical_currents)):
            if n1 < 2:
                type_of_current = "I"+str(n1)
                label = pg.TextItem(text="", color=(0, 0, 0), fill=(0, 255, 255), anchor=(0, -1))

            else:
                type_of_current = "I"+str(n1)
                label = pg.TextItem(text="", color=(0, 0, 0), fill=(0, 255, 255), anchor=(0, 2))

            I_c = type_of_current+':(' + '{:.2E}'.format(I[critical_currents[n1]]) + ','+ '{:.2E}'.format(V[critical_currents[n1]]) + ')'
            label.setText(I_c)
            label.setPos(I[critical_currents[n1]], V[critical_currents[n1]])
            graph = plots[i]
            graph.addItem(label)
            current_toplot = critical_currents[n1]
            new_curve = plots[i].plot()
            new_curve.setData(I[current_toplot:current_toplot+1], V[current_toplot:current_toplot+1], symbol='o', symbolBrush='c', symbolSize=10)

            critical_currents_save_I.append(I[current_toplot])
            critical_currents_save_V.append(V[current_toplot])
              
        # Saving locally
        filename = (folder + name)
        print(filename)
        create_dir(filename)
       
                
        sub_folder = "/RawData"
        filename = (folder+sub_folder+name+"_Ic_raw.dat")
        create_dir(filename) # function to create dir if doesn't exist
        print(filename)
        iv.save_data_live(I,V,R,(folder+sub_folder+name+"_Ic_raw.dat")) # save the raw data
        
        sub_folder = "/Ic_values"
        filename = (folder+sub_folder+name)
        print(filename)
        create_dir(filename) # function to create dir if doesn't exist
        save_ic_data(critical_currents_save_I, critical_currents_save_V,(folder+sub_folder+name)) # save the important data
        
        sub_folder = "/Graphs"
        filename = (folder + sub_folder + name + "_Ic.png")
        print(filename)
        create_dir(filename) # function to create dir if doesn't exist
        
        return_measurements.append(critical_currents_save_I) # append to the final return array

       # Save to database
        meas_id = d.save_JJ_Measurements_Ic(chip, critical_currents_save_I, folder_link, devices[i])
        
        meas_ids.append(meas_id)
    
        try:
            my_exporters[i].export(filename) # export the graph
        except:
            sys.stdout = sys.__stdout__
            print("Oh noooooo wrapped object was deleted\n")
            
        
        # repeat
        index = index + 1
        index_pairs = index_pairs + 2

        app.processEvents()
        print("End Device %s sweep\n" %(i))
    
    return return_measurements, meas_ids

#=================
# functions used
#=================

def create_name(chip, device):
    '''
    Takes in a chip and a device and creates the name with format: 
    chip_device_size
    '''
    chip = str(chip)
    dev_name = str(device.name)
    dev_size = str(device.JJ_radius_nom)
    return "/" + chip + "_" + dev_name + "_" + dev_size

def create_dir(filepath):
    '''
    Creates the directory of the path given. If it already exists,
    it does nothing
    '''
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.mkdir(directory)
        
def save_ic_data(crit_I, crit_V, name):
    '''
    Save the critical values in a text file
    '''
    column = len(crit_I)
    data = np.zeros((2, column))
    data[0] = crit_I
    data[1] = crit_V
    name = name + "_Ic.dat"
    np.savetxt(name, data, header = 'row1: Critical Current, row2: Voltage at Critical Current\nOrder: I0, I1')