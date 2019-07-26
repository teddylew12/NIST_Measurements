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
import pyqtgraph as pg
#from pygame import mixer


#app = QtGui.QApplication([])

#=================================
#Global variables
#=================================
nplc = 1
Vrange = 'auto'

globalVrange = '0.002'

VDwellTime = 0
Irange = 10e-03 
Fluxrange = 2e-03
compliance_voltage = 10.
shorts = [[10,40],0,[10,40],0,0,0,0,0,0,10] # index corresponds to the card #, value is the short on that card

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
    

def sweep_current(app,curve,current_point,ic_curve,plot,card1,card2,channel1,channel2,I_min,I_max,step):
    """
    Inputs are min and max current for sweep, steps, card and channels for switch
    Returns an array with current steps, measured voltages, and calculated resistances
    
    """ 
    ##VARIABLE DECLARATIONS##
    #Going to use lists to start with for flexibility, even though slower than arrays
    I_values = []
    V_values = []
    
    current_x = []
    current_y = []
    
    ##INITIALIZATION OF HARDWARE##    
    Voltmeter = vf.get_voltage()
    CurrentSource= vf.get_current()
    Switch = vf.get_switch()
    
    vf.intialize_switch_all(Switch) #For some reason causes things to break. ADD THIS BACK
    vf.intialize_current_yoko(CurrentSource, Irange, compliance_voltage)
    time.sleep(0.2)
    vf.intialize_voltage(Voltmeter, nplc, Vrange)
    vf.close_channel(Switch,card1,channel1)
    time.sleep(0.2)
    vf.close_channel(Switch, card2, channel2) # instead of card, used to be 1
    time.sleep(0.2)
    vf.turnon_current_yoko(CurrentSource)    
    time.sleep(0.2)    
    vf.open_short(Switch, card1, shorts) 
    time.sleep(0.2)
    
    offset = vf.read_voltage_fast(Voltmeter, VDwellTime)
    
    global go
    go = 1

    #Sweep Current up
    print('Starting sweep up')
    for I in np.arange(I_min, I_max, step):
        vf.set_current_fast_yoko(CurrentSource, I)
        V = vf.read_voltage_fast(Voltmeter, VDwellTime)
        I_values.append(I)                
        V_values.append(V)
        
        current_x.append(I)
        current_y.append(V) 
        
        curve.setData(I_values,V_values, symbol='o', symbolBrush='w', symbolSize=5)
        current_point.setData(current_x, current_y, symbol='o', symbolBrush='r', symbolSize=7)
        app.processEvents()
        
        current_x = []
        current_y = []
        
        if go == 0: #If the stop button on the GUI is pressed
            exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
            return 0,0,0
            
    print('Starting sweep down')
    #Sweep Current down
    for I in np.arange(I_max-step, I_min, -step):
        vf.set_current_fast_yoko(CurrentSource, I)
        V = vf.read_voltage_fast(Voltmeter, VDwellTime)
        I_values.append(I)                
        V_values.append(V)
        
        current_x.append(I)
        current_y.append(V) 
        
        curve.setData(I_values,V_values, symbol='o', symbolBrush='w', symbolSize=5)
        current_point.setData(current_x, current_y, symbol='o', symbolBrush='r', symbolSize=7)
        app.processEvents()
        
        current_x = []
        current_y = []
        
        if go == 0: #If the stop button on the GUI is pressed
            exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
            return 0,0,0
            
        

    #SHUT IT DOWN!##
    print("Exited current sweep")
    vf.set_current_fast_yoko(CurrentSource, 0)
    time.sleep(.2)
    vf.close_short(Switch, card1, shorts)
    time.sleep(0.2)
    if channel1 != 10:
        vf.open_channel(Switch,card1,channel1)
        vf.open_channel(Switch,card2,channel2)
        
    V_values=np.array(V_values) 
    V_values=V_values-offset
    I_values = np.array(I_values)
    
    ###########
    #Magical code for finding the 4 Ics
    Ic_values = find_Ic(I_values, V_values) #Ted needs to FIX this
   # Ic_values = [0,0,0,0]
    ###########
    
    # setting labels
    for n1 in range(0,len(Ic_values)):
        if n1 < 2:
            type_of_current = "I"+str(n1)
            label = pg.TextItem(text="", color=(0, 0, 0), fill=(0, 255, 255), anchor=(0, -1))
        else:
            type_of_current = "I"+str(n1)
            label = pg.TextItem(text="", color=(0, 0, 0), fill=(0, 255, 255), anchor=(0, 2))

        I_c = type_of_current+':(' + '{:.2E}'.format(Ic_values[n1]) + ','+ '{:.2E}'.format(V_values[(np.where(I_values == Ic_values[n1]))[0]][0]) + ')'
        label.setText(I_c)
        label.setPos(Ic_values[n1], V_values[(np.where(I_values == Ic_values[n1]))[0]][0])
        plot.addItem(label)
        ic_curve[n1].setData([Ic_values[n1]], [V_values[(np.where(I_values == Ic_values[n1]))[0]][0]], symbol='o', symbolBrush='c', symbolSize=10)
        app.processEvents()
    
    
    return I_values, V_values, Ic_values

