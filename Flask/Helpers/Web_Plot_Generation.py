# -*- coding: utf-8 -*-
"""
Created on Thu Mar 22 11:27:18 2018

@author: sdk

helpers

"""

from Helpers import database_for_flask as d
#import database_for_flask as d
import numpy as np
import math

def find_D(name, chipname):
    """ Function to search a long share point link and find the important stuff

    :param name: the link
    
    :returns: the index of the start of the data directy name
    """
    i = -1
    while(1):
        if (abs(i)>len(name)):
            return -1
        if (name[i]==chipname[0]):
            # this will break in 2020 I guess
            if (name[i+1]=="1"):
                break
        
        i =  i-1
        
    
    return i

def get_directories(chip, given_dir):
    """ Gets the directories where the data for a chip is stored in

    :param chip: chip to find all the data directories for
    :param given_dir: a place to start searching, can be None
    
    :returns: array of directory strings
    """
    
    if not given_dir:
        full_directories = d.get_data_directory(chip)
    else:
        full_directories = [given_dir]
    
    directories = []


    # get the important part of each full weblink
    
    if full_directories != -1:
        for directory in full_directories:
            d_location = find_D(directory, chip.name)
            
            if d_location==-1:
                return -1
            
            directories.append(directory[d_location:])
    else:
        print("\nERROR: for chip %s"%chip.name)
    
    return directories


# old?
def get_rawdata(chip, devices, given_dir=None, rn=False):
    from urllib.request import urlopen
    
#    if not given_dir:
#        full_directories = d.get_data_directory(chip)
#    else:
#        full_directories = [given_dir]
#    
#    directories = []
#    
#    # get the important part of each full weblink
#    for directory in full_directories:
#        d_location = find_D(directory)
#        
#        if d_location==-1:
#            return -1
#        
#        directories.append(directory[d_location:])
        
    directories = get_directories(chip, given_dir)
    if directories == -1:
        return -1

    
    devices_notfound = []
    for dev in devices:
        devices_notfound.append(dev)
        
    rawdata_files = []
    for directory in directories:
        path = "http://132.163.82.9:3000/"
        if rn:
            path = path + directory + "/RawData_Rn/" + chip.name + "_"
        else:
            path = path + directory + "/RawData/" + chip.name + "_"
        
        for dev in devices: 
            size = dev.JJ_radius_nom
            
            raw_path = path + dev.name + "_" + (str)(size)
            
            if rn:
                raw_data_filename = raw_path + "_Rn_raw.dat"
            else:
                raw_data_filename = raw_path + "_Ic_raw.dat"
           
            
            if dev in devices_notfound:
                try: 
                    raw_file = urlopen(raw_data_filename, timeout = 5)
                    # found file
                    
                    rawdata_files.append(raw_file)
                    devices_notfound.remove(dev)
               
                
                except:
                    rawdata_files.append([])
            
    data = format_data(rawdata_files)
    
    return data


def format_data(files):
    """ Uses numpy to read data from a text file and format it, geared towards highcharts
    
    :param files: The .txt files to get data from
    
    :returns: Multi-layed array, with the lowest level being pairs of I,V points
    """
    import numpy as np
    
    full_data = []
    for file in files:
        try:
            I, V, R = np.loadtxt(file, unpack=True)
            data = []
            for i in range(0,len(I)):
                data.append([I[i],V[i]])
        
            full_data.append(data)
        except:
            full_data.append([])
                
        
    
    return full_data
    

def get_data(chip, devices):
    """ Main function to get the full IV and Rn curves, used by chip_report.
    Also checks the IV curve to see if data is good
    
    :param chip: The chip where data is wanted from
    :param devices: An array of device objects
    
    :returns: Json of format {device:{date:{Ic:{data, worked},Rn:{data}}}}
    """
    from urllib.request import urlopen
    import re
    import pdb
    #get data directories, find d, append dir[d:] to filtered
    # or just call new function below, and split to '_'
    filtered_dirs = get_directories(chip, None)
