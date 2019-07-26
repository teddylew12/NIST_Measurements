# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 13:42:57 2017

@author: Soroush
"""
import Visa_Functions as vf
import Input_Functions as inpfunc
import time
import numpy as np
import IV_curve_v3 as iv
from scipy import stats
nplc = 1.0
Vrange = 'auto'
VDwellTime = 0.25
Irange = 1e-01
compliance_voltage = 2
shorts = [[10,40],0,[10,40],0,0,0,0,0,0,10] # index corresponds to the card #, value is the short on that card

def plot_Resistance_Array_live(app, curve, card1, card2, channel1, channel2, max_current,continuity=False,extra_res=0):
    '''
    Plots a sweep from 0 to 3mA and returns the values plotted
    Updates a live plot with current on x axis, voltage on y axis
    
    :param app: pyqtgraph construct
    
    :param curve: pyqtgraph constuct
    
    :param card1, card 2: Target card2
    
    :param channel1, channel2: Target Channels
    
    :param max_Current: max_current before function breaks
    
    :return: I-Values: Arrays of Current Values
    
    :return: V-Values: Array of Voltage Values
    
    :return: R-Values: Array of Resistance Values
        
    :return: Funykgraphs Any Sweeps that had non-linear slopes (Determined by Lin-regress)
   
    Called By:
        
        -Measure_Via_Resistance
        
        -Measure_Device_Resistance
        
        -Resistance Curve
        
        -Measure_Resistor_Arrays
        
    Calls on:
        
        -All Visa Functions
        
    Uses:
        
        -Linregress to determine whether a graph is linear or not
        
        -Looks for a negative slope or an r^2 value below .9
        
    '''
    global go
    go = 1    
    # current initialization variables
    # lower range has less noise
    Irange = 1e-02
    compliance_voltage = 30.
    
    # get GPIB instruments
    Voltmeter = vf.get_voltage()
    CurrentSource = vf.get_current()
    Switch = vf.get_switch()


    vf.intialize_switch_all(Switch)

    vf.intialize_current_yoko(CurrentSource, Irange, compliance_voltage)
    time.sleep(0.2)

    vf.intialize_voltage(Voltmeter, nplc, Vrange)

    vf.close_channel(Switch, card1,channel1) # instead of card, used to be 1
    time.sleep(0.2)

    vf.close_channel(Switch,card2,channel2) # instead of card, used to be 1
    time.sleep(0.2)
    
    vf.turnon_current_yoko(CurrentSource)    
    time.sleep(0.2)

    vf.open_short(Switch, card1, iv.shorts)
        
    time.sleep(.2)

    #Going to use lists to start with for flexibility, even though slower than arrays
    I_values = []
    V_values = []
    R_values = []

    # starting 7/24: voltmeter reads non zero when the current is zero
    offset = vf.read_voltage_fast(Voltmeter, VDwellTime)

    print('Offset: %s' %offset)
    
    #Sweep Current up
    if continuity:
        step=max_current/10
    else:
        step = max_current / 30
    

    print('\nChannel %d:%d SweepUp Current:'%(channel1,channel2))
    
    
    for I in np.arange(0, max_current, step):
        vf.set_current_fast_yoko(CurrentSource, I)
        
        V = vf.read_voltage_fast(Voltmeter, VDwellTime)
        V=V-I*extra_res
        I_values.append(I)
        # new, for fixing the offset 7/24:
        V_values.append(V-offset)
        if I != 0:
            R_values.append(float(V)/float(I))
        else:
            R_values.append(0.0)
        
        # live plotting
        curve.setData(I_values,V_values, symbol='o', symbolBrush='w', symbolSize=5)
        app.processEvents()
        print('%e '%I,end=" ")
        
        if go==0: # input passed from GUI
            iv.exitfunc(Switch,CurrentSource,card1,card2,channel1,channel2)
            return 0,0,0,0
    funkygraphs=False
    m,_,r2,_,_=stats.linregress(I_values,V_values)
    r2=r2**2
   
    if m <= 0 or r2<=.9:
        funkygraphs=True
    vf.set_current_fast_yoko(CurrentSource, 0)
    time.sleep(.2)

    vf.close_short(Switch, card1, iv.shorts)    
    time.sleep(.2)
    
    vf.open_channel(Switch,card1,channel1)
    vf.open_channel(Switch,card2,channel2)
    return I_values, V_values, R_values, funkygraphs

def plot_pcm3b(app, curve, card1, card2, channel1, channel2, max_current):
    '''
    Plots a sweep from 0 to 3mA and returns the values plotted
    Updates a live plot with current on x axis, voltage on y axis
    Looks for discontinuity
    '''
    global go
    go = 1    
    # current initialization variables
    # lower range has less noise
    Irange = 1.1e-01
    compliance_voltage = 30.
    
    # get GPIB instruments
    Voltmeter = vf.get_voltage()
    CurrentSource = vf.get_current()
    Switch = vf.get_switch()


    vf.intialize_switch_all(Switch)

    vf.intialize_current_yoko(CurrentSource, Irange, compliance_voltage)
    time.sleep(0.2)
    Vrange=30
    vf.intialize_voltage(Voltmeter, nplc, Vrange)

    vf.close_channel(Switch, card1,channel1) # instead of card, used to be 1
    time.sleep(0.2)

    vf.close_channel(Switch,card2,channel2) # instead of card, used to be 1
    time.sleep(0.2)
    
    vf.turnon_current_yoko(CurrentSource)    
    time.sleep(0.2)

    vf.open_short(Switch, card1, iv.shorts)
        
    time.sleep(.2)
    I_values = []
    V_values = []
    R_values = []
    slope=0
    Imax=0
    # starting 7/24: voltmeter reads non zero when the current is zero
    offset = vf.read_voltage_fast(Voltmeter, VDwellTime)

    print('Offset: %s' %offset)
    
    #Sweep Current up
    step = max_current / 50

    print('\nChannel %d:%d SweepUp Current:'%(channel1,channel2))
    
    
    for I in np.arange(0, max_current, step):
        vf.set_current_fast_yoko(CurrentSource, I)
        
        V = vf.read_voltage_fast(Voltmeter, VDwellTime)
        I_values.append(I)
        # new, for fixing the offset 7/24:
        V_values.append(V-offset)
        if I != 0:
            R_values.append(float(V)/float(I))
        else:
            R_values.append(0.0)
        
        # live plotting
        curve.setData(I_values,V_values, symbol='o', symbolBrush='w', symbolSize=5)
        app.processEvents()
        print('%e '%I,end=" ")
        
        if go==0: # input passed from GUI
            iv.exitfunc(Switch,CurrentSource,card1,card2,channel1,channel2)
            return 0,0,0,0
    '''
    Assumes that the slope in the region from 0 to step*6 mA (currently step =2ma so 12ma)
    is the resisitive slope when superconducting... it then looks for strong changes in slope, based off the delta
    so if the slope starts at X but reaches a discontinuity and then becomes less than (1-delta)*x the program will 
    detect it as the Imax point
    '''
    slope=sum(R_values[:5])/6
    delta=.35
    discont=False
    count=8
    while not discont:
        if R_values[count]<slope*(1-delta) or R_values[count]>slope*(1+delta):
            discont=True
            Imax=I_values[count]
        count+=1
    vf.set_current_fast_yoko(CurrentSource, 0)
    time.sleep(.2)

    vf.close_short(Switch, card1, iv.shorts)    
    time.sleep(.2)
    
    vf.open_channel(Switch,card1,channel1)
    vf.open_channel(Switch,card2,channel2)
    return I_values, V_values, R_values, Imax,slope
'''
def discretepoints(folder,chip,devices,points):
  
    inputs = inpfunc.format_input_resistance(devices)
    cards = inputs[0]
    channels = inputs[1]
    
    return_measurements_Resistance = []
    

    for i in range (0,len(channels),2):
        chan1 = channels[i]
        chan2 = channels[i+1]
        card1 = cards[i]
        card2 = cards[i+1]

        V,R = run_disc_point(card1,card2,chan1,chan2,points)
        return_measurements_Resistance.append(R)
    return return_measurements_Resistance

def run_disc_point(card1,card2,chan1,chan2,points):
    global go
    go = 1    
    # current initialization variables
    # lower range has less noise
    Irange = 1e-02
    compliance_voltage = 30.
    
    # get GPIB instruments
    Voltmeter = vf.get_voltage()
    CurrentSource = vf.get_current()
    Switch = vf.get_switch()


    vf.intialize_switch_all(Switch)

    vf.intialize_current_yoko(CurrentSource, Irange, compliance_voltage)
    time.sleep(0.2)

    vf.intialize_voltage(Voltmeter, nplc, Vrange)

    vf.close_channel(Switch, card1,chan1) # instead of card, used to be 1
    time.sleep(0.2)

    vf.close_channel(Switch,card2,chan2) # instead of card, used to be 1
    time.sleep(0.2)
    
    vf.turnon_current_yoko(CurrentSource)    
    time.sleep(0.2)

    vf.open_short(Switch, card1, iv.shorts)
        
    time.sleep(.2)

    #Going to use lists to start with for flexibility, even though slower than arrays
    V_values = []
    R_values = []

    # starting 7/24: voltmeter reads non zero when the current is zero
    offset = vf.read_voltage_fast(Voltmeter, VDwellTime)

    print('Offset: %s' %offset)
    for point in points:
        vf.set_current_fast_yoko(CurrentSource, point)
        V = vf.read_voltage_fast(Voltmeter, VDwellTime)
        V_values.append(V-offset)
        R_values.append(float(V)/float(point))
    
        if go==0: # input passed from GUI
            iv.exitfunc(Switch,CurrentSource,card1,card2,chan1,chan2)
            return 0,0,0,0
    vf.set_current_fast_yoko(CurrentSource, 0)
    time.sleep(.2)

    vf.close_short(Switch, card1, iv.shorts)    
    time.sleep(.2)
    
    vf.open_channel(Switch,card1,chan1)
    vf.open_channel(Switch,card2,chan2)
    return V_Values,R_values
    
    
'''    
    
    
    
    
    
    
    
    
    
    
    
    
    