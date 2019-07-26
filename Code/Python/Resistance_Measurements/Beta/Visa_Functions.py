# -*- coding: utf-8 -*-
"""
Created on Thu May 25 10:15:13 2017
--This purpose of this file is to have basic function library that all the different scripts can use 
@author: JPulecio
"""

#=================================
#Import libraries
#=================================

import time
import visa 
#=================================
#Global variables
#=================================
yoko_GS200 = 2
yoko_GS200b = 10 #need to add the address of the second current source here
yoko_GS610 = 24
address_I = yoko_GS200
address_I_flux = yoko_GS200b
address_V = 23
address_keithley_7001 = 26
address_keithley_7002 = 27
address_Switch = address_keithley_7002
short_channel = 40
card = '1'
#cards_with_shorts = [1, 1, 3, 3]
#short_for_cards = [10, 40, 10, 40] #These are the shorts for the cards above which match via index
cards_with_shorts = [3, 3]
short_for_cards = [10, 40] #These are the shorts for the cards above which match via index

total_cards = [1,2,3,10]

#=================================
#Function definitions
#=================================


def open_instrument(address):
    """
    :param Address: Opens the connection to the instrument at the particular address 
    
    :return: Instrument
    """
    instrument=visa.ResourceManager().open_resource('GPIB0::%d::INSTR' % address)


    return instrument


#========================
# functions for yoko using address I
#========================
def intialize_current_yoko(CurrentSource, Irange, compliance_voltage):
    """
    Initializes current source
     
    :param CurrentSource: Address of current source
    
    :param Irange: Current range
    
    :param compliance_voltage: compliance_voltage

    Called By:
        
        -Resistance Curve
        
        -Visa Functions
        
        -Iv_Curve_v2
    """

    if address_I == 24:
        CurrentSource.write(':SOUR:FUNC CURR')
        CurrentSource.write(':SOUR:CURR:RANG %f' % (Irange))  # sets current range
        CurrentSource.write(':SOUR:CURR:PROT:VOLT %f' % compliance_voltage)  # sets complaince voltage
    else:
        CurrentSource.write(':SOUR:FUNC CURR')
        CurrentSource.write(':SOUR:RANG %f' % (Irange))  # sets current range
        CurrentSource.write(':SOUR:PROT:VOLT %f' % compliance_voltage)  # sets complaince voltage


def turnon_current_yoko(CurrentSource):
    """
    Turns on current from CurrentSource input address
    """
    CurrentSource.write("OUTP ON")
        
def set_current_fast_yoko(CurrentSource, I):
    """
    Sets Current
    
    :param CurrentSource: Address of current source
    
    :param I: Target Current 
    
    :return: Current Source Address
    
    Called By:
        
        -Resistance Curve
        
        -Visa Functions
        
        -Iv_Curve_v2
    """

    if address_I == 24:
        CurrentSource.write(":SOUR:CURR:LEV %0.3E" % I)
    else:
        CurrentSource.write(":SOUR:LEV:FIX %0.3E" % I)
    return CurrentSource
        

#===================

##The following functions were written to measure resistance
def get_current():
    """
    Opens current source
    
   :return: Current Source Address
    """
    CurrentSource = open_instrument(address_I)
    return CurrentSource

def get_current_flux():
    FluxSource = open_instrument(address_I_flux)
    return FluxSource

def get_switch():
    """
    Opens switch
    
    :return: Switch Address
    """  
    Switch = open_instrument(address_Switch)    
    return Switch
    
def get_voltage():
    """
    Opens Voltmeter
    
    :return: Voltmeter Address
    """  
    Voltmeter = open_instrument(address_V)    
    return Voltmeter


def open_short(Switch, card, shorts):
    """
    Opens shorts 
    
    :param Switch: Switch Address
    
    :param Card: Targeted Card Address
   
    :param shorts: Array of Shorts
    
    Called by:
        
        -Resistance Curve
        
        -Iv_Curve_v2
        
    Calls on:
        
        -open_channel()
    """ 
