# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 13:59:00 2017

@author: Soroush
"""

'''
This holds all the functions to retrieve information from the database and
format how it will be passed into measure_Rn_Imax(chip, channels, num_JJs), and
measure_Ic_Ir(chip, card, channels, currents, steps, sweeps)
'''

import database_v4 as d
import re

#===================
# functions to pull info from dattabase
#===================

def get_devices(chip):
    devices = d.show_devices_from_chip(chip)
    return devices

def get_channels(device):
    '''
    :return: [chan1, chan2] array
    '''
    if type(device) == str:
        device = d.find_device(device)
    channels = []
    chan1 = device.channel1
    channels.append(chan1)
    chan2 = device.channel2
    channels.append(chan2)
    return channels

def get_sweep(device, Jc):
    '''
    :param device: target Device
    
    :param Jc: Critical Current
    
    :return: Sweep- Array of Imin and Imax
    '''

    # need two different definitions for SQUIDs and Single/Arrays
    if device.device_type == 'SQUID':
        # for the SQUIDs all using the same current tap, need bigger range
        if device.channel1 == 1:
            sweep = d.sweep_def_SQUID_bigger_range(Jc, device.JJ_radius_nom*1e-06)
        else:
            sweep = d.sweep_def_SQUID_smaller_range(Jc, device.JJ_radius_nom*1e-06)
    else:
        print(device)
        sweep = d.sweep_def(Jc, device.JJ_radius_nom*1e-06)
    return sweep

def get_cards(device):
    '''
    :return: Card that the device is using
    '''
    if type(device) == str:
        device = d.find_device(device)
    card1 = device.card1
    card2 = device.card2
    return [card1, card2]

def create_steps_VPhi(sweep):
    '''
    Create 100 steps based on sweep range
    
    '''
    sweep_range = sweep[1] - sweep[0]
    return (sweep_range/100)


def create_steps(device, Jc):
    '''
    400 steps for SQUIDs, 200 for Single/ Array JJs
    Was 100, updated to 200 for higher accuracy 10/24/17
    
    '''
    sweeps = get_sweep(device, Jc)
    sweep_range = sweeps[1] - sweeps[0]
    # We want a constant # of points, therefore divide out here
    if device.device_type == 'SQUID':
        return (sweep_range/400)
    else:
        return (sweep_range/200)

def create_steps_no_dev(sweeps):
    sweep_range = sweeps[1] - sweeps[0]
    return (sweep_range/100)

def get_sweep_Vphi(device):
    '''
    Create sweep for taking VPhi curves, different ranges based on sizes, which
    come from the name of device
    
    '''
    dev_name = device.name
    dev_is_small = re.findall('small', dev_name)
    dev_is_med = re.findall('med', dev_name)
    dev_is_lg = re.findall('lg', dev_name)
    if len(dev_is_small) == 1:
        return [-3e-03, 3e-03]
    elif len(dev_is_med) == 1:
        return [-2.5e-03, 2.5e-03]
    elif len(dev_is_lg) == 1:
        return [-1.5e-03, 1.5e-03]


def format_input_resistance(devices):
    '''
    Format the input for the resistance curve 
    
    (Device continuity, Vias, Resistor Arrays)

    :return: array of [[cards], [chan1, chan2,...]] 
    
    '''
    card_a = []
    channels_a = []
    for i in range (0,len(devices)):
        device = devices[i]
        cards = get_cards(device)
        channels = get_channels(device)

        card_a.append(cards[0])
        card_a.append(cards[1])
        channels_a.append(channels[0])
        channels_a.append(channels[1])

    return card_a, channels_a


def format_input_V_Phi_device(devices):
    '''
    Format the input for taking the V Phi curve for SQUIDs

    :return: Array of [[cards],[chan1, chan2,.], [Imin, Imax.], [Ibias],[steps], [num_sweeps]]
   
    '''
    card_a = []
    channels_a = []
    sweep_a = []
    Ib_a = []
    steps_a = []
    num_sweep_a = []

    for i in range (0,len(devices)):
        device = devices[i]
        cards = get_cards(device)
        channels = get_channels(device)
        sweep = get_sweep_Vphi(device)
        steps = create_steps_VPhi(sweep)
        Ib = 352e-06
        num_sweep = 1 

        card_a.append(cards[0])
        card_a.append(cards[1])
        channels_a.append(channels[0])
        channels_a.append(channels[1])
        sweep_a.append(sweep[0])
        sweep_a.append(sweep[1])
        Ib_a.append(Ib)
        steps_a.append(steps)
        num_sweep_a.append(num_sweep)

    return card_a, channels_a, sweep_a, Ib_a, steps_a, num_sweep_a


def format_input_Rn_Imax_devices(devices):
    '''
    Format the input for taking the sweep to find normal resistance

    :return: Array of [[chan1, chan2,..], [num_JJs], [cards]]
    
    '''
    channels_a = []
    steps_a = []
    num_JJs_a = []
    card_a = []

    for i in range (0,len(devices)):
        device = devices[i]
        channels = get_channels(device)
        num_JJs = device.num_JJs
        cards = get_cards(device)
        channels_a.append(channels[0])
        channels_a.append(channels[1])
        num_JJs_a.append(num_JJs)
        card_a.append(cards[0])
        card_a.append(cards[1])


    return channels_a, num_JJs_a, card_a

def format_input_Ic_Ir_devices(devices, Jc):
    '''
    Format the input for taking the IV sweep to find Ic and Iret

    :return: Array of [[cards], [chan1, chan2,..], [Imin, Imax..], [steps], [num_sweeps]]
    
    '''
    card_a = []
    channels_a = []
    sweep_a = []
    steps_a = []
    num_sweep_a = []

    for i in range (0,len(devices)):
        device = devices[i]
        cards = get_cards(device)
        channels = get_channels(device)
        sweep = get_sweep(device, Jc)
        steps = create_steps(device, Jc)
        num_sweep = 1 
        card_a.append(cards[0])
        card_a.append(cards[1])
        channels_a.append(channels[0])
        channels_a.append(channels[1])
        sweep_a.append(sweep[0])
        sweep_a.append(sweep[1])
        steps_a.append(steps)
        num_sweep_a.append(num_sweep)

    return card_a, channels_a, sweep_a, steps_a, num_sweep_a
