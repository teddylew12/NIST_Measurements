"""
test
"""
import sys, os
from PyQt5 import QtCore, QtGui, uic, QtWidgets

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import pyqtgraph.exporters
from pyqtgraph.ptime import time
import random
import imp

import IV_curve_v3 as iv
import Input_Functions as inpfunc
import database_v4 as d

qtCreatorFile = "IV_GUI.ui"  # Enter ui file here.
print(qtCreatorFile)
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

# suppress all printing
# sys.stdout = open(os.devnull, 'w')
Save=False
class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
   
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.Save=False
        self.setupUi(self)
        self.my_graph1 = GraphWidget(self)
        self.my_graph.addWidget(self.my_graph1)

        self.mA_button.toggled.connect(self.unitsFunc)
        self.clear_button.clicked.connect(self.clearFunc)
        self.refresh_button.clicked.connect(self.refreshFunc)
        self.measure_button.clicked.connect(self.plotter)
        self.stop_button.clicked.connect(self.stopfunc)
        self.exit_button.clicked.connect(self.close)
        self.export_button.clicked.connect(self.exportfunc)
        self.Wafer.currentIndexChanged.connect(self.waferselectionchange)
        self.Chip.currentIndexChanged.connect(self.chipselectionchange)
        self.Device.currentIndexChanged.connect(self.deviceselectionchange)
        # defining functions for enter being pressed in a field:
        self.I_min_EditField.returnPressed.connect(self.I_min_enter)
        self.I_max_EditField.returnPressed.connect(self.I_max_enter)
        self.step_EditField.returnPressed.connect(self.step_enter)
        self.card_EditField.returnPressed.connect(self.card_enter)
        self.saveRadio.toggled.connect(self.changeSave)
        #
        # these are different because they are drop-downs
        channel1_edit = self.channel1_EditField.lineEdit()
        channel2_edit = self.channel2_EditField.lineEdit()
        channel1_edit.returnPressed.connect(self.channel1_enter)
        channel2_edit.returnPressed.connect(self.channel2_enter)
        self.sweep_EditField.returnPressed.connect(self.sweep_enter)
        wafers = d.show_all_wafers()
        for i in range(0,len(wafers)):
            self.Wafer.addItem(wafers[i].name)


        # self.status_text.setText("Status: Ready")

    # functions to change focus when enter is pressed:
    def I_min_enter(self):
        self.I_max_EditField.setFocus()
    def I_max_enter(self):
        self.step_EditField.setFocus()
    def step_enter(self):
        self.card_EditField.setFocus()
    def card_enter(self):
        self.channel1_EditField.setFocus()
    def channel1_enter(self):
        self.channel2_EditField.setFocus()
    def channel2_enter(self):
        self.sweep_EditField.setFocus()
    def sweep_enter(self):
        self.plotter()

    # To save the plot, when 'export' is pressed
    def exportfunc(self):
        self.exporter = pg.exporters.ImageExporter(self.my_graph1.plot.plotItem)
        self.exporter.export()

    # Clear Button
    def clearFunc(self):
        try:
            self.my_graph1.plot.clear()
        except:
            pass
    def changeSave(self):
        if (self.saveRadio.isChecked()):
            self.Save=True
            
        else:
            self.Save=False
    def unitsFunc(self):
        if (self.mA_button.isChecked()):
            self.label.setText("I Min (mA)")
            self.label_2.setText("I Max (mA)")
            self.label_9.setText("mA")
            self.step_helper.setItemText(0,"(mA) Increment")
            multiplier = 1e03

        else:
            self.label.setText("I Min (A)")
            self.label_2.setText("I Max (A)")
            self.label_9.setText("A")
            self.step_helper.setItemText(0,"(A) Increment")
            multiplier = 1e-03
        try:
            I_min = (float)(self.I_min_EditField.text())
            I_max = (float)(self.I_max_EditField.text())
            steps = (float)(self.step_EditField.text())
    
            self.I_min_EditField.setText(str(multiplier*I_min))
            self.I_max_EditField.setText(str(multiplier*I_max))
            self.step_EditField.setText(str(multiplier*steps))
        except:
            pass






    def refreshFunc(self):
        imp.reload(d)
        imp.reload(iv)
        wafer_count = self.Wafer.count()
        for i in range(1, wafer_count+1):
            self.Wafer.removeItem(1)

        chip_count = self.Chip.count()
        for i in range(1, chip_count + 1):
            self.Chip.removeItem(1)

        device_count = self.Device.count()
        for i in range(1, device_count + 1):
            self.Device.removeItem(1)

        wafers = d.show_all_wafers()
        for i in range(0, len(wafers)):
            self.Wafer.addItem(wafers[i].name)

        self.I_min_EditField.setText('');self.I_max_EditField.setText('')
        self.step_EditField.setText('');self.card_EditField.setText('')
        self.channel1_EditField.setCurrentIndex(0);self.channel2_EditField.setCurrentIndex(0)
        self.sweep_EditField.setText('')

    # Function for JJ Radius drop-down selection change
    # def selectionchange(self):
    #     current = self.JJRadius.currentText()  # get text of the current selection
        # try:
        #     if float(current) == 0.6:
        #         self.I_max_EditField.setText('0.01e-03')
        #         self.I_min_EditField.setText('-0.01e-03')
        #         self.expected_ic.setText('0.003e-03')
        #     elif float(current) == 0.8:
        #         self.I_max_EditField.setText('0.01e-03')
        #         self.I_min_EditField.setText('-0.01e-03')
        #         self.expected_ic.setText('0.006e-03')
        #     elif float(current) == 0.9:
        #         self.I_max_EditField.setText('0.012e-03')
        #         self.I_min_EditField.setText('-0.012e-03')
        #         self.expected_ic.setText('0.009e-03')
        #     elif float(current) == 1.2:
        #         self.I_max_EditField.setText('0.02e-03')
        #         self.I_min_EditField.setText('-0.02e-03')
        #         self.expected_ic.setText('0.015e-03')
        #     elif float(current) == 1.9:
        #         self.I_max_EditField.setText('0.1e-03')
        #         self.I_min_EditField.setText('-0.1e-03')
        #         self.expected_ic.setText('0.04e-03')
        #     elif float(current) == 2.4:
        #         self.I_max_EditField.setText('0.1e-03')
        #         self.I_min_EditField.setText('-0.1e-03')
        #         self.expected_ic.setText('0.07e-03')
        #     elif float(current) == 3.0:
        #         self.I_max_EditField.setText('0.2e-03')
        #         self.I_min_EditField.setText('-0.2e-03')
        #         self.expected_ic.setText('0.11e-03')
        #     elif float(current) == 3.6:
        #         self.I_max_EditField.setText('0.2e-03')
        #         self.I_min_EditField.setText('-0.2e-03')
        #         self.expected_ic.setText('0.16e-03')
        # except:
        #     self.I_max_EditField.setText('')
        #     self.I_min_EditField.setText('')
        #     self.expected_ic.setText('-')

    def waferselectionchange(self):
        current = self.Wafer.currentText()
        if current!='Wafer':
            chips = d.show_chips_from_wafer(current)
            chip_count = self.Chip.count()
            for i in range(1,chip_count+1):
                self.Chip.removeItem(1)
            for i in range(0,len(chips)):
                self.Chip.addItem(chips[i].name)

    def chipselectionchange(self):
        current = self.Chip.currentText()
        if current != 'Chip':
            devices = d.show_devices_from_chip(current)
            dev_count = self.Device.count()
            for i in range(1,dev_count+1):
                self.Device.removeItem(1)
            for i in range(0,len(devices)):
                self.Device.addItem(devices[i].name)
            self.Jc = d.chip_Jc(current)
    def deviceselectionchange(self):
        current = self.Device.currentText()
        if current != 'Device':
            device = d.find_device(current)
            Input = inpfunc.format_input_Ic_Ir_devices([device], self.Jc)
            # print(input)
            cards = Input[0]
            channels = Input[1]
            chan1 = channels[0]
            chan2 = channels[1]
            sweeps = Input[2]
            Imin = sweeps[0]
            # Imin = "%0.2E" % Imin
            Imax = sweeps[1]
            # Imax = "%0.2E" % Imax
            step = Input[3]
            step = (float)("%0.2E"%step[0])
            # step = step[0]
            num_sweep= Input[4]

            self.channel1_EditField.setCurrentIndex(chan1 - 1)
            self.channel2_EditField.setCurrentIndex(chan2 - 1)

            if self.mA_button.isChecked():
                multplier = 1000
            else:
                multplier = 1
            print(cards)
            if not self.lockbutton.isChecked():
                self.I_min_EditField.setText(str(Imin*multplier)); self.I_max_EditField.setText(str(Imax*multplier))
                self.step_EditField.setText(str(step*multplier)); self.card_EditField.setText(str(cards[0]))
                self.card2_EditField.setText(str(cards[1]))
                self.step_helper.setCurrentIndex(0)

                # print("ok")
                self.sweep_EditField.setText(str(num_sweep[0]))
                # print(input)



        # Event that is called when the 'X', or 'Exit' button is pushed
    def closeEvent(self, a0: QtGui.QCloseEvent):
        try:
            self.timer.stop()
        except:
            pass
        finally:
            cancel_menu = QtWidgets.QMessageBox()
            cancel_menu.setWindowTitle('Exiting')
            cancel_menu.setText('Are you sure?')
            cancel_menu.setIcon(QtWidgets.QMessageBox.Warning)
            cancel_menu.setDetailedText('Selecting \'OK\' will set currents to zero and exit,'
                                        ' \'Cancel\' will return back to program.')
            cancel_menu.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            response = cancel_menu.exec_()
            if response == QtWidgets.QMessageBox.Ok:
                # -***Turn currents off here***
                iv.exitfunc()
                print("Exiting...")
                # QtCore.QCoreApplication.quit() # close the program # this was the fix to kernel die issue
                a0.accept()
            else:
                a0.ignore()

    def stopfunc(self):
        iv.stop()

    # When measure button is pushed
    def plotter(self):
        # Clear graph
        try:
            self.my_graph1.plot.clear()
        except:
            pass
        # Get inputs
        inputs = self.getInput()
       
        # Format: [I_min, I_max, step, card, card2, channel1, channel2, sweep]
        # -1 if all are numbers, gives location of error otherwise
        wrong_box = self.checkValues(inputs)

        # units
        if self.mA_button.isChecked():
            multiplier = 1e-03
        else:
            multiplier = 1
        # Plotting:
        if wrong_box == -1:
            # converting from strings to int or float
            #for i in range(len(inputs)):
             #   try:
              #      inputs[i] = int(inputs[i])
               # except:
                #    inputs[i] = float(inputs[i])
            # print(variables) # for test purposes
            if "Increment" in self.step_helper.currentText():
                number = False
            else:
                number = True
            
            inputs[2] = iv.calc_steps(inputs[0], inputs[1], inputs[2], number)
            # print(inputs[2])
            title_text = "I-V Curve for %s_%s" % (self.Chip.currentText(), self.Device.currentText())
            g = self.my_graph1
            plot=g.plot
            g.plot.setTitle(title_text)
            self.data = [0]
            curves = []
            for i in range(0,inputs[6]):
                self.curve = g.plot.getPlotItem().plot()
                curves.append(self.curve)
            # print("here")
            # print(inputs)