#    if card == 2:
#        card = 1
#    if card == 4:
#        card = 3
#    try:
#        for i in shorts[card-1]:
#            open_channel(Switch, card, i)
#    except:
#        open_channel(Switch, card, shorts[card-1])
#    
    e = 0
    for card in cards_with_shorts:
        open_channel(Switch, card, short_for_cards[e])
        e = e + 1
        
def close_short(Switch, card, shorts):
    """
    Closes short
    
    :param Switch: Switch Address
    
    :param Card: Targeted Card Address
   
    :param shorts: Array of Shorts
    
    Called by:
        
        -Resistance Curve
        
        -Iv_Curve_v2
    
    Calls on:
        
        -close_channel()
    """ 
#    if card == 2:
#        card = 1
#    if card == 4:
#        card = 3
#    try:
#        for i in shorts[card-1]:
#            close_channel(Switch, card, i)
#    except:
#        close_channel(Switch, card, shorts[card-1])
#    
    e = 0
    for card in cards_with_shorts:
        close_channel(Switch, card, short_for_cards[e])
        e = e + 1
        
def intialize_switch_all(Switch):
    """
    Initialized Switch
    
    :param Switch: Switch Address
    
    :return: Switch the Switch Address
    
    Called by:
        
        -Resistance Curve 
        
        -Iv_Curve_v2
        
    Calls on:
        
        -not_initialized(Switch)
    """ 

    Switch.write('*rst')    
    #Following opens all the channels except the short
    if (not_initialized(Switch)): 
        Switch.write(":OPEN ALL")
        for n, i in enumerate(cards_with_shorts):
            short = '@%s!%s'%(i, short_for_cards[n]) #change short_for_cards array in global variable above
            Switch.write('close (%s)' % short)
            time.sleep(0.1)
        
    else:
        print("Switch Already Init.")
        
    print ("\n")
    
    return Switch



def not_initialized(Switch):
    """
    Checks if Switch is initialized
    
    :param Switch: Switch Address
    
    Returns:
        
        -True if not Initialized
        
        -False if Initialized
        
    Called by:
        
        -Visa Functions 
    
    """
    status = str(Switch.query(":clos:stat?"))
    init_state = "(@"
    for i in range(0,len(cards_with_shorts)):
        init_state = init_state + ("%s!%s" %(cards_with_shorts[i], short_for_cards[i]))
        if i == len(cards_with_shorts) - 1:
            init_state = init_state + ")\n"
        else: 
            init_state = init_state + ","


#    print(status)
#    print(init_state)
    if (status == init_state):
        return False
    else:
        return True
 
def open_channel(Switch,card, channel):
    """
    Open switch channel
    
    The procedure for changing channels is:
        
        1. set output current to zero
        
        2. close the shorted line
        
        3. open any lines besides the shorted line
    
    :param Switch: Switch Address
    
    :param Card: Targeted Card Address
   
    :param channel: Current Targeted Channel
       
    Called by:
        
        -Iv_Curve_V2
        
        -Visa Functions
        
        -Resisitance Curve   
    
    
    """
    desired_channel = '@' + str(card) + '!' + str(channel)
    
    
    #Step 1    
    closed = str(Switch.query('route:close:state?')) #THIS IS GOING TO RETURN A STRING THAT DOESNT WORK WITH CLOSED
    
    #Step 2    
    time.sleep(.25)
    
    Switch.write('open (%s)'% desired_channel) #open the channel that was previously closed IF it wasnt the short

def close_channel(Switch,card, channel):
    """
    close switch channel
    
    The procedure for changing channels is:
        
            1. set output current to zero
            
            2. close the desired line
            
            3. open the shorted line
    
    :param Switch: Switch Address
    
    :param Card: Targeted Card Address
   
    :param channel: Current Targeted Channel
       
   Called by:
        
        -Iv_Curve_V2
        
        -Visa Functions
        
        -Resisitance Curve
        
    """
    desired_channel = '@' + str(card) + '!' + str(channel)
    
 
    #Step 2    
    Switch.write('close (%s)'%desired_channel) 
    time.sleep(.25)
    

