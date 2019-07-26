# -*- coding: utf-8 -*-
"""
Have functions to generate plots showing data
Created on Tue Sep  5 17:29:30 2017

@author: Soroush
"""

import numpy as np
from pyqtgraph.Qt import QtGui
import sys
import Live_Plot_Functions as lpf
from scipy import stats
import database_v4 as d
import pdb

def initialization(num_plots):
    '''
    Creates all the live plot elements
    
    :param Num_plots: Number of Plots to Initialize
    
    :return: Curves
        
    Called by:
        
        -Plot Generation
        
            -Plot_Ic_RN
        
    '''
    global windows, plots, curves
    windows = lpf.create_windows(num_plots)
    plots = lpf.create_plots(windows)
    curves = lpf.create_curves(plots)
    return curves



def plot_Ic_Rn_from_type(Wafers, Designs):
    """
    
    Plots Ic and RN of a certain design type in popup individual windows
    
    :param Wafers: Target Wafers
    
    :param Designs: Target Designs
   
    :Graphs: Ic for Devices and Rn for Devices
        
    Called By:
        
        - Measurement_GUI_V3
            
            -showData
        
    Calls On:
        
        - Database V4
        
            -Show_chips_from_wafer
            
            -show_devices_from_chip
            
            -show_measurements_from_device
        
        -Plot Generation
        
            -Initialization
        
    """
    # function to plot all Ic's on same window

    global app, windows, plots, curves
    import database_v4 as d

    
    # create app instance
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
    else:
        pass
   
    # create plotting elements
    initialization(len(Wafers)*2)

    for n in range(0, len(Wafers)*2, 2):

        all_chips = d.show_chips_from_wafer(Wafers[n])
        
        if not all_chips:
            print("\nNo chips found, did you enter design name right?")
            for window in windows:
                window.close()
            return -1
        
        chips = []

        for i in range(0, len(all_chips)):
            if all_chips[i].type.name == Designs[n]:
                chips.append(all_chips[i])

        if chips == []:
            print("\nNo chips found, did you enter design name right?")
            for window in windows:
                window.close()
            return -1

        # Ic plot
        plots[n].setLabel('left', 'Ic', 'A')
        plots[n].setLabel('bottom', 'Device', '')

        # Rn Plot
        plots[n+1].setLabel('left', 'Rn', 'A')
        plots[n+1].setLabel('bottom', 'Device', '')

        Ic_curves = []
        Rn_curves = []
        for i in range(0, len(chips)):
            Ic_curve = plots[n].plot()
            Ic_curves.append(Ic_curve)
            
            Rn_curve = plots[n+1].plot()
            Rn_curves.append(Rn_curve)

        # plot
        
        Ic_legend = plots[n].addLegend()
        plots[n].showGrid(x=True, y=True, alpha=0.3)


        Rn_legend = plots[n+1].addLegend()
        plots[n+1].showGrid(x=True, y=True, alpha=0.3)

        num_devices = 20

        for i in range(0, len(chips)):
            devices = d.show_devices_from_chip(chips[i].name)
            devices = devices[:num_devices]
            Ics = []
            Rns = []
            x_axis = []
            x_label = []
            for j in range(0, len(devices)):
                # Query database, returns [Ic, Rn]
                data = d.show_measurements_from_device(chips[i], devices[j])
                Ics.append(data[0])
                Rns.append(data[1])
                x_axis.append(j)
                x_label.append(devices[j].name)
            Ic_curves[i].setData(x_axis, Ics, pen=i, symbol='o', symbolBrush=i)

            Rn_curves[i].setData(x_axis, Rns, pen=i, symbol='o', symbolBrush=i)

            Ic_legend.addItem(Ic_curves[i], chips[i].name)
            Rn_legend.addItem(Rn_curves[i], chips[i].name)
            app.processEvents()
            x_label = dict(enumerate(x_label))

        plots[n].getAxis('bottom').setTicks([x_label.items()])
        plots[n].setTitle("%s Ic"%Wafers[n])
        
        
        plots[n+1].getAxis('bottom').setTicks([x_label.items()])
        plots[n+1].setTitle("%s Rn"%Wafers[n])
        
    return 0


def find_D(name, Chip):
    '''
    Starts at the end of the data directory and looks to match the first two 
    characters of the chip name with the placement in the directory name 
    signifying that the name of the chip starts here
    Ted on 6/12/19: changing the function to not break in 2020 
    Example:
    Name='.../SEG - SFQ_Circuits/D180802-G12_2019-06-27_14-51-13_Temp'
    Chip=D180802-G12
    Output:-36
    How its used:
    Name[-36:]=D180802-G12_2019-06-27_14-51-13_Temp
    '''
    i = -1
    while(1):
        if (abs(i)>len(name)):
            return -1
        if (name[i]==Chip[0]):
            if (name[i+1]==Chip[1]):
                break
        
        i -=1
        
    return i
