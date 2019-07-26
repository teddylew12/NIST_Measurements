'''
Created at some point in the past

@author: Soroush
'''
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.Point import Point
import pyqtgraph as pg
import random
import sys
import numpy as np
import math
import IV_curve_v3 as iv
import matplotlib.pyplot as plt
import Input_Functions as inpfunc


#====================
# Functions to initialize the multi-window set up
#====================

def create_windows(num):
    '''
    Creates pyqtgraph windows, top level of graphics
    
    :param num: number of window to create
    '''
    windows = []
    for i in range(0, num):
        window = pg.GraphicsWindow()
        window.setWindowTitle("Window #%s" % i)
        windows.append(window)
    return windows

def create_layout_window(num):
    layouts = []
    for i in range(0,num):
        window = pg.GraphicsWindow()
        window.setWindowTitle("Window #%s" %i)
        layouts.append(window)
        
    return layouts

def create_plots(windows,formatt="IV"):
    '''
    Creates pyqtgraph plots, which are stord in the windows
    
    :param windows: array of pyqtgraph windows
    '''
    plots = []

    for i in range (0,len(windows)):
        p1 = windows[i].addPlot()
        if formatt =="PCM3B":
            p1.setLabel('left', 'Resistance', 'Ohm')
            p1.setLabel('bottom', 'Time', 's')
        elif formatt=="Temp":
            p1.setLabel('left', 'Temp', 'K')
            p1.setLabel('bottom', 'Time', 's')
        elif formatt=="Nathan":
            p1.setLabel('left', 'Temp', 'K')
            p1.setLabel('bottom', 'Time', 's')
            p1.setLabel('right','Resistance','Ohm')
        elif formatt == 'RvsT':
            p1.setLabel('left', 'Resistance', 'Ohm')
            p1.setLabel('bottom', 'Temperature', 'K')
        else:
            p1.setLabel('left', 'V', 'V')
            p1.setLabel('bottom', 'I', 'A')
       
        plots.append(p1)
    return plots

def create_curves(plots,extraarg="None"):
    '''
    Creates pyqtgraph 'curves' or the plotting scene,this is what updates
    
    :param plots: array of pyqtgraph plots
    '''
    curves = []
    for i in range(0,len(plots)):
        if extraarg=="Double":
            curve1 = plots[i].plot()
            curves.append(curve1)
            curve2 = plots[i].plot()
            curves.append(curve2)
        else:
            curve1 = plots[i].plot()
            curves.append(curve1)
    return curves

def create_current_point(plots):
    '''
    Creates another set of curves, in order to store the current point that is 
    a different color
    
    :param plots: array of pyqtgraph plots
    '''
    curves = []
    for i in range(0,len(plots)):
        curve = plots[i].plot()
        curves.append(curve)
    return curves

def create_data(curves):
    '''
    Create empty set of data, used to store the full arrays of data
    
    :param curves: array of pyqtgraph curves
    '''
    x = []
    y = []
    for i in range (0,len(curves)):
        x.append([])
        y.append([])
    return x,y

def create_vb(plots):
    '''
    Creates the Viewbox for a plot, maps the scene being viewed to the plot
    
    :param plots: array of pyqtgraph plots
    '''
    vbs = []
    for i in range(0, len(plots)):
        vb = plots[i].vb
        vbs.append(vb)
    return vbs

def create_lines(plots):
    '''
    Creates the infinite, yellow horizontal and vertical lines which constitute
    the crosshair in Overwrite_Rn
    
    :param plots: array of pyqtgraph plots
    '''
    vLines = []
    hLines = []
    for i in range(0, len(plots)):
        vLine = pg.InfiniteLine(angle=90, movable=False)
        hLine = pg.InfiniteLine(angle=0, movable=False)
        vLines.append(vLine)
        hLines.append(hLine)

        plots[i].addItem(vLine, ignoreBounds=True)
        plots[i].addItem(hLine, ignoreBounds=True)
    return vLines, hLines

def create_slope_plots_resistor_arrays(plots):
    '''
    Creates three separate lines that data can be set to visualize the slope
    
    :param plots: array of pyqtgraph plots
    '''
    slope_plots = []
    for i in range(0, len(plots)):
        current_slope_plot = []
        for n in range(0,3):
            slope_plot = plots[i].plot()
            current_slope_plot.append(slope_plot)
        slope_plots.append(current_slope_plot)    
    return slope_plots

def create_slope_plots(plots):
    '''
    Creates a separate line that data can be set to visualize the slope
    
    :param plots: array of pyqtgraph plots
    '''
    slope_plots = []
    for i in range(0, len(plots)):
        slope_plot = plots[i].plot()
        slope_plots.append(slope_plot)
    return slope_plots