def find_Ic(I_values, V_values):
    critcurrs=np.zeros(4)#[Ineg, Ipos, Iretpos, Iretneg]    
    halfpoint=int((len(I_values)/2)-1)
    supI=I_values[:halfpoint]
    supV=V_values[:halfpoint]
    sdownI=I_values[halfpoint:]
    sdownV=V_values[halfpoint:]
    '''
    Find Sweep Up Crit currents
    '''
    numJJ=2
    upbound = numJJ * 0.25e-06
    lowbound=-1*upbound
    firstfound=False

    for i in range(0,len(supI)):
        #Find where the curve enters the bounded region and only take the first point
        if supV[i]>=lowbound and not firstfound:
            critcurrs[0]=supI[i]
            firstfound=True
        #Find where the curve leaves the bounded region and take the point directly before it leaves
        if supV[i]>upbound:
            critcurrs[1]=supI[i-1]
            break
    '''
    Find Sweep Down Crit currents
    '''
    firstfound=False
    for i in range(0,len(sdownI)):
        #Find where the curve enters the bounded region and only take the first point
        if sdownV[i]<=upbound and not firstfound:
            critcurrs[2]=sdownI[i]
            firstfound=True
        #Find where the curve leaves the bounded region and take the point directly before it leaves
        if sdownV[i]<lowbound:
            critcurrs[3]=sdownI[i-1]
            break
    print(critcurrs)
    return critcurrs
def sweep_current_vphi(app,curve,current_point,card1,card2,channel1,channel2, I_minflux, I_maxflux, Iflux_step, Ibias_min, Ibias_max, Ibias_step):
    """
    Inputs are min and max current for sweep for flux of the SQUIDs, step
    Returns an array with current steps, measured voltages, and calculated resistances
    *********NOTE: This will have to be modified if the second current source is wired through the switch matrix
    """   
    ##VARIABLE DECLARATIONS##
    #Going to use lists to start with for flexibility, even though slower than arrays
    I_values = []
    V_values = []
        
    current_x = []
    current_y = []
    
    ##INITIALIZATION OF HARDWARE##    
    Voltmeter = vf.get_voltage()
    CurrentSource = vf.get_current()
    FluxSource = vf.get_current_flux()
    Switch = vf.get_switch()
    
    vf.intialize_switch_all(Switch)
    vf.intialize_current_yoko(CurrentSource,Irange,compliance_voltage) #50 mA instead of 10 mA because we want a larger range for periodicity tests
    time.sleep(0.2)
    vf.intialize_current_yoko(FluxSource,50e-03,compliance_voltage)
    time.sleep(0.2)
    vf.intialize_voltage(Voltmeter, nplc, Vrange)
    vf.close_channel(Switch,card1,channel1)
    time.sleep(0.2)
    vf.close_channel(Switch, card2, channel2) # instead of card, used to be 1
    time.sleep(0.2)
    vf.turnon_current_yoko(CurrentSource)    
    time.sleep(0.2)    
    vf.turnon_current_yoko(FluxSource)    
    time.sleep(0.2)
    vf.open_short(Switch, card1, shorts) 
    time.sleep(0.2)
    
    offset = vf.read_voltage_fast(Voltmeter, VDwellTime)
    
    global go
    go = 1
    
    for Ibias in np.arange(Ibias_min, Ibias_max, Ibias_step):
        vf.set_current_fast_yoko(CurrentSource, Ibias)
    
        I = []
        V = []
        ##CURRENT SWEEPS##
        #Sweep Current up
        print('Starting sweep with Ibias = %f' %Ibias)
        for Iflux in np.arange(I_minflux, I_maxflux, Iflux_step):
            vf.set_current_fast_yoko(FluxSource,Iflux)
            Vread = vf.read_voltage_fast(Voltmeter, VDwellTime)
            I.append(Iflux)                
            V.append(Vread)
            
            current_x.append(Iflux)
            current_y.append(Vread) 
            
            curve.setData(I,V, symbol='o', symbolBrush='w', symbolSize=5)
            current_point.setData(current_x, current_y, symbol='o', symbolBrush='r', symbolSize=7)
            app.processEvents()
            
            current_x = []
            current_y = []
            
            if go == 0: #If the stop button on the GUI is pressed
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                vf.set_current_fast_yoko(FluxSource,0)  
                return 0,0,0
            
        vf.set_current_fast_yoko(CurrentSource, 0)
        vf.set_current_fast_yoko(FluxSource,0)
        
        I = np.array(I)
        V = np.array(V)
        I_values.append(I)
        V_values.append(V-offset)
        
        if go == 0: #If the stop button on the GUI is pressed
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                vf.set_current_fast_yoko(FluxSource,0)  
                return 0,0,0
    
    print("Exited current sweep")
    vf.set_current_fast_yoko(CurrentSource, 0)
    time.sleep(.2)
    vf.set_current_fast_yoko(FluxSource, 0)
    time.sleep(.2)
    vf.close_short(Switch, card1, shorts)
    time.sleep(0.2)
    if channel1 != 10:
        vf.open_channel(Switch,card1,channel1)
        vf.open_channel(Switch,card2,channel2)
    x=I
    y=np.full(np.shape(I),np.mean(V))
    current_point.setData(x,y,symbol='o', symbolBrush='g', symbolSize=7)
    return find_period(I_values, V_values) 
    #return[0,0,0,0]
 