#    filtered_dirs = ["D180531-F7/2018-06-05_15-38-55", "D180531-F7/2018-06-04_15-38-55"]
    
    full_dir = 'https://nistgov.sharepoint.com/sites/SEG/Shared%20Documents/Forms/AllItems.aspx?newTargetListUrl=%2Fsites%2FSEG%2FShared%20Documents&viewpath=%2Fsites%2FSEG%2FShared%20Documents%2FForms%2FAllItems%2Easpx&id=%2Fsites%2FSEG%2FShared%20Documents%2FSFQ_Circuits_Measurements%2F'


    dates = []
    for direct in filtered_dirs:
        try:
            dates.append('2' + re.split('_2', direct)[1])
#            dates.append(re.split('/', direct)[1])
        except:
            print("returning")
            return

#    device_names = []
#    for dev in devices:
#        device_names.append(dev.name)

    meas = {}
    for dev in devices:
        meas[dev.name] = {}
    
        meas[dev.name]["size"] = dev.JJ_radius_nom
        meas[dev.name]["type"] = dev.device_type
    for dev in devices:
        max_I_crit=0
        max_R=0
        
        for date in dates:
            if dev.name=="A1_1.8" and date=="2018-08-13_13-38-58_cold":
                pdb.set_trace()
            path = "http://132.163.82.9:3000/" + chip.name + "_" + date
#            path = "http://132.163.181.143:9000/" + chip.name + "/" + date + "/"
            
            if dev.name == 'A3_3.9' or dev.name == 'S1_1.5':
                extra_res = True
            # option for rn here
            raw_path = path + "/RawData/"
            crit_path = path + "/Ic_Values/"
            
            raw_path_rn = path + "/RawData_Rn/"
            
            raw_path = raw_path + chip.name + "_" + dev.name + "_" + str(dev.JJ_radius_nom)
			#raw_path =  chip.name + "_" + dev.name + "_" + str(dev.JJ_radius_nom)
            crit_path = crit_path + chip.name + "_" + dev.name + "_" + str(dev.JJ_radius_nom)
            raw_path_rn = raw_path_rn + chip.name + "_" + dev.name + "_" + str(dev.JJ_radius_nom)
            
            # option for rn here
            raw_path = raw_path + "_Ic_raw.dat"
            crit_path = crit_path + "_Ic.dat"
            
            raw_path_rn = raw_path_rn + "_Rn_raw.dat"
            #pdb.set_trace()
            try:
                raw_file = urlopen(raw_path, timeout=3)
                crit_file = urlopen(crit_path, timeout=3)
                #pdb.set_trace()
                if dev.name == 'A3_3.9' or dev.name == 'S1_1.5':    
                    success, data, I_crit = judge_data_from_files(raw_file, crit_file,extra_res=True)
                else:
                    success, data, I_crit = judge_data_from_files(raw_file, crit_file)
#                data = format_data_new(raw_file)
                
                
                
                meas[dev.name][date[:-5]] = {}
                meas_current = meas[dev.name][date[:-5]]
                meas_current["Ic"] = {}
                meas_current["Rn"] = {}
                

                meas_current["Ic"]["data"] = data
                meas_current["Ic"]["worked"] = success
                if I_crit>=max_I_crit:
                    meas_current["Ic"]["crit"] = I_crit
                    
                raw_file_rn = urlopen(raw_path_rn, timeout=3)
                
                data_rn = format_data_new(raw_file_rn)
                
                meas_current["Rn"]["data"] = data_rn
                try:
                    db_meas = d.find_meas_by_dir(date, dev.name, chip.name, partial_dir=True)
                    #meas_current["Rn"]["crit"] = db_meas.Rn
                    
                except Exception as e:
                    db_meas.Rn=0
                    #meas_current["Rn"]["crit"] = 0

                meas_current["Rn"]["crit"] = db_meas.Rn
                if db_meas.Rn < max_R:
                    meas_current["Rn"]["crit"]=0
                else:
                    max_R=db_meas.Rn
                if meas[dev.name][date[:-5]]["Rn"]["crit"] !=max_R:
                    meas[dev.name][date[:-5]]["Rn"].pop("crit")    
#                for date in meas[dev.name]:
                    
#                meas[dev.name][date[:-5]]["data"] = data
#                meas[dev.name][date[:-5]]["worked"] = success
            except Exception as e:
                print(e)
            
           
                           


        

    return meas
            
    
         

def format_data_new(file):
    """ See format_data above
    """
    import numpy as np

    try:
        I, V, R = np.loadtxt(file, unpack=True)
        data = []
        for i in range(0,len(I)):
            data.append([I[i],V[i]])
    except:
        data = [[]]

    return data
    