def plot_from_GUI(app,plot,chipname,devicename,plottype="RN"):
    from urllib.request import urlopen
    import database_v4 as d4

    pick=False
    while not pick:
        if plottype=="RN":
            directories = d.get_data_directory(chipname)
            filemidraw="/RawData_Rn/"
            fileendraw="_Rn_raw.dat"
            filemidcrit="/Rn_values/"
            fileendcrit="_Rn.dat"
            pick=True
        elif plottype=="TC":
            directories = d.get_data_directory(chipname,typeofdata="Crossbar")
            filemidraw="/"
            fileendraw= "_ResistvsTemp_raw.dat"
            filemidcrit=""
            fileendcrit=""
            pick=True
        elif plottype=="LC":
            directories = d.get_data_directory(chipname,typeofdata="Squid")
            filemidraw="/"
            fileendraw= "_Ic_raw.dat"
            filemidcrit="/"
            fileendcrit="_LC_step_raw.dat"
            #filemidcrit=""
            #fileendcrit=""
            pick=True
        elif plottype=="Imax": 
            directories = d.get_data_directory(chipname,typeofdata="Via")
            filemidraw="/"
            fileendraw="_Via_Raw.dat"
            filemidcrit=""
            fileendcrit=""
            pick=True
        elif plottype=="SQRN": #SQUID Rn
            directories = d.get_data_directory(chipname,typeofdata="Squid")
            filemidraw="/"
            fileendraw= "_Ic_raw.dat"
            filemidcrit=""
            fileendcrit=""
            pick=True
        elif plottype=="IC":
            directories = d.get_data_directory(chipname)
            filemidraw="/RawData/"
            fileendraw="_Ic_raw.dat"
            filemidcrit="/Ic_values/"
            fileendcrit="_Ic.dat"
            pick=True
        else:
            print("Hmm, not sure what to do with this")
            plottype=input("Enter a valid input: RN,SQRN,TC,LC,IC or Imax")
            return -1
    if filemidcrit:
        raw_locations=[]
        crit_locations=[]
    else:
        raw_locations=[]
        crit_locations=int(5)
    if directories == -1:
        print("No directories found for chip %s and device %s"%(chipname,devicename))
        return -1
    device = d4.find_device(devicename,output=0)
    if (device==-1):
        print("No device found with name %s" % devicename)
        return -1
    print("Directories for chip %s and device %s"%(chipname,devicename))
    for i,dire in enumerate(directories):
        print("%d : %s"%(i,dire))
    for directory in directories:
        path = "http://132.163.82.9:3000/"
        
        d_location = find_D(directory,chipname)
        
        if (d_location==-1):
            print("No matching chipname found using find_D")
            return -1
        
        path = path + directory[d_location:]
        
        size = device.JJ_radius_nom
        chip_info_name = chipname + "_" + devicename + "_" + (str)(size)

        raw_filename= path + filemidraw + chip_info_name + fileendraw
        
        if " " in raw_filename:   
            raw_filename=raw_filename.replace(" ","_")
        raw_locations.append(raw_filename)    
              
        if type(crit_locations)==int:
            pass
        else:
            crit_filename=path + filemidcrit + chip_info_name + fileendcrit
            crit_locations.append(crit_filename)

    for i,raw in enumerate(raw_locations):
        
        try:   
            raw_file= urlopen(raw, timeout=5) 
            print("Opened file with location %s" % raw)
            goodraw=raw
            goodcrit=crit_locations[i]
        except:        
            print("Unable to open raw data url at %s"% raw)
            pass
        
        if type(crit_locations)==int or crit_locations == []:
                pass
        else:
            try:
                crit_file =urlopen(crit_locations[i],timeout=5)
            except:
                print("Unable to open crit data url at %s"% crit_locations[i])
                pass
    if plottype=="RN":
        try:
            I, V, _ = np.loadtxt(raw_file, unpack=True)

        except:
            print("Problem opening raw file with successful urlopen!")
            return -1
        try:
             Ic,Vc = np.loadtxt(crit_file)
        except:
            print("Problem opening crit file with successful urlopen!")
            pass
        plot.showGrid(x=True, y=True, alpha=0.3)
        plot.setLabel('left','V','V')
        plot.setLabel('bottom', 'I','A')
        
        curve = plot.plot()
        curve.setData(I,V, symbol='o', symbolBrush='w', symbolSize=5)
        
        return I,V, goodraw
    
    elif plottype=="IC":
        try:
            I,V,_ = np.loadtxt(raw_file,unpack=True)
        except:
            print("Problem opening raw file with successful urlopen!")
            return -1
        plot.showGrid(x=True, y=True, alpha=0.3)
        plot.setLabel('left','V','V')
        plot.setLabel('bottom', 'I','A')
        
        curve1 = plot.plot()
        curve2 = plot.plot()
        curve1.setData(I[:int((len(I)+1)/2)],V[:int((len(I)+1)/2)], symbol='o', symbolBrush='w', symbolSize=5)
        curve2.setData(I[int((len(I)+1)/2):],V[int((len(I)+1)/2):], symbol='o', symbolBrush='r', symbolSize=5)
        return I,V, raw_file,goodcrit
    elif plottype=="TC":
       # pdb.set_trace()
        try:
            R,T = np.loadtxt(raw_file, unpack=True)
        
            
        except:
            print("Problem opening raw file with successful urlopen!")
            return -1
     
        tc=d4.show_crossbar_measurements_from_device(chipname,devicename).Tc
       
        plot.showGrid(x=True, y=True, alpha=0.3)
        plot.setLabel('left','R','Ohms')
        plot.setLabel('bottom', 'T','K')
        
        curve = plot.plot()
        curve.setData(T,R, symbol='o', symbolBrush='w', symbolSize=5)
        
        return R,T,tc
    elif plottype=="LC":
        lcI=[]
        lcV=[]
        try:
            fullI,fullV = np.loadtxt(raw_file, unpack=True)
        except Exception as e:
            print("The issue is %s" % e)
            print("Problem reading file!")
            return -1
        try:
             lcI,lcV=np.loadtxt(crit_file,unpack=True)
             critfile=True
        except:
           print("Problem opening LC step file with successful urlopen!")
           critfile=False
           pass    
            
       
     
        
        plot.showGrid(x=True, y=True, alpha=0.3)
        plot.setLabel('bottom','I','Amps')
        plot.setLabel('left', 'V','Volts')
        
        curve1 = plot.plot()
        #Only display data in the first quadrant
        fullI=np.array(fullI)
        fullV=np.array(fullV)
        mask=fullI>0
        fullI=fullI[mask]
        fullV=fullV[mask]
       
        curve1.setData(fullI,fullV, symbol='o', symbolBrush='r', symbolSize=5)
        if critfile:
            curve2 = plot.plot()
            curve2.setData(lcI,lcV, symbol='o', symbolBrush='w', symbolSize=5)
            return fullI,fullV,lcI,lcV
        else:
            return fullI,fullV,[0],[0]
        '''
        from pyqtgraph import exporters
    
        scene=plot.scene()
        
        exporter = exporters.ImageExporter(scene)
        try:
            exporter.export(currpng)
        except:
            print("oh noooo, wrapped object was deleted\n")
        '''
        
    elif plottype=="Imax":
        try:
            I,V,R = np.loadtxt(raw_file, unpack=True)
        
            
        except Exception as e:
            print("The issue is %s" % e)
            print("Problem reading file!")
            return -1
     
        meas=d4.show_via_measurements_from_device(chipname,devicename)
        Imax=meas.Imax
        
        plot.showGrid(x=True, y=True, alpha=0.3)
        plot.setLabel('left','V','Volts')
        plot.setLabel('bottom', 'I','Amps')
        
        curve = plot.plot()
        curve.setData(I,V, symbol='o', symbolBrush='w', symbolSize=5)
        
        return I,V,Imax
    elif plottype=="SQRN":
        try:
            I, V = np.loadtxt(raw_file, unpack=True)

        except:
            print("Problem opening raw file with successful urlopen!")
            return -1

        plot.showGrid(x=True, y=True, alpha=0.3)
        plot.setLabel('left','V','V')
        plot.setLabel('bottom', 'I','A')
        I=np.array(I)
        V=np.array(V)
        mask=I>0
        I=I[mask]
        V=V[mask]
        curve = plot.plot()
        curve.setData(I,V, symbol='o', symbolBrush='w', symbolSize=5)
        
        return I,V,raw_file
    else:
        print("HMMMM, this shouldnt be possible")
        return -1
    