def find_period(I_values,V_values):
    '''
    To write Ted
    I vals and V vals are arrays of arrays
    for each IV pair, get the max range of the data
    use that pair to find period
    start with simple but likely use least squares in the end
    '''
    import numpy as np
    import math
   # from scipy.optimize import leastsq
    maxrange=0
    whichsweep=-1
    for i in range(0,len(I_values)):
        if np.ptp(V_values)>maxrange:
            whichsweep=i
            maxrange=np.ptp(V_values)
    bestI=I_values[whichsweep]
    bestV=V_values[whichsweep]
    '''
    Attempt with least squares, incorrectly assumed sinusoidal IV curve
    
    guesses=[np.ptp(bestV),1,0,np.mean(bestV)]
    func=lambda x:x[0]*np.sin(x[1]*bestI + x[2])+x[3]-bestV
    _,est_freq,_,_=leastsq(func,guesses)[0]
    index=0
    
    
    #while bestI[index]<est_freq*2*np.pi:
    #    index+=1
    #Imin_flux=min(bestV[:index])
    
    return est_freq*2*np.pi,Imin_flux, bestI,bestV
    '''
    aver=np.mean(bestV)
    jumps=[]
    for i in range(len(bestV)-1):
        if (bestV[i]<aver and bestV[i+1]>aver) or (bestV[i]>aver and bestV[i+1]<aver):
            jumps.append(i)
    pers2=[]
    for i in range(math.ceil(len(jumps)/2)-1):
        pers2.append(bestI[jumps[i+2]]-bestI[jumps[i]])
    period=np.mean(pers2)
    for index,val in enumerate(bestI):
        if val>=0:
            break
    iminI=bestI[index:]
    iminV=bestV[index:]
    count=[]
    for i in range(len(bestV)-2):
        if (iminV[i]<aver and iminV[i+1]>aver) or (iminV[i]>aver and iminV[i+1]<aver):
            count.append(i)
        if len(count)==2:
            break
    if len(count)<2:
        print("hmmmmm")
        iminflux=0
    else:
        iminI=iminI[count[0]:count[1]]
        iminV=iminV[count[0]:count[1]]
        iminflux=iminI[np.argmax(iminV)]
        print("The period is %f and the imin flux is %f" % (period,iminflux))
    return period,iminflux,bestI,bestV