def format_data_from_raw(I,V):
    data = []
    for i in range(0,len(I)):
        data.append([I[i], V[i]])
    return data

 
def judge_data_and_view(chip, devices):
    """ Decides if an IV was a "good" measurement, shows graphs outlining why
    
    :param chip: The chip
    :param devices: Any devices that the measurements should be checked
    
    :returns: Nothing, but many matplotlib graphs will pop up
    """
    import numpy as np
    import matplotlib.pyplot as plt
    from urllib.request import urlopen


    directories = get_directories(chip, None)
    if directories==-1:
        return -1
    
    for directory in directories:    
#        path = "C:/Users/sdk/Downloads/Serve/" + directory
        path = "http://132.163.82.9:3000/" + directory
        for dev in devices:
            raw_filename = path + "/RawData/" + chip.name + "_" + dev.name + "_" + str(dev.JJ_radius_nom)
            raw_filename = raw_filename + "_Ic_raw.dat"
            
            crit_filename = path + "/Ic_Values/" + chip.name + "_" + dev.name + "_" + str(dev.JJ_radius_nom)
            crit_filename = crit_filename + "_Ic.dat"
            
            #try/except http open set into file
            try:
                raw_file = urlopen(raw_filename, timeout=4)
                crit_file = urlopen(crit_filename, timeout=4)

    
#            raw_file = raw_filename
#            crit_file = crit_filename
            
                try:
                    I,V,R = np.loadtxt(raw_file,unpack=True)
                    I_c, V_c = np.loadtxt(crit_file)
                
                    locations = [i for i,e in enumerate(I) if e==I_c[0] or e==I_c[1]]
                    start = locations[0] + 10
                    end = locations[1] - 10
                    
                    I_sub = I[start:end]
                    V_sub = V[start:end]
                    
                    
                    plt.figure()             
                    plt.plot(I,V)
                    plt.plot(I_sub, V_sub)
                    
                    lin_x = []
                    lin_y = []
                
                    if len(I_sub) == 0:
                        plt.title(dev.name + " is bad")
                    else:
#                        m,b = np.polyfit(I_sub,V_sub,1)
#                        for i in np.arange(I_sub[0]*2, I_sub[-1]*2, I_sub[-1]*2/100):
#                            lin_x.append(i)
#                            lin_y.append(m*i+b)
#                        
#                        plt.plot(lin_x, lin_y)
#                        if abs(b)<5e-6:
#                            if abs(m)<.1*dev.num_JJs:
#                                plt.title(dev.name + " is Good with int " + str(b) + " slope " + str(m))
#                            else:    
#                                plt.title(dev.name + " is bad with slope" + str(m))
#                        else:
#                            plt.title(dev.name + " is bad with int " + str(b))
                        
                        np_V = np.array(V_sub) / dev.num_JJs
                        np_straight = np.zeros(np_V.size)
                        plt.plot(I_sub, np_straight)
                        r = np.sum((np_V - np_straight)**2)
                        plt.title(str(r))
#
                        if r < 1e-10:
                            plt.title("Good")
                        else:
                            plt.title("Bad")
            
                except Exception as e:
                    print(e)
                    pass
            except:
                print("nah")
                pass
 

def judge_data_from_files(raw_file, crit_file, extra_res=False):
    """ Checks to see if IV curve is "good"
    
    :param raw_file: The raw .txt file of the full IV curve
    :param crit_file: The .txt file containing the Ic value
    
    :retunrs: tuple of Bool describing if data is good and formatted data
    """
    import numpy as np
    

    data = []

    try:
        I,V,R = np.loadtxt(raw_file,unpack=True)
        I_c, V_c = np.loadtxt(crit_file)
        
        data = format_data_from_raw(I,V)
    
        #locations = [i for i,e in enumerate(I) if e==I_c[0] or e==I_c[1]]
        locations=[np.argmin(abs(I-I_c[0])),np.argmin(abs(I-I_c[1]))]
        start = locations[0] + 10
        end = locations[1] - 10
        
        if extra_res:
            threshold = 1e-3
            #import pdb; pdb.set_trace()
        else:
            threshold = 1e-06
        
        I_sub = I[start:end]
        V_sub = V[start:end]
        Ic_val=0
        mini=1000
        maxi=-1000
        for i in I_c:
            if i<mini:
                mini=i
            if i>maxi:
                maxi=i
        Ic_val=.5*(maxi-mini)
        print("Ic array:")
        print(I_c)
        
        print("Min %f, max %f , average %f "%(mini,maxi,Ic_val))

        if len(I_sub) == 0:
            pass

        else:
            m,b = np.polyfit(I_sub,V_sub,1)

            if abs(b)<threshold:
                return True, data, Ic_val
            else:
                pass

    except Exception as e:
        print(e)

   
            
    return False, data, Ic_val

    

