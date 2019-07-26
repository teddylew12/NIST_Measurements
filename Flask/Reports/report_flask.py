# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 14:08:50 2018

@author: sdk

Many comments added by Nathan 
This file contains all of the view functions for the web application. Each @app.route() specifies a url and the following function tells the browser what to do
when at that url. In most cases, data is pulled from the database, manipulated, and then sent to an HTML template for rendering. Each 'redirect' tells the 
browser to redirect to some other url (specified by url_for()) and each render_template tells the browser to display the specified html template with the
specified data
"""
from flask import Flask
from flask import render_template, request, redirect, url_for
import sqlalchemy as sa

import sys

sys.path.append("..")
from Helpers import Web_Plot_Generation as wpg
from Helpers import database_for_flask as d

app = Flask(__name__)

app.config['SQLALCHEMY_POOL_RECYCLE'] = 30  # was 299
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 20


engine = sa.create_engine("mysql+pymysql://volt:pass@132.163.82.9/seg_sfq_v0", echo=False, pool_recycle=30) #creates engine for talking with the database
d.Base.metadata.create_all(engine) #creates all tables in database_for_flask if not already created
Session = sa.orm.sessionmaker(bind=engine) #opens the session between the database and engine
session = Session()

# ====
# Global vairables
# ====
wafer_chip_grid = ['0','1','2',
                   'https://nistgov.sharepoint.com/sites/SEG/Shared%20Documents/SFQ_circuits_info/Designs/ChipGrid-Challenger.png?web=1',
                   '4','5',
                   'https://nistgov.sharepoint.com/sites/SEG/Shared%20Documents/SFQ_circuits_info/Designs/Wafer-ChipTray-pcm2a-singleJJs.png?web=1',
                   'https://nistgov.sharepoint.com/sites/SEG/Shared%20Documents/SFQ_circuits_info/Designs/Wafer-ChipTray-resonators.png?web=1']


@app.route('/')
@app.route('/index')
def index():
    # redirect to the real home page
    return redirect(url_for('report'))

#Note: David wanted the wafer reports separated by design, so this is a new version that separates the reports into singles and everything else
#the old version rendered wafer_report2.html which is still in the templates folder.
@app.route('/wafer_report', methods=['GET', 'POST'])
def wafer_report():
    #wafer_report comes after the user inputs a wafer on the report page and a design on the wafer_selected_report page
    # get id from form 
    wafer_id = request.args.get('wafer_select')

    try:
        wafer_id = int(wafer_id)
    except:
        return redirect(url_for('report')) #If no wafer was specified, the user didn't come from the report page, so redirect them there
    
    wafer = d.find_wafer(wafer_id) #Find the wafer associated with wafer_id
    comment=wafer.comment #Get the comment associated with the wafer
    
    measured_map = measured_chips(wafer)
    
    chips = d.show_chips_from_wafer(wafer.id) #get all of the chips from the wafer
    
    
    devices = d.show_devices_from_chip(chips[0].id) 
    devices = [d for d in devices if d.num_JJs is not None and d.num_JJs!=0]
    
    # will be Json with critical values
    
    
#    Ic_data = wpg.get_crit_data(chips, devices)
    
    design_id = int(request.form.get('design_select')) #get the design from the form on the wafer_selected_report page
    design = d.find_design(design_id) #get the design object given its id
    
    #Format chip_dict for passing into get_crit_data
    chip_dict = {} #Initialize a chip dictionary
    chip_dict[design_id] = [] #Make its first key the current design_id
    for chip in chips: #Loop through the chips with measurements
      if chip.design_id == design_id: #If the chip has the correct design
        chip_dict[design_id].append(chip) #Add the chip to the dictionary under the design id

    Ic_data = wpg.get_crit_data(chip_dict) #Get the data

    dev_names = [d.name for d in devices]
    device_types = []
    
    for dev in devices: 
        if dev.device_type not in device_types:
            device_types.append(dev.device_type)
    
    print("design.name")
    print(design.name)
    if design.name == "Singles2_2.7":
      return render_template('wafer_report_singles.html',
                              wafer=wafer,
                              measured_map=measured_map,
                              dev_names=dev_names,
                              device_types=device_types,
                              Ic_data=Ic_data,
                              design=design,
                              comment=comment)
    else:  
      return render_template('wafer_report_pcm3a.html', 
                           wafer=wafer,
                           measured_map=measured_map, 
                           dev_names=dev_names,
                           device_types=device_types,
                           design=design,
                           Ic_data=Ic_data,
                           comment=comment,
                           test="test")
     
    
@app.route('/chip_report', methods=['GET','POST'])
def chip_report():
    import re
    from flask import request

    chip_name = 0

    dev_filter = request.form.get('filter_dev')
    chip_id = request.form.get('chip_select')
#    chip_id = 112
    
    if dev_filter is not None:
        post_params = re.split('//', str(dev_filter))
        chip_name = post_params[0]
        dev_filter = post_params[1]
        if dev_filter == "All":
            dev_filter = 0
    
    #Find the correct chip
    if chip_name == 0:
        try: 
            chip = d.find_chip(int(chip_id))
        except:
            d.session.rollback()
    else: 
        try:
            chip = d.find_chip(chip_name)
        except:
            d.session.rollback()
    
    #Find the associated wafer
    wafer=d.find_wafer(chip.wafer_id)
    comment=wafer.comment
    
    #For other types of chips
    if ("PCM3B" in  d.find_design(chip.design_id).name):
        pcm3b_data = wpg.get_data_pcm3b(chip.name)
        SQUID_data = wpg.get_data_SQUID(chip.name)
    elif ("SQUID Chip" in d.find_design(chip.design_id).name):
    	SQUID_data = wpg.get_data_SQUID(chip.name)
    elif("PCMRS" in d.find_design(chip.design_id).name):
        pcmrs_data = wpg.get_data_PCMRS(chip.name)
    
    if chip is None:
        return "Error! Known bug due to A/B in wafer name!"
    
    devices = d.show_devices_from_chip(chip.id)
    
    design = ""
    try:
        design = d.find_design(chip.design_id).name
    except:
        pass
    
    device_types = []
    
    for dev in devices: 
        if dev.device_type not in device_types:
            device_types.append(dev.device_type)

    
    device_type_filtered = "All"
    if dev_filter in device_types:
        device_type_filtered = dev_filter
        devices = [x for x in devices if x.device_type==dev_filter]
        device_types = [dev_filter]
   
    
    data = wpg.get_data(chip, devices)
    
    other_chips = d.show_chips_from_wafer(chip.wafer_id)
    
    if ("Singles" in  d.find_design(chip.design_id).name):
        return render_template('single_chip_report2.html', chip=chip,
                           other_chips=other_chips,
                           data=data,
                           device_types=device_types,
                           device_type_filtered=device_type_filtered,
                           design=design,
                           test=d.find_design(chip.design_id).name.lower())
    elif("PCM3B" in  d.find_design(chip.design_id).name):
        return render_template('pcm3b_report.html', chip=chip,
                               other_chips=other_chips,
                               pcm3b_data=pcm3b_data,
                               SQUID_data=SQUID_data,
                               design=design,
                               comment=comment)
    elif("SQUID Chip" in d.find_design(chip.design_id).name):
    	return render_template('SQUID_report.html', chip=chip,
    							other_chips=other_chips,
    							SQUID_data=SQUID_data,
    							design=design,
    							comment=comment)
    elif("PCMRS" in d.find_design(chip.design_id).name):
        return render_template('pcmrs_report.html', chip=chip,
                               other_chips=other_chips,
                               pcmrs_data=pcmrs_data,
                               design=design,
                               comment=comment)
    else:
        return render_template('chip_report_format.html', chip=chip,
                           other_chips=other_chips,
                           data=data,
                           device_types=device_types,
                           device_type_filtered=device_type_filtered,
                           design=design,
                           comment=comment,
                           test= d.find_design(chip.design_id).name.upper())
    
@app.route('/report')
def report():
    session.commit()

    wafers = d.show_all_wafers()

    wafer = wafers[-4]
    chips = d.show_chips_from_wafer(wafer.name)

    session.close()
    return render_template('reports.html',
                           title='Report',
                           wafers=wafers,
                           chips = chips,
                           )




@app.route("/wafer_selected", methods=['GET', 'POST'])
def wafer_selected():
    wafer_id = int(request.form.get('wafer_selected_for_chips'))
    wafer = d.find_wafer(wafer_id)
    chips = d.show_chips_from_wafer(wafer_id)
#    
#    
    return render_template('wafer_selected_form.html', chips = chips,
                           wafer = wafer)

@app.route("/wafer_selected_report", methods=['GET', 'POST'])
def wafer_selected_report():
  wafer_id = int(request.form.get('wafer_select'))
  wafer = d.find_wafer(wafer_id)
  chips = d.show_chips_from_wafer(wafer_id)
  designs = []
  for c in chips:
    if c.type not in designs:
      designs.append(c.type)

  return render_template('wafer_selected_report.html', wafer = wafer, designs = designs)

def measured_chips(wafer):
    '''
    This creates the array for the chip map which is plotted in wafer_report
    '''

    #wafer_id = 3
    #wafer = session.query(Wafer).first()
    chips = d.show_chips_from_wafer(wafer.name)
    heat_map = ''
    row_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H','I','J','K', 'L']
    
    exclude_poses = [(0,0), (0,1), (0,2), (1,0), (1,1), (2,0), # bottom left
                     (0,9), (0,10), (0,11), (1,10), (1,11), (2,11), # top left
                     (11,11), (11,10), (11,9), (10,11), (10,10), (9,11), # top right
                     (11,0), (11,1), (11,2), (10,0), (10,1), (9,0)] # bottom right
    
    
    #This is loop is going to make the entire list in a str
    
    for row in range(0,12):
        for col in range(0,12):
            if (col,row) not in exclude_poses:
                value = '0'
                heat_map = heat_map + '[' + str(col) + ',' + str(row) + ',' + value + '],'

    #This loop appends values for any found chips
    for i, chip in enumerate(chips):
        c = chips[i]
        row = row_labels.index(c.location[0])
         
        col = int(c.location[1])-1

        #Check to see if we have a ten's digit 
        if len(c.location) == 3:
            col = int(c.location[1] + c.location[2]) - 1

        #Lets get the measurements for this chip

        value = '100'
        heat_map = heat_map + '[' + str(col) + ',' + str(row) + ',' + value + '],'

        

    return heat_map



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=7000, threaded=True) #host='0.0.0.0' allows for the local ip to be used of the pc. I allows had to create an exception in windows firewall for port 5000
