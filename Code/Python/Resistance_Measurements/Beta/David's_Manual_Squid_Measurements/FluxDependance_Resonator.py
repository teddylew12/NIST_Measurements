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
import matplotlib.pyplot as plt
import numpy as np
import time
#from pygame import mixer


#app = QtGui.QApplication([])

#=================================
#Global variables
#=================================
#address_I = 12
address_I_yoko_GS200 = 2
address_NWA=30
Fluxrange = 2e-03
compliance_voltage=10
path = 'D:\DATA\StackJunctions_2017_10_24\CHIP33\RESONATOR6\\'

#=================================
#Function definitions
#=================================  

def test():
    print('working')

def Resonator_Sweep_Flux(I_min, I_max, step, *args):
    """
    flux dependance of resonators 
    """
    global Fluxrange 
    
    downswitch = args[0]
    print(path)

    
    ##VARIABLE DECLARATIONS##
    #Going to use lists to start with for flexibility, even though slower than arrays
    I_values = []
    
    NWA=vf.get_NWA(address_NWA)
    
   
    
    ##INITIALIZATION OF HARDWARE##    
    CurrentSource= vf.get_current(address_I_yoko_GS200)
    vf.intialize_current_yoko_GS200(CurrentSource, Fluxrange, compliance_voltage)
    vf.set_current_fast_yoko_GS200(CurrentSource, 0)
    NWA.write('SENS1:AVER:CLE')
    time.sleep(4)
    freq0,data0=vf.get_traces(NWA,1)
    
    plt.figure(1)
    plt.plot(freq0[0,:],data0[0,:])
    plt.hold(False)
    vf.save_data_NWA(freq0,data0,path,'fluxdependance_off.txt')

    # measure zero field resonance
    
    counter=0
    #Sweep Current up
    print('Starting sweep up')
    for I in np.arange(I_min, I_max+step, step):
        vf.set_current_fast_yoko_GS200(CurrentSource, I)
        NWA.write('SENS1:AVER:CLE')
        time.sleep(4)
        freq,data=vf.get_traces(NWA,1)
        plt.figure(1)
        plt.show() 
        plt.plot(freq[0,:],data[0,:],freq0[0,:],data0[0,:])
        plt.pause(0.1)
        plt.draw()
        vf.save_data_NWA(freq,data,path,'fluxdependance_%s.txt' %counter)
        counter=counter+1
        I_values.append(I)            
        name = path + 'fluxvalues.txt'
        np.savetxt(name, I_values, header = 'flux values')
        
    if downswitch :
        print('Starting sweep down')
        #Sweep Current down
        for I in np.arange(I_max-step, I_min, -step):
            vf.set_current_fast_yoko_GS200(CurrentSource, I)
            NWA.write('SENS1:AVER:CLE')
            time.sleep(8)
            freq,data=vf.get_traces(NWA,1)
            plt.figure(1)
            plt.plot(freq[0,:],data[0,:],freq0[0,:],data0[0,:])
            plt.pause(0.1)
            plt.draw()
            vf.save_data_NWA(freq,data,path,'fluxdependance_%s.txt' %counter)
            counter=counter+1
            I_values.append(I)            
            name = path + 'fluxvalues.txt'
            np.savetxt(name, I_values, header = 'flux values')

            
    print("Exited current sweep")
    vf.set_current_fast_yoko_GS200(CurrentSource, 0)
    time.sleep(.1)
    
 
