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
import numpy as np
import time
#from pygame import mixer


#app = QtGui.QApplication([])

#=================================
#Global variables
#=================================
#address_I = 12
address_I_yoko_GS200 = 1  #for IV
address_I_yoko_GS200b = 2 #for flux
address_V = 25
nplc = 1

globalVrange = '0.002'

VDwellTime = 0
Irange = 10e-03
Fluxrange = 2e-03
compliance_voltage = 10.

#global variables
title = "Voltage over time"
xlabel = "sample"
ylabel = "V"


#=================================
#Function definitions
#=================================  
def turn_current_off():
    CurrentSource = vf.get_current()
    vf.set_current_fast_yoko_GS200(CurrentSource, 0)
    

def sweep_current(I_min, I_max, step, *args):
    """
    Inputs are min and max current for sweep, steps, card and channels for switch
    Returns an array with current steps, measured voltages, and calculated resistances
    
    """
    global globalVrange 
    
    downswitch = args[0]
    print(globalVrange)    
    ##VARIABLE DECLARATIONS##
    #Going to use lists to start with for flexibility, even though slower than arrays
    I_values = []
    V_values = []
    
    
    ##INITIALIZATION OF HARDWARE##    
    Voltmeter = vf.get_voltage(address_V)
    CurrentSource= vf.get_current(address_I_yoko_GS200)
    vf.intialize_current_yoko_GS200(CurrentSource, Irange, compliance_voltage)

    time.sleep(0.2)

    vf.intialize_voltage(Voltmeter, nplc, globalVrange)
    offset = vf.read_voltage_fast(Voltmeter, VDwellTime)
    
    ##CURRENT SWEEPS##
    #Sweep Current up
    print('Starting sweep up')
    for I in np.arange(I_min, I_max, step):
        vf.set_current_fast_yoko_GS200(CurrentSource, I)
        V = vf.read_voltage_fast(Voltmeter, VDwellTime)
        I_values.append(I)                
        V_values.append(V)
            
        #print('%e '%I,end=" ")
        
    if downswitch :
        print('Starting sweep down')
        #Sweep Current down
        for I in np.arange(I_max-step, I_min, -step):
            vf.set_current_fast_yoko_GS200(CurrentSource, I)
            V = vf.read_voltage_fast(Voltmeter, VDwellTime)
            I_values.append(I)                
            V_values.append(V)
            
         #   print('%e'%I,end=" ")
        
    V_values=np.array(V_values) 
    V_values=V_values-offset
    #SHUT IT DOWN!##
    print("Exited current sweep")
    vf.set_current_fast_yoko_GS200(CurrentSource, 0)
    time.sleep(.1)
    return np.array(I_values), V_values
# 
#def sweep_current2(I_min, I_max, step, *args):
#    """
#    Inputs are min and max current for sweep, steps, card and channels for switch
#    Returns an array with current steps, measured voltages, and calculated resistances
#    uses yoko 610 and multimeter
#    """
#    global globalVrange2
#    
#    downswitch = args[0]
#    print(globalVrange2)    
#    ##VARIABLE DECLARATIONS##
#    #Going to use lists to start with for flexibility, even though slower than arrays
#    I_values = []
#    V_values = []
#    
#    
#    ##INITIALIZATION OF HARDWARE##    
#    Voltmeter = vf.get_voltage(address_Vb)
#    CurrentSource= vf.get_current(address_I_yoko_GS200b)
#    vf.intialize_current_yoko_GS200(CurrentSource, Irangeb, compliance_voltage)
#
#    time.sleep(0.2)
#
#    vf.intialize_voltage(Voltmeter, nplc, globalVrange2)
#    offset = vf.read_voltage_fast(Voltmeter, VDwellTime)
#    
#    ##CURRENT SWEEPS##
#    #Sweep Current up
#    print('Starting sweep up')
#    for I in np.arange(I_min, I_max, step):
#        vf.set_current_fast_yoko_GS200(CurrentSource, I)
#        V = vf.read_voltage_fast(Voltmeter, VDwellTime)
#        I_values.append(I)                
#        V_values.append(V)
#            
#        #print('%e '%I,end=" ")
#        
#    if downswitch :
#        print('Starting sweep down')
#        #Sweep Current down
#        for I in np.arange(I_max-step, I_min, -step):
#            vf.set_current_fast_yoko_GS200(CurrentSource, I)
#            V = vf.read_voltage_fast(Voltmeter, VDwellTime)
#            I_values.append(I)                
#            V_values.append(V)
#            
#         #   print('%e'%I,end=" ")
#        
#    V_values=np.array(V_values) 
#    V_values=V_values-offset
#    #SHUT IT DOWN!##
#    print("Exited current sweep")
#    vf.set_current_fast_yoko_GS200(CurrentSource, 0)
#    time.sleep(.1)
#    return np.array(I_values), V_values
# 
#    

