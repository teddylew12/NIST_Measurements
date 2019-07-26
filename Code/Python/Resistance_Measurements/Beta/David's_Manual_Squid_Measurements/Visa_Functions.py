# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 14:07:11 2017
--This purpose of this file is to have basic function library that all the different scripts can use 
@author: Manuel
"""

#=================================
#Import libraries
#=================================
import visa 
import time
import numpy as np

#=================================
#Global variables
#=================================
#yoko_GS200 = 1
#yoko_GS600 = 25
#Agilent_34420 = 24
#Agilent_34401 = 22
#Agilent_E4287 = 29
#Keithley_6220 = 12

#address_I = yoko_GS200
#address_V = Agilent_34420
#address_V2 = Agilent_34401
#address_flux = Keithley_6220

#=================================
#Function definitions
#=================================
def whats_connected():
    """
    tells you what instruments are connected via GPIB
    """
    #rm=visa.ResourceManager()
    #visa.Resource.clear(rm)
    rm=visa.ResourceManager()
    connected_instruments = rm.list_resources() 
    
    print("Found following connections:")
    for p in connected_instruments: print("\t%s" %p)
    
    print("\nGPIB connected devices"        )
    for x in range(0 , len(connected_instruments)):
        address = connected_instruments[x]
        if address.find("GPIB")!= -1:
            instrument=visa.ResourceManager().open_resource(address)
            print("\t%s\t@ %s\n" %(instrument.query('*IDN?'), address))

        
    
def open_instrument(address):
    """
    Pass in the address and it will open the connection to the instrument at the particular address 
    """
    instrument=visa.ResourceManager().open_resource('GPIB0::%d::INSTR' % address)
    #print(instrument.query('*IDN?'))

    return instrument


#========================
# functions for yoko GS200
#========================
def intialize_current_yoko_GS200(CurrentSource, Irange, compliance_voltage):
    """
    Initializes current source
    intialize_current_yoko_GS200(CurrentSource, Irange, compliance_voltage):
    """
    # CurrentSource = get_current()
    CurrentSource.write(':SOUR:FUNC CURR')
    CurrentSource.write(':SOUR:RANG %f' % (Irange))  # sets current range
    CurrentSource.write(':SOUR:PROT:VOLT %f' % compliance_voltage)  # sets complaince voltage
    set_current_fast_yoko_GS200(CurrentSource, 0)    
    turnon_current_yoko_GS200(CurrentSource)
    # return CurrentSource

def turnon_current_yoko_GS200(CurrentSource):
    CurrentSource.write("OUTP ON")

def turnoff_current_yoko_GS200(CurrentSource):
    CurrentSource.write("OUTP OFF")

def set_current_fast_yoko_GS200(CurrentSource, I):
    CurrentSource.write(":SOUR:LEV:FIX %0.3E" % I)

def set_current_yoko_GS200(CurrentSource, I):
    """
    Input current in amps
    """
    CurrentSource.write(":SOUR:LEV:AUTO %0.3E" % I)
    
def get_current(address):
    """
    Opens current source
    """
    CurrentSource = open_instrument(address)
    return CurrentSource

#========================
# functions for Keithley 6220
#========================
def initialize6220(address,comp,range_in_mA):

    global currentsource6220
    currentsource6220=visa.ResourceManager().open_resource('GPIB0::%d::INSTR' % address)
    ident = currentsource6220.query('*IDN?')    
    currentsource6220.write('sour:cle:imm')
    currentsource6220.write('sour:curr:comp %f' %comp)
    #print(currentsource6220.query('source:curr:comp?')
    
    #Could also try simply calling setCurrentRange, however this will mean the drop down menu doesn't actually do anything
    if (range_in_mA == "100 mA"):
        currentsource6220.write('sour:curr:range %f' % (100/1000.0))
    elif (range_in_mA == "20 mA"):
        currentsource6220.write('sour:curr:range %f' % (20/1000.0))
    elif (range_in_mA == "2 mA"):
        currentsource6220.write('sour:curr:range %f' % (2/1000.0))
    else:
        currentsource6220.write('sour:curr:range %s' % range_in_mA) #might not work
    

def readCurrent6220():
    global currentsource6220
    return(1e3*float(currentsource6220.query('curr?'))) # in mA
        

def setCurrent6220(current_in_mA):
    global currentsource6220
    currentsource6220.write('sour:curr %f' % (current_in_mA/1000.0))
    return(1e3*float(currentsource6220.query('curr?'))) # in mA


def setCurrentRange6220(stop_current_in_mA):   
    setCurrent6220(0)
    stop=stop_current_in_mA
    if 0.02< stop <= 0.2:
        range_in_mA=0.2                 #200uA range
    elif 0.2< stop <= 2:
        range_in_mA=2.0                 #2mA range
    elif 2.0< stop <= 20:
        range_in_mA=20.0                #20mA range
    else:
        range_in_mA=100
    time.sleep(.25)
    currentsource6220.write('sour:curr:range %f' % (range_in_mA/1000.0))
    return range_in_mA

       
def enableCurrent6220():
    currentsource6220.write('outp:stat on')
    print('Current source enabled')

    
def disableCurrent6220():
    currentsource6220.write('outp:stat off')
    print('Current source disabled')   

#
##========================
## functions for yoko GS610
##========================
def intialize_current_yoko_GS610(CurrentSource, Irange, compliance_voltage):
    """
    Initializes current source
    """
    # CurrentSource = get_current()
#    CurrentSource = yoko_GS610
    CurrentSource.write(':SOUR:FUNC CURR')        
    CurrentSource.write(':SOURce:CURRent:RANGe:AUTO OFF')      
    CurrentSource.write(':SOUR:CURR:RANG %f' % (Irange))  # sets current range
    CurrentSource.write(':SOUR:VOLT:PROT ON' )
    CurrentSource.write(':SOUR:VOLT:PROT:ULIM %f' % compliance_voltage)  # sets complaince voltage
    turnon_current_yoko_GS610(CurrentSource)
    # return CurrentSource

def turnon_current_yoko_GS610(CurrentSource):
    CurrentSource.write("OUTP ON")

def turnoff_current_yoko_GS610(CurrentSource):
    CurrentSource.write("OUTP OFF")

def set_current_fast_yoko_GS610(CurrentSource, I):
#    CurrentSource.write(":SOUR:LEV:FIX %0.3E" % I)
#    CurrentSource = yoko_GS610
#    CurrentSource = get_current()
    CurrentSource.write(":SOUR:CURR:LEV %0.3E" % I)
def set_current_yoko_GS610(CurrentSource, I):
#    CurrentSource.write(":SOUR:LEV:FIX %0.3E" % I)
#    CurrentSource = yoko_GS610
#    CurrentSource = get_current()
    CurrentSource.write(":SOUR:CURR:LEV %0.3E" % I)
##    
##############################################
##Keithley 6220
#def intialize_current_K(CurrentSource, Irange, compliance_voltage):
#    """
#    Initializes current source
#    """
#    #CurrentSource = get_current()
#    CurrentSource.write('sour:curr:range %f' % (Irange)) #sets current range
#    CurrentSource.write('sour:cle:imm') #clears out memory etc. 
#    CurrentSource.write('sour:curr:comp %f' %compliance_voltage) #sets complaince voltage
#    turnon_current_K(CurrentSource)
#
#    #return CurrentSource
#    
#def set_current_K(CurrentSource,I):
#    """
#    Input current in amps
#    """
#    CurrentSource.write('sour:curr %f' % (I))
#    
#
#def turnon_current_K(CurrentSource):
#    """
#    Turns on current and leaves it on
#    """
#    #CurrentSource = get_current()
#    CurrentSource.write('outp:stat on')
#    #time.sleep(dwell_time)
#    
#def turnoff_current_K(CurrentSource):
#    """
#    Turns off current
#    """
#    #CurrentSource = get_current()
#    CurrentSource.write('outp:stat off')
#        
#def current_filter_K(CurrentSource, filter):
#    if filter == 1:
#        CurrentSource.write('curr:filt on')
#    else: CurrentSource.write('curr:filt off')
#
#def current_display_K(CurrentSource, display):
#    if display == 0:
#        CurrentSource.write('disp:enab off')
#    else: CurrentSource.write('disp:enab on')
#