def my_round(num):
    """ Attempt at a custom rounding function
    NOTE: doesn't work because of scientific notation
    """
    if str(num)[-1] == '5':
        num = float(str(num)[:-1] + '6')
        
    return round(num,8)

def judge_data(chip, devices):
    """ Same as other judge data functions, MAIN one used
    In order to determine if the IV curve was "good", function draws a line
    between Ic_pos and Ic_neg and checks that (1) it is straight enough and (2)
    the y-intercept is close enought to 0
    
    :param chip: The chip
    :param devices: The devices
    
    :returns: working data in json: {device:{Ic:[Ic], Rn:[Rn], size:size, type:device_type}
    """
    import numpy as np
    from urllib.request import urlopen

    Ic_json = {}
    for dev in devices:
        Ic_json[dev.name] = {}
        Ic_json[dev.name]["Ic"] = []
        Ic_json[dev.name]["Rn"] = []
        Ic_json[dev.name]["size"] = dev.JJ_radius_nom
        Ic_json[dev.name]["type"] = dev.device_type

    directories = get_directories(chip, None)
    if directories==-1:
        return -1
    
    filter_dir = 'https://nistgov.sharepoint.com/sites/SEG/Shared%20Documents/Forms/AllItems.aspx?newTargetListUrl=%2Fsites%2FSEG%2FShared%20Documents&viewpath=%2Fsites%2FSEG%2FShared%20Documents%2FForms%2FAllItems%2Easpx&id=%2Fsites%2FSEG%2FShared%20Documents%2FSFQ_Circuits_Measurements%2F'
    
    for directory in directories:    
#        path = "C:/Users/sdk/Downloads/Serve/" 
        path = "http://132.163.82.9:3000/" 
        path = path + directory
        for dev in devices:
            raw_filename = path + "/RawData/" + chip.name + "_" + dev.name + "_" + str(dev.JJ_radius_nom)
            raw_filename = raw_filename + "_Ic_raw.dat"
            
            crit_filename = path + "/Ic_Values/" + chip.name + "_" + dev.name + "_" + str(dev.JJ_radius_nom)
            crit_filename = crit_filename + "_Ic.dat"
            
            Rn_filename = path + "/Rn_Values/" + chip.name + "_" + dev.name + "_" + str(dev.JJ_radius_nom)
            Rn_filename = Rn_filename + "_Rn.dat"
            
            
            #try/except http open set into file
            
#            raw_file = raw_filename
#            crit_file = crit_filename
            
            try:
                raw_file = urlopen(raw_filename, timeout=4)
                crit_file = urlopen(crit_filename, timeout=4)

    
                try:
                    I,V,R = np.loadtxt(raw_file,unpack=True)
                    I_c, V_c = np.loadtxt(crit_file)

                    
                    locations = [i for i,e in enumerate(I) if e==I_c[0] or e==I_c[1]]
                    
                    start = locations[0] + 10
                    end = locations[1] - 10
                    Ic_val=0
                    min=1000
                    max=-1000
                    for i in I_c:
                        if i<min:
                            min=i
                        if i>max:
                            max=i
                    Ic_val=.5*(max-min)
    
                    I_sub = I[start:end]
                    V_sub = V[start:end]
                    
                
                    if len(I_sub) == 0:
                        pass
    
                    else:
                        m,b = np.polyfit(I_sub,V_sub,1)
    
                        if abs(b)<1e-6:
                            
                            try:
#                                print(filter_dir + directory)
                                meas = d.find_meas_by_dir(filter_dir + directory, dev.name, chip.name)
                                Rn = meas.Rn