def setFluxCurrent(IfluxuA):
	global globalVrange 
	    
    
    ##INITIALIZATION OF HARDWARE##    
    
	FluxSource= vf.get_current(address_I_yoko_GS200b)
	#vf.intialize_current_yoko_GS200(FluxSource,Fluxrange,compliance_voltage)

	time.sleep(0.2)
	Iflux = 1e-6 * IfluxuA
	vf.set_current_fast_yoko_GS200(FluxSource,Iflux)

def sweep_current_vphi(I_minflux, I_maxflux, step, Ibias, *args):
    """
    Inputs are min and max current for sweep for flux of the SQUIDs, step
    Returns an array with current steps, measured voltages, and calculated resistances
    
    """
    global globalVrange 
    
    downswitch = args[0]
    print(downswitch)    
    ##VARIABLE DECLARATIONS##
    #Going to use lists to start with for flexibility, even though slower than arrays
    I_values = []
    V_values = []
    
    
    ##INITIALIZATION OF HARDWARE##    
    Voltmeter = vf.get_voltage(address_V)
    CurrentSource= vf.get_current(address_I_yoko_GS200)
    FluxSource= vf.get_current(address_I_yoko_GS200b)
    
    
    vf.intialize_current_yoko_GS200(CurrentSource, Irange, compliance_voltage)
    vf.intialize_current_yoko_GS200(FluxSource,Fluxrange,compliance_voltage)

    time.sleep(0.2)

    vf.intialize_voltage(Voltmeter, nplc, globalVrange)
    offset = vf.read_voltage_fast(Voltmeter, VDwellTime)
    
    vf.set_current_fast_yoko_GS200(CurrentSource, Ibias)
    
    ##CURRENT SWEEPS##
    #Sweep Current up
    print('Starting sweep up')
    for Iflux in np.arange(I_minflux, I_maxflux, step):
        
        vf.set_current_fast_yoko_GS200(FluxSource,Iflux)
        V = vf.read_voltage_fast(Voltmeter, VDwellTime)
        I_values.append(Iflux)                
        V_values.append(V)
            
        #print('%e '%I,end=" ")
        
    if downswitch :
        print('Starting sweep down')
        #Sweep Current down
        for Iflux in np.arange(I_maxflux-step, I_minflux, -step):
            vf.set_current_fast_yoko_GS200(FluxSource,Iflux)
            V = vf.read_voltage_fast(Voltmeter, VDwellTime)
            I_values.append(Iflux)                
            V_values.append(V)
            
         #   print('%e'%I,end=" ")
        
    V_values=np.array(V_values) 
    V_values=V_values-offset
    #SHUT IT DOWN!##
    print("Exited current sweep")
    vf.set_current_fast_yoko_GS200(CurrentSource, 0)
    vf.set_current_fast_yoko_GS200(FluxSource,0)        

    time.sleep(.1)
    return np.array(I_values), V_values
 

