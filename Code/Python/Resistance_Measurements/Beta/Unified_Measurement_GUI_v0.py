# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 11:44:11 2019

@author: Theodore Lewitt

Unified GUI and Funcitonality for All Current Measurement Flows
"""

import sys
from PyQt5 import QtCore, QtGui, uic, QtWidgets
import numpy as np
import pyqtgraph as pyg
import pyqtgraph.exporters
import imp

#Local Function Imports
import IV_curve_v3 as iv
import Input_Functions as inpfunc
import database_v4 as d
import Visa_Functions as vf
import measure_pcm3b as m3b
import Measurement_Functions as mf
import Plot_Generation_v2 as pg

#File that dictates layout of GUI
qtCreatorFile="Unified_Measurement_GUI_v0.ui"

#Generates C++ code to create User interface
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        global app
        self.app = app
        
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        #Global Vars
        self.ready = 0
        
        #FixRN Vars
        self.count = 0
        self.Rnvb = 0 
        self.vLine = 0
        self.hLine = 0
        self.vLine_meas = 0
        self.hLine_meas = 0
        self.RnI = 0
        self.RvV = 0
        self.slopePlot = 0
        self.ImaxPlot = 0
        self.slope_x = []
        self.slope_y = []
        self.xpos = 0
        self.slope = 0
        self.squid=False
        
        #FixImax Vars
        self.countImax=0
        self.Imaxvb=0
        self.ImaxI=0
        self.ImaxV=0
        self.ImaxCrit=0
        
        #FixTc Vars
        self.counttc=0
        self.Tcvb=0
        self.TcR=0
        self.TcT=0
        self.TcCrit=0
        self.Rcrit=0
        
        #FixLC Vars
        self.LcI=0
        self.LcV=0
        self.LcCrit=0
        self.Lcvb=0
        self.countLc=0
        self.Lcx=0
        self.Lcy=0
        
        #FixIC vars
        self.IcI=0
        self.IcV=0
        self.icneg=0
        self.icpos=0
        self.icretpos=0
        self.icretneg=0
        self.countIc=0
        self.Icvb=0
        self.newIcI=[]
        self.newIcV=[]
        self.critfile=0
       
        #Top Page Functions
        self.tabWidget.currentChanged.connect(self.tabIndexChanged)
        self.Wafer.currentIndexChanged.connect(self.waferselectionchange)
        self.Chip.currentIndexChanged.connect(self.chipselectionchange)
        self.Device.currentIndexChanged.connect(self.meas_deviceselectionchange)
        
        #PCM3A Tab Functions
        self.coldMeasure.clicked.connect(self.coldmeasure3a) #Button Name: Cold
        self.warmMeasure.clicked.connect(self.warmmeasure3a) #Button Name: Warm
        self.bothMeasure.clicked.connect(self.fullTest)#Button Name: Full Test
        self.ivMeasure.clicked.connect(self.ivmeasure)#Button Name: I-V
        self.rnMeasure.clicked.connect(self.rnmeasure)#Button Name: Rn
        self.continuityMeasure.clicked.connect(self.contmeasure)#Button Name: Continuity
        self.closeButton.clicked.connect(self.closegraphs)#Button Name: Close All Graphs
        self.stopButton.clicked.connect(self.stopfunc)#Button Name: Stop
        self.dataButton.clicked.connect(self.showData)#Button Name: View Wafer Data (Initially Hidden)
        self.selectAll.clicked.connect(self.selectall)#Button Name:All
        self.refreshButton.clicked.connect(self.refresh)#Button Name: Refresh DB
        
        
        
        #PCM3B Tab Functions
        self.resistancetemp.clicked.connect(self.resisttemp)#Button Name: Resistance Vs. Temperature(Manual)
        self.resistancetime.clicked.connect(self.resisttime)#Button Name: Resistance Vs. Time
        self.cold10k.clicked.connect(self.coldmeasure10k)#Button Name:Cold 10K
        self.cold4k.clicked.connect(self.coldmeasure4k)#Button Name: Cold 4K
        self.resistancetempsave.clicked.connect(self.resisttempwithsave)#Button Name: Resistance Vs. Temp (Manual) With Save
        self.warmMeasure_3b.clicked.connect(self.warmmeasure3b)#Button Name: Warm
        self.closeButton_3b.clicked.connect(self.closegraphs)#Button Name: Close All Graphs 
        self.selectAll_3b.clicked.connect(self.selectall)#Button Name:All
        self.stopButton_3b.clicked.connect(self.stopfunc)#Button Name: Stop
        self.dataButton_3b.clicked.connect(self.showData)#Button Name: View Wafer Data (Initially Hidden)
        self.refreshButton_3b.clicked.connect(self.refresh)#Button Name: Refresh DB
        
        #PCMRS Tab Functions
        self.rs4k.clicked.connect(self.coldmeasureRS)#Button Name: RS 4K
        self.rsroomtemp.clicked.connect(self.warmmeasureRS)#Button Name: RS Continuity
        self.closeButton_rs.clicked.connect(self.closegraphs)#Button Name: Close All Graphs 
        self.selectAll_rs.clicked.connect(self.selectall)#Button Name:All
        self.stopButton_rs.clicked.connect(self.stopfunc)#Button Name: Stop
        self.dataButton_rs.clicked.connect(self.showData)#Button Name: View Wafer Data (Initially Hidden)
        self.refreshButton_rs.clicked.connect(self.refresh)#Button Name: Refresh DB
        #self.temptimetune.clicked.connect(self.tempvstime)#Button Name: Temp Vs Time-PID Tuning
        #To be added later with more fucntionality
        self.tbd2.clicked.connect(self.NOTHINGHERE)
        self.tbd3.clicked.connect(self.NOTHINGHERE)
        self.tbd4.clicked.connect(self.NOTHINGHERE)
        self.tbd5.clicked.connect(self.NOTHINGHERE)
        
        #SQUID Tab Functions
        self.full_test_SQUID.clicked.connect(self.measureSQUID)#Button Name: Full Test
        self.IV_SQUID_Iflux0.clicked.connect(self.measure_IV_no_Flux)#Button Name: I-V with Iflux = 0
        self.periodicity.clicked.connect(self.measurePeriod)#Button Name: Periodicity Test
        self.IV_SQUID.clicked.connect(self.measure_IV_with_Flux)#Button Name: I-V for different Iflux
        self.refreshButton_SQUID.clicked.connect(self.refresh)#Button Name: Refresh DB
        self.closeButton_SQUID.clicked.connect(self.closegraphs)#Button Name: Close All Graphs
        self.dataButton_SQUID.clicked.connect(self.showData)#Button Name: View Wafer Data (Initially Hidden)
        self.stopButton_SQUID.clicked.connect(self.stopfunc)#Button Name: Stop
        self.selectAll_SQUID.clicked.connect(self.selectall)#Button Name:All
        #self.IV_save_SQUID.clicked.connect(self.measure_iv_save_SQUID)
        #self.IV_nosave_SQUID.clicked.connect(self.measure_iv_no_save_SQUID)
        
        
        #GRAPHS Tab Functions
        self.plotButton.clicked.connect(self.plot) #Plot button on Graphs Page
        self.singleOption.clicked.connect(self.meas_singleoptionclicked)
        self.allOption.clicked.connect(self.meas_alloptionclicked)
        
        #FIX_RN Tab Functions
        self.clearRnButton.clicked.connect(self.clearRn) #Button Name:Clear
        self.saveRnButton.clicked.connect(self.saveRn) #Button Name:Save to DB
        
        #FIX_TC Tab Functions
        self.clearTcButton.clicked.connect(self.clearTc)#Button Name:Clear
        self.saveTcButton.clicked.connect(self.saveTc) #Button Name:Save to DB
        #FIX_IMAX Tab Functions
        self.clearImaxButton.clicked.connect(self.clearImax)#Button Name:Clear
        self.saveImaxButton.clicked.connect(self.saveImax) #Button Name:Save to DB
        
        #FIX_LC Tab Functions
        self.clearLCButton.clicked.connect(self.clearLC)#Button Name:Clear
        self.saveLCButton.clicked.connect(self.saveLC) #Button Name:Save to DB
        
        #Fix_IC Tab Functions
        self.clearICButton.clicked.connect(self.clearIc)#Button Name:Clear
        self.saveIcButton.clicked.connect(self.saveIc) #Button Name:Save to DB
        #Reports Tab Functions
        self.icReportButton.clicked.connect(self.icReport)
        self.rnReportButton.clicked.connect(self.rnReport)
        self.productReportButton.clicked.connect(self.productReport)
        
        #PID Tuning Functions
        #self.range_choose.currentIndexChanged.connect(self.heater_range_changed)
        self.send_values_button.clicked.connect(self.set_temp_controller)
        self.temp_vs_time_button.clicked.connect(self.tempvstime)
        self.tempandres_vs_time_button.clicked.connect(self.tempandresvstime)
        self.update_values.clicked.connect(self.update_temp_values)
        self.stopButton_PID.clicked.connect(vf.safe_temp_controller)
        self.update_tempsetpoint.clicked.connect(self.update_setpoint)
        self.update_pid.clicked.connect(self.update_PID)
        self.update_manual.clicked.connect(self.update_manual_output)
        self.update_range.clicked.connect(self.update_heater_range)
        

        # init actions
        self.tabWidget.setCurrentIndex(0)
        #Hide Initial Buttons
        for warning in self.getAllExistWarnings():
            warning.hide()
        self.Device.hide()
        self.dataButton.hide()
        #Populate the Wafer ComboBox
        wafers = d.show_all_wafers()
        for i in range(0, len(wafers)):
            self.Wafer.addItem(wafers[i].name)
            
        heatranges = ['Off - 0 W','Low - 0.5 W','Medium - 5 W','High - 50 W']
        for i in range(0, len(heatranges)):
            self.range_choose.addItem(heatranges[i])
        
        
    def tabIndexChanged(self):
        '''
        Changes between tabs on the GUI
        '''
        deviceneeded=["Fix Rn","Fix Tc","Fix Imax","Fix LC","Fix IC","Reports","PID Tuning"]
        devicenot=["SQUID Test","PCM3A Functions","PCM3B Functions","PCMRS + Other Ftcns","Reports"]
        devicemaybe=["Graphs"]
        #Checks the Title of the current Tab to see whether the Device ComboBox is needed
        if self.tabWidget.tabText(self.tabWidget.currentIndex()) in  deviceneeded:
            self.Device.show()
        if self.tabWidget.tabText(self.tabWidget.currentIndex()) in devicemaybe:
            if not self.singleOption.isChecked():
                self.Device.hide()
        if self.tabWidget.tabText(self.tabWidget.currentIndex()) in devicenot:
            self.Device.hide()
    
    #Toggle the visibility of the Device ComboBox 
    def meas_singleoptionclicked(self):
        self.Device.show()
    def meas_alloptionclicked(self):
        self.Device.hide()
   
    def reportGraphInfo(self):
        '''
        Returns a array of graph info including current plot,current chip and current type
        '''
        plot = self.graphicsView_Reports.getPlotItem()
        plot.clear()

        try:
            legend = plot.legend
            legend.scene().removeItem(legend)
        except:
            pass
        # check inputs

        if (self.Wafer.currentText() == 'Wafer'):
            self.message_box("Please select a wafer", 1)
            return

        if (self.Chip.currentText() == 'Chip'):
            self.message_box("Please select a chip", 1)
            return

        return plot, self.Chip.currentText(), self.deviceGroup.currentText()
    
    def icReport(self):
        '''
        Shows the Ic graph of sqrt(Ic) vs Radius
        Calls the plot_Ic_radius_from_GUI function from plot_generation_v2
        '''
        graphinfo = self.reportGraphInfo()
        if not graphinfo:
            return

        if graphinfo[2] == "Device Group":
            self.message_box("Please pick a device group", 1)
            return

        rv = pg.plot_Ic_radius_from_GUI(self.app, graphinfo[0], graphinfo[1], graphinfo[2])

        if (rv == -1):
            self.message_box("Something went wrong", 2)

        self.slopeEdit.setText((str)(rv[0]))
        self.interceptEdit.setText((str)(rv[1]))
        self.r2Edit.setText((str)(rv[2]))
    

    def rnReport(self):
        '''
        Shows the Rn graph of sqrt(rn) vs Radius
        Calls the plot_Rn_radius_from_GUI function from plot_generation_v2
        '''
        graphinfo = self.reportGraphInfo()
        if not graphinfo:
            return

        if graphinfo[2] == "Device Group":
            self.message_box("Please pick a device group", 1)
            return

        rv = pg.plot_Rn_radius_from_GUI(self.app, graphinfo[0], graphinfo[1], graphinfo[2])


        if (rv == -1):
            self.message_box("Something went wrong", 2)
            return

        self.slopeEdit.setText((str)(rv[0]))
        self.interceptEdit.setText((str)(rv[1]))
        self.r2Edit.setText((str)(rv[2]))


    
    def productReport(self):
        '''
        Shows the graph of Ic*Rn for each Device
        Calls the plot_product_device_from_GUI function from plot_generation_v2
        '''
        graphinfo = self.reportGraphInfo()
        if not graphinfo:
            return

        rv = pg.plot_product_device_from_GUI(self.app, graphinfo[0], graphinfo[1])

        if (rv == -1):
            self.message_box("Something went wrong", 2)



    def plot(self):
        """
        Runs the Graphs Tab of the GUI
        
        :param Each Device: Radio Button on GUI
        
        :param Single Device: Radio Button on GUI
       
        :return: Iv Curve of Single Device or Ic Overlay of All Chips
            
        Calls On:
            
            Measurement_GUI_v3
            
                -message_Box
            
            Plot_Generation_v2
                
                -plot Ic_Rn_from_GUI
                
                -plot_IV_from_GUI
        """

        plot=self.graphicsView.getPlotItem() # use for axis, title, etc
        plot.clear()
        try:
            legend = plot.legend
            legend.scene().removeItem(legend)
        except:
            pass

        if(self.Wafer.currentText()=='Wafer'):
            self.message_box("Please select a wafer", 1)
            return

        if(self.allOption.isChecked()):
            pg.plot_Ic_Rn_from_GUI(self.app,plot,self.Wafer.currentText())

        if(self.singleOption.isChecked()):
            if(self.Chip.currentText()=='Chip'):
                self.message_box("Please select a chip", 1)
                return
            if(self.Device.currentText()=='Device'):
                self.message_box("Please select a device", 1)
                return

            rv = pg.plot_IV_from_GUI(self.app,plot,self.Chip.currentText(),self.Device.currentText())
            if (rv==-1):
                self.message_box("Something went wrong",2)

    def dialog_box(self, window_title, message, default_text=''):
        '''
        
        :param Window Title: Title of pop-up window
        
        :param Message: Prompt for user imput
        
        :param Default_text: text to be changed to response
    
        :return: Response-User Inputed text
       
        :return: Ok-boolean on validity of input text
        '''

        response, ok = QtWidgets.QInputDialog.getText(self, window_title, message, text=default_text)

        return response,ok

    def message_box(self, message, type):
        '''
        
        :param Message: the message to display on the pop-up 
        
        :param Type: the icon that will be displayed: 
            
            -0 for info
            
            -1 for warning 
            
            -2 for critcal 
        
        :Pop-up: Message with Importance of Type
        '''
        popup = QtWidgets.QMessageBox()
        popup.setText(message)
        popup.setWindowTitle("Pop-up")
        popup.activateWindow()
        if type == 0:
            popup.setIcon(QtWidgets.QMessageBox.Information)
            popup.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        if type == 1:
            popup.setIcon(QtWidgets.QMessageBox.Warning)
            popup.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        if type == 2:
            popup.setIcon(QtWidgets.QMessageBox.Critical)

        response = popup.exec_()

        if response == QtWidgets.QMessageBox.Ok:
            return 1
        if response == QtWidgets.QMessageBox.Cancel:
            return 0

        return -1
    
    
    
    def stopfunc(self):
        '''
        Stops any functions currently running and safely exits
        '''
        
        import Resistance_curve as rc
        import IV_curve_SQUID as ivS
        try:
            iv.go = 0
            rc.go = 0
            ivS.go = 0
            self.setstatus("ready")
        except:
            pass
        
    def closegraphs(self):
        '''
        Closes all graphs currently open
        '''
        import measure_Ic as ic
        import measure_Rn as rn
        import measure_Device_Resistance as mdr
        import measure_Resistor_Arrays_v2 as mra
        import measure_Via_Resistance as mvr
        import measure_pcm3b as m3b
        # we want to find the open windows by getting the instance from each of the
        # measurement scripts
        graph_windows = []

        #if the try fails, it is because the windows have not been created yet

        try:
            graph_windows.append(ic.windows)
        except:
            pass
        try:
            graph_windows.append(rn.windows)
        except:
            pass
        try:
            graph_windows.append(mdr.windows)
        except:
            pass
        try:
            graph_windows.append(mra.windows)
        except:
            pass
        try:
            graph_windows.append(mvr.windows)
        except:
            pass
        try:
            graph_windows.append(m3b.windows)
        except:
            pass
        # loop through array or arrays of windows, close what's there
        for win_list in graph_windows:
            if len(win_list) != 0:
                for win in win_list:
                    win.close()
    
    def getAllDeviceWidgets(self):
        '''
        Returns all Device Widgets so they can all be cleared together
        '''
        return [self.deviceWidget,self.deviceWidget_3b,self.deviceWidget_rs,self.deviceWidget_SQUID]
   
    def getDeviceWidget(self):
        '''
        Device Widgets are the Blank space where the devices will be populated once a Chip and Wafer are selected
        Needs to return the correct one based on the current tab
        '''
        if self.tabWidget.tabText(self.tabWidget.currentIndex())=="PCM3A Functions":
            return self.deviceWidget
        elif self.tabWidget.tabText(self.tabWidget.currentIndex())=="PCM3B Functions":
            return self.deviceWidget_3b
        elif self.tabWidget.tabText(self.tabWidget.currentIndex())=="PCMRS + Other Ftcns":
            return self.deviceWidget_rs
        elif self.tabWidget.tabText(self.tabWidget.currentIndex())=="SQUID Test":
            return self.deviceWidget_SQUID
        else:
            print("Hmm why are you calling this on tab %d for getDeviceWidget()" % self.tabWidget.currentIndex())
    
    
    def getDataButton(self):
        '''
        The View Wafer Data Buttonswill return importnat info about the wafer currently selected
        Needs to return the correct one based on the current tab
        '''
        if self.tabWidget.tabText(self.tabWidget.currentIndex())=="PCM3A Functions":
            return self.dataButton
        elif self.tabWidget.tabText(self.tabWidget.currentIndex())=="PCM3B Functions":
            return self.dataButton_3b
        elif self.tabWidget.tabText(self.tabWidget.currentIndex())=="PCMRS + Other Ftcns":
            return self.dataButton_rs
        elif self.tabWidget.tabText(self.tabWidget.currentIndex())=="SQUID Test":
            return self.dataButton_SQUID
        else:
            print("Hmm why are you calling this on tab %d for getDataButton()" % self.tabWidget.currentIndex())
            return self.dataButton
    
    
    def getAllExistWarnings(self):
        '''
        Returns all Exist Warnings so they can all be hidden/unhidden together
        '''
        return [self.exist_warning,self.exist_warning_3b,self.exist_warning_rs,self.exist_warning_SQUID,self.SQUIDWARNING]
    
    
    def get_exist_warning(self):
        '''
        Exist Warnings are the Yellow Text boxes that alert a user that measurements already exist for the current Wafer and Chip
        Needs to return the correct one based on the current tab
        '''
        if self.tabWidget.tabText(self.tabWidget.currentIndex())=="PCM3A Functions":
            return self.exist_warning
        elif self.tabWidget.tabText(self.tabWidget.currentIndex())=="PCM3B Functions":
            return self.exist_warning_3b
        elif self.tabWidget.tabText(self.tabWidget.currentIndex())=="PCMRS + Other Ftcns":
            return self.exist_warning_rs
        elif self.tabWidget.tabText(self.tabWidget.currentIndex())=="SQUID Test":
            return self.exist_warning_SQUID
        else:
            print("Hmm why are you calling this on tab %d for get_exist_warning()" % self.tabWidget.currentIndex())
    def getselectAll(self):
        '''
        Select All toggles the checkboxes of the device widgets, but must return the correct one
        Needs to return the correct one based on the current tab
        '''
        if self.tabWidget.tabText(self.tabWidget.currentIndex())=="PCM3A Functions":
            return self.selectAll
        elif self.tabWidget.tabText(self.tabWidget.currentIndex())=="PCM3B Functions":
            return self.selectAll_3b
        elif self.tabWidget.tabText(self.tabWidget.currentIndex())=="PCMRS + Other Ftcns":
            return self.selectAll_rs
        elif self.tabWidget.tabText(self.tabWidget.currentIndex())=="SQUID Test":
            return self.selectAll_SQUID
        else:
            print("Hmm why are you calling this on tab %d for getselectAll()" % self.tabWidget.currentIndex())
    def getStatus(self):
        '''
        Status Fields are the Green/Yellow Text boxes that alert a user that the program is either ready for measurements or currently taking measurements
        Needs to return the correct one based on the current tab
        '''
        if self.tabWidget.tabText(self.tabWidget.currentIndex())=="PCM3A Functions":
            return self.status
        elif self.tabWidget.tabText(self.tabWidget.currentIndex())=="PCM3B Functions":
            return self.status_3b
        elif self.tabWidget.tabText(self.tabWidget.currentIndex())=="PCMRS + Other Ftcns":
            return self.status_rs
        elif self.tabWidget.tabText(self.tabWidget.currentIndex())=="SQUID Test":
            return self.status_SQUID
        else:
            print("Hmm why are you calling this on tab %d" % self.tabWidget.currentIndex())
   
    def refresh(self):
        '''
        Refresh the database to get new chips entered
        '''
        #Reloads the python scripts
        imp.reload(d)
        imp.reload(iv)
        wafer_count = self.Wafer.count()
        #Clears Wafer ComboBox
        for i in range(1, wafer_count+1):
            self.Wafer.removeItem(1)
        #Clears Chip ComboBox
        chip_count = self.Chip.count()
        for i in range(1, chip_count + 1):
            self.Chip.removeItem(1)
        #Clears Device Widgets
        for device in self.getAllDeviceWidgets():
            device.clear()
        #Resets Radio Buttons
        self.getselectAll().setChecked(True)
        #REpopulates Wafer
        wafers = d.show_all_wafers()
        for i in range(0, len(wafers)):
            self.Wafer.addItem(wafers[i].name)
    def waferselectionchange(self):
        '''
        Allows user to select or change wafer
        '''
        current = self.Wafer.currentText()
       
        if current != 'Wafer':
            if self.tabWidget.currentIndex() in [0,1,2,3]:
                self.getDataButton().show()
            chips = d.show_chips_from_wafer(current)
            chip_count = self.Chip.count()
            for i in range(1, chip_count + 1):
                self.Chip.removeItem(1)
            for i in range(0, len(chips)):
                self.Chip.addItem(chips[i].name)
        else:
            for device in self.getAllDeviceWidgets():
                device.clear()
            chip_count = self.Chip.count()
            for i in range(1, chip_count + 1):
                self.Chip.removeItem(1)
            self.getDataButton().hide()
            for warning in self.getAllExistWarnings():
                warning.hide()

    def chipselectionchange(self):
        """
        Allows user to select or change chip
        """
        
        self.ready = 0
        for device in self.getAllDeviceWidgets():
            device.clear()
        

        currentChip = self.Chip.currentText()

        if currentChip!="Chip":
            devices = d.show_devices_from_chip(currentChip)
            num_row = len(devices)
            num_col = 4 #for now
            for device in self.getAllDeviceWidgets():
                device.setRowCount(num_row)
                device.setColumnCount(num_col)
                device.setHorizontalHeaderLabels(["Device", "Num JJs", "JJ Radius","Enabled"])

            for device in self.getAllDeviceWidgets():
                for r in range (0,num_row):
                    name = QtWidgets.QTableWidgetItem(devices[r].name)
                    num = QtWidgets.QTableWidgetItem(str(devices[r].num_JJs))
                    radius = QtWidgets.QTableWidgetItem(str(devices[r].JJ_radius_nom))        

                    device.setItem(r,0,name)
                    device.setItem(r,1,num)
                    device.setItem(r,2,radius)
                    #import pdb;pdb.set_trace()
                    checkboxItem = QtWidgets.QTableWidgetItem()
                    checkboxItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                    checkboxItem.setCheckState(QtCore.Qt.Checked)
                    device.setItem(r, 3, checkboxItem)

            meas = d.show_measurements_from_chip(currentChip)
            for warning in self.getAllExistWarnings():
                if meas:               
                    warning.show()
                else:
                    warning.hide()

        else:
            for warning in self.getAllExistWarnings():
                warning.hide()


        current = self.Chip.currentText()
        if current != 'Chip':
            # set the device droipdown
            devices = d.show_devices_from_chip(current)
            dev_count = self.Device.count()
            for i in range(1,dev_count+1):
                self.Device.removeItem(1)
            for i in range(0,len(devices)):
                self.Device.addItem(devices[i].name)

            # set the device group dropdown
            device_types = []
            for dev in devices:
                device_types.append(dev.device_type)

            device_types = list(set(device_types))

            for i in range(1,dev_count+1):
                self.deviceGroup.removeItem(1)
            for i in range(0,len(device_types)):
                self.deviceGroup.addItem(device_types[i])


        self.ready = 1

    def showData(self):
        """
        Pops-up numerous graphs of Ic and Rn
        """
        response = self.message_box('A few graphs will now pop up', 0)
        if response == 1:
            wafer = []
            wafer.append(self.Wafer.currentText())
            design_type = []
            design_type.append('PCMS2A')

            plot_generation = pg.plot_Ic_Rn_from_type(wafer, design_type)

            if plot_generation != 0: # something went wrong
                response = self.message_box('Oops, something went wrong',1)

    def selectall(self):
        """
        Radio Button on Measurement page below 'View Wafer Data'
        
        Lets you toggle which devices are selected for measurement
        """
        num_row = self.getDeviceWidget().rowCount()
        num_col = self.getDeviceWidget().columnCount()

        for r in range(0,num_row):
            checkbox = self.getDeviceWidget().item(r,num_col-1)
            if self.getselectAll().isChecked():
                checkbox.setCheckState(QtCore.Qt.Checked)
            else:
                checkbox.setCheckState(QtCore.Qt.Unchecked)

    def setstatus(self, message):
        """
        Shows status of program in bottom right corner
        """
        stats1=self.getStatus()
        if message == "ready":
            stats1.setText("Ready")
            stats1.setStyleSheet("background: rgb(0,255,0)")
        if message == "meas":
            stats1.setText("Measuring...")
            stats1.setStyleSheet("background: rgb(255,255,0)")
        app.processEvents()
    
    def contmeasure(self):
        """
        Measures Continuity to check for shorts
        
        Calls On:
            
            -Measurement_GUI_v3-Get_enabled_devices,
            
            -Measurement_Functions-check_connections
        """
        #Checks that the Chip and Wafer fields are populated
        if self.Chip.currentText()!='Chip' and self.Wafer.currentText()!='Wafer':
            self.setstatus("meas")
            #Gets devices to be used
            devices_to_measure = self.get_enabled_devices()
            chip = self.Chip.currentText()
            oddgraphs=[]
            oddgraphs=mf.check_connections(chip, devices_to_measure)
            #Returns Pop-up with any devices showing abnormal behavior
            if oddgraphs:
                odd=' , '.join(str(x) for x in oddgraphs)
                self.message_box("Abnormal Devices(s): " + odd,0)
            else:
                self.message_box("No abnormal devices!",0)
            
        else:
            message="Please pick a Chip and Wafer before pressing this button! :)"
            self.message_box(message, 2)
        self.setstatus("ready")

    def ivmeasure(self):
        """
        Measures IV withouts saving to database
        
        Calls On:
            
            -Measurement_GUI_v3-
                
                -Get_enabled_devices
                
                -dialog_Box
            
            -Database_v4
                
                -Predict_IC
            
            -Measurement_Functions
                
                -Measure_JJs_IC
        
        """
       #Checks that the Chip and Wafer fields are populated
        if self.Chip.currentText()!='Chip' and self.Wafer.currentText()!='Wafer':
            #Gets devices to be used
            devices_to_measure = self.get_enabled_devices()
            chip = self.Chip.currentText()
            self.setstatus("meas")
            good_to_go = 1
            ok = False
            if self.highDensity.isChecked():
              warning_text = "Estimated Ic:"
              estimated_Ic = d.predict_Ic(d.chip_Jc(chip),
                                          devices_to_measure[0].JJ_radius_nom * 1e-06)  # radius in m, need in um
              estimated_Ic = (str)(estimated_Ic)
              response, ok = self.dialog_box("High Density Sweep", warning_text, default_text=estimated_Ic)
            if ok:
                Ic_to_pass = float(response)
                mf.measure_JJs_Ic(chip, devices_to_measure, optionalIc=Ic_to_pass)
                good_to_go = 0

            if (good_to_go):
                mf.measure_JJs_Ic(chip, devices_to_measure)
        else:
            message="Please pick a Chip and Wafer before pressing this button! :)"
            self.message_box(message, 2)
        
        self.setstatus("ready")

    def rnmeasure(self):
        """
        Measures RN withouts saving to database
       
        Calls On:
           
            -Get_enabled_devices
            
            -Measure_JJs_Rn
        
        """
        if self.Chip.currentText()!='Chip' and self.Wafer.currentText()!='Wafer':
            self.setstatus("meas")
            devices_to_measure = self.get_enabled_devices()
            chip = self.Chip.currentText()

            mf.measure_JJs_Rn(chip, devices_to_measure)
        else:
            message="Please pick a Chip and Wafer before pressing this button! :)"
            self.message_box(message, 2)
        self.setstatus("ready")
    def fullTest(self):
        """
        Measurement flow:
            
            1. Plug in probe while it is not dunked
            
            2. Run measure_PCM_chip_warm before dunking. Will plot simple I-V line to make
            sure there are no open connections, and measure RT values
            
            3. Slowly dunk probe
            
            4. Call measure_PCM_chip_cold. This will take IV's of all the devices on the PCM
            i.e. SJs and arrays. Then it will find resistance of Resistor Arrays and Vias
            then it find normal resistance for devices.

        Performs Warm and Cold tests in order
        
        :Graphs: Continuity, followed by Iv and Rn graphs
            
        Calls On:
           
            -Measurement_GUI_v3-warmmeasure,coldmeasure,closegraphs,message_box
           
            -Database_v4-Predict_IC
           
            -Measurement_Functions-Measure_JJs_IC
        
        """
        if self.Chip.currentText()!='Chip' and self.Wafer.currentText()!='Wafer':
            running = True
            if running:
                self.warmmeasure3a()
                running=False
            a=self.message_box("Continue with Cold Test?\n The test will start immediately after hitting Okay ",1)
            if a==1: 
                self.closegraphs()
                self.coldmeasure3a()
            else:
                return
        else:
            message="Please pick a Chip and Wafer before pressing this button! :)"
            self.message_box(message, 2)
        
            
    def coldmeasure3a(self):
        '''
        Runs Cold tests for PCM3A devices
        '''
        self.setstatus("meas")
        good_to_go = 1

       
        
       

        if self.Chip.currentText()!='Chip' and self.Wafer.currentText()!='Wafer':
            devices_to_measure = self.get_enabled_devices()
            chip = self.Chip.currentText()
            if self.highDensity.isChecked():
                warning_text = "Estimated Ic:"
                estimated_Ic = d.predict_Ic(d.chip_Jc(chip),devices_to_measure[0].JJ_radius_nom*1e-06) # radius in m, need in um
                estimated_Ic = (str)(estimated_Ic)
                response, ok = self.dialog_box("High Density Sweep", warning_text, default_text =estimated_Ic)
                if ok:
                    Ic_to_pass = float(response)
                    mf.measure_PCM_chip_cold(chip, devices_to_measure, optionalIc=Ic_to_pass)
                else:
                    good_to_go = 0
                    self.setstatus("ready")
            else:
                mf.measure_PCM_chip_cold(chip, devices_to_measure)
                self.setstatus("meas")
        else:
            message="Please pick a Chip and Wafer before pressing this button! :)"
            self.message_box(message, 2)
        self.setstatus("ready")
        
    def coldmeasure4k(self): 
        '''
        Runs 4K Cold tests for PCM3B devices 
        '''
        if self.Chip.currentText()!='Chip' and self.Wafer.currentText()!='Wafer':
            self.setstatus("meas")
            fourk=True
            devices_to_measure = self.get_enabled_devices()
            chip = self.Chip.currentText()
            mf.measure_PCM3b_cold(chip, devices_to_measure,fourk)
        else:
            message="Please pick a Chip and Wafer before pressing this button! :)"
            self.message_box(message, 2)
        
            
    def coldmeasure10k(self):      
        '''
        Runs 10K Cold tests for PCM3B devices
        '''
        if self.Chip.currentText()!='Chip' and self.Wafer.currentText()!='Wafer':
            good_to_go = 1
            self.setstatus("meas")
        else:
            message="Please pick a Chip and Wafer before pressing this button! :)"
            self.message_box(message, 2)
        fourk=False
        devices_to_measure = self.get_enabled_devices()
        chip = self.Chip.currentText()
        if(good_to_go):
            print(devices_to_measure)
            mf.measure_PCM3b_cold(chip, devices_to_measure,fourk)
    def coldmeasureRS(self):
        '''
        Runs Cold tests for PCMRS devices
        '''
        if self.Chip.currentText()!='Chip' and self.Wafer.currentText()!='Wafer':
            devices_to_measure = self.get_enabled_devices()
            chip = self.Chip.currentText()
            self.setstatus("meas")
            _=mf.measureRS(chip,devices_to_measure,warm=False)
        else:
            message="Please pick a Chip and Wafer before pressing this button! :)"
            self.message_box(message, 2)
      
    def warmmeasure3b(self):
        '''
        Runs Warm tests for PCM3B devices
        '''
        devices_to_measure = self.get_enabled_devices()
        chip = self.Chip.currentText()
        if self.Chip.currentText()!='Chip' and self.Wafer.currentText()!='Wafer':
            self.setstatus("meas")
            mf.measure_PCM3b_warm(chip,devices_to_measure)
        else:
            message="Please pick a Chip and Wafer before pressing this button! :)"
            self.message_box(message, 2)
        
        
        self.setstatus("ready")
        
    def warmmeasureRS(self):
        """
        Measures the chip warm and checks for shorts and other graphical oddities
        
        :Graphs: Continuity
            
        :Pop-up: Abnormal Graphs-If a graph is nonlinear or has negative slope
            this function will return which device to look at for the issue
        
        Called By:
            
            -fullTest
        
        Calls On:
            
            -Measurement_GUI_v3-Get_enabled_devices,message_Box
            
            -Measurement_Functions-Measure_PCM_chip_warm
        """
        
        devices_to_measure = self.get_enabled_devices()
        chip = self.Chip.currentText()
        if self.Chip.currentText()!='Chip' and self.Wafer.currentText()!='Wafer':
            self.setstatus("meas")
            oddgraphs=[]
            oddgraphs=mf.measureRS(chip, devices_to_measure, warm=True)
       
            if oddgraphs:
                odd=' '.join(str(x-1) for x in oddgraphs)
                self.message_box("Abnormal Devices(s): " + odd,0)
            else:
                self.message_box("No abnormal devices!",0)
        else:
            message="Please pick a Chip and Wafer before pressing this button! :)"
            self.message_box(message, 2)
        self.setstatus("ready")
    def warmmeasure3a(self):
        """
        Measures the PCM3A chip warm and checks for shorts and other graphical oddities
        
        :Graphs: Continuity
            
        :Pop-up: Abnormal Graphs-If a graph is nonlinear or has negative slope
            this function will return which device to look at for the issue
        
        Called By:
            
            -fullTest
        
        Calls On:
            
            -Measurement_GUI_v3-Get_enabled_devices,message_Box
            
            -Measurement_Functions-Measure_PCM_chip_warm
        """
        
        
        if self.Chip.currentText()!='Chip' and self.Wafer.currentText()!='Wafer':
            devices_to_measure = self.get_enabled_devices()
            chip = self.Chip.currentText()
            oddgraphs=[]
            self.setstatus("meas")
            oddgraphs=mf.measure_PCM_chip_warm(chip, devices_to_measure)
       
            if oddgraphs:
                odd=' '.join(str(x) for x in oddgraphs)
                self.message_box("Abnormal Devices(s): " + odd,0)
            else:
                self.message_box("No abnormal devices!",0)
        else:
            message="Please pick a Chip and Wafer before pressing this button! :)"
            self.message_box(message, 2)
        self.setstatus("ready")
    
    def tempvstime(self):
        if self.setpoint_choose.text():   
            ideal=float(self.setpoint_choose.text())
        else:
            ideal=float(input("You fool! Set an temperature setpoint: \n"))
        iv.temptime(ideal)
        
    def tempandresvstime(self):
        chip = self.Chip.currentText()
        device = self.Device.currentText()
        target = self.setpoint_choose.text()
        tempSetpoint = self.setpoint_choose.text()
        PID = [self.p_choose.text(), self.i_choose.text(), self.d_choose.text()]
        manual = self.manual_choose.text()
        m3b.continuousResistTemp_Nathan(chip, device, target, tempSetpoint, PID, manual)
        
    def resisttemp(self):
        if self.Chip.currentText()!='Chip' and self.Wafer.currentText()!='Wafer':
            devices_to_measure = self.get_enabled_devices()
            chip = self.Chip.currentText()
            mf.resistancetemp(chip,devices_to_measure,False)
            self.setstatus("meas")
        else:
            message="Please pick a Chip and Wafer before pressing this button! :)"
            self.message_box(message, 2)
        
        self.setstatus("ready")
    def resisttime(self):
       
        if self.Chip.currentText()!='Chip' and self.Wafer.currentText()!='Wafer':
            devices_to_measure = self.get_enabled_devices()
            chip = self.Chip.currentText()
            mf.resistancetime(chip,devices_to_measure)
            self.setstatus("meas")
        else:
            message="Please pick a Chip and Wafer before pressing this button! :)"
            self.message_box(message, 2)

        
        self.setstatus("ready")
    def resisttempwithsave(self):
        if self.Chip.currentText()!='Chip' and self.Wafer.currentText()!='Wafer':
            devices_to_measure = self.get_enabled_devices()
            chip = self.Chip.currentText()
            mf.resistancetemp(chip,devices_to_measure,True)
            self.setstatus("meas")
        else:
            message="Please pick a Chip and Wafer before pressing this button! :)"
            self.message_box(message, 2)

        
        self.setstatus("ready")

    def get_enabled_devices(self):
        """
        Gets Devices that need to be measured
    
        
        :return: Devices to be Measured
        
        Called By:
        
            Measurement_GUI_V3-
            
                -All measurement functions
        
        Calls On:
            
            Database V4
                
                -show_devices_from_chip
        
        """
        currentChip = self.Chip.currentText()
        devices = d.show_devices_from_chip(currentChip)
        num_rows = self.getDeviceWidget().rowCount()
        num_col = self.getDeviceWidget().columnCount()
        enabledDevices = []
        for r in range(0, num_rows):
            checkbox = self.getDeviceWidget().item(r, num_col-1)
            enabledDevices.append(checkbox.checkState() == QtCore.Qt.Checked)

        devices_to_measure = []

        for i in range(0, len(enabledDevices)):
            if enabledDevices[i]:
                devices_to_measure.append(devices[i])

        return devices_to_measure
    def meas_deviceselectionchange(self):
        if (self.ready):
            if self.tabWidget.currentIndex() ==4:
                self.plot()
            elif self.tabWidget.currentIndex() == 5:
                self.plotRn()
            elif self.tabWidget.currentIndex() == 6:
                self.plotTc()
            elif self.tabWidget.currentIndex() == 7:
                self.plotImax()
            elif self.tabWidget.currentIndex() == 8:
                self.plotLC()
            elif self.tabWidget.currentIndex()==9:
                self.plotIc()
            else:
                pass
    
    '''
    #######################################
    SQUID Measurement functions
    #######################################
    '''  
    def measureSQUID(self):
        devices_to_measure = self.get_enabled_devices()
        chip = self.Chip.currentText()
        if self.Chip.currentText()!='Chip' and self.Wafer.currentText()!='Wafer':
            self.setstatus("meas")
            mf.measureSQUID(chip,devices_to_measure)
        else:
            message="Please pick a Chip and Wafer before pressing this button! :)"
            self.message_box(message, 2)
        
        
        self.setstatus("ready")
        
    def measure_IV_no_Flux(self):
        devices_to_measure = self.get_enabled_devices()
        chip = self.Chip.currentText()
        save = self.save_IV_Iflux0.isChecked()
        min_Ibias = float(self.min_Ibias_IV_Iflux0.text()) * 0.001
        max_Ibias = float(self.max_Ibias_IV_Iflux0.text()) * 0.001
        step_Ibias = float(self.step_Ibias_IV_Iflux0.text()) * 0.001
        if self.Chip.currentText()!='Chip' and self.Wafer.currentText()!='Wafer':
            self.setstatus("meas")
            mf.measure_iv_SQUID(chip,devices_to_measure, save, min_Ibias, max_Ibias, step_Ibias)
        else:
            message="Please pick a Chip and Wafer before pressing this button! :)"
            self.message_box(message, 2)
        
        self.setstatus("ready")
        
    def measurePeriod(self):
        devices_to_measure = self.get_enabled_devices()
        chip = self.Chip.currentText()
        save = self.save_periodicity.isChecked()
        min_Iflux = float(self.min_Iflux_periodicity.text()) * 0.001
        max_Iflux = float(self.max_Iflux_periodicity.text()) * 0.001
        step = float(self.step_Iflux_periodicity.text()) * 0.001
        I_bias = float(self.ibias_periodicity.text()) * 0.001
        if self.Chip.currentText()!='Chip' and self.Wafer.currentText()!='Wafer':
            self.setstatus("meas")
            mf.measure_periodicity_SQUID(chip,devices_to_measure, save, min_Iflux, max_Iflux, step, I_bias)
        else:
            message="Please pick a Chip and Wafer before pressing this button! :)"
            self.message_box(message, 2)
        
        self.setstatus("ready")
        
    def measure_IV_with_Flux(self):
        import measure_Ic as ic
        import IV_curve_SQUID as iv2
        devices_to_measure = self.get_enabled_devices()
        SQUIDS = [] #Only measure SQUIDS
        for i in range(0, len(devices_to_measure)):
            if devices_to_measure[i].device_type == 'SQUID':
                SQUIDS.append(devices_to_measure[i])
        chip = self.Chip.currentText()
        save = self.save_IV.isChecked()
        down = self.down_Ibias_IV.isChecked()
        min_Ibias = float(self.min_Ibias_IV.text()) * 0.001
        max_Ibias = float(self.max_Ibias_IV.text()) * 0.001
        step_Ibias = float(self.step_Ibias_IV.text()) * 0.001
        min_Iflux = float(self.min_Iflux_IV.text()) * 0.001
        max_Iflux = float(self.max_Iflux_IV.text()) * 0.001
        step_Iflux = float(self.step_Iflux_IV.text()) * 0.001
        for device in SQUIDS:
            if self.Chip.currentText()!='Chip' and self.Wafer.currentText()!='Wafer':
                self.setstatus("meas")
                allI,allV,colors,folder,var=mf.measure_iv_flux_SQUID(chip,device, save, down, min_Iflux, max_Iflux, step_Iflux, min_Ibias, max_Ibias, step_Ibias)
                
                if save:
                    #message="Zoom on graph to decide which color has largest lc step, click OK when done"
                    #self.message_box( message, 0)
                    
                    message="Pick the color of the curve with the largest Lc step"
                    color,okpressed=self.dropDown("LC Picker",message,colors)
                    index=colors.index(color)
                    new, meas = d.save_SQUID_with_flux(chip, 0, folder, device) #only if we end up writing a function for finding the LC step
                    name=ic.create_name(chip,device)
                    if new:
                        ic.create_dir(folder+name)
                    else:
                        folder = 'E:/Users/volt.686QVACTEST/National Institute of Standards and Technology (NIST)/SEG - SFQ_Circuits' + '/' + meas.data_directory[pg.find_D(meas.data_directory,chip):]
                    iv2.save_data(allI[index],allV[index],(folder+name+"_LC_step_raw.dat")) #Save data to sharepoint
                    
            else:
                message="Please pick a Chip and Wafer before pressing this button! :)"
                self.message_box(message, 2)
                
        self.setstatus("ready")
        
    def dropDown(self, titletext,prompttext,iterable,startindex=0,editable=False):
        a=QtWidgets.QInputDialog(self)
        a.setModal(False)
        color, okPressed = a.getItem(self,titletext, prompttext,iterable,startindex,editable)
        
        return color,okPressed
    '''
    #######################################
    FIX IMAX FUNCTIONALITY
    #######################################
    '''    
    
    def plotImax(self):
        plot= self.graphicsView_Imax.getPlotItem()  
        try:
            plot.scene().sigMouseClicked.disconnect()
            plot.scene().sigMouseMoved.disconnect()
            self.clearImax()
        except:
            pass
        plot.clear()
        try:
            legend = plot.legend
            legend.scene().removeItem(legend)
        except:
            pass
        if (self.Wafer.currentText() == 'Wafer'):
            self.message_box("Please select a wafer", 1)
            return

        if (self.Chip.currentText() == 'Chip'):
            self.message_box("Please select a chip", 1)
            return
        if (self.Device.currentText() == 'Device'):
            self.message_box("Please select a device", 1)
            return
        if not self.is_Via(self.Device.currentText()):
            self.message_box("You can only fix Imax for Via devices!", 1)
            return
            
    
        outputs=pg.plot_from_GUI(self.app,plot,self.Chip.currentText(),self.Device.currentText(),plottype="Imax")
        if (outputs == -1):
            self.message_box("Something went wrong", 2)
            return
        else:
            '''
            IMAX OUTPUTS
            '''
            self.ImaxI = outputs[0]
            self.ImaxV = outputs[1]
            self.ImaxCrit=outputs[2]
            
        device = d.find_device(self.Device.currentText())
        

        self.waferName.setText("Wafer: %s"%self.Wafer.currentText())
        self.chipName.setText("Chip: %s"%self.Chip.currentText())
        self.deviceName.setText("Device: %s (um)"%device.name)
        self.imaxEdit_via.setText(str(self.ImaxCrit))
        self.Imaxvb = plot.vb

        self.vLine = pyg.InfiniteLine(angle=90, movable=False)
        self.hLine = pyg.InfiniteLine(angle=0, movable=False)

        plot.addItem(self.vLine, ignoreBounds = True)
        plot.addItem(self.hLine, ignoreBounds = True)

        plot.scene().sigMouseClicked.connect(self.onClickImax)
        plot.scene().sigMouseMoved.connect(self.MouseMovedImax)

        self.slopePlot = plot.plot()
        self.ImaxPlot = plot.plot()
        
        meas = d.show_via_measurements_from_device(self.Chip.currentText(),device.name)
        Imax = meas.Imax
        self.current_Imax_2.setText("Current Imax: %f" %Imax)
        
        self.waferName_Imax.setText("Wafer: %s"%self.Wafer.currentText())
        self.chipName_Imax.setText("Chip: %s"%self.Chip.currentText())
        self.deviceName_Imax.setText("Device: %s "%device.name)
        
        self.vLine_meas = pyg.InfiniteLine(angle=90, movable=False, label="Current Imax")
        plot.addItem(self.vLine_meas, ignoreBounds = True)
        self.vLine_meas.setPos(Imax)
        
    def clearImax(self):
        self.plotPoints(type="clear")
        self.countImax=0
        self.Imaxvb=0
        self.ImaxCrit=0
        self.dataDirectory=0    
        self.imaxEdit_via.setText('')   

        
    def saveImax(self):
        self.saveImaxButton.setText("Saving...")
        self.saveImaxButton.setEnabled(False)
        app.processEvents()
        import database_v4 as d
        device = d.find_device(self.Device.currentText())
        data_direct=d.show_via_measurements_from_device(self.Chip.currentText(),self.Device.currentText()).data_directory
        R_4k=[d.show_via_measurements_from_device(self.Chip.currentText(),self.Device.currentText()).R_4k]
        Imax=[(float)(self.imaxEdit_via.text())]       
        
        d.save_Via_Measurements_PCM3B_cold(self.Chip.currentText(),R_4k,Imax, data_direct, device)         
        self.saveImaxButton.setText("Save to DB")
        self.saveImaxButton.setEnabled(True)
    def onClickImax(self,event):
        pos = event.pos()
        
        self.Imaxvb = self.graphicsView_Imax.getPlotItem().vb
        mousePoint = self.Imaxvb.mapSceneToView(pos)

        # try to match positon to index in data, this works well now
        [index, val] = min(enumerate(self.ImaxI), key = lambda i: abs(i[1]-self.xpos))

        self.countImax +=1
        # every two clicks find slope and display in text box
        if self.countImax==1:
            self.ImaxCrit=self.ImaxI[index]
            self.Imaxx=[self.ImaxI[index]]
            self.Imaxy=[self.ImaxV[index]]
            self.plotPoints(type="imax")
            self.imaxEdit_via.setText((str)(self.ImaxCrit))

        else:
           pass

    def MouseMovedImax(self,evt):
        '''
        Reacts to mouse movement
        '''
        pos = evt
        self.Imaxvb = self.graphicsView_Imax.getPlotItem().vb
        mousePoint = self.Imaxvb.mapSceneToView(pos)

        self.vLine.setPos(mousePoint.x())
        self.hLine.setPos(mousePoint.y())

        self.xpos = mousePoint.x()
    '''
    #######################################
    FIX TC FUNCTIONALITY
    #######################################
    '''       
    def MouseMovedTc(self,evt):
        '''
        Reacts to mouse movement
        '''
        pos = evt
        self.Tcvb = self.graphicsView_tc.getPlotItem().vb
        mousePoint = self.Tcvb.mapSceneToView(pos)

        self.vLine.setPos(mousePoint.x())
        self.hLine.setPos(mousePoint.y())

        self.xpos = mousePoint.x()
    def clearTc(self):
        '''
        Resets all TC related Variables
        '''
        self.counttc=0
        self.Tcvb=0
        self.TcI=0
        self.TcV=0
        self.TcCrit=0
        self.dataDirectory=0    
        self.tcEdit.setText('')   
        self.Rcrit=0
        self.plotPoints(type="clear")
    def plotTc(self):
        plot= self.graphicsView_tc.getPlotItem()  
        try:
            plot.scene().sigMouseClicked.disconnect()
            plot.scene().sigMouseMoved.disconnect()
            self.clearTc()
        except:
            pass
        plot.clear()
        try:
            legend = plot.legend
            legend.scene().removeItem(legend)
        except:
            pass
        if (self.Wafer.currentText() == 'Wafer'):
            self.message_box("Please select a wafer", 1)
            return

        if (self.Chip.currentText() == 'Chip'):
            self.message_box("Please select a chip", 1)
            return
        if (self.Device.currentText() == 'Device'):
            self.message_box("Please select a device", 1)
            return
        if not self.is_Crossbar(self.Device.currentText()):
            self.message_box("You can only fix Tc for Crossbar devices!", 1)
            return
        
        outputs=pg.plot_from_GUI(self.app,plot,self.Chip.currentText(),self.Device.currentText(),plottype="TC")
        if (outputs == -1):
            self.message_box("Something went wrong", 2)
            return
        else:
            self.TcR = outputs[0]
            self.TcT = outputs[1]
            self.TcCrit=outputs[2]
        
        device = d.find_device(self.Device.currentText())
    
        self.waferName.setText("Wafer: %s"%self.Wafer.currentText())
        self.chipName.setText("Chip: %s"%self.Chip.currentText())
        self.deviceName.setText("Device: %s "%device.name)
        
        meas = d.show_crossbar_measurements_from_device(self.Chip.currentText(),device.name)
        Tc = meas.Tc
        self.current_Tc.setText("Current Tc: %f" %Tc)
        self.Tcvb = plot.vb
        
        self.vLine = pyg.InfiniteLine(angle=90, movable=False)
        self.hLine = pyg.InfiniteLine(angle=0, movable=False)

        plot.addItem(self.vLine, ignoreBounds = True)
        plot.addItem(self.hLine, ignoreBounds = True)

        plot.scene().sigMouseClicked.connect(self.onClickTc)
        plot.scene().sigMouseMoved.connect(self.MouseMovedTc)

        self.slopePlot = plot.plot()
        self.ImaxPlot = plot.plot()
        
        self.vLine_meas = pyg.InfiniteLine(angle=90, movable=False, label="Current Tc")
        plot.addItem(self.vLine_meas, ignoreBounds = True)
        self.vLine_meas.setPos(Tc)
        
    def onClickTc(self,event):
        pos = event.pos()
        
        self.Tcvb = self.graphicsView_tc.getPlotItem().vb
        mousePoint = self.Tcvb.mapSceneToView(pos)

        # try to match positon to index in data, this works well now
        [index, val] = min(enumerate(self.TcT), key = lambda i: abs(i[1]-self.xpos))

        self.counttc +=1
        # every two clicks find slope and display in text box
        if self.counttc==1:
            self.TcCrit=self.TcT[index]
            self.RCrit=self.TcR[index]
            self.plotPoints(type="tc")
            self.tcEdit.setText((str)(self.TcCrit))

        else:
           self.counttc=0
    def saveTc(self):
        '''
        Saves TC measurement
        

        '''
        self.saveTcButton.setText("Saving...")
        self.saveTcButton.setEnabled(False)
        app.processEvents()
        import database_v4 as d
        chip = d.find_chip(self.Chip.currentText())
        device = d.find_device(self.Device.currentText())
        data_direct=d.show_crossbar_measurements_from_device(chip,device).data_directory
        TcIn=float(self.tcEdit.text())            
        d.save_Crossbar_Tc(chip, TcIn, data_direct, device)         
        self.saveTcButton.setText("Save to DB")
        self.saveTcButton.setEnabled(True)
    '''
    #######################################
    FIX RN FUNCTIONALITY
    #######################################
    '''
 
    def plotRn(self):
        '''
    
        Plots RN for a selected chip
        
        Calls the plot_rn_from_GUI function from Plot Generation v2 
    
        '''
        plot = self.graphicsView_Rn.getPlotItem()
        try:
            plot.scene().sigMouseClicked.disconnect()
            plot.scene().sigMouseMoved.disconnect()
            self.clearRn()
        except:
            pass
        plot.clear()

        try:
            legend = plot.legend
            legend.scene().removeItem(legend)
        except:
            pass

        if (self.Wafer.currentText() == 'Wafer'):
            self.message_box("Please select a wafer", 1)
            return


        if (self.Chip.currentText() == 'Chip'):
            self.message_box("Please select a chip", 1)
            return
        if (self.Device.currentText() == 'Device'):
            self.message_box("Please select a device", 1)
            return

        if self.is_Squid(self.Device.currentText()):
            rv = pg.plot_from_GUI(self.app, plot, self.Chip.currentText(), self.Device.currentText(),plottype="SQRN")
            self.squid=True
            self.SQUIDWARNING.show()
        else:
            rv = pg.plot_from_GUI(self.app, plot, self.Chip.currentText(), self.Device.currentText())
            self.SQUIDWARNING.hide()

        if (rv == -1):
            self.message_box("Something went wrong", 2)
            return
        else:
            self.RnI = rv[0]
            self.RnV = rv[1]
            self.dataDirectory = rv[2]
        print("Used Directory %s" % self.dataDirectory)
        self.Rnvb = plot.vb

        self.vLine = pyg.InfiniteLine(angle=90, movable=False)
        self.hLine = pyg.InfiniteLine(angle=0, movable=False)

        plot.addItem(self.vLine, ignoreBounds = True)
        plot.addItem(self.hLine, ignoreBounds = True)

        plot.scene().sigMouseClicked.connect(self.onClick)
        plot.scene().sigMouseMoved.connect(self.MouseMoved)

        self.slopePlot = plot.plot()
        self.ImaxPlot = plot.plot()

        device = d.find_device(self.Device.currentText())
        self.numJJs = device.num_JJs

        self.nameLabel.setText("Name: %s "%device.name)
        self.numLabel.setText("Num JJs: %s"%device.num_JJs)
        self.sizeLabel.setText("JJ Size: %s (um)"%device.JJ_radius_nom)
        if self.squid:
            '''
            Get current_RN
            '''
            Rn=d.show_squid_measurement_from_device_recent(self.Chip.currentText(), self.Device.currentText()).Rn
            self.current_Rn.setText("Current Rn: %f" %Rn)
        else:
            meas = d.get_measurement_from_device_recent(self.Chip.currentText(),device.name)
            Rn = meas.Rn
            Imax = meas.Imax
            self.current_Rn.setText("Current Rn: %f" %Rn)
            self.current_Imax.setText("Current Imax: %f" %Imax)
            self.vLine_meas = pyg.InfiniteLine(angle=90, movable=False, label="Current Imax")
            plot.addItem(self.vLine_meas, ignoreBounds = True)
            self.vLine_meas.setPos(Imax)
        
    def clearRn(self):
        '''
        Resets class variables to zero, empty string or empty array
        '''
        self.slope_x = []
        self.slope_y = []
        self.Imaxx = []
        self.Imaxy = []
        self.count = 0



        self.rnEdit.setText('')
        self.imaxEdit.setText('')

        self.plotPoints(type="clear")

    def plotPoints(self,type="rn"):
        '''
        Plots points with color based on what type of graph it is
        '''
        if type=="rn":
            color = 'r'
            self.slopePlot.setData(self.slope_x, self.slope_y, symbol='o', symbolBrush=color, pen=color)
        elif type=="imax":
            color = 'g'
            self.ImaxPlot.setData(self.Imaxx, self.Imaxy, symbol='o', symbolBrush=color, pen=color)
        elif type=="clear":
            color='w'
            if self.tabWidget.currentIndex()==4:
                self.slopePlot.setData(self.slope_x, self.slope_y)
                self.ImaxPlot.setData(self.Imaxx, self.Imaxy)
            elif self.tabWidget.currentIndex()==6:
                self.ImaxPlot.setData(self.Imaxx, self.Imaxy, symbol='o', symbolBrush=color, pen=color)
            else:
                try:
                    self.slopePlot.setData([], [])
                    self.ImaxPlot.setData([], [])
                except AttributeError:
                    pass
        elif type=="tc":
            color='g'
            self.ImaxPlot.setData([self.TcCrit],[self.Rcrit],symbol='o', symbolBrush=color, pen=color)
        elif type=="lc":
            color='g'
            self.ImaxPlot.setData(self.Lcx, self.Lcy, symbol='o', symbolBrush=color, pen=color)
        elif type=="Ic":
            color='b'
            self.slopePlot.setData(self.newIcI,self.newIcV,symbol='o',symbolBrush=color,pen=None)
    def saveRn(self):
        '''
        Saves RN measurement
        
        Calls:
            
            Database v4
               
                -get_measurement_from_device
                
                -save_JJ_measurements_Rn 
        '''

        

       
        self.saveRnButton.setText("Saving...")
        self.saveRnButton.setEnabled(False)
        app.processEvents()
        import database_v4 as d
        chip = d.find_chip(self.Chip.currentText())
        device = d.find_device(self.Device.currentText())
        self.squid=self.is_Squid(self.Device.currentText())
        if not self.squid:
            import re,pdb
           # pdb.set_trace()
            self.dataDirectory = re.split("/", self.dataDirectory)[-3]
    
            measurements = d.get_measurements_from_device(chip,device)
            if measurements==-1:
                self.message_box("Measurement not found", 2)
                return
            if len(measurements)==1:
                m = measurements[0]
                if self.dataDirectory == self.findDateInfo(m.data_directory):
                    try:
                        new_rn = (float)(self.rnEdit.text())
                    except:
                       # self.message_box("No new rn value found", 2)
                        #return
                        pass
                    try:
                        new_imax = (float)(self.imaxEdit.text())
                    except:
                        # use the old one
                        new_imax = m.Imax
                    d.save_JJ_Measurements_Rn(chip.name, new_rn, new_imax, m.id, device.name)
                        
                    self.message_box("Success", 0)
                    
            else:
                for m in measurements:
                    if self.dataDirectory == self.findDateInfo(m.data_directory):
                        try:
                            new_rn = (float)(self.rnEdit.text())
                            print(new_rn)
                        except:
                            #self.message_box("No new rn value found", 2)
                            #return
                            pass
                        try:
                            new_imax = (float)(self.imaxEdit.text())
                        except:
                            # use the old one
                            new_imax = m.Imax
                        d.save_JJ_Measurements_Rn(chip.name, new_rn, new_imax, m.id, device.name)
                       
                        self.message_box("Success", 0)
        else:

            try:
                new_rn = (float)(self.rnEdit.text())
            except:
                self.message_box("No rn value found", 2)
                pass
            
            d.save_SQUID_Rn(self.Chip.currentText(), new_rn, device)
                    
        self.saveRnButton.setText("Save to DB")
        self.saveRnButton.setEnabled(True)
    def MouseMoved(self, evt):
        '''
        Reacts to mouse movement
        '''
        pos = evt

        mousePoint = self.Rnvb.mapSceneToView(pos)

        self.vLine.setPos(mousePoint.x())
        self.hLine.setPos(mousePoint.y())

        self.xpos = mousePoint.x()
        
    def onClick(self, event):
        '''
        Reacts to mouse click
        '''
        pos = event.pos()
        
        self.Rnvb = self.graphicsView_Rn.getPlotItem().vb
        mousePoint = self.Rnvb.mapSceneToView(pos)

        # try to match positon to index in data, this works well now
        [index, val] = min(enumerate(self.RnI), key = lambda i: abs(i[1]-self.xpos))

        self.count +=1
        # every two clicks find slope and display in text box
        if index>0 and index<len(self.RnV):
            if not self.squid:
                if self.count == 1:
                    self.slope_x.append(self.RnI[index])
                    self.slope_y.append(self.RnV[index])
                    self.plotPoints(type="rn")

                elif self.count == 2:
                    self.slope_x.append(self.RnI[index])
                    self.slope_y.append(self.RnV[index])
                    self.plotPoints(type="rn")
    
                    # find slope
                    self.slope = abs((self.slope_y[0]-self.slope_y[1])/(self.slope_x[0]-self.slope_x[1]))
                    self.slope = self.slope/self.numJJs
    
                    self.rnEdit.setText((str)(self.slope))
                elif self.count == 3:
                    self.Imaxx = [self.RnI[index]]
                    self.Imaxy = [self.RnV[index]]
                    self.plotPoints(type="imax")
                    self.imaxEdit.setText((str)(self.Imaxx[0]))
                else:
                    pass
            else:
                if self.count == 1:
                    self.slope_x.append(self.RnI[index])
                    self.slope_y.append(self.RnV[index])
                    self.plotPoints(type="rn")
    
                elif self.count == 2:
                    self.slope_x.append(self.RnI[index])
                    self.slope_y.append(self.RnV[index])
                    self.plotPoints(type="rn")
                    
                    # find slope
                    self.slope = abs((self.slope_y[0]-self.slope_y[1])/(self.slope_x[0]-self.slope_x[1]))
                    if not self.is_Squid(self.Device.currentText()):
                        self.slope = self.slope/self.numJJs
    
                    self.rnEdit.setText((str)(self.slope))
                else:
                    pass

    '''
    #######################################
    FIX LC FUNCTIONALITY
    #######################################
    '''
        
    def plotLC(self):
        plot= self.graphicsView_LC.getPlotItem()  
        try:
            plot.scene().sigMouseClicked.disconnect()
            plot.scene().sigMouseMoved.disconnect()
            self.clearLC()
        except:
            pass
        plot.clear()
        try:
            legend = plot.legend
            legend.scene().removeItem(legend)
        except:
            pass
        if (self.Wafer.currentText() == 'Wafer'):
            self.message_box("Please select a wafer", 1)
            return

        if (self.Chip.currentText() == 'Chip'):
            self.message_box("Please select a chip", 1)
            return
        if (self.Device.currentText() == 'Device'):
            self.message_box("Please select a device", 1)
            return
        if not self.is_Squid(self.Device.currentText()):
            self.message_box("You can only fix LC for Squid devices!", 1)
            return
            
        outputs=pg.plot_from_GUI(self.app,plot,self.Chip.currentText(),self.Device.currentText(),plottype="LC")
        if (outputs == -1):
            self.message_box("Something went wrong", 2)
            return
        else:
            '''
            IMAX OUTPUTS
            '''
            
            self.LcI = outputs[2]
            self.LcV = outputs[3]
            

        
        self.current_Vresstep.setText("Test")
        self.device_SQ.setText("Current Vresstep:")
        self.Lcvb = plot.vb

        self.vLine = pyg.InfiniteLine(angle=90, movable=False)
        self.hLine = pyg.InfiniteLine(angle=0, movable=False)

        plot.addItem(self.vLine, ignoreBounds = True)
        plot.addItem(self.hLine, ignoreBounds = True)

        plot.scene().sigMouseClicked.connect(self.onClickLC)
        plot.scene().sigMouseMoved.connect(self.MouseMovedLC)
        
        
        self.slopePlot = plot.plot()
        self.ImaxPlot = plot.plot()
        
        device = d.find_device(self.Device.currentText())
        self.device_SQ.setText("Device: %s "%device.name)
        
        meas = d.show_squid_measurement_from_device_recent(self.Chip.currentText(),device.name)
        Vresstep = meas.I_LC_step
        self.current_Vresstep.setText("Current Vresstep: "+str(Vresstep))
        
        self.hLine_meas = pyg.InfiniteLine(angle=0, movable=False, label="Current Vresstep")
        plot.addItem(self.hLine_meas, ignoreBounds = True)
        self.hLine_meas.setPos(Vresstep)

        
    def clearLC(self):
        self.plotPoints(type="clear")
        self.countLc=0
        self.Lcvb=0
        self.LcCrit=0
        self.dataDirectory=0    
        self.LcEdit.setText('')   

        
    def saveLC(self):
        self.saveLCButton.setText("Saving...")
        self.saveLCButton.setEnabled(False)
        app.processEvents()
        import database_v4 as d
        chip = d.find_chip(self.Chip.currentText())
        device=d.find_device(self.Device.currentText())
        d.save_SQUID_LC(chip.name, self.LcCrit, device)
        self.saveLCButton.setText("Save to DB")
        self.saveLCButton.setEnabled(True)
    def onClickLC(self,event):
        pos = event.pos()
        
        self.Lcvb = self.graphicsView_LC.getPlotItem().vb
        mousePoint = self.Lcvb.mapSceneToView(pos)

        # try to match positon to index in data, this works well now
        [index, val] = min(enumerate(self.LcI), key = lambda i: abs(i[1]-self.xpos))

        self.countLc +=1
        # every two clicks find slope and display in text box
        if self.countLc==1:
            self.LcCrit=self.LcV[index]
            self.Lcx=[self.LcI[index]]
            self.Lcy=[self.LcV[index]]
            self.plotPoints(type="lc")
            self.LcEdit.setText((str)(self.LcCrit))

        else:
           pass

    def MouseMovedLC(self,evt):
        '''
        Reacts to mouse movement
        '''
        pos = evt
        self.Lcvb = self.graphicsView_LC.getPlotItem().vb
        mousePoint = self.Lcvb.mapSceneToView(pos)

        self.vLine.setPos(mousePoint.x())
        self.hLine.setPos(mousePoint.y())

        self.xpos = mousePoint.x()
        
        
    '''
    #######################################
    FIX IC FUNCTIONALITY
    #######################################
    '''
 
    def plotIc(self):
        '''
    
        Plots RN for a selected chip
        
        Calls the plot_from_GUI function from Plot Generation v2 
    
        '''
        plot = self.graphicsView_Ic.getPlotItem()
        self.Icvb = plot.vb
        try:
            plot.scene().sigMouseClicked.disconnect()
            plot.scene().sigMouseMoved.disconnect()
            self.clearIc()
        except:
            pass
        plot.clear()

        try:
            legend = plot.legend
            legend.scene().removeItem(legend)
        except:
            pass

        if (self.Wafer.currentText() == 'Wafer'):
            self.message_box("Please select a wafer", 1)
            return


        if (self.Chip.currentText() == 'Chip'):
            self.message_box("Please select a chip", 1)
            return
        if (self.Device.currentText() == 'Device'):
            self.message_box("Please select a device", 1)
            return
        
        rv = pg.plot_from_GUI(self.app, plot, self.Chip.currentText(), self.Device.currentText(),plottype="IC")
        
        if (rv == -1):
            self.message_box("Something went wrong", 2)
            return
        else:
            self.IcI = rv[0]
            self.IcV = rv[1]
            self.dataDirectory = rv[2]
            self.critfile=rv[3]
        print("Used Directory %s" % self.dataDirectory)
        

        self.vLine = pyg.InfiniteLine(angle=90, movable=False)
        self.hLine = pyg.InfiniteLine(angle=0, movable=False)

        plot.addItem(self.vLine, ignoreBounds = True)
        plot.addItem(self.hLine, ignoreBounds = True)

        plot.scene().sigMouseClicked.connect(self.onClickIc)
        plot.scene().sigMouseMoved.connect(self.MouseMovedIc)

        self.slopePlot = plot.plot()

        device = d.find_device(self.Device.currentText())
        self.numJJs = device.num_JJs

        self.nameLabel.setText("Name: %s "%device.name)
        self.numLabel.setText("Num JJs: %s"%device.num_JJs)
        self.sizeLabel.setText("JJ Size: %s (um)"%device.JJ_radius_nom)
        
        meas=d.get_measurement_from_device_recent(self.Chip.currentText(),self.Device.currentText())
        Iclist=[meas.Ic_neg,meas.Ic_pos,meas.Iret_pos,meas.Iret_neg]
        
        self.current_Ic_Neg.setText('Current Ic Neg: %.7f' % Iclist[0])
        self.current_Ic_Pos.setText('Current Ic Pos: %.7f' % Iclist[1])
        self.current_Ic_Ret_Pos.setText('Current Ic Ret Neg: %.7f' % Iclist[2])
        self.current_Ic_Ret_Neg.setText('Current Ic Ret Neg: %.7f' % Iclist[3])
    def clearIc(self):
        '''
        Resets class variables to zero, empty string or empty array
        '''
        self.icneg=0
        self.icpos=0
        self.icretpos=0
        self.icretneg=0
        self.countIc=0
        self.newIcI=[]
        self.newIcV=[]

        

        self.Select_Ic_Neg.setText('')
        self.Select_Ic_Pos.setText('')
        self.Select_Ic_Ret_Pos.setText('')
        self.Select_Ic_Ret_Neg.setText('')

        self.plotPoints(type="clear")

   
    def saveIc(self):
        '''
        Saves Updated Ic measurement to files and database
        '''
        import measure_Ic as ic
        import database_v4 as d

       
        self.saveIcButton.setText("Saving...")
        self.saveIcButton.setEnabled(False)
        app.processEvents()
        
        chip = d.find_chip(self.Chip.currentText())
        device = d.find_device(self.Device.currentText())

        Iclist=self.newIcI
        Vclist=self.newIcV
        
        self.critfile=self.critfile[25:-7]
        path="E:/Users/volt.686QVACTEST/National Institute of Standards and Technology (NIST)/SEG - SFQ_Circuits/"
        filename=path+self.critfile
        
        ic.save_ic_data(Iclist,Vclist, filename)   
        d.save_Fix_Ic(chip, device, Iclist)  
        
        print("Database and File Updated!")
        self.saveIcButton.setText("Save to DB")
        self.saveIcButton.setEnabled(True)
    
    def MouseMovedIc(self, evt):
        '''
        Reacts to mouse movement
        '''
        pos = evt
        mousePoint = self.Icvb.mapSceneToView(pos)

        self.vLine.setPos(mousePoint.x())
        self.hLine.setPos(mousePoint.y())

        self.xpos = mousePoint.x()
        
    def onClickIc(self, event):
        '''
        Reacts to mouse click
        '''
        pos = event.pos()
        
        self.Icvb = self.graphicsView_Ic.getPlotItem().vb
        mousePoint = self.Icvb.mapSceneToView(pos)

        # try to match positon to index in data, this works well now
        [index, val] = min(enumerate(self.IcI), key = lambda i: abs(i[1]-self.xpos))

        self.countIc +=1
        # every two clicks find slope and display in text box
        if index>0 and index<len(self.IcV):
            if self.countIc == 1:
                    self.icneg=self.IcI[index]
                    self.newIcI.append(self.IcI[index])
                    self.newIcV.append(self.IcV[index])
                    self.Select_Ic_Neg.setText('%.7f'%self.IcI[index])
        
                    self.plotPoints(type="Ic")

            elif self.countIc == 2:
                self.icpos=self.IcI[index]
                self.newIcI.append(self.IcI[index])
                self.newIcV.append(self.IcV[index])
                self.Select_Ic_Pos.setText('%.7f'%self.IcI[index])
        
                self.plotPoints(type="Ic")

                # find slope

            elif self.countIc == 3:
                self.icretpos=self.IcI[index]
                self.newIcI.append(self.IcI[index])
                self.newIcV.append(self.IcV[index])
                self.Select_Ic_Ret_Pos.setText('%.7f'%self.IcI[index])
        
                self.plotPoints(type="Ic")

            elif self.countIc==4:
                self.icretneg=self.IcI[index]
                self.newIcI.append(self.IcI[index])
                self.newIcV.append(self.IcV[index])
                self.Select_Ic_Ret_Neg.setText('%.7f'%self.IcI[index])
                self.plotPoints(type="Ic")
            else:
                pass
            
    '''
    #######################################
    PID Tune Functionality
    #######################################
    '''
    def update_temp_values(self):
        #Get all the values
        lake = vf.getLake()
        tempK = vf.getTempK(lake)
        tempC = tempK - 273
        setpoint = vf.getTempSetpoint(lake)
        heat_range = vf.getHeatRange(lake)
        heat_out = vf.getHeatOut(lake)
        #man_out = vf.
        pid = vf.getPID(lake)
        pid_split = pid.split(',')
        P = pid_split[0]
        I = pid_split[1]
        D = pid_split[2]
        
        #Put them in the QLineEdits
        self.tempK_disp.setText(str(tempK))
        self.tempC_disp.setText('%.2f'%tempC)
        self.setpoint_disp.setText(str(setpoint))
        #self.range_disp.setText(str(heat_range))
        self.output_disp.setText(str(heat_out))
        #self.manual_disp.setText(***)
        self.p_disp.setText(str(P))
        self.i_disp.setText(str(I))
        self.d_disp.setText(str(D))
       
        if heat_range == '0':
            self.range_disp.setText('Off - 0 W')
            self.range_disp2.setText('0 W')
        elif heat_range == '1':
            self.range_disp.setText('Low - 0.5 W')
            self.range_disp2.setText('0.5 W')
        elif heat_range == '2':
            self.range_disp.setText('Medium - 5 W')
            self.range_disp2.setText('5 W')
        elif heat_range == '3':
            self.range_disp.setText('High - 50 W')
            self.range_disp2.setText('50 W')

    def set_temp_controller(self):
        lake = vf.getLake()
        vf.setTempSetpoint(lake, self.setpoint_choose.text())
        try:
            vf.setPID(lake, float(self.p_choose.text()), float(self.i_choose.text()), float(self.d_choose.text()))
        except ValueError:
            if not self.d_choose.text():
                 self.d_choose.text()==0
            if not self.p_choose.text():
                self.p_choose.text()==1
            if not self.i_choose.text():
                self.i_choose.text()==1
            vf.setPID(lake, float(self.p_choose.text()), float(self.i_choose.text()), float(self.d_choose.text()))
        
        vf.setManualOutput(lake, self.manual_choose.text())

        if str(self.range_choose.currentText()) == 'Off - 0W':
            vf.setRange(lake, 0)
        elif str(self.range_choose.currentText()) == 'Low - 0.5 W':
            vf.setRange(lake, 1)
        elif str(self.range_choose.currentText()) == 'Medium - 5 W':
            vf.setRange(lake, 2)
        elif str(self.range_choose.currentText()) == 'High - 50 W':
            vf.setRange(lake, 3)
            
    def update_setpoint(self):
        if not (self.setpoint_choose.text()):
            self.message_box("Make sure you have entered a value for the temperature setpoint!")
        else:
            lake = vf.getLake()
            vf.setTempSetpoint(lake,self.setpoint_choose.text())
    
    def update_PID(self):
        if not (self.d_choose.text() and self.p_choose.text() and self.i_choose.text()):
            self.message_box("Make sure you have entered values for P, I, and D!", 1)
        else:
            lake = vf.getLake()
            vf.setPID(lake, float(self.p_choose.text()), float(self.i_choose.text()), float(self.d_choose.text()))
    
    def update_manual_output(self):
        if not (self.manual_choose.text()):
            self.message_box("Make sure you have entered a value for manual output!", 1)
        else:
            lake = vf.getLake()
            vf.setManualOutput(lake, self.manual_choose.text())

    def update_heater_range(self):
        lake = vf.getLake()
        if str(self.range_choose.currentText()) == 'Off - 0W':
            vf.setRange(lake, 0)
        elif str(self.range_choose.currentText()) == 'Low - 0.5 W':
            vf.setRange(lake, 1)
        elif str(self.range_choose.currentText()) == 'Medium - 5 W':
            vf.setRange(lake, 2)
        elif str(self.range_choose.currentText()) == 'High - 50 W':
            vf.setRange(lake, 3)     

    def findDateInfo(self, directory):
        """
        Gets date information based on directory string parameter
        """
        import re
        return  re.split("%2F",directory)[-1]

   
    def is_Crossbar(self,device_name):
        device = d.find_device(device_name)
        return device.device_type == 'Crossbar'

        
    def is_Via(self, device_name):
        device = d.find_device(device_name)
        return device.device_type == 'Via'
    def is_Squid(self, device_name):
        device = d.find_device(device_name)
        return device.device_type == 'SQUID'


    def NOTHINGHERE():
        print("Someday a great function will grace this workspace, until that day we wait")
    
def main():
    global app
    app = QtCore.QCoreApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    else:
        pass
    window = MyApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    
    
    
    
       
    
        
       
    