def get_data_direct(Chip,Device):
    import numpy as np
    from urllib.request import urlopen
    import database_v4 as d
    path = "C:/Users/sdk/Downloads/"
    path = "E:/Users/volt.686QVACTEST/National Institute of Standards and Technology (NIST)/SEG - SFQ_Circuits/"
   
    
    directories = d.get_data_directory(Chip)
    rn_locations = []
    raw_locations =[]
    
    if directories == -1:
        return -1

    print(directories)
    for directory in directories:
        path = "http://132.163.82.9:3000/"
        d_location = find_D(directory,Chip)
    
        if (d_location==-1):
            return -1
    
        path = path + directory[d_location:]
    
        device = d.find_device(Device,output=0)
    
        if (device==-1):
            return -1
        size = device.JJ_radius_nom
    
        chip_info_name = Chip + "_" + Device + "_" + (str)(size)
    
        raw_data_filename = path + "/RawData_Rn/" + chip_info_name + "_Rn_raw.dat"
    
        rn_filename = path + "/Rn_values/" + chip_info_name + "_Rn.dat"
        
        rn_locations.append(rn_filename)
        raw_locations.append(raw_data_filename)
        
        
    for i,raw in enumerate(raw_locations):
        print(raw)
        try:   

            raw_file = urlopen(raw, timeout=5)
            Rn_file = urlopen(rn_locations[i], timeout=5)
            worked_raw = raw
            
        except:        
            pass
    try:

        I, V, R = np.loadtxt(raw_file, unpack=True)
    
        Ic,Vc = np.loadtxt(Rn_file)
        
    except:
        print("Problem reading file!")
        return -1
    return I,V,worked_raw
    