def sweep_current_flux(I_min, I_max, step,I_minflux, I_maxflux, stepflux, *args):
    """
    Inputs are min and max current for sweep, steps, card and channels for switch
    Returns an array with current steps, measured voltages, and calculated resistances
    
    """
    global globalVrange 
    
    downswitch = args[0]
    print(globalVrange)    
    ##VARIABLE DECLARATIONS##
    #Going to use lists to start with for flexibility, even though slower than arrays
    
    
    
    ##INITIALIZATION OF HARDWARE##    
    Voltmeter = vf.get_voltage(address_V)
    CurrentSource= vf.get_current(address_I_yoko_GS200)
    FluxSource= vf.get_current(address_I_yoko_GS200b)
    vf.intialize_current_yoko_GS200(CurrentSource, Irange, compliance_voltage)
    vf.intialize_current_yoko_GS200(FluxSource,Fluxrange,compliance_voltage)
    
    if downswitch :
        I_valuesall = np.zeros([2*(np.arange(I_min, I_max, step).size)-1,np.arange(I_minflux, I_maxflux, stepflux).size],float)
        V_valuesall = np.zeros([2*(np.arange(I_min, I_max, step).size)-1,np.arange(I_minflux, I_maxflux, stepflux).size],float)
    else:
        I_valuesall = np.zeros([np.arange(I_min, I_max, step).size,np.arange(I_minflux, I_maxflux, stepflux).size],float)
        V_valuesall = np.zeros([np.arange(I_min, I_max, step).size,np.arange(I_minflux, I_maxflux, stepflux).size],float)
    
    time.sleep(0.2)
    counter=0

    for Iflux in np.arange(I_minflux, I_maxflux, stepflux):
        I_values = []
        V_values = []
        vf.set_current_fast_yoko_GS200(FluxSource,Iflux)
        
        vf.intialize_voltage(Voltmeter, nplc, globalVrange)
        offset = vf.read_voltage_fast(Voltmeter, VDwellTime)
        time.sleep(0.2)
        ##CURRENT SWEEPS##
        #Sweep Current up
        print('Starting sweep up')
        for I in np.arange(I_min, I_max, step):
            vf.set_current_fast_yoko_GS200(CurrentSource, I)
            V = vf.read_voltage_fast(Voltmeter, VDwellTime)
            I_values.append(I)                
            V_values.append(V)
                
            #print('%e '%I,end=" ")
            
        if downswitch :
            print('Starting sweep down')
            #Sweep Current down
            for I in np.arange(I_max-step, I_min, -step):
                vf.set_current_fast_yoko_GS200(CurrentSource, I)
                V = vf.read_voltage_fast(Voltmeter, VDwellTime)
                I_values.append(I)                
                V_values.append(V)
                
             #   print('%e'%I,end=" ")
        
        V_values=np.array(V_values) 
        V_values=V_values-offset
        #SHUT IT DOWN!##
        print("Exited current sweep")
        vf.set_current_fast_yoko_GS200(CurrentSource, 0)
        time.sleep(.1)
        I_valuesall[:,counter]=np.array(I_values)
        V_valuesall[:,counter]=V_values
        counter=counter+1
        
    vf.set_current_fast_yoko_GS200(FluxSource,0)        
    Iflux=np.arange(I_minflux, I_maxflux, stepflux)        
    return I_valuesall, V_valuesall, Iflux 
 
def save_data_flux(I_values, V_values, flux,pathfromrun,name):
    """
    Saves the raw data as ASCII seperated by tab
    """
    I_values=np.concatenate(( np.array(flux,ndmin=2),I_values),0)
    V_values=np.concatenate(( np.array(flux,ndmin=2),V_values),0)
    aux=I_values.shape
    data = np.concatenate((I_values,V_values),1)
    name = pathfromrun + name
    np.savetxt(name, data, header = ('flux first row, I ,  V  Dimension is =  \n' + str(aux)),delimiter=',')
   
   
def save_data(I_values, V_values, pathfromrun, name):
    """
    Saves the raw data as ASCII seperated by tab
    """
    column = len(I_values)
    data = np.zeros((column, 2))
    data[:,0] = I_values
    data[:,1] = V_values
    name = pathfromrun + name
    np.savetxt(name, data, header = 'col1: I, col2: V')
    
def open_data(filename):
    """
    Returns the values of I, V, R and plots data
    if newplot == 1 it will plot the file in new plot window otherwise it will plot it on same window
    """
    I, V= np.loadtxt(filename, unpack=True)