#nano voltmeter
###################################
def get_voltage(address_V):
    """
    Opens voltmeter
    """  
    Voltmeter = open_instrument(address_V)    
    return Voltmeter

def intialize_voltage(Voltmeter, nplc, Vrange):
    """
    Initializes voltmeter
    """  
    #Voltmeter = get_voltage()
    Voltmeter.write('*RST; status:preset; *cls')
    Voltmeter.write('conf:volt:dc %s' % Vrange) #this is important!!!
    #when vrange is set to auto or something small, sample speed is very slow (<10 pts/second)
    #To speed up sampling, set vrange = 1.
    
    Voltmeter.write("*sre 32") #not sure what this does either
    #Voltmeter.write("display off") #speeds up the measurement!!!
    Voltmeter.write("input:filter off") #Should be done manually with data in python
    
    #The following line sets the rate at which the voltmeter averages the data over (ie sampling rate)
    ##0.02, 0.2, 1, 2, 10, 20, 100, 200 where 0.02 is the fastest sampling rate and lowest averaging
    Voltmeter.write("SENS:VOLT:DC:NPLC %f" %nplc) #number of power line cycles to average over
    Voltmeter.write("trigger:source bus")
    Voltmeter.write("trigger:delay 0")
    #return Voltmeter

def set_voltage_range(Vrange):
    """
    Input voltage in V
    Range options are 'auto' and 1e2 to 1e-9
    """
    Voltmeter = get_voltage()
    Voltmeter.write('conf:volt:dc %s' % Vrange) #this is important!!!
    #when vrange is set to auto or something small, sample speed is very slow (<10 pts/second)
    #To speed up sampling, set vrange = 1.        

def read_voltage(dwell_time):
    Voltmeter = get_voltage() 
    time.sleep(dwell_time)    
    Voltmeter.write("initiate")
    Voltmeter.assert_trigger()
    measured_V = Voltmeter.query("fetch?")
    return measured_V