def plot_IV_from_GUI(app, plot, Chip, Device):
    """
    Plots an Raw IV curve for a single device
    
    :param app: pyqtgraph construct
    
    :param plot: pyqtgraph constuct
    
    :param Chip: Target Chip
    
    :param Device: Target Device 
    
    
    :Graphs: Voltage on y axis and Current on x axis
   
    Called By:
    
        -Measurement_GUI_V3-Plot
    
    Calls on:
    
        -Database V4
        
            -Show_devices_from_chip
            
            -show_measurements_from_device

    """
    import numpy as np
    from urllib.request import urlopen
    import database_v4 as d
    import pyqtgraph as pg
    path = "C:/Users/sdk/Downloads/"
    path = "E:/Users/volt.686QVACTEST/National Institute of Standards and Technology (NIST)/SEG - SFQ_Circuits/"
   
    
    directories = d.get_data_directory(Chip)
    ic_locatoins = []
    raw_locations =[]
    
    if directories == -1:
        return -1

    for directory in directories:
        path = "http://132.163.82.9:3000/"
        d_location = find_D(directory, Chip)
    
        if (d_location==-1):
            return -1
    
        path = path + directory[d_location:]
        
        
        chip = d.find_chip(Chip)
        device = d.find_device(Device,output=0, optional_designid=chip.design_id)    
        if (device==-1):
            return -1
        size = device.JJ_radius_nom
    
        chip_info_name = Chip + "_" + Device + "_" + (str)(size)
    
        raw_data_filename = path + "/RawData/" + chip_info_name + "_Ic_raw.dat"
    
        ic_filename = path + "/Ic_values/" + chip_info_name + "_Ic.dat"
        
        ic_locatoins.append(ic_filename)
        raw_locations.append(raw_data_filename)
        

    for i,raw in enumerate(raw_locations):
        try:   
    
            raw_file = urlopen(raw, timeout=5)
            Ic_file = urlopen(ic_locatoins[i], timeout=5)            
            
        except:   
            pass
      
    try:
        I, V, R = np.loadtxt(raw_file, unpack=True)
    
        Ic,Vc = np.loadtxt(Ic_file)
    except:
        print("Problem reading file")
        return -1


    plot.showGrid(x=True, y=True, alpha=0.3)
    plot.setLabel('left','V','V')
    plot.setLabel('bottom', 'I','A')
    plot.getAxis('bottom').setTicks(None)
    
    curve = plot.plot()
    curve.setData(I,V, symbol='o', symbolBrush='w', symbolSize=5)
    
    
    for n1 in range(0,len(Ic)):
            if n1 < 2:
                type_of_current = "I"+str(n1)
                label = pg.TextItem(text="", color=(0, 0, 0), fill=(0, 255, 255), anchor=(0, -1))
            else:
                type_of_current = "I"+str(n1)
                label = pg.TextItem(text="", color=(0, 0, 0), fill=(0, 255, 255), anchor=(0, 2))

            I_c = type_of_current+':(' + '{:.2E}'.format(Ic[n1]) + ','+ '{:.2E}'.format(Vc[n1]) + ')'
            label.setText(I_c)
            label.setPos(Ic[n1], Vc[n1])
            plot.addItem(label)
            new_curve = plot.plot()
            new_curve.setData(Ic[n1:n1+1], Vc[n1:n1+1], symbol='o', symbolBrush='c', symbolSize=10)
    
    app.processEvents()
      

def plot_product_device_from_GUI(app, plot, Chip):
    """
    Plots Ic*RN for each Device on a Chip
   
    :param app: pyqtgraph construct
    
    :param plot: pyqtgraph constuct
    
    :param Chip: Target Chip
    
    :param dev_type: Device Type
    
    
    :return: m- slope of trendline
    
    :return: b- intercept of trendline
    
    :return: r2- R^2 fit (number between 0 and 1), gives linearity of trendline
   
    :Graphs: Ic*RN product on y axis and device on x axis
    
    Called By:
   
        -Measurement_GUI_V3-productReport
    
    Calls On:
   
        -Database V4
            
            -show_devices_from_chip
            
            -show_measurements_from_device
    """
    
    import database_v4 as d

    plot.clear()
    
    chip = d.find_chip(Chip)
    
    if not chip:
        return -1
    
    devices = d.show_devices_from_chip(chip.id)    
        
    curve = plot.plot()
    

    ic_rn_product = []
    
    x_axis = []
    x_label = []
    for j in range(0, len(devices)):
        # Query database, returns [Ic, Rn]
        data = d.show_measurements_from_device(chip, devices[j])
        ic_rn_product.append(data[0]*data[1])
            
        x_axis.append(j)
        x_label.append(devices[j].name)

        curve.setData(x_axis, ic_rn_product, pen=None, symbol='o', symbolSize=5, symbolBrush='w')
   
    x_label = dict(enumerate(x_label))

    plot.getAxis('bottom').setTicks([x_label.items()])
    plot.showGrid(x=True, y=True, alpha=0.3)
    plot.setLabel('left','Ic*Rn','A*Ohms')
    plot.setLabel('bottom', 'Device')    

