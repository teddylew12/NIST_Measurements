# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 15:20:52 2018

@author: sdk
"""

# imports
from flask import Flask, redirect, url_for, render_template, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose

from flask_sqlalchemy import SQLAlchemy

app =  Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://volt:pass@132.163.82.9/seg_sfq_v0"
'''
The absolute opposite of a Secret Key smh
'''
app.config['SECRET_KEY'] = '123456790'
app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600
db = SQLAlchemy(app)

import sys
sys.path.append("Z:/JPulecio/Flask/")

from Helpers.database_for_flask import Chip, Wafer, JJ_Measurement, Design, Device, Squid_Measurement, Resistor_Measurement, Via_Measurement,Crossbar_Measurement
from Helpers import database_for_flask as d
from Helpers import Web_Plot_Generation as wpg

import json

@app.route('/')
def index():
    return redirect(url_for('admin.index'))

@app.route('/test')
def test():
    return "test"

class DeviceAdmin(ModelView):
    column_filters = ('name', 'card1', 'card2')
    column_default_sort = ('id', True)
    
    def __init__(self, session):
        # Just call parent class with predefined model.
        super(DeviceAdmin, self).__init__(Device, session)



class JJ_MeasurementAdmin(ModelView):
    column_filters = ('date', 'chip_name', 'time', 'design_name','device_name','num_JJs','JJ_radius_nom',\
                      'Ic_pos', 'Ic_neg', 'Iret_pos', 'Iret_neg', 'Imax', 'Rn')
    column_default_sort = ('id', True)
    
    def __init__(self, session):
        # Just call parent class with predefined model.
        super(JJ_MeasurementAdmin, self).__init__(JJ_Measurement, session)

class Squid_MeasurementAdmin(ModelView):
    column_filters = ('date', 'chip_name', 'time', 'design_name','device_name','num_JJs',\
                      'Ic_pos', 'Ic_neg', 'Iret_pos', 'Iret_neg', 'Imax', 'Rn')
    column_default_sort = ('id', True)
    
    def __init__(self, session):
        # Just call parent class with predefined model.
        super(Squid_MeasurementAdmin, self).__init__(Squid_Measurement, session)
class Resistor_MeasurementAdmin(ModelView):
    column_filters = ('date', 'chip_name', 'time', 'design_name','device_name','num_Rs',\
                      'R_4k_2000uA', 'R_4k_1000uA','R_4k_500uA', 'Rsqs_4k_2000uA', ' Rsqs_4k_1000uA', 'Rsqs_4k_500uA')
    column_default_sort = ('id', True)
    
    def __init__(self, session):
        # Just call parent class with predefined model.
        super(Resistor_MeasurementAdmin, self).__init__(Resistor_Measurement, session)
class Via_MeasurementAdmin(ModelView):
    column_filters = ('date', 'chip_name', 'time', 'design_name','device_name','R_4k','R_RT','Imax')
    column_default_sort = ('id', True)
    
    def __init__(self, session):
        # Just call parent class with predefined model.
        super(Via_MeasurementAdmin, self).__init__(Via_Measurement, session)
        
class Crossbar_MeasurementAdmin(ModelView):
    column_filters = ('date', 'chip_name', 'time', 'design_name','device_name','R_10k','R_RT','Tc')
    column_default_sort = ('id', True)
    
    def __init__(self, session):
        # Just call parent class with predefined model.
        super(Crossbar_MeasurementAdmin, self).__init__(Crossbar_Measurement, session)
class Custom_JJ_Meas(BaseView):
    """ This a custom class that subclasses BaseView, allows to add to the flask 
    navigation menu
    
    """
    def __init__(self, session, name=None, endpoint=None):
        # is this needed?
        # pass the session into this class so it can be used        
        self.session = session
        super(Custom_JJ_Meas, self).__init__(name, endpoint)
        
    @expose('/')
    def index(self):
        # see if a rollback is needed, the except block
        try:
            d.find_chip(111)
        except:
            d.session.rollback()
        
        #TODO format this as a Json
        # get all JJ measurements
        meas = d.show_all_JJ_measurements()
        meas[:] = [x.toJson() for x in meas]
        return self.render('JJ_meas_custom.html', meas=meas)#, test_data=json.dump(meas[-4:]))

# this page is navigated to when a custom JJ meas is clicked on
@app.route('/device_detail', methods=['GET','POST'])
def device_detail():
    
    # comes from the hidden forms on html for custom JJ page
    chip_name = str(request.form.get('chip_name'))
    dev_name = str(request.form.get('dev_name'))
    dir_name = str(request.form.get('dir_name'))
    
    # find objects
    chip = d.find_chip(chip_name)
    dev = [d.find_device(dev_name, chip.design_id)]
    
    # get data from files 
    ic_data = wpg.get_rawdata(chip, dev, given_dir=dir_name)
    rn_data = wpg.get_rawdata(chip, dev, given_dir=dir_name, rn=True)
    
    
    return render_template('device_detail.html', 
                           chip_name=chip_name,
                           dev_name=dev_name,
                           dir_name=dir_name,
                           ic_data=ic_data,
                           rn_data=rn_data)
 
def toJSON(obj):
        return json.dumps(obj, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)


class WaferView(ModelView):
    column_labels = dict(Jc_approx='Jc (kA/(cm)^2)') #Changed from A/m^2 to kA/(cm)^2 on 7/22/19

if __name__ == '__main__':

    admin = Admin(app, name = 'SFQ Cirucits')
    admin.add_view(WaferView(Wafer, db.session)) 
    admin.add_view(ModelView(Chip, db.session))
    admin.add_view(ModelView(Design, db.session))
    admin.add_view(ModelView(Device, db.session))
   
    admin.add_view(JJ_MeasurementAdmin(db.session))
    admin.add_view(ModelView(Squid_Measurement, db.session))
    admin.add_view(ModelView(Resistor_Measurement, db.session))
    admin.add_view(ModelView(Via_Measurement, db.session))
    admin.add_view(ModelView(Crossbar_Measurement,db.session))
    admin.add_view(Custom_JJ_Meas(session=db.session))
   
    app.run(debug=True, host='0.0.0.0') #host='0.0.0.0' allows for the local ip to be used of the pc. I allows had to create an exception in windows firewall for port 5000