def read_voltage_fast(Voltmeter, dwell_time):
    """
    Passes in the volmeter address instead of doing it in the function
    """
    #time.sleep(dwell_time)    
    Voltmeter.write("initiate")
    Voltmeter.assert_trigger()
    measured_V = float(Voltmeter.query("fetch?"))
    return measured_V
 
    
#multimeter
###################################
def get_voltage2():
    """
    Opens voltmeter
    """  
    Voltmeter = open_instrument(address_V2)    
    return Voltmeter

def intialize_voltage2(Voltmeter, nplc, Vrange):
    """
    Initializes voltmeter
    """  
    #Voltmeter = get_voltage()
    Voltmeter.write('*RST; status:preset; *cls')
    Voltmeter.write('conf:volt:dc %s' % Vrange) #this is important!!!
    #when vrange is set to auto or something small, sample speed is very slow (<10 pts/second)
    #To speed up sampling, set vrange = 1.
    
    Voltmeter.write("*sre 32") #not sure what this does either
    #Voltmeter.write("display off") #speeds up the measurement!!!

    
    #The following line sets the rate at which the voltmeter averages the data over (ie sampling rate)
    ##0.02, 0.2, 1, 2, 10, 20, 100, 200 where 0.02 is the fastest sampling rate and lowest averaging
    Voltmeter.write("SENS:VOLT:DC:NPLC %f" %nplc) #number of power line cycles to average over
    Voltmeter.write("trigger:source bus")
    Voltmeter.write("trigger:delay 0")
    #return Voltmeter

def set_voltage_range2(Vrange):
    """
    Input voltage in V
    Range options are 'auto' and 1e2 to 1e-9
    """
    Voltmeter = get_voltage()
    Voltmeter.write('conf:volt:dc %s' % Vrange) #this is important!!!
    #when vrange is set to auto or something small, sample speed is very slow (<10 pts/second)
    #To speed up sampling, set vrange = 1.        

def read_voltage2(dwell_time):
    Voltmeter = get_voltage() 
    time.sleep(dwell_time)    
    Voltmeter.write("initiate")
    Voltmeter.assert_trigger()
    measured_V = Voltmeter.query("fetch?")
    return measured_V

def read_voltage_fast2(Voltmeter, dwell_time):
    """
    Passes in the volmeter address instead of doing it in the function
    """
    #time.sleep(dwell_time)    
    Voltmeter.write("initiate")
    Voltmeter.assert_trigger()
    measured_V = float(Voltmeter.query("fetch?"))
    return measured_V
 
    




#####
##Network analyzer


# i do not want to initialize it so i will skip that

def get_NWA(address_NWA):
    """
    Opens voltmeter
    """  
    NWA = open_instrument(address_NWA)    
    return NWA

def get_catalog_measurements(NWA,channel):
    NWA.write('CALCulate%s:PARameter:CATalog:EXTended?' %channel)
    measurements=NWA.read()
    return measurements
    
def get_traces(NWA,channel):
    measurements=get_catalog_measurements(NWA,channel)
    measlist=measurements.split("\"")
    measlist=measlist[1].split(",")
    nomeas=int(len(measlist)/2);
    data=[]
    freq=[]
    for k in range(nomeas):
        print(k)
        print(measlist[(k)*2])            
        NWA.write("CALCulate%s:PARameter:SELect " %channel +measlist[k*2])
        NWA.write("CALCULATE%s:DATA? FDATA" %channel)
        dataux=NWA.read()
        dataaux= list(map(float, dataux.split(",")))
        f0=float(NWA.query("SENSe%s:FREQuency:START?" %channel))
        f1=float(NWA.query("SENSe%s:FREQuency:STOP?" %channel))
        freqaux=np.linspace(f0,f1,len(dataaux))
        data.append(dataaux)
        freq.append(freqaux)
    return np.array(freq),np.array(data)

 
def save_data_NWA(freq, data,path,name):
    """
    Saves the raw data as ASCII seperated by tab
    """
    aux=data.shape
    dataall = np.concatenate((freq,data),0)
    name = path + name
    print(name)
    np.savetxt(name, dataall, header = ('freq, data  Dimension is =  \n' + str(aux)),delimiter=',')
   
    



#####
##Agilent generator


# i do not want to initialize it so i will skip that

def get_siggen(Agilent_E4287):
    """
    Opens voltmeter
    """  
    siggen = open_instrument(Agilent_E4287)    
    return siggen
def set_siggen_freq(siggen,freq):
    """
    Changes frequency of signal generator
    
    """
    siggen.write(':SOURce:FREQuency %e' % freq) 
    return

def set_siggen_amp_mVolts(siggen,sigpow):
    """
    Changes amplitude of signal generator in volts!!
    
    """
    sigpow=abs(sigpow)
    if sigpow>1000:
        print('signal too big')
        return
    else:
    
        siggen.write(':SOURce:POWer %fmV ' % sigpow) 
        
    return

def set_siggen_output(siggen,state):
    """
    Changes frequency of signal generator
    state  = ON or OFF
    """
    
    siggen.write(':OUTPut:STATe ' + state) 
    return