#            iv.plot_IV_test(app,curves,inputs[6],inputs[0],inputs[1],inputs[2],inputs[3],inputs[4],inputs[5])
            # print("here1")
            # order of inputs: app, curve, num_sweeps, min, max, step, card, chan1, chan2
#            print(float(self.step_EditField.text()))

            # Format: [I_min, I_max, step, card, card2, channel1, channel2, sweep]
            
            I_min = inputs[0] * multiplier
            I_max = inputs[1] * multiplier
            step = inputs[2] * multiplier
            card1 = inputs[3]
            card2 = inputs[4]
            channel1 = inputs[5]
            channel2 = inputs[6]
            sweep = inputs[7]
            chip=d.find_chip(self.Chip.currentText())
            device=d.find_device(self.Device.currentText())
            iv.sweep_current_live_GUI(app,plot,curves,sweep,I_min,I_max,step,card1,card2,channel1,channel2,self.Save,chip,device)
            # Format: (app, curves, number_of_sweeps, I_min, I_max, step, card1, card2, channel1, channel2)


        # self.timer = QtCore.QTimer()
        # self.timer.timeout.connect(self.update)
        # self.timer.start(0)


        else:
            warning_box = QtWidgets.QMessageBox()
            if (wrong_box == 0):
                warning_box.setText("Increment is too big.")
            else:
                warning_box.setText(self.whichBox(wrong_box) + " needs to be a number.")
            warning_box.exec_()

            # Function to retrieve all editfield values and return them in an array of str
    def getInput(self):
        I_min =  float(self.I_min_EditField.text())
        I_max =  float(self.I_max_EditField.text())
        step =  float((self.step_EditField.text()))
        card =  int((self.card_EditField.text()))
        card2 = int((self.card2_EditField.text()))
        channel1 = int((self.channel1_EditField.currentText()))
        channel2 = int((self.channel2_EditField.currentText()))
        sweep = int( (self.sweep_EditField.text()))
        print(step)
        
        return [I_min, I_max, step, card, card2, channel1, channel2, sweep]

    # Function to check if all values are either ints or floats
    # returns -1 if contains no chars
    # returns 0 if Increment is too large
    def checkValues(self, inputs):
        for i in range(len(inputs)):
            try:
                int(inputs[i])
            except:
                try:
                    float(inputs[i])
                except:
                    return i
        if (float(inputs[1]) < float(inputs[0]) + float(inputs[2])):
            if self.step_helper.currentText() == 'Increment':
                return 0
        return -1

    # Return which edit field had chars in it
    def whichBox(self, number):
        a = ""
        if number == 0:
            a = "I_min"
        if number == 1:
            a = "I_max"
        if number == 2:
            a = "step"
        if number == 3:
            a = "card"
        if number == 4:
            a = "channel 1"
        if number == 5:
            a = "channel 2"
        if number == 6:
            a = "sweep"
        return a


# Class to add graph from pyqtgraph into the gui
class GraphWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(GraphWidget, self).__init__(parent)
        layout = QtWidgets.QGridLayout()
        self.plot = pg.PlotWidget()
        title_text = "I-V Curve between Channel X and Channel X"
        self.plot.setTitle(title_text)
        self.plot.setLabel('left', 'V', 'V')
        self.plot.setLabel('bottom', 'I', 'A')
        layout.addWidget(self.plot)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QtCore.QCoreApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    else:
        pass
    window = MyApp()
    window.show()
    sys.exit(app.exec_())