def plot_Ic_radius_from_GUI(app, plot, Chip, dev_type):
    """
    Plots Square Root of IC vs Device Radius
    
    :param app: pyqtgraph construct
    
    :param plot: pyqtgraph constuct
    
    :param Chip: Target Chip
    
    :param Device: Target Device
    
    :return: m- slope of trendline
    
    :return: b- intercept of trendline
    
    :return: r2- R^2 fit (number between 0 and 1), gives linearity of trendline
   
    :Graphs: sqrt(IC) on y axis and Device Radius on x axis
    

    Called By:
   
        -Measurement_GUI_V3- icReport

    Calls On:
   
        -Database V4
            
            -show_devices_from_chip
            
            -show_measurements_from_device
    """
    
    import database_v4 as d
    from math import sqrt
    
    plot.clear()
    
    
    chip = d.find_chip(Chip)
    
    if not chip:
        return -1
    
    unfiltered_devices = d.show_devices_from_chip(chip.id)
    devices = []
    
    for dev in unfiltered_devices:
        if dev.device_type == dev_type:
            devices.append(dev)
    
    if not devices:
        return -1
    
    curve = plot.plot()
    curve2=plot.plot()
    #curve.showButtons()
    
    radii = []
    root_ic = []
    zero_radii=[]
    zero_ic=[]

    for dev in devices:
        radii.append(dev.JJ_radius_nom*1e-06)
        ic = d.show_measurements_from_device(chip,dev)[0]
        root_ic.append(sqrt(ic))
    # linear fit, remove zero's
    for index,element in enumerate(root_ic):
        if element == 0:
            zero_radii.append(radii[index])
            zero_ic.append(root_ic[index])
            del root_ic[index]
            del radii[index]        
        
        
    plot.showGrid(x=True, y=True, alpha=0.3)
    plot.setLabel('left','Ic','A')
    plot.setLabel('bottom', 'Device Radius','m')
    
    curve.setData(radii, root_ic, symbol='o', symbolBrush='w', symbolSize=5, pen=None)
    curve2.setData(zero_radii,zero_ic,symbol='o',symbolBrush='r',symbolSize=5,pen=None)
         
    import numpy as np
    m,b = np.polyfit(radii, root_ic, 1)
    a,b,r,p,std_err = stats.linregress(radii,root_ic)
    r2=r**2
    lin_x = []
    lin_y = []
    lin_curve = plot.plot()
    for i in np.arange(0,radii[-1]*2,(radii[-1]*2)/100):
        lin_x.append(i)
        lin_y.append(m*i + b)
        lin_curve.setData(lin_x,lin_y)
        
    plot.getAxis('bottom').setTicks(None)
    
    return m,b,r2

def plot_Rn_radius_from_GUI(app, plot, Chip, dev_type):
    """
    Plots 1/RN vs Device Radius
    
    :param app: pyqtgraph construct
    
    :param plot: pyqtgraph constuct
    
    :param Chip: Target Chip
    
    :param dev_type: Device Type
    
    :return: m- slope of trendline
    
    :return: b- intercept of trendline
    
    :return: r2- R^2 fit (number between 0 and 1), gives linearity of trendline
   
    :Graphs:  1/RN on y axis and Device Radius on x axis
    
    Called By:
   
        -Measurement_GUI_V3-rnReport
    
    Calls On:
   
        -Database V4
            
            -show_devices_from_chip
            
            -show_measurements_from_device
        
    """
    
    
    import database_v4 as d
    from math import sqrt
    
    plot.clear()
    
    chip = d.find_chip(Chip)
    
    if not chip:
        return -1
    
    unfiltered_devices = d.show_devices_from_chip(chip.id)
    devices = []
    
    for dev in unfiltered_devices:
        if dev.device_type == dev_type:
            devices.append(dev)
    
    if not devices:
        return -1

    curve = plot.plot()
    curve2=plot.plot()
    
   # curve.showButtons()
    
    radii = []
    i_root_rn = []
    zero_radii=[]
    zero_rn=[]
    
    for dev in devices:
        radii.append(dev.JJ_radius_nom*1e-06)
        rn = d.show_measurements_from_device(chip,dev)[1]
        print(rn)
        if rn<=0:
            i_root_rn.append(0)
            
        else:
            i_root_rn.append(1/sqrt(rn))
     # linear fit, remove zero's
    for index,element in enumerate(i_root_rn):
        if element == 0:
            zero_radii.append(radii[index])
            zero_rn.append(i_root_rn[index])
            del i_root_rn[index]
            del radii[index]
    
        
    plot.showGrid(x=True, y=True, alpha=0.3)
    plot.setLabel('left','1/Rn','Ohms')
    plot.setLabel('bottom', 'Device Radius','m')
    plot.getAxis('bottom').setTicks(None)
    curve.setData(radii, i_root_rn, symbol='o', symbolBrush='w', symbolSize=5, pen=None)
    curve2.setData(zero_radii,zero_rn,symbol='o',symbolBrush='r',symbolSize=5,pen=None)

    import numpy as np
    m,b = np.polyfit(radii, i_root_rn, 1)  
    a,c,r,p,std_err = stats.linregress(radii,i_root_rn)
    r2=r**2
    lin_x = []
    lin_y = []
    lin_curve = plot.plot()
    for i in np.arange(0,radii[-1]*2,(radii[-1]*2)/100):
        lin_x.append(i)
        lin_y.append(m*i + b)
        lin_curve.setData(lin_x,lin_y)
        
    return m,b,r2
    