def intialize_voltage(Voltmeter, nplc, Vrange):
    """
    Initializes voltmeter
   
    :param Voltmeter: The Voltmeter machine address  
    
    :param NPLC: Number of Power Line Cycles to average over
    
    :param Vrange: Voltage Range  
    
    Called by:
        
        -Iv_Curve_V2
        
        -Resisitance Curve
    """  
 
    Voltmeter.write('*RST; status:preset; *cls')
    Voltmeter.write('conf:volt:dc %s' % Vrange) #this is important!!!
    #when vrange is set to auto or something small, sample speed is very slow (<10 pts/second)
    #To speed up sampling, set vrange = 1.
    
    Voltmeter.write("*sre 32") #not sure what this does either

    Voltmeter.write("input:filter off") #Should be done manually with data in python
    
    #The following line sets the rate at which the voltmeter averages the data over (ie sampling rate)
    ##0.02, 0.2, 1, 2, 10, 20, 100, 200 where 0.02 is the fastest sampling rate and lowest averaging
    Voltmeter.write("SENS:VOLT:DC:NPLC %f" %nplc) #number of power line cycles to average over
    Voltmeter.write("trigger:source bus")
    Voltmeter.write("trigger:delay 0")


    

def read_voltage_fast(Voltmeter, dwell_time):
    """
    Passes in the voltmeter address instead of doing it in the function
   
    :param Voltmeter: The Voltmeter machine address  
    
    :param Dwell_time: Time to sleep
   
    :return: Measured_V-Measure Voltage    
    
    Called by:
        
        -Iv_Curve_V2
        
        -Resisitance Curve
    """
    
    Voltmeter.write("initiate")
    Voltmeter.assert_trigger()
    measured_V = float(Voltmeter.query("fetch?"))
    return measured_V
 
##END The preceding functions were written to measure resistance
'''
######################################################################
Temperature Controls
######################################################################
'''

###START The following functions are for using the Lakeshore 332 Temperature Controller

def getLake():
    rm = visa.ResourceManager()
    Lake = rm.open_resource("GPIB0::15::INSTR") #Controller is plugged into GPIB0 address 15 in the computer
    return Lake

def closeLake(Lake):
    Lake.close()

def getTempK(Lake):
    temp = Lake.query("KRDG?").replace('+','').replace('\n','').replace('\r','')
    temp=float(temp)
    return temp

def getHeatRange(Lake):
    range1 = Lake.query("RANGE?").replace('\n','').replace('\r','')
    return range1

def getHeatOut(Lake):
    out = Lake.query("HTR?").replace('+','').replace('\n','').replace('\r','')
    return out

def getTempSetpoint(Lake):
    setpoint = Lake.query("SETP? 1").replace('+','').replace('\n','').replace('\r','')
    return setpoint

def getPID(Lake):
    PID = str(Lake.query("PID? 1").replace('+','').replace('\n','').replace('\r',''))
    return PID

def setRange(Lake, H):
    try:
        Lake.query("RANGE "+str(H))
        print("Range updated successfully!")
    except Exception as e:
           print(e)
           print("Unable to update range.")

    time.sleep(1)

def setManualOutput(Lake, M):
    try:
        Lake.query("MOUT 1,"+str(M))
        print("Manual output updated successfully!")
    except Exception as e:
           print(e)
           print("Unable to update manual output.")

    time.sleep(1)

def setPID(Lake, P, I, D):
    try:
        #import pdb;pdb.set_trace()
        Lake.query("PID 1,"+str(P)+","+str(I)+","+str(D))
        print("PID coefficients updated successfully!")
    except Exception as e:
           print(e)
           print("Unable to update PID coefficients.")

    time.sleep(1)

def setTempSetpoint(Lake, valT):
    try:
        Lake.query("SETP 1,"+str(valT))
        print("Temperature setpoint updated successfully!")
    except Exception as e:
           print(e)
           print("Unable to update temperature setpoint.")

    time.sleep(1)
    
def safe_temp_controller(Lake):
    if not Lake:
        Lake = getLake()
    try:
        setManualOutput(Lake, 0)
        setTempSetpoint(Lake, 1)
        setPID(Lake, 0.1,0.1,0)
        setRange(Lake, 0)
        closeLake(Lake)
        global go
        go=0
    except:
        print('Temperature Controller not successfully safed!')