def sweep_current_flux(app,curves,current_point,card1,card2,channel1,channel2,I_min,I_max,step,I_minflux,I_maxflux,stepflux,down):
    """
    Inputs are min and max current for sweep, steps, card and channels for switch
    Returns an array with current steps, measured voltages, and calculated resistances
    
    """
    curve_colors = ['b','g','r','c','m','y','k','w']
    
    I_values_all = [] #(Ibias)
    V_values_all = []
    
    current_x = []
    current_y = []
    
    ##INITIALIZATION OF HARDWARE##    
    Voltmeter = vf.get_voltage()
    CurrentSource= vf.get_current()
    FluxSource= vf.get_current_flux()
    Switch = vf.get_switch()
    
    vf.intialize_switch_all(Switch)
    vf.intialize_current_yoko(CurrentSource, Irange, compliance_voltage)
    time.sleep(0.2)
    vf.intialize_current_yoko(FluxSource,Fluxrange,compliance_voltage)
    time.sleep(0.2)
    vf.intialize_voltage(Voltmeter, nplc, Vrange)
    vf.close_channel(Switch,card1,channel1)
    time.sleep(0.2)
    vf.close_channel(Switch, card2, channel2) # instead of card, used to be 1
    time.sleep(0.2)
    vf.turnon_current_yoko(CurrentSource)    
    time.sleep(0.2)    
    vf.turnon_current_yoko(FluxSource)    
    time.sleep(0.2)
    vf.open_short(Switch, card1, shorts) 
    time.sleep(0.2)
        
    time.sleep(0.2)
    curve_counter = 0
    
    global go
    go = 1
    colorsused=[]
    for Iflux in np.arange(I_minflux, I_maxflux, stepflux):
        I_values = []
        V_values = []
        vf.set_current_fast_yoko(FluxSource,Iflux) #Set the flux current
        
        #vf.intialize_voltage(Voltmeter, nplc, Vrange)
        offset = vf.read_voltage_fast(Voltmeter, VDwellTime)
        time.sleep(0.2)
        ##CURRENT SWEEPS##
        #Sweep Current up
        print('Starting sweep up with Iflux =', Iflux)
        for I in np.arange(I_min, I_max, step):
            vf.set_current_fast_yoko(CurrentSource, I)
            V = vf.read_voltage_fast(Voltmeter, VDwellTime)
            I_values.append(I)                
            V_values.append(V)
            
            current_x.append(I)
            current_y.append(V)
            
            curves[curve_counter].setData(I_values,V_values, symbol='o', symbolBrush=curve_colors[curve_counter % 8], symbolSize = 5)
            
            current_point.setData(current_x, current_y, symbol='o', symbolBrush='r', symbolSize=7)
            app.processEvents()
            
            current_x = []
            current_y = []
            
            if go == 0: #If the stop button on the GUI is pressed
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                vf.set_current_fast_yoko(FluxSource,0)  
                return 0,0,0
            
        if down:
            print('Starting sweep down')
            #Sweep Current down
            for I in np.arange(I_max-step, I_min, -step):
                vf.set_current_fast_yoko(CurrentSource, I)
                V = vf.read_voltage_fast(Voltmeter, VDwellTime)
                I_values.append(I)                
                V_values.append(V)
                
                current_x.append(I)
                current_y.append(V)
                
                curves[curve_counter].setData(I_values,V_values, symbol='o', symbolBrush=curve_colors[curve_counter % 8], symbolSize = 5)
                current_point.setData(current_x, current_y, symbol='o', symbolBrush='r', symbolSize=7)
                app.processEvents()
            
                current_x = []
                current_y = []
            
                if go == 0: #If the stop button on the GUI is pressed
                    exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                    vf.set_current_fast_yoko(FluxSource,0)  
                    return 0,0,0
        
        V_values=np.array(V_values) 
        V_values=V_values-offset
        
        #SHUT IT DOWN!##
        print('Exited current sweep with Iflux =', Iflux)
        vf.set_current_fast_yoko(CurrentSource, 0)
        time.sleep(.1)
        I_values_all.append(I_values)
        V_values_all.append(V_values)
        colorsused.append(curve_colors[curve_counter % 8])
        curve_counter = curve_counter + 1
        
        
    print('Finished all current sweeps')    
    #Safe all of the hardware
    vf.set_current_fast_yoko(FluxSource,0) 
    time.sleep(0.2)   
    vf.close_short(Switch, card1, shorts)
    time.sleep(0.2)
    if channel1 != 10:
        vf.open_channel(Switch,card1,channel1)
        vf.open_channel(Switch,card2,channel2) 
       
    #Iflux=np.arange(I_minflux, I_maxflux, stepflux)
        
    return I_values_all, V_values_all,colorsused 
 
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
   
   
def save_data(I_values, V_values, name):
    """
    Saves the raw data as ASCII seperated by tab
    """
    column = len(I_values)
    
    data = np.zeros((column, 2))
    data[:,0] = I_values
    data[:,1] = V_values
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