def plot_Ic_Rn_from_GUI(app, plot, Wafer):
    '''
    
    Pass in wafer and design name, will generate plot for Ic of all devices
    
    :param app: pyqtgraph construct
    
    :param plot: pyqtgraph constuct
    
    :param Wafer: Target Wafer
    
    :Graphs: IC vs Device for each chip overlayed
    
    Called By:
        
        -Measurement_GUI_v3 plot()
        
    Calls on:
        
        -Database V4
            
            -show_devices_from_chip
            
            -show_measurements_from_device
            
            -show_chips_from_wafer
    '''
    import database_v4 as d
    plot.clear()
    
    all_chips = d.show_chips_from_wafer(Wafer)
    
    if not all_chips:
        print("\nNo chips found, did you enter design name right?")

        return -1
    
    chips = []

    for i in range(0, len(all_chips)):
        chips.append(all_chips[i])

    if chips == []:
        print("\nNo chips found, did you enter design name right?")
        return -1
    
    # Ic plot
    plot.setLabel('left', 'Ic', 'A')
    plot.setLabel('bottom', 'Device', '')

    Ic_curves = []

    for i in range(0, len(chips)):
        Ic_curve = plot.plot()
        #Ic_curve.showButtons()
        Ic_curves.append(Ic_curve)
        
    # plot
    Ic_legend = plot.addLegend()
    plot.showGrid(x=True, y=True, alpha=0.3)
    
    num_devices = 20

    for i in range(0, len(chips)):
        devices = d.show_devices_from_chip(chips[i].name)
        devices = devices[:num_devices]
        Ics = []
    
        x_axis = []
        x_label = []
        for j in range(0, len(devices)):
            # Query database, returns [Ic, Rn]
            data = d.show_measurements_from_device(chips[i], devices[j])
            Ics.append(data[0])
            
            x_axis.append(j)
            x_label.append(devices[j].name)

        Ic_curves[i].setData(x_axis, Ics, pen=i, symbol='o', symbolBrush=i)
        Ic_legend.addItem(Ic_curves[i], chips[i].name)
        
        app.processEvents()
        x_label = dict(enumerate(x_label))
        
    plot.getAxis('bottom').setTicks([x_label.items()])
    plot.setTitle("%s Ic"%Wafer)
    
    return 0
###############################################
#Depreciated Functions
###############################################       