#                                Rn_file = urlopen(Rn_filename, timeout=3)
#                                
#                                try:
#                                    Rn, Imax = np.loadtxt(Rn_file)
#                                except:
#                                    Rn = -1
                            except:
                                print("Rn not found")
                                Rn = -1
                            
                            Ic_json[dev.name]["Ic"].append(Ic_val)
                            Ic_json[dev.name]["Rn"].append(Rn)
                            
                            
                        else:
                            pass
            
                except:
                    print("nope")
                    pass
            
            except:
                pass
            
    return Ic_json


           
def get_crit_data_old(chips, devices):
    """ MAIN function called by wafer report
    
    :param chips: Array of chips
    :param devices: Array of devices
    
    :returns a fat json: {chip_name:{*see json in judge_data*}}
    """
    meas = {}
    for chip in chips:
        meas[chip.name] = judge_data(chip, devices)
        
    return meas

def get_crit_data(chip_dict):
    meas = {}
    for design_id in chip_dict:
        design = d.find_design(design_id)
        devices = design.device_id
        devices = [dev for dev in devices if dev.num_JJs is not None and dev.num_JJs!=0]

        
        for chip in chip_dict[design_id]:
            meas[chip.name] = judge_data(chip, devices)
            
    return meas
    
        
#Nathan's function for packaging PCM3B data into a dictionary

