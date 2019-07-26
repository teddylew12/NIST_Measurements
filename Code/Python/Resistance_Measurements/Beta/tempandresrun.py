# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 08:42:53 2019

@author: volt
"""


def tempandresrun(app,curve,card1,card2,channel1,channel2,target,PID,manual):
    '''
    Written by Nathan. This is a temporary backup of the tempandresrun function
    Inputs:
    :param app, curve: (both pyqtgraph constructs)
    
    :param current_point: pyqtgraph contruct used to plot current point
       
    :param card1, card2: Target Cards 1 and 2
   
    :param channel1,channel 2: Target Channels
     
    :Graphs: Updates a live plot with current on x axis, voltage on y axis
    '''
    global go
    go = 1
    currentlevel=1e-3 #We will constantly output 1 mA
    Irange = 1e-02
    compliance_voltage = 2.
    
    #Initialize voltmeter, current source, and switch matrix
    Voltmeter = vf.get_voltage()
    CurrentSource = vf.get_current()
    Switch = vf.get_switch()
    vf.intialize_switch_all(Switch)
    
    vf.intialize_current_yoko(CurrentSource, Irange, compliance_voltage)
    time.sleep(0.2)
    vf.intialize_voltage(Voltmeter, nplc, Vrange)
    vf.close_channel(Switch, card1, channel1) # instead of card, used to be 1
    time.sleep(0.2)
    vf.close_channel(Switch, card2, channel2) # instead of card, used to be 1
    time.sleep(0.2)
    vf.turnon_current_yoko(CurrentSource)    
    time.sleep(0.2)    
    vf.open_short(Switch, card1, shorts)    
    time.sleep(.2)
    
    down_curve = curve[0]
    up_curve = curve[1]
    lake=vf.getLake()
    #Initialize temperature controller
    vf.setManualOutput(lake,manual)
    vf.setTempSetpoint(lake,7.9)
    vf.setPID(lake,3,1000,0)
    vf.setRange(lake,1)
    
    #T_values=[4.2]
   # R_values=[0]
    #timevals=[0]
    T_values1 =[]
    R_values1 =[]
  #  
    T_values2 =[]
    R_values2 =[]

    stillrunning = True
    passage = 0
    first1 = True
    current_setpoint = 7.9
    #count = 0
    #start_time=time.time()
    offset = vf.read_voltage_fast(Voltmeter, VDwellTime)
    vf.set_current_fast_yoko(CurrentSource,currentlevel) #Set the current source to one constant value initially
    print("Temperature sweep up on channels %d and %d"%(channel1,channel2))
    empty=True
    while stillrunning and passage<600: #Runs until with 100mK of target temp
        #print('\nChannel %d:%d Constant Current:'%(channel1,channel2))
        try:
            if not empty and abs(T_values1[-1] - float(target)) < 0.1:
                break
            V = vf.read_voltage_fast(Voltmeter, VDwellTime) - offset
            T = vf.getTempK(lake)
            #passage=time.time()-start_time
            
            if abs(T-current_setpoint) < 0.01:
                if first1:
                    vf.setPID(lake, 3, 100, 0)
                    first1=False
                current_setpoint += 0.01
                vf.setTempSetpoint(lake, current_setpoint)
            
            #timevals.append(passage)
            R_values1.append(float(V)/float(currentlevel))
            T_values1.append(T)              
            empty=False
            up_curve.setData(T_values1,R_values1,symbol='o',symbolBrush='w',symbolSize=5)            
            app.processEvents()
            
            if go == 0: #Asynchronous safe exit
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                vf.safe_temp_controller(lake)
                stillrunning=False
  
        except KeyboardInterrupt:
                print("\nExiting...\n")
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                stillrunning=False

    #vf.setTempSetpoint(lake,9) #Turn off the temperature controller after getting up to target temp
    print("Temperature sweep down on channels %d and %d"%(channel1,channel2))
    empty=True
    #first1 = True; first2 = True; first3 = True; first4 = True; first5 = True;
    while stillrunning and passage<600: #Runs until the temp is back below 4.5K
        try:
            if not empty and abs(T_values2[-1] - 7.9) < 0.1:
                break
            V = vf.read_voltage_fast(Voltmeter, VDwellTime)
            T = vf.getTempK(lake)
            #passage=time.time()-start_time
            
            if abs(T-current_setpoint) < 0.01:
                current_setpoint -= 0.01
                vf.setTempSetpoint(lake, current_setpoint)
            
            R_values2.append(float(V)/float(currentlevel))
            T_values2.append(T)              
            empty=False
            down_curve.setData(T_values2,R_values2,symbol='o',symbolBrush='r',symbolSize=5)            
            app.processEvents()
            
            if go == 0: #Asynchronous safe exit
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                vf.safe_temp_controller(lake)
                stillrunning=False
  
        except KeyboardInterrupt:
                print("\nExiting...\n")
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                stillrunning=False

    #Put the voltmeter, switch matrix, and current source back in safe configurations
    vf.set_current_fast_yoko(CurrentSource, 0)
    time.sleep(.2)
    vf.close_short(Switch, card1, shorts)
    time.sleep(.2)
    if channel1 != 10:
        vf.open_channel(Switch,card1,channel1)
        vf.open_channel(Switch,card2,channel2)
        
    vf.safe_temp_controller(lake)
    
    Tc=findTc(R_values1,T_values1,R_values2,T_values2)
    R_values=R_values1+R_values2
    T_values=T_values1+T_values2
    return R_values,T_values,Tc


def tempandresrun(app,curve,card1,card2,channel1,channel2,target,PID,manual):
    '''
    Written by Nathan
    Inputs:
    :param app, curve: (both pyqtgraph constructs)
    
    :param current_point: pyqtgraph contruct used to plot current point
       
    :param card1, card2: Target Cards 1 and 2
   
    :param channel1,channel 2: Target Channels
     
    :Graphs: Updates a live plot with current on x axis, voltage on y axis
    '''
    global go
    go = 1
    currentlevel=1e-3 #We will constantly output 1 mA
    Irange = 1e-02
    compliance_voltage = 2.
    
    #Initialize voltmeter, current source, and switch matrix
    Voltmeter = vf.get_voltage()
    CurrentSource = vf.get_current()
    Switch = vf.get_switch()
    vf.intialize_switch_all(Switch)
    
    vf.intialize_current_yoko(CurrentSource, Irange, compliance_voltage)
    time.sleep(0.2)
    vf.intialize_voltage(Voltmeter, nplc, Vrange)
    vf.close_channel(Switch, card1, channel1) # instead of card, used to be 1
    time.sleep(0.2)
    vf.close_channel(Switch, card2, channel2) # instead of card, used to be 1
    time.sleep(0.2)
    vf.turnon_current_yoko(CurrentSource)    
    time.sleep(0.2)    
    vf.open_short(Switch, card1, shorts)    
    time.sleep(.2)
    
    down_curve = curve[0]
    up_curve = curve[1]
    lake=vf.getLake()
    
    '''
    #Initialize temperature controller
    vf.setManualOutput(lake,manual)
    vf.setTempSetpoint(lake,7.9)
    vf.setPID(lake,3,1000,0)
    vf.setRange(lake,1)
    '''
    #T_values=[4.2]
   # R_values=[0]
    #timevals=[0]
    T_values1 =[]
    R_values1 =[]
  #  
    T_values2 =[]
    R_values2 =[]

    stillrunning = True
    passage = 0
    first1 = True
    current_setpoint = 7.9
    #count = 0
    #start_time=time.time()
    offset = vf.read_voltage_fast(Voltmeter, VDwellTime)
    vf.set_current_fast_yoko(CurrentSource,currentlevel) #Set the current source to one constant value initially
    print("Temperature sweep up on channels %d and %d"%(channel1,channel2))
    empty=True
    
    '''
    #First loop gets gets a guess for the Tc
    while stillrunning and passage<600: #Runs until with 100mK of target temp
        #print('\nChannel %d:%d Constant Current:'%(channel1,channel2))
        try:
            if not empty and abs(T_values1[-1] - float(target)) < 0.1:
                break
            V = vf.read_voltage_fast(Voltmeter, VDwellTime) - offset
            T = vf.getTempK(lake)
            #passage=time.time()-start_time
            
            if abs(T-current_setpoint) < 0.1:
                if first1:
                    vf.setPID(lake, 3, 100, 0)
                    first1=False
                current_setpoint += 0.1
                vf.setTempSetpoint(lake, current_setpoint)
            
            #timevals.append(passage)
            R = float(V)/float(currentlevel)
            if R > 0.01:
                guess_Tc = T
                target = guess_Tc + 0.12
                vf.setPID(lake, 3, 200, 0)
                vf.setTempSetpoint(lake, guess_Tc - 0.02)
                while not abs(vf.getTempK(lake) - (guess_Tc - 0.02)) < 0.01:
                    pass
                vf.setPID(lake, 3, 20, 0) #PID for slow sweeps
                break
            
            R_values1.append(R)
            T_values1.append(T)              
            empty=False
            up_curve.setData(T_values1,R_values1,symbol='o',symbolBrush='w',symbolSize=5)            
            app.processEvents()
            
            if go == 0: #Asynchronous safe exit
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                vf.safe_temp_controller(lake)
                stillrunning=False
  
        except KeyboardInterrupt:
                print("\nExiting...\n")
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                stillrunning=False

    #second loop sweeps the temperature up to target slowly
    empty = True; R_values1 = []; T_values1 = []
    current_setpoint = guess_Tc
    vf.setTempSetpoint(lake, current_setpoint)
    
    while stillrunning and passage<600: 
        try:
            if not empty and abs(T_values1[-1] - float(target) + 0.01) < 0.01:
                break
            V = vf.read_voltage_fast(Voltmeter, VDwellTime) - offset
            T = vf.getTempK(lake)
            #passage=time.time()-start_time
            
            if abs(T-current_setpoint) < 0.01:
                current_setpoint += 0.01
                vf.setTempSetpoint(lake, current_setpoint)
            
            #timevals.append(passage)
            R_values1.append(float(V)/float(currentlevel))
            T_values1.append(T)              
            empty=False
            up_curve.setData(T_values1,R_values1,symbol='o',symbolBrush='w',symbolSize=5)            
            app.processEvents()
            
            if go == 0: #Asynchronous safe exit
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                vf.safe_temp_controller(lake)
                stillrunning=False
  
        except KeyboardInterrupt:
                print("\nExiting...\n")
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                stillrunning=False

    #vf.setTempSetpoint(lake,9) #Turn off the temperature controller after getting up to target temp
    print("Temperature sweep down on channels %d and %d"%(channel1,channel2))
    empty=True
    while stillrunning and passage<600: #Runs until the temp is back below 4.5K
        try:
            if not empty and abs(T_values2[-1] - guess_Tc - 0.01) < 0.01:
                break
            V = vf.read_voltage_fast(Voltmeter, VDwellTime)
            T = vf.getTempK(lake)
            #passage=time.time()-start_time
            
            if abs(T-current_setpoint) < 0.01:
                current_setpoint -= 0.01
                vf.setTempSetpoint(lake, current_setpoint)
            
            R_values2.append(float(V)/float(currentlevel))
            T_values2.append(T)              
            empty=False
            down_curve.setData(T_values2,R_values2,symbol='o',symbolBrush='r',symbolSize=5)            
            app.processEvents()
            
            if go == 0: #Asynchronous safe exit
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                vf.safe_temp_controller(lake)
                stillrunning=False
  
        except KeyboardInterrupt:
                print("\nExiting...\n")
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                stillrunning=False
    '''
    
    #manual control
    while stillrunning and passage<600: #Runs until with 100mK of target temp
        #print('\nChannel %d:%d Constant Current:'%(channel1,channel2))
        try:
            V = vf.read_voltage_fast(Voltmeter, VDwellTime)
            R = float(V)/float(currentlevel)   
            T = vf.getTempK(lake)
            R_values1.append(R)
            T_values1.append(T)              
            #empty=False
            up_curve.setData(T_values1,R_values1,symbol='o',symbolBrush='w',symbolSize=5)            
            app.processEvents()
            
            if go == 0: #Asynchronous safe exit
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                vf.safe_temp_controller(lake)
                stillrunning=False
  
        except KeyboardInterrupt:
                print("\nExiting...\n")
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                stillrunning=False
                

    #Put the voltmeter, switch matrix, and current source back in safe configurations
    vf.set_current_fast_yoko(CurrentSource, 0)
    time.sleep(.2)
    vf.close_short(Switch, card1, shorts)
    time.sleep(.2)
    if channel1 != 10:
        vf.open_channel(Switch,card1,channel1)
        vf.open_channel(Switch,card2,channel2)
        
    vf.safe_temp_controller(lake)
    
    Tc=findTc(R_values1,T_values1,R_values2,T_values2)
    R_values=R_values1+R_values2
    T_values=T_values1+T_values2
    return R_values,T_values,Tc


#Really slow version
def tempandresrun(app,curve,card1,card2,channel1,channel2,target,PID,manual):
    '''
    Written by Nathan
    Inputs:
    :param app, curve: (both pyqtgraph constructs)
    
    :param current_point: pyqtgraph contruct used to plot current point
       
    :param card1, card2: Target Cards 1 and 2
   
    :param channel1,channel 2: Target Channels
     
    :Graphs: Updates a live plot with current on x axis, voltage on y axis
    '''
    global go
    go = 1
    currentlevel=1e-3 #We will constantly output 1 mA
    Irange = 1e-02
    compliance_voltage = 2.
    
    import pdb; pdb.set_trace()
    #Initialize voltmeter, current source, and switch matrix
    Voltmeter = vf.get_voltage()
    CurrentSource = vf.get_current()
    Switch = vf.get_switch()
    vf.intialize_switch_all(Switch)
    
    vf.intialize_current_yoko(CurrentSource, Irange, compliance_voltage)
    time.sleep(0.2)
    vf.intialize_voltage(Voltmeter, nplc, Vrange)
    vf.close_channel(Switch, card1, channel1) # instead of card, used to be 1
    time.sleep(0.2)
    vf.close_channel(Switch, card2, channel2) # instead of card, used to be 1
    time.sleep(0.2)
    vf.turnon_current_yoko(CurrentSource)    
    time.sleep(0.2)    
    vf.open_short(Switch, card1, shorts)    
    time.sleep(0.2)
    
    down_curve = curve[0]
    up_curve = curve[1]
    lake=vf.getLake()
    time.sleep(0.2)
    
    
    #Initialize temperature controller
    vf.setManualOutput(lake,manual)
    vf.setTempSetpoint(lake,7.9)
    vf.setPID(lake,3,1000,0)
    vf.setRange(lake,1)

    #T_values=[4.2]
   # R_values=[0]
    #timevals=[0]
    T_values1 =[]
    R_values1 =[]
  #  
    T_values2 =[]
    R_values2 =[]

    stillrunning = True
    passage = 0
    first1 = True
    current_setpoint = 7.9
    #count = 0
    #start_time=time.time()
    offset = vf.read_voltage_fast(Voltmeter, VDwellTime)
    vf.set_current_fast_yoko(CurrentSource,currentlevel) #Set the current source to one constant value initially
    print("Temperature sweep up on channels %d and %d"%(channel1,channel2))
    empty=True
    
    
    #First loop gets gets a guess for the Tc
    while stillrunning and passage<600: #Runs until with 100mK of target temp
        #print('\nChannel %d:%d Constant Current:'%(channel1,channel2))
        try:
            if not empty and abs(T_values1[-1] - float(target)) < 0.1:
                break
            V = vf.read_voltage_fast(Voltmeter, VDwellTime) - offset
            T = vf.getTempK(lake)
            #passage=time.time()-start_time
            
            if abs(T-current_setpoint) < 0.1:
                if first1:
                    vf.setPID(lake, 3, 100, 0)
                    first1=False
                current_setpoint += 0.1
                vf.setTempSetpoint(lake, current_setpoint)
            
            #timevals.append(passage)
            R = float(V)/float(currentlevel)
            if R > 0.1:
                guess_Tc = T
                target = guess_Tc + 0.12
                vf.setPID(lake, 3, 200, 0)
                vf.setTempSetpoint(lake, guess_Tc - 0.02)
                while not abs(vf.getTempK(lake) - (guess_Tc - 0.02)) < 0.01:
                    pass
                vf.setPID(lake, 3, 20, 0) #PID for slow sweeps
                break
            
            R_values1.append(R)
            T_values1.append(T)              
            empty=False
            up_curve.setData(T_values1,R_values1,symbol='o',symbolBrush='w',symbolSize=5)            
            app.processEvents()
            
            if go == 0: #Asynchronous safe exit
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                vf.safe_temp_controller(lake)
                stillrunning=False
  
        except KeyboardInterrupt:
                print("\nExiting...\n")
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                stillrunning=False
           
    empty = True; R_values1 = []; T_values1 = []
    print("Finished first guess: %d K", guess_Tc)
    current_setpoint = guess_Tc
    vf.setTempSetpoint(lake, current_setpoint)
    
    #Second loop gets a better guess for the Tc
    while stillrunning and passage<600: #Runs until with 100mK of target temp
        #print('\nChannel %d:%d Constant Current:'%(channel1,channel2))
        try:
            if not empty and abs(T_values1[-1] - float(target)) < 0.01:
                break
            V = vf.read_voltage_fast(Voltmeter, VDwellTime) - offset
            T = vf.getTempK(lake)
            #passage=time.time()-start_time
            
            if abs(T-current_setpoint) < 0.01:
                if first1:
                    vf.setPID(lake, 3, 200, 0)
                    first1=False
                current_setpoint += 0.01
                vf.setTempSetpoint(lake, current_setpoint)
            
            #timevals.append(passage)
            R = float(V)/float(currentlevel)
            if R > 0.1:
                guess_Tc = T-0.005
                target = guess_Tc + 0.022
                vf.setTempSetpoint(lake, guess_Tc)
                vf.setPID(lake, 3, 1000, 0)
                break
            
            R_values1.append(R)
            T_values1.append(T)              
            empty=False
            up_curve.setData(T_values1,R_values1,symbol='o',symbolBrush='w',symbolSize=5)            
            app.processEvents()
            
            if go == 0: #Asynchronous safe exit
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                vf.safe_temp_controller(lake)
                stillrunning=False
  
        except KeyboardInterrupt:
                print("\nExiting...\n")
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                stillrunning=False
    
    #third loop sweeps the temperature up to target slowly
    empty = True; R_values1 = []; T_values1 = []
    current_setpoint = guess_Tc
    print("Finished second guess: %d K", guess_Tc)
    #vf.setTempSetpoint(lake, current_setpoint)
    start_time = time.time()
    while stillrunning and passage<600: 
        try:
            if not empty and abs(T_values1[-1] - target) < 0.003:
                break
            
            T = vf.getTempK(lake)
            #passage=time.time()-start_time
            
            if abs(T-current_setpoint) < 0.002:
                persistence = time.time()-start_time
            else:
                start_time = time.time()
                persistence = 0
                
                
            if persistence > 30:
                current_setpoint += 0.001
                V = vf.read_voltage_fast(Voltmeter, VDwellTime) - offset
                vf.setTempSetpoint(lake, current_setpoint)
                R_values1.append(float(V)/float(currentlevel))
                T_values1.append(T)              
                empty=False
                up_curve.setData(T_values1,R_values1,symbol='o',symbolBrush='w',symbolSize=5)
                print("Added point with T = %d K, R = %d ohms with persistence of %d seconds", T, R, persistence)
                persistence = 0
                app.processEvents()
            
            if go == 0: #Asynchronous safe exit
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                vf.safe_temp_controller(lake)
                stillrunning=False
  
        except KeyboardInterrupt:
                print("\nExiting...\n")
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                stillrunning=False

    #fourth loop sweeps down
    #vf.setTempSetpoint(lake,9) #Turn off the temperature controller after getting up to target temp
    empty = True
    
    print("Temperature sweep down on channels %d and %d"%(channel1,channel2))
    empty=True
    while stillrunning and passage<600: #Runs until the temp is back below 4.5K
        try:
            if not empty and abs(T_values2[-1] - target) < 0.003:
                break
            
            T = vf.getTempK(lake)
            
            if abs(T-current_setpoint) < 0.002:
                persistence = time.time()-start_time
            else:
                start_time = time.time()
                persistence = 0
                
            
            if persistence > 30:
                current_setpoint -= 0.001
                V = vf.read_voltage_fast(Voltmeter, VDwellTime) - offset
                vf.setTempSetpoint(lake, current_setpoint)
                R_values1.append(float(V)/float(currentlevel))
                T_values1.append(T)              
                empty=False
                down_curve.setData(T_values1,R_values1,symbol='o',symbolBrush='w',symbolSize=5)
                print("Added point with T = %d K, R = %d ohms with persistence of %d seconds", T, R, persistence)
                persistence = 0
                app.processEvents()
            
            if go == 0: #Asynchronous safe exit
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                vf.safe_temp_controller(lake)
                stillrunning=False
  
        except KeyboardInterrupt:
                print("\nExiting...\n")
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                stillrunning=False
        
    '''manual control
    while stillrunning and passage<600: #Runs until with 100mK of target temp
        #print('\nChannel %d:%d Constant Current:'%(channel1,channel2))
        try:
            V = vf.read_voltage_fast(Voltmeter, VDwellTime)
            R = float(V)/float(currentlevel)   
            T = vf.getTempK(lake)
            R_values1.append(R)
            T_values1.append(T)              
            #empty=False
            up_curve.setData(T_values1,R_values1,symbol='o',symbolBrush='w',symbolSize=5)            
            app.processEvents()
            
            if go == 0: #Asynchronous safe exit
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                vf.safe_temp_controller(lake)
                stillrunning=False
  
        except KeyboardInterrupt:
                print("\nExiting...\n")
                exitfunc(Switch, CurrentSource, card1, card2, channel1, channel2)
                stillrunning=False
                '''

    #Put the voltmeter, switch matrix, and current source back in safe configurations
    vf.set_current_fast_yoko(CurrentSource, 0)
    time.sleep(.2)
    vf.close_short(Switch, card1, shorts)
    time.sleep(.2)
    if channel1 != 10:
        vf.open_channel(Switch,card1,channel1)
        vf.open_channel(Switch,card2,channel2)
        
    vf.safe_temp_controller(lake)
    
    Tc=findTc(R_values1,T_values1,R_values2,T_values2)
    R_values=R_values1+R_values2
    T_values=T_values1+T_values2
    return R_values,T_values,Tc