#    fig = plt.figure() #opens new plot
#    plt.xlabel('I')
#    plt.ylabel('V') 
#    plt.ticklabel_format(style='sci', axis='both', scilimits=(0,0))
#    plt.title(filename)
#    plt.plot(I,V,'-o', label=filename, alpha = 0.7, markerfacecolor="None")
#    plt.legend(loc='best')
#    plt.show()
    return I, V

#
#
#def sweep_current_live(I_min, I_max, step):
#    """
#    Inputs are min and max current for sweep, steps, card and channels for switch
#    Returns an array with current steps, measured voltages, and calculated resistances
#    """
#    
#    ##VARIABLE DECLARATIONS##
#    #Going to use lists to start with for flexibility, even though slower than arrays
#    I_values = []
#    V_values = []
#    
#    
#    ##INITIALIZATION OF HARDWARE##    
#    Voltmeter = vf.get_voltage()
#    CurrentSource= vf.get_current()
#    vf.intialize_current_yoko_GS200(CurrentSource, Irange, compliance_voltage)
#
#    time.sleep(0.2)
#
#    vf.intialize_voltage(Voltmeter, nplc, globalVrange)
#    offset = vf.read_voltage_fast(Voltmeter, VDwellTime)
#    
#    ##CURRENT SWEEPS##
#    #Sweep Current up
#    print('Starting sweep up')
#    for I in np.arange(I_min, I_max, step):
#        vf.set_current_fast_yoko_GS200(CurrentSource, I)
#        V = vf.read_voltage_fast(Voltmeter, VDwellTime)
#        I_values.append(I)                
#        V_values.append(V)
#        if I != 0:
#            R_values.append(float(V)/float(I))
#        else: R_values.append(0.0)
#            
#        print('%e '%I,end=" ")
#        
#    print('Starting sweep down')
#    #Sweep Current down
#    for I in np.arange(I_max-step, I_min, -step):
#        vf.set_current_fast_yoko_GS200(CurrentSource, I)
#        V = vf.read_voltage_fast(Voltmeter, VDwellTime)
#        I_values.append(I)                
#        V_values.append(V)
#        if I != 0:
#            R_values.append(float(V)/float(I))
#        else: R_values.append(0.0)
#        
#        print('%e'%I,end=" ")
#    
#    #SHUT IT DOWN!##
#    print("Exited current sweep")
#    vf.set_current_fast_yoko_GS200(CurrentSource, 0)
#    time.sleep(.1)
#    return np.array(I_values), np.array(V_values)
# 
#
#def plot_IV(number_of_sweeps, I_min, I_max, step, card, channel1, channel2):
#    
#    plt.figure()
#    #fig, ax = plt.subplots()
#            
#    plt.xlabel('I')
#    plt.ylabel('V') 
#    plt.ticklabel_format(style='sci', axis='both', scilimits=(0,0))
#    plt.title('Channels '+str(channel1)+':'+str(channel2))
#    
#    for n in range(0, number_of_sweeps):
#        I, V, R = sweep_current(I_min, I_max, step, card, channel1, channel2)
#        Ic_pos, Iret_pos, critical_currents = find_max_y_change(I,V) #finds Ic and Iret
#        plt.plot(I,V,'-o', label="Sweep "+str(n), alpha = 0.7, markerfacecolor="None") #plots the line sweeps
#        
#        #plots the critical currents
#        for n1 in range(0,len(critical_currents)):
#            if n1 < 2:
#                type_of_current = "I"+str(n1)
#                htext_offset = abs(I[(len(critical_currents)-1)]*.0)
#                vtext_offset = -abs(V[(len(critical_currents)-1)]*.3)
#
#            else: 
#                type_of_current = "I"+str(n1)
#                #htext_offset = 1.15
#                vtext_offset = -abs(V[(len(critical_currents)-1)]*.15)
#
#            plt.plot(I[critical_currents[n1]],V[critical_currents[n1]], "ro") #plots Ic
#            #plt.plot(I[Iret_pos],V[Iret_pos], "ro") #plots Iret
#            I_c = type_of_current+':(' + '{:.2E}'.format(I[critical_currents[n1]]) + ','+ '{:.2E}'.format(V[critical_currents[n1]]) + ')'
#            #I_r = 'Ir:(' + '{:.2E}'.format(I[Iret_pos]) + ','+ '{:.2E}'.format(V[Iret_pos]) + ')'
#
#            #plt.annotate(I_c, xy=(2, 1), xytext=(3, 4), arrowprops=dict(facecolor='black', shrink=0.05))
#            plt.annotate(I_c, xy=(I[critical_currents[n1]]+htext_offset, V[critical_currents[n1]]+vtext_offset))
#            #plt.annotate(I_r, xy=(I[Iret_pos]*1.15, V[Iret_pos]))
#
#  #print "I_c = %f, I_r = %f" %(position1, position2)
#        plt.legend(loc='best')
#        plt.show()
#        plt.pause(5)
#        #print(I)
#        
#    name = 'C' +str(card)+'_Ch'+str(channel1)+'-'+str(channel2)+'_'+time.strftime("%Y-%m-%d_%H.%M.%S")+'.dat'    
#    save_data(I,V,R,name) 
#    plt.savefig('data\\'+ name + '.png')
#    
#def plot_IV_yoko(number_of_sweeps, I_min, I_max, step, card, channel1, channel2):
#    
#    plt.figure()
#    #fig, ax = plt.subplots()
#            
#    plt.xlabel('I')
#    plt.ylabel('V') 
#    plt.ticklabel_format(style='sci', axis='both', scilimits=(0,0))
#    plt.title('Channels '+str(channel1)+':'+str(channel2))
#    
#    for n in range(0, number_of_sweeps):
#        I, V, R = sweep_current_yoko(I_min, I_max, step, card, channel1, channel2)
#        Ic_pos, Iret_pos, critical_currents = find_max_y_change_old(I,V) #finds Ic and Iret
#        plt.plot(I,V,'-o', label="Sweep "+str(n), alpha = 0.7, markerfacecolor="None") #plots the line sweeps
#        
#        #plots the critical currents
#        for n1 in range(0,len(critical_currents)):
#            if n1 < 2:
#                type_of_current = "I"+str(n1)
#                htext_offset = abs(I[(len(critical_currents)-1)]*.0)
#                vtext_offset = -abs(V[(len(critical_currents)-1)]*.3)
#
#            else: 
#                type_of_current = "I"+str(n1)
#                #htext_offset = 1.15
#                vtext_offset = -abs(V[(len(critical_currents)-1)]*.15)
#
#            plt.plot(I[critical_currents[n1]],V[critical_currents[n1]], "ro") #plots Ic
#            #plt.plot(I[Iret_pos],V[Iret_pos], "ro") #plots Iret
#            I_c = type_of_current+':(' + '{:.2E}'.format(I[critical_currents[n1]]) + ','+ '{:.2E}'.format(V[critical_currents[n1]]) + ')'
#            #I_r = 'Ir:(' + '{:.2E}'.format(I[Iret_pos]) + ','+ '{:.2E}'.format(V[Iret_pos]) + ')'
#
#            #plt.annotate(I_c, xy=(2, 1), xytext=(3, 4), arrowprops=dict(facecolor='black', shrink=0.05))
#            plt.annotate(I_c, xy=(I[critical_currents[n1]]+htext_offset, V[critical_currents[n1]]+vtext_offset))
#            #plt.annotate(I_r, xy=(I[Iret_pos]*1.15, V[Iret_pos]))
#
#  #print "I_c = %f, I_r = %f" %(position1, position2)
#        plt.legend(loc='best')
#        plt.show()
#        plt.pause(5)
#        #print(I)
#        
#    name = 'C' +str(card)+'_Ch'+str(channel1)+'-'+str(channel2)+'_'+time.strftime("%Y-%m-%d_%H.%M.%S")+'.dat'    
#    save_data(I,V,R,name) 
#    plt.savefig('data\\'+ name + '.png')
#
#def plot_IV_live(app, curve, number_of_sweeps, I_min, I_max, step, card, channel1, channel2):
#    '''
#    Calls sweep current live, returns I, V and R
#    '''
#
#    I, V, R = sweep_current_live(app, curve, number_of_sweeps, I_min, I_max, step, card, channel1, channel2)
##    I, V, R = sweep_current_live_from_zero(app, curve, number_of_sweeps, I_min, I_max, step, card, channel1, channel2)
#    
#    Ic_pos, Iret_pos, critical_currents = find_max_y_change_old(I,V) #finds Ic and Iret
#
#
#
#   
#
#    return I, V, R
#
#def plot_IV_live_variable_points(app, curve, number_of_sweeps, I_min, I_max, step, card, channel1, channel2):
#    '''
#    Calls sweep current live variable points, returns I, V and R
#    '''
#
#    I, V, R = sweep_current_live_variable_points(app, curve, number_of_sweeps, I_min, I_max, step, card, channel1, channel2)
##    I, V, R = sweep_current_live_from_zero(app, curve, number_of_sweeps, I_min, I_max, step, card, channel1, channel2)
#
#    return I, V, R
#
#def plot_IV_test(app, curves, number_of_sweeps, I_min, I_max, step, card, channel1, channel2):
#    global go
#    go = 1
#    print(I_min)
#    print(I_max)
#    print(step)
#    for n in range (0,number_of_sweeps):
#        x = []
#        y = []
#        if n%2 ==0:
#            color = 'w'
#        else:
#            color = 'b'
#            
#        if n>1:
#            curves[n-2].setData([],[])
#        for i in np.arange(I_min, I_max, step):
#            x.append(i)
#            y.append(i*n)
#            curves[n].setData(x,y,symbol='o', symbolBrush=color)
#            app.processEvents()
#            if go==0:
#                break
#
#def plot_IV_live_Rn(app, curve, number_of_sweeps, I_min, V_max, step, card, channel1, channel2):
#
#
#    I, V, R = sweep_current_live_Rn(app, curve, number_of_sweeps, I_min, V_max, step, card, channel1, channel2)
#
#    return I, V, R
#
#def plot_warm_resistance(app, curve, number_of_sweeps, I_min, V_max, step, card, channel1, channel2):
#    
#    I, V, R = sweep_current_live_warm_resistance(app, curve, number_of_sweeps, I_min, V_max, step, card, channel1, channel2)
#    
#    return I,V,R
#
# 
#def create_plot_window(title, xlabel, ylabel):
#    """
#    Creates an instance of a pyqtwindow
#    """
#    p = pg.plot()
#    p.setTitle(title)
#    #p.setRange(QtCore.QRectF(0, -10, 5000, 20)) 
#    #p.setLabel(xlabel, ylabel)
#    p.setLabel('bottom', xlabel)
#    p.setLabel('left', ylabel)
#    curve = p.plot()
#    return curve
#    
#def live_plot(I_min, I_max, step, card, channel1, channel2):
#    """
#    Inputs are min and max current for sweep and steps
#    Returns an array with current steps and measured voltages
#    """
#    app = QtGui.QApplication([])
#    curve = create_plot_window(title, xlabel, ylabel)
#    
#    Voltmeter = vf.get_voltage()
#    CurrentSource= vf.get_current()
#    Switch = vf.get_switch()
#    
#    vf.intialize_switch(Switch)
#    vf.intialize_current(CurrentSource, Irange, compliance_voltage)
#    vf.current_filter(CurrentSource, 0) # turns on filter
#    #vf.current_display(CurrentSource, 0)# turns display off
#    time.sleep(0.2)
#
#    
#    #Turn on low to earth    
#    #vf.turnoff_current(CurrentSource) #have to turn off current source to turn on low to earth
#    #sleep.time(0.1)
#    #CurrentSource.write('outp:lte on') #turns on low to earth
#    #sleep.time(0.1)
#    
#    vf.intialize_voltage(Voltmeter, nplc, Vrange)
#    
#    vf.close_channel(Switch, 1,channel1)
#    time.sleep(.2)
#    
#    vf.close_channel(Switch,1,channel2)
#    time.sleep(.2)
#    
#    vf.turnon_current(CurrentSource)
#    time.sleep(.2)
#
#    vf.open_channel(Switch,card, short) #open short
#    time.sleep(.2)
#    
#    #Going to use lists to start with for flexibility, even though slower than arrays
#    global I_values 
#    global V_values 
#    global R_values 
#
#
#    #setup range
#    #np.arange(I_min, I_max, step)
#    #print("Entering current sweep")
#    
#    #Sweep Current up
#    print('\nChannel %d:%d SweepUp Current:'%(channel1,channel2))
#    for I in np.arange(I_min, I_max+step, step):
#        vf.set_current_fast(CurrentSource, I)
#        V = vf.read_voltage_fast(Voltmeter, VDwellTime)
#        I_values.append(I)                
#        V_values.append(V)
#        R_values.append(float(V)/float(I))
#        #print('%e '%I,end=" ")
#        curve.setData(I_values, V_values, symbol='o')
#        #print(x, data)
#        #t.sleep(1)
#        app.processEvents()  ## force complete redraw for every plot
#        
#    #Sweep Current down
#    print('\nChannel %d:%d SweepDown Current:'%(channel1,channel2))
#    for I in np.arange(I_max+step, I_min-step, -step):
#        vf.set_current_fast(CurrentSource, I)
#        V = vf.read_voltage_fast(Voltmeter, VDwellTime)
#        I_values.append(I)                
#        V_values.append(V)
#        R_values.append(float(V)/float(I))
#        #print('%e'%I,end=" ")
#        curve.setData(I_values, V_values, symbol='o')
#        #print(x, data)
#        #t.sleep(1)
#        app.processEvents()  ## force complete redraw for every plot
#                     
#    
#    #print("Exited current sweep")
#    vf.set_current_fast(CurrentSource, 0)
#    time.sleep(.2)
#
#    
#    vf.close_channel(Switch,card,short)
#    time.sleep(.2)
#    
#    #print("opening channels before exit")
#    vf.open_channel(Switch,card,channel1)
#    vf.open_channel(Switch,card,channel2)
#    #vf.turnoff_current()
#    
#    #R = float(V)/float(I) #current is in milli Amps
#    #print 'Voltage: %e V' %float(V)
#    #print 'Applied I: %e A' %float(I)
#    #print 'Resistance: %e Ohms' %float(R) 
#    
#    return I_values, V_values, R_values  
#
#def plot_all(directory):
#    # function to plot all iv curves on same window
#    
#    import Live_Plot_Functions as lpf
#    global windows, plots, curves
#    import re
#    import os
#    all_I = []
#    all_V = []
#    devices = []
#    for filename in os.listdir(directory):
#        if len(re.findall('_Ic_raw', filename)) ==1:
##            print(filename)
#            # get info from filename
#            chip_info = re.split('_Ic_raw', filename) # split the descrtiption
#            chip_info = chip_info[0]
#            chip_info_split = re.split('_', chip_info)
#            if len(chip_info_split)==4:
#                chip_name = chip_info_split[0]
#                dev_name = chip_info_split[1]+ '_' +chip_info_split[2]
#                dev_size = chip_info_split[3]
#            else:
#                chip_name = chip_info_split[0]
#                dev_name = chip_info_split[1]
#                dev_size = chip_info_split[2]
#            print(dev_name)
#            
#            # get values
#            vals = np.loadtxt(directory+ '/'+filename) # raw
#            I_np = vals[:,0] # in format of np.array
#            V_np = vals[:,1]
#            
#            
#            # append to lists
#            devices.append(dev_name)
#            I = []
#            V = []
#            for i in range(0,len(I_np)):
#                I.append(I_np[i])
#                V.append(V_np[i])
#                
#            all_I.append(I)
#            all_V.append(V)
##    print(all_I)
##    print(all_V)
##            
#    # create plotting elements
#    windows = lpf.create_windows(1)
#    plots = lpf.create_plots(windows)
#    curves = []
#    
#    for i in range(0,len(devices)):
#        curve = plots[0].plot()
#        curves.append(curve)
#        
#    # create app instance
#    app = QtGui.QApplication.instance()
#    if app is None:
#        app = QtGui.QApplication(sys.argv)
#    else:
#        pass
#    
#    # plot
#    legend = plots[0].addLegend()
#    
#    for i in range(0,len(devices)):
#        curves[i].setData(all_I[i], all_V[i], pen=i)
#        legend.addItem(curves[i], devices[i])
#        app.processEvents()
#    plots[0].setTitle(chip_name)
#