def get_data_pcm3b(chip_name):
    chip = d.find_chip(chip_name)
    resistor_measurements = chip.resistor_measurements
    via_measurements = chip.via_measurements
    crossbar_measurements = chip.crossbar_measurements


    #Initialize data arrays for crossbars
    RL_RT = [None, None, None, None, None] 
    Rcross_RT = [None, None, None, None, None]
    Rsq_RT = [None, None, None, None, None] #calculated
    Width_RT = [None, None, None, None, None] #calculated
    RL_10K = [None, None, None, None, None]
    Rcross_10K = [None, None, None, None, None] 
    Rsq_10K = [None, None, None, None, None] #calculated
    Width_10K = [None, None, None, None, None] #calculated
    RRR = [None, None, None, None, None] #calculated
    Tc = [None, None, None, None, None]
    Tcsum =[0,0,0,0,0]
    Tccount = [0,0,0,0,0]

    for meas in crossbar_measurements:
        if meas.device_name == 'RS RL':
            RL_RT[0] = meas.R_RT
            RL_10K[0] = meas.R_10K
            if meas.Tc != None:
                Tcsum[0] += meas.Tc
                Tccount[0] += 1
        elif meas.device_name == 'M0 RL':
            RL_RT[1] = meas.R_RT
            RL_10K[1] = meas.R_10K
            if meas.Tc != None:
                Tcsum[1] += meas.Tc
                Tccount[1] += 1
        elif meas.device_name == 'M1 RL':
            RL_RT[2] = meas.R_RT
            RL_10K[2] = meas.R_10K
            if meas.Tc != None:
                Tcsum[2] += meas.Tc
                Tccount[2] += 1
        elif meas.device_name == 'M2 RL':
            RL_RT[3] = meas.R_RT
            RL_10K[3] = meas.R_10K
            if meas.Tc != None:
                Tcsum[3] += meas.Tc
                Tccount[3] += 1
        elif meas.device_name == 'M3 RL':
            RL_RT[4] = meas.R_RT
            RL_10K[4] = meas.R_10K
            if meas.Tc != None:
                Tcsum[4] += meas.Tc
                Tccount[4] += 1
        elif meas.device_name == 'RS Rsq':
            Rcross_RT[0] = meas.R_RT
            Rcross_10K[0] = meas.R_10K
            if meas.Tc != None:
                Tcsum[0] += meas.Tc
                Tccount[0] += 1
        elif meas.device_name == 'M0 Rsq':
            Rcross_RT[1] = meas.R_RT
            Rcross_10K[1] = meas.R_10K
            if meas.Tc != None:
                Tcsum[1] += meas.Tc
                Tccount[1] += 1
        elif meas.device_name == 'M1 Rsq':
            Rcross_RT[2] = meas.R_RT
            Rcross_10K[2] = meas.R_10K
            if meas.Tc != None:
                Tcsum[2] += meas.Tc
                Tccount[2] += 1
        elif meas.device_name == 'M2 Rsq':
            Rcross_RT[3] = meas.R_RT
            Rcross_10K[3] = meas.R_10K
            if meas.Tc != None:
                Tcsum[3] += meas.Tc
                Tccount[3] += 1
        elif meas.device_name == 'M3 Rsq':
            Rcross_RT[4] = meas.R_RT
            Rcross_10K[4] = meas.R_10K
            if meas.Tc != None:
                Tcsum[4] += meas.Tc
                Tccount[4] += 1

    #Calculate the apropriate values for Rsq, Width, and RRR
    for c in range(0,5):
        if Rcross_RT[c] is not None:
            Rsq_RT[c] = round((math.pi / math.log(2)) * Rcross_RT[c], 3)
        if Rcross_10K[c] is not None:
            Rsq_10K[c] = round((math.pi / math.log(2)) * Rcross_10K[c], 3)
        if Rsq_RT[c] is not None and RL_RT[c] is not None:
            Width_RT[c] = round(200 * (Rsq_RT[c] / RL_RT[c]), 3)
        if Rsq_10K[c] is not None and RL_10K[c] is not None:
            Width_10K[c] = round(200 * (Rsq_10K[c] / RL_10K[c]), 3)
        if RL_RT[c] is not None and RL_10K[c] is not None:
            RRR[c] = round(RL_RT[c] / RL_10K[c], 3)
        if Tccount[c] != 0:
            Tc[c] = Tcsum[c] / Tccount[c]

    crossbar_pass = {"RL_RT": RL_RT, "Rsq_RT": Rsq_RT, 
                     "Width_RT": Width_RT, "RL_10K": RL_10K, 
                     "Rsq_10K": Rsq_10K, "Width_10K": Width_10K, 
                     "RRR": RRR, "Tc": Tc}

    #Initialize data arrays for RS arrays
    R_RT = [None, None]
    R_4K = [None, None, None, None, None, None]
    R_256 = [None, None, None, None, None, None] #calculated
    R_27 = [None, None, None, None, None, None] #calculated

    for meas in resistor_measurements:
        if meas.device_name == 'RA750':
            R_RT[0] = meas.R_RT_IV
            R_4K[0] = meas.R_4k_2000uA
            R_4K[1] = meas.R_4k_1000uA
            R_4K[2] = meas.R_4k_500uA
        elif meas.device_name == 'RA1000':
            R_RT[1] = meas.R_RT_IV
            R_4K[3] = meas.R_4k_2000uA
            R_4K[4] = meas.R_4k_1000uA
            R_4K[5] = meas.R_4k_500uA

    for c in range(0,6):
        if R_4K[c] is not None:
            R_256[c] = round(R_4K[c] / 256, 3)
        if R_256[c] is not None:
            R_27[c] = round(R_256[c] / 2.7, 3)

    resistor_pass = {"R_RT": R_RT, "R_4K": R_4K, "R_256": R_256, "R_27": R_27}

    #Initialize data arrays for Via measurements
    R_4K_vias = [None, None, None, None, None]
    Imax = [None, None, None, None, None]

    for meas in via_measurements:
        if meas.device_name == 'M2_I2_M3-1':
            R_4K_vias[4] = meas.R_4k
            Imax[4] = meas.Imax
        elif meas.device_name == 'M1_I0_M0-1':
            R_4K_vias[3] = meas.R_4k
            Imax[3] = meas.Imax
        elif meas.device_name == 'M1_I0_M0-0.75':
            R_4K_vias[2] = meas.R_4k
            Imax[2] = meas.Imax
        elif meas.device_name == 'M1_I1_M2-1':
            R_4K_vias[1] = meas.R_4k
            Imax[1] = meas.Imax
        elif meas.device_name == 'M1_I0_M0-0.75':
            R_4K_vias[0] = meas.R_4k
            Imax[0] = meas.Imax

    via_pass = {"R_4K_vias": R_4K_vias, "Imax": Imax}

    full_pass={"crossbar_data": crossbar_pass, "resistor_data": resistor_pass, "via_data": via_pass}

    return full_pass

