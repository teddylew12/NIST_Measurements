# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 15:51:37 2017

@author: Soroush + Javi + Ted

"""

import measure_Ic as ic
import measure_Rn as rn

import measure_Resistor_Arrays_v2 as mra
import measure_Device_Resistance as mdr
import measure_Via_Resistance as mvr
import measure_pcm3b as m3b
import measure_SQUID as msq

import time 
import database_v4 as d

'''
Measurement flow: all completed by the fulltest button on the GUI
    
    1. Plug in probe while it is not dunked
    
    2. Run measure_PCM_chip_warm before dunking. Will plot simple I-V line to make
        sure there are no open connections, and measure RT values
        r
    3. Slowly dunk probe
    
    4. Call measure_PCM_chip_cold. This will take IV's of all the devices on the PCM
        i.e. SJs and arrays. Then it will find resistance of Resistor Arrays and Vias
        then it find normal resistance for devices
'''

# globals
dirname = ("E:/Users/volt.686QVACTEST/National Institute of Standards and Technology (NIST)/SEG - SFQ_Circuits/")
web_link = ("https://nistgov.sharepoint.com/sites/SEG/Shared%20Documents/Forms/AllItems.aspx?newTargetListUrl=%2Fsites%2FSEG%2FShared%20Documents&viewpath=%2Fsites%2FSEG%2FShared%20Documents%2FForms%2FAllItems%2Easpx&id=%2Fsites%2FSEG%2FShared%20Documents%2FSFQ_Circuits_Measurements%2F")
web_link = ("https://nistgov.sharepoint.com/sites/SEG/Shared%20Documents/Forms/AllItems.aspx?newTargetListUrl=%2Fsites%2FSEG%2FShared%20Documents&viewpath=%2Fsites%2FSEG%2FShared%20Documents%2FForms%2FAllItems%2Easpx&id=%2Fsites%2FSEG%2FShared%20Documents%2FSFQ_Circuits_Measurements%2F")


def measure_PCM_chip_cold(chip, devices, optionalic=0):
    '''
    This is the main function to call when PCM chip is fully dunked. Will 
    measure and save the ICs of all the Junctions, then the resistances of the
    resistor arrays and vias, then the normal resistance of the junctions.
    
    :param chip: Target chip
    
    :param devices: Array of target devices
   
    :param optionalIC: Optional input Ic
    
    :Graphs: IV and RN graphs
    
    Called By:
        
        -Measurement_GUI_v3-coldmeasure
    
    Calls On:
        
        -Get_Ic_Iret_and_save
        
        -get_resistance_arrays
        
        -get_resistance_Via
        
        -save_Resistance_Measurements_cold
        
        -save_Via_Measurements_cold
        
        -get_Rn_Imax_and_save
    '''
    current_time = time.strftime("_%Y-%m-%d_%H-%M-%S_cold")
    folder = dirname+ str(chip)+current_time
    folder_link = web_link+ str(chip)+current_time
    Jc = d.chip_Jc(chip)
    print("Weblink: %s" %folder_link)
    
    # sort the devices into Junctions, Resistors, and Vias
    JJs = []
    RAs = []
    Vias = []
    
    for i in range(0, len(devices)):
        if devices[i].device_type == 'ResistorArray':
            RAs.append(devices[i])
        elif devices[i].device_type == 'Via':
            Vias.append(devices[i])
        else:
            JJs.append(devices[i])
       
    # added 1/18/18, not tested yet
    design = d.find_chip(chip).design_id
    
    if design ==4 and optionalic==0:
        print("\nYou are measuring a SingleJJ design without passing in an \
              optional ic. In order to take a high point density sweep you \
              must pass in an optional ic.")
    
    # take IV curves for all Junctions, save after each device
    if optionalic == 0: # optional was not passed in
        Ic_measurements, meas_ids = ic.get_Ic_Iret_and_save(folder, folder_link, chip, JJs, Jc)
    else: # optional was passed in, pass on to next function
        Ic_measurements, meas_ids = ic.get_Ic_Iret_and_save(folder, folder_link, chip, JJs, Jc, optionalic=optionalic)
    
    # if there was a keyboard interrupt, do not continue
    if Ic_measurements == 0 and meas_ids == 0:
        return

    # take the sweep to find the resistance of the Resistor Arrays
    Resistance_measurements = mra.get_resistance_arrays(folder, chip, RAs)
    # save the resistance measurements 
    for i in range(0,len(Resistance_measurements)):
        try:
            d.save_Resistance_Measurements_cold(chip, Resistance_measurements[i], folder_link, RAs[i])
        except:
            pass    

    # take the sweep to find the resistance of the Vias
    Via_measurements = mvr.get_Resistance_Via(folder, chip, Vias)
    # save the via measurements
    for i in range(0,len(Via_measurements)):
        try:
            d.save_Via_Measurements_cold(chip, Via_measurements[i], folder_link, Vias[i])
        except:
            pass

    # find normal resistance for all Junctions, save after each
    if optionalic == 0 and meas_ids != 0: # only do if Ic was not passed in, and there was a return for meas_id
        # Note: meas_ids will be 0 iff there was a keyboard interrupt handled
        Rn_measurements, Imax_measurements = rn.get_Rn_Imax_and_save(folder, folder_link, chip, JJs, meas_ids)
        
    print("Weblink: %s" %folder_link)




def measure_PCM_chip_warm(chip, devices):
    '''
    This is the main function to call when PCM chip hasn't been dunked. Will 
    measure the continuity of all the Junctions, then the resistances of the
    resistor arrays and vias, and save the resistances to the database.
    
    :param chip: Target chip
    
    :param devices: Array of target devices
   
    :return: funkygraph2-array of abnormal graphs
    
    :Graphs: Continuity Graphs, IV from 0 mA to 300 mA
    
    Called By:
        
        -Measurement_GUI_v3-warmmeasure
    
    Calls On:
        
        -Get_Resistance
        
        -get_resistance_arrays
        
        -get_resistance_Via
        
        -save_Resistance_Measurements_warm
        
        -save_Via_Measurements_warm
    '''
    current_time = time.strftime("_%Y-%m-%d_%H-%M-%S_warm")
    folder = dirname+ str(chip)+current_time
    folder_link = web_link+ str(chip)+current_time
    Jc = d.chip_Jc(chip)
    print("Weblink: %s" %folder_link)
    
    # sort the devices into Junctions, Resistors, and Vias
    JJs = []
    RAs = []
    Vias = []
    
        
    for i in range(0, len(devices)):
        if devices[i].device_type == 'ResistorArray':
            RAs.append(devices[i])
        elif devices[i].device_type == 'Via':
            Vias.append(devices[i])
        else:
            JJs.append(devices[i])

    device_resistance,funkygraphs = mdr.get_Resistance(folder, chip, JJs)
 
    
    # take the sweep to find the resistance of the Resistor Arrays
    Resistance_measurements = mra.get_resistance_arrays(folder, chip, RAs)
    #Resistance_measurements = mra.get_resistance_arrays(folder, chip, RAs)
    # save the resistance measurements 
    
    for i in range(0,len(Resistance_measurements)):
        d.save_Resistance_Measurements_warm(chip, Resistance_measurements[i], folder_link, RAs[i])
    # take the sweep for the vias
    Via_measurements = mvr.get_Resistance_Via(folder, chip, Vias)
    # save the via measurements
    for i in range(0,len(Via_measurements)):
        d.save_Via_Measurements_warm(chip, Via_measurements[i], folder_link, Vias[i])
        
    print("Weblink: %s" %folder_link)

    return funkygraphs
#===================
# check to make sure there are no opens
# simply takes a current sweep and returns the slope
#===================

def check_connections(chip, devices):
    '''
    Simply check that there are no opens. Takes a current sweep from 0 to 3mA
    saves images and raw numbers.
    
    :param chip: Target chip
    
    :param devices: Array of target devices
    '''
    current_time = time.strftime("_%Y-%m-%d_%H-%M-%S_connections")
    folder = dirname+ str(chip)+current_time
    R,oddgraphs = mdr.get_Resistance(folder, chip, devices)
    print(R)
    # save to the database here
    return oddgraphs

def measure_JJs_Ic(chip, devices ,optionalIc=0):
    '''
    Takes just an I-V curve for the JJs, saves images but does not add to the
    database
    
    :param chip: Target chip
    
    :param devices: Array of target devices
   
    :param optionalIC: Optional input Ic
    
    Calls:
        
        -Measure_Ic-get_Ic_Iret_and_save
    '''
    current_time = time.strftime("_%Y-%m-%d_%H-%M-%S")
    folder = dirname+ str(chip)+current_time
    folder_link = web_link+ str(chip)+current_time
    Jc = d.chip_Jc(chip)
    
    # take sweeps
    _= ic.get_Ic_Iret_and_save(folder, folder_link, chip, devices, Jc, optionalIc)
                               
def measure_JJs_Rn(chip, devices):
    '''
    Takes just the normal resistance sweep for the JJs, saves images but does 
    not add to the database
    
    :param chip: Target chip
    
    :param devices: Array of target devices

    Calls:
        
        -Measure_Rn-Measure_Rn_Imax
    '''
    folder = (dirname+ str(chip)+time.strftime("_%Y-%m-%d_%H-%M-%S"))


    # take sweeps
    Rn_measurements, Imax_measurements = rn.get_Rn_Imax(folder, chip, devices)

#TODO add to front end. @ ted we do use this one
def resistancetime(chip,devices):
    '''
    Runs indefinitely until told to stop or ~10 minute max runtime
    '''
    '''
    Pick a device to use, use a 1ma current and just run continously with live plotting
    with an Crossbar device
    '''

    device=[]
    count=0    
    for i in range(0, len(devices)):
        if devices[i].device_type == 'Crossbar':
           count+=1
           if count >=4:
               device=devices[i]
               break 
    m3b.continousresist(chip,device)
            
def resistancetemp(chip,devices,save):
    
    current_time = time.strftime("_%Y-%m-%d_%H-%M-%S_Temp")
    folder = dirname+ str(chip)+current_time
    folder_link = web_link+ str(chip)+current_time
    print("Weblink: %s" %folder_link)
    crossbars=[]   
    for i in range(0, len(devices)):
        if devices[i].device_type == 'Crossbar':
           crossbars.append(devices[i])

    m3b.continousResistTemp(chip,crossbars,folder,save)
    

def measure_PCM3b_warm(chip,devices):
    '''
    For all metal layers, sweep 0-3ma
    For all RS arrays measuring at 3 distinct points
    No Tests for Vias

    '''
    current_time = time.strftime("_%Y-%m-%d_%H-%M-%S_warm")
    folder = dirname+ str(chip)+current_time
    folder_link = web_link+ str(chip)+current_time
    print("Weblink: %s" %folder_link)
    
    # sort the devices into Junctions, Resistors, and Vias
    
    CrossBars = []
    RSs = []
    Vias = []
    
        
    for i in range(0, len(devices)):
        if devices[i].device_type == 'Crossbar':
            CrossBars.append(devices[i])
        elif devices[i].device_type == 'Via':
            Vias.append(devices[i])
        else:
            RSs.append(devices[i])        
    #Crossbar meas function here
    m3b.measure_PCM3b_Crossbars(folder,folder_link,chip,CrossBars,True)
    #RS meas func here
    m3b.measure_PCM3b_RS(folder,folder_link,chip,RSs,True)
    
    
    '''
    Add save functions here
    '''
    #d.save_JJ_measurements
def measure_PCM3b_cold(chip,devices,fourk):
    '''
    For all metal layers, sweep 0-3ma-10K
    For all RS arrays measuring at 3 distinct points-4K
    For all vias, just can do a sweep to 100ma looking for discontinuity-4K
    '''
    current_time = time.strftime("_%Y-%m-%d_%H-%M-%S_cold")
    folder = dirname+ str(chip)+current_time
    folder_link = web_link+ str(chip)+current_time
    print("Weblink: %s" %folder_link)
    
    # sort the devices into Junctions, Resistors, and Vias
    
    CrossBars = []
    RSs = []
    Vias = []
    
        
    for i in range(0, len(devices)):
        if devices[i].device_type == 'Crossbar':
            CrossBars.append(devices[i])
        elif devices[i].device_type == 'Via':
            Vias.append(devices[i])
        else:
            RSs.append(devices[i])
    '''
    Resistance Measures
    '''
    if fourk:
    
    #RS meas func here
    
        m3b.measure_PCM3b_RS(folder,folder_link,chip,RSs,False)
        m3b.measure_PCM3B_Vias(folder,folder_link,chip,Vias)
    else:
        m3b.measure_PCM3b_Crossbars(folder,folder_link,chip,CrossBars,False)

def measureRS(chip,devices,warm):
    if warm:
        current_time = time.strftime("_%Y-%m-%d_%H-%M-%S_warm")
    else:
        current_time = time.strftime("_%Y-%m-%d_%H-%M-%S_cold")
    folder = dirname+ str(chip)+current_time
    folder_link = web_link+ str(chip)+current_time
    print("Weblink: %s" %folder_link)
    oddgraphs= m3b.measure_PCMRS(folder,folder_link,chip,devices,warm)
    return oddgraphs

def measureSQUID(chip,devices):
    current_time = time.strftime("_%Y-%m-%d_%H-%M-%S_cold")
    folder = dirname+ str(chip)+current_time
    folder_link = web_link+ str(chip)+current_time
    print("Weblink: %s" %folder_link)
    
    SQUIDS = [] #Only measure SQUIDS
    for i in range(0, len(devices)):
        if devices[i].device_type == 'SQUID':
            SQUIDS.append(devices[i])
            
    msq.measure_SQUID_IV_no_flux(folder,folder_link,chip,SQUIDS,True,False,0,0,0)
    msq.measure_SQUID_periodicity(folder,folder_link,chip,SQUIDS,True,False,0,0,0,0)
    msq.measure_SQUID_IV_with_flux(folder,folder_link,chip,SQUIDS,True,True,False,0,0,0,0,0,0)

def measure_iv_SQUID(chip, devices, save, min_Ibias, max_Ibias, step_Ibias):
    current_time = time.strftime("_%Y-%m-%d_%H-%M-%S_cold")
    folder = dirname+ str(chip)+current_time
    folder_link = web_link+ str(chip)+current_time
    print("Weblink: %s" %folder_link)
    
    SQUIDS = [] #Only measure SQUIDS
    for i in range(0, len(devices)):
        if devices[i].device_type == 'SQUID':
            SQUIDS.append(devices[i])
    
    msq.measure_SQUID_IV_no_flux(folder,folder_link,chip,SQUIDS,save,True,min_Ibias,max_Ibias,step_Ibias)
    
def measure_periodicity_SQUID(chip, devices, save, minIflux, maxIflux, step, Ibias):
    current_time = time.strftime("_%Y-%m-%d_%H-%M-%S_cold")
    folder = dirname+ str(chip)+current_time
    folder_link = web_link+ str(chip)+current_time
    print("Weblink: %s" %folder_link)
    
    SQUIDS = [] #Only measure SQUIDS
    for i in range(0, len(devices)):
        if devices[i].device_type == 'SQUID':
            SQUIDS.append(devices[i])
    
    msq.measure_SQUID_periodicity(folder,folder_link,chip,SQUIDS,save,True,minIflux,maxIflux,step,Ibias)
    
def measure_iv_flux_SQUID(chip,device, save, down, min_Iflux, max_Iflux, step_Iflux, min_Ibias, max_Ibias, step_Ibias):
    current_time = time.strftime("_%Y-%m-%d_%H-%M-%S_cold")
    folder = dirname+ str(chip)+current_time
    folder_link = web_link+ str(chip)+current_time
    print("Weblink: %s" %folder_link)
    a,b,c,window=msq.measure_SQUID_IV_with_flux(folder,folder_link,chip,device,save,down,True,min_Iflux,max_Iflux,step_Iflux,min_Ibias,max_Ibias,step_Ibias)
    return a,b,c,folder,window
    
def copy_design():
    '''
    Copies a design, allowing mass copying of device
    
    '''
    designs = d.show_all_designs()
    
    for i in range(0,len(designs)):
        print("%s: %s"%(i, designs[i].name))
    
    print("c: cancel\n")
    inp = input("Please enter the number of the design you wish to copy:\n")
    
    if inp=='c':
        return
    
    try:
        inp = (int)(inp)
    except:
        print("wrong")
        return
        
    des_id = designs[inp].id
    rv = d.copy_design(des_id)
    
    if rv==0:
        print("Success")
    else:
        print("Something went wrong")