'''
def heat_map(Wafer):
    
    Can only run on Soroush's computer, need Plotly. Generates an HTML heat map 
    of a wafer's Jc. Check Plot_Generation folder in volt for HTML files
    
    import plotly as py

    import plotly.graph_objs as go
    import database_v4 as d
    import imp
    
    imp.reload(d)

    
    all_chips = d.show_chips_from_wafer(Wafer)
    
    
    # create blank matrix of all 0's
    Jc_data = []
    
    for i in range (0,11):
        rows = []
        for j in range (0,11):
            rows.append(0)
        Jc_data.append(rows)
            
    
    num_devcices = 20
    
    for i in range(0, len(all_chips)):
        chip = all_chips[i]
        
        if chip.type.name == 'PCMS2A':
            # find the location, in row, col form
            location = chip.location
            row = ord(location[0]) - 65
            row = abs(row)
            col = int(location[1:]) - 1
            
            print(row, " ", col)
            
            devices = d.show_devices_from_chip(chip.name)
            devices = devices[:num_devcices]
            
            Jc_total = 0
            for j in range (0,len(devices)):
                meas = d.show_measurements_from_device(chip, devices[i])
                Jc = d.calc_Jc(meas[0],devices[i].JJ_radius_nom*1e-06)/1e07
                
                Jc_total = Jc_total + Jc
                
            Jc_avg = Jc_total/len(devices)
            
            Jc_data[row][col] = Jc_avg
        

    print(Jc_data)
    x = ['1', '2', '3', '4', '5', '6','7', '8',
                            '9', '10', '11']
    
    y = ['A','B','C', 'D', 'E', 'F','G', 'H',
                            'I', 'J', 'K']
    trace = go.Heatmap(y = y, x = x, z = Jc_data,
                        xgap = 10, ygap = 10)
    data = [trace]
    import plotly.figure_factory as ff
    fig = ff.create_annotated_heatmap(Jc_data, x=x, y=y)

    py.offline.plot(data, filename='Z:/JPulecio/Code/Python/Resistance_Measurements/Plot_Generation/%s_HeatMap_final.html'%Wafer, auto_open=False)
    



    def plot_LC_from_GUI(app,plot,chipname,devicename):
    from urllib.request import urlopen
    path = "E:/Users/volt.686QVACTEST/National Institute of Standards and Technology (NIST)/SEG - SFQ_Circuits/"

    
    directories = d.get_data_directory(chipname,typeofdata="Squid")
    lc_locations =[]
    full_locations=[]
    pngs=[]
    
    if directories == -1:
        return -1

    print(directories)
    for directory in directories:
        path = "http://132.163.82.9:3000/"
        
        d_location = find_D(directory,chipname)
        if (d_location==-1):
            return -1
        path = path + directory[d_location:]
    
        device = d.find_device(devicename,output=0)
        if (device==-1):
            return -1
        
        size = device.JJ_radius_nom
        chip_info_name = chipname + "_" + devicename + "_" + (str)(size)

        lc_data_filename = path + "/" + chip_info_name + "_Ic_raw.dat"
        full_data_filename=path + "/" + chip_info_name + "_LC_step_raw.dat"
        png_filename=path + "/" + chip_info_name + "full_sweep_with_lc.png"
        lc_locations.append(lc_data_filename)
        full_locations.append(full_data_filename)
        pngs.append(png_filename)
        

    for i,raw in enumerate(lc_locations):
        
        try:   

            lc_raw_file = urlopen(raw, timeout=5)    
            full_raw_file=urlopen(full_locations[i],timeout=5)
            currpng=pngs[i]
        except:        
            print("Error here")
            print(raw)
            pass
        
    try:
        fullI,fullV = np.loadtxt(full_raw_file, unpack=True)
        lcI,lcV=np.loadtxt(lc_raw_file,unpack=True)
        
        
    except Exception as e:
        print("The issue is %s" % e)
        print("Problem reading file!")
        return -1
 
    
    plot.showGrid(x=True, y=True, alpha=0.3)
    plot.setLabel('bottom','I','Amps')
    plot.setLabel('left', 'V','Volts')
    
    curve1 = plot.plot()
    curve2 = plot.plot()
    curve1.setData(lcI,lcV, symbol='o', symbolBrush='w', symbolSize=5)
    curve2.setData(fullI,fullV, symbol='o', symbolBrush='r', symbolSize=5)
    from pyqtgraph import exporters

    scene=plot.scene()

    exporter = exporters.ImageExporter(scene)
    try:
        exporter.export(currpng)
    except:
        print("oh noooo, wrapped object was deleted\n")

    return fullI,fullV,lcI,lcV
def plot_Imax_from_GUI(app,plot,Chip,Device):
    from urllib.request import urlopen
    import database_v4 as d4

   
    path = "E:/Users/volt.686QVACTEST/National Institute of Standards and Technology (NIST)/SEG - SFQ_Circuits/"

    
    directories = d.get_data_directory(Chip,typeofdata="Via")
    raw_locations =[]
    
    if directories == -1:
        return -1

    print(directories)
    for directory in directories:
        path = "http://132.163.82.9:3000/"
        
        d_location = find_D(directory,Chip)
        if (d_location==-1):
            return -1
        path = path + directory[d_location:]
    
        device = d4.find_device(Device,output=0)
        if (device==-1):
            return -1
        
        size = device.JJ_radius_nom
        chip_info_name = Chip + "_" + Device + "_" + (str)(size)
        raw_data_filename = path + "/" + chip_info_name + "_Via_Raw.dat"

    
        raw_locations.append(raw_data_filename)
        

    for i,raw in enumerate(raw_locations):
        
        try:   

            raw_file = urlopen(raw, timeout=5)    
            
        except:        
            print("Error here")
            print(raw)
            raw_file=raw
            pass
        
    try:
        I,V,R = np.loadtxt(raw_file, unpack=True)
    
        
    except Exception as e:
        print("The issue is %s" % e)
        print("Problem reading file!")
        return -1
 
    meas=d4.show_via_measurements_from_device(Chip,Device)
    Imax=meas.Imax
    
    plot.showGrid(x=True, y=True, alpha=0.3)
    plot.setLabel('left','I','Amps')
    plot.setLabel('bottom', 'V','Volts')
    
    curve = plot.plot()
    curve.setData(I,V, symbol='o', symbolBrush='w', symbolSize=5)
    
    return I,V,Imax
def plot_tc_from_GUI(app,plot,Chip,Device):
    from urllib.request import urlopen
    import database_v4 as d4

    path = "E:/Users/volt.686QVACTEST/National Institute of Standards and Technology (NIST)/SEG - SFQ_Circuits/"

    
    directories = d.get_data_directory(Chip,typeofdata="CrossBar")
    raw_locations =[]
    
    if directories == -1:
        return -1

    print(directories)
    for directory in directories:
        path = "http://132.163.82.9:3000/"
        
        d_location = find_D(directory,Chip)
        if (d_location==-1):
            return -1
        path = path + directory[d_location:]
    
        device = d4.find_device(Device,output=0)
        if (device==-1):
            return -1
        
        size = device.JJ_radius_nom
        chip_info_name = Chip + "_" + Device + "_" + (str)(size)
        raw_data_filename = path + "/" +chip_info_name + "_ResistvsTemp_raw.dat"
        raw_data_filename = raw_data_filename.replace(" ","_")
        if "Temp" in raw_data_filename:
            raw_locations.append(raw_data_filename)
        

    for i,raw in enumerate(raw_locations):
        print(raw)
        try:   

            raw_file = urlopen(raw, timeout=5)    
            
        except:        
            pass
    try:
        R,T = np.loadtxt(raw_file, unpack=True)
    
        
    except:
        print("Problem reading file!")
        return -1
 
    tc=d4.show_crossbar_measurements_from_device(Chip,Device).Tc
   
    plot.showGrid(x=True, y=True, alpha=0.3)
    plot.setLabel('left','R','Ohms')
    plot.setLabel('bottom', 'T','K')
    
    curve = plot.plot()
    curve.setData(T,R, symbol='o', symbolBrush='w', symbolSize=5)
    
    return R,T,tc
def get_data_direct(Chip,Device):
    import numpy as np
    from urllib.request import urlopen
    import database_v4 as d
    path = "C:/Users/sdk/Downloads/"
    path = "E:/Users/volt.686QVACTEST/National Institute of Standards and Technology (NIST)/SEG - SFQ_Circuits/"
   
    
    directories = d.get_data_directory(Chip)
    rn_locations = []
    raw_locations =[]
    
    if directories == -1:
        return -1

    print(directories)
    for directory in directories:
        path = "http://132.163.82.9:3000/"
        d_location = find_D(directory,Chip)
    
        if (d_location==-1):
            return -1
    
        path = path + directory[d_location:]
    
        device = d.find_device(Device,output=0)
    
        if (device==-1):
            return -1
        size = device.JJ_radius_nom
    
        chip_info_name = Chip + "_" + Device + "_" + (str)(size)
    
        raw_data_filename = path + "/RawData_Rn/" + chip_info_name + "_Rn_raw.dat"
    
        rn_filename = path + "/Rn_values/" + chip_info_name + "_Rn.dat"
        
        rn_locations.append(rn_filename)
        raw_locations.append(raw_data_filename)
        
        
    for i,raw in enumerate(raw_locations):
        print(raw)
        try:   

            raw_file = urlopen(raw, timeout=5)
            Rn_file = urlopen(rn_locations[i], timeout=5)
            worked_raw = raw
            
        except:        
            pass
    try:

        I, V, R = np.loadtxt(raw_file, unpack=True)
    
        Ic,Vc = np.loadtxt(Rn_file)
        
    except:
        print("Problem reading file!")
        return -1
    return I,V,worked_raw
def plot_rn_from_GUI(app, plot, Chip, Device):
    """
    
    Plots Ic*RN for each Device on a Chip
   
    :param app: pyqtgraph construct
    
    :param plot: pyqtgraph constuct
    
    :param Chip: Target Chip
    
    :param Device: Target Device
    
    :return: I- Array of Current Data
   
    :return: V- Array of Voltage Data
    
    :return: worked_raw- Number of raw_location files??
    
    :Graphs: Voltage on y axis and Current on x axis
    
    Called By:
    
        -Measurement_GUI_V3-plotRN
    
    Calls On:
        
        -Database V4
            
            -show_devices_from_chip
            
            -show_measurements_from_device
        
    """
    import numpy as np
    from urllib.request import urlopen
    import database_v4 as d

    path = "C:/Users/sdk/Downloads/"
    path = "E:/Users/volt.686QVACTEST/National Institute of Standards and Technology (NIST)/SEG - SFQ_Circuits/"
   
    
    directories = d.get_data_directory(Chip)
    rn_locations = []
    raw_locations =[]
    
    if directories == -1:
        print("No Directories")
        return -1

    #print(directories)
    for directory in directories:
        path = "http://132.163.82.9:3000/"
        d_location = find_D(directory,Chip)
    
        if (d_location==-1):
            print("find_D failed")
            return -1
    
        path = path + directory[d_location:]
    
        device = d.find_device(Device,output=0)
    
        if (device==-1):
            print("find_device failed")
            return -1
        size = device.JJ_radius_nom
    
        chip_info_name = Chip + "_" + Device + "_" + (str)(size)
    
        raw_data_filename = path + "/RawData_Rn/" + chip_info_name + "_Rn_raw.dat"
    
        rn_filename = path + "/Rn_values/" + chip_info_name + "_Rn.dat"
        
        rn_locations.append(rn_filename)
        raw_locations.append(raw_data_filename)
        
        
    for i,raw in enumerate(raw_locations):
        print(raw)
        try:   

            raw_file = urlopen(raw, timeout=5)
            Rn_file = urlopen(rn_locations[i], timeout=5)
            worked_raw = raw
            
        except:        
            pass
    try:

        I, V, R = np.loadtxt(raw_file, unpack=True)
    
        Ic,Vc = np.loadtxt(Rn_file)
        
    except:
        print("Problem reading file!")
        return -1


    plot.showGrid(x=True, y=True, alpha=0.3)
    plot.setLabel('left','V','V')
    plot.setLabel('bottom', 'I','A')
    
    curve = plot.plot()
    curve.setData(I,V, symbol='o', symbolBrush='w', symbolSize=5)
    
    return I,V, worked_raw
'''