def get_data_SQUID(chip_name):
    chip = d.find_chip(chip_name)
    SQUID_measurements = chip.squid_measurements

    full_pass = []

    for meas in SQUID_measurements:
        if meas.Ic_pos != None and meas.Iret_neg != None:
            Ic = round(1000*np.mean([meas.Ic_pos, abs(meas.Iret_neg)]),7)
        else:
            Ic = None

        if meas.Iflux_period != None:
            period = round(1000*meas.Iflux_period, 5)
        else:
            period = None
            
        if meas.Rn != None:
            Rn = round(meas.Rn,5)
        else:
            Rn = None
            
        if meas.I_LC_step != None:
            Vresstep = round(meas.I_LC_step,9)
        else:
            Vresstep = None
            
        current_pass = {"device_name": meas.device_name, "Ic": Ic, "Rn": Rn, "Period": period, "Vresstep": Vresstep}
        full_pass.append(current_pass)

    return full_pass

def get_data_PCMRS(chip_name):
    chip = d.find_chip(chip_name)
    wafer = d.find_wafer(chip.wafer_id)
    measurements = chip.resistor_measurements
    
    table1_rows = []
    table2_rows = []
    table3_rows = []
    table4_rows = []
    table5_rows = []
    table6_rows = []
    
    vias1 = ['1 x 1','1 x 1','1 x 2','1 x 3','1 x 4','1 x 5','1 x 6','1 x 7','1 x 8']
    vias2 = ['1 x 1','1 x 1','1 x 1','1 x 1','1 x 1','1 x 1','1 x 1','1 x 1','1 x 1']
    
    missing = wafer.missing_width #Needs to be changed later
    
    for meas in measurements:
        if '180' in meas.device_name:
            idx = meas.device_name.index('x')
            R4K = meas.R_4k_1000uA
            sq = 179/(int(meas.device_name[:2].replace('x','')) - missing)
            row = [meas.device_name[:idx]+' x '+meas.device_name[idx+1:], vias1[int(meas.device_name[:2].replace('x','')) - 2], round(R4K,3), round(sq,3), round(R4K/sq,3)]
            table1_rows.append(row)
        elif '90' in meas.device_name:
            idx = meas.device_name.index('x')
            R4K = meas.R_4k_1000uA
            sq = 89/(int(meas.device_name[:2].replace('x','')) - missing)
            row = [meas.device_name[:idx]+' x '+meas.device_name[idx+1:], vias1[int(meas.device_name[:2].replace('x','')) - 2], round(R4K,3), round(sq,3), round(R4K/sq,3)]
            table2_rows.append(row)
        elif '40' in meas.device_name:
            idx = meas.device_name.index('x')
            R4K = meas.R_4k_1000uA
            sq = 39/(int(meas.device_name[:2].replace('x','')) - missing)
            row = [meas.device_name[:idx]+' x '+meas.device_name[idx+1:], vias1[int(meas.device_name[:2].replace('x','')) - 2], round(R4K,3), round(sq,3), round(R4K/sq,3)]
            table3_rows.append(row)
        elif '20' in meas.device_name:
            idx = meas.device_name.index('x')
            R4K = meas.R_4k_1000uA
            sq = 19/(int(meas.device_name[:2].replace('x','')) - missing)
            row = [meas.device_name[:idx]+' x '+meas.device_name[idx+1:], vias1[int(meas.device_name[:2].replace('x','')) - 2], round(R4K,3), round(sq,3), round(R4K/sq,3)]
            table4_rows.append(row)
        elif '10-1' in meas.device_name:
            idx = meas.device_name.index('x')
            R4K = meas.R_4k_1000uA
            sq = 9/(int(meas.device_name[:2].replace('x','')) - missing)
            row = [meas.device_name[:idx]+' x '+meas.device_name[idx+1:], vias2[int(meas.device_name[:2].replace('x','')) - 2], round(R4K,3), round(sq,3), round(R4K/sq,3)]
            table6_rows.append(row)
        else:
            idx = meas.device_name.index('x')
            R4K = meas.R_4k_1000uA
            sq = 9/(int(meas.device_name[:2].replace('x','')) - missing)
            row = [meas.device_name[:idx]+' x '+meas.device_name[idx+1:], vias1[int(meas.device_name[:2].replace('x','')) - 2], round(R4K,3), round(sq,3), round(R4K/sq,3)]
            table5_rows.append(row)

    full_pass = {'table1': table1_rows, 'table2': table2_rows, 'table3': table3_rows, 'table4': table4_rows, 'table5': table5_rows, 'table6': table6_rows}
    
    return full_pass