# -*- coding: utf-8 -*-
"""
Created on Fri Jun 30 16:52:50 2017

@author: javier pulecio
"""

import numpy as np
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, Float, String, ForeignKey, DECIMAL, ARRAY
from sqlalchemy.orm import relationship
import time
sa.__version__

#global variables
Ic_range_scale = 2.1 #Ic_range_scale sets the min and max sweep values for the IV curves
engine = sa.create_engine("mysql+pymysql://volt:pass@132.163.82.9/seg_sfq_v0", echo=False, pool_recycle=3600)
#Base class for objects
Base = declarative_base()
#Lets create our base classes

#Lets define our design_devices many to many assoication table
design_devices = Table('design_devices', Base.metadata,
    Column('design_id', Integer, ForeignKey('design.id')),
    Column('device_id', Integer, ForeignKey('device.id')))

class Wafer(Base):
    __tablename__ = 'wafer'

    id = Column(Integer, primary_key = True)
    name = Column(String(50))
    date = Column(String(12))
    Jc_approx = Column(Float)
    comment= Column(String(150))
    missing_width = Column(Float) #In um. Only used for wafers with PCMRS chips
   # chips = relationship("Chip", order_by=Chip.id, back_populates="wafer")
	
    def __repr__(self):
        return "<Wafer(name='%s', date='%s', Jc_approx='%s', comment='%s')>" %(self.name, self.date, self.Jc_approx, self.comment)

class Chip(Base):
    __tablename__ = 'chip'
    id = Column(Integer, primary_key = True)
    name = Column(String(50))
    location = Column(String(10))
    wafer_id = Column(Integer, ForeignKey('wafer.id'))
    design_id = Column(Integer, ForeignKey('design.id'))
    #wafer_name = Column(Integer, ForeignKey('wafer.name'))
    #design_name = Column(Integer, ForeignKey('design.name'))


    #wafer = relationship("Wafer", back_populates="chips") 
    #design = Column(String(50))
    #devices = Column(String(1000))

    def __repr__(self):
        return "<Chip(name='%s', location='%s', wafer_id='%s', design_id='%s')>" %(self.name, self.location, self.wafer_id, self.design_id)
     #return "<Chip(name='%s', location='%s', wafer_id='%s', design_id='%s', comment='%s')>" %(self.name, self.location, self.wafer_id, self.design_id,self.comment)

class Design(Base):
    'This takes in name of the device and string of tuples (device type, number of devices, junction radius in um, pads, channels)'
    __tablename__ = 'design'
    id = Column(Integer, primary_key = True)
    name = Column(String(50))
    date = Column(String(12))
    
    device_id = relationship("Device", secondary=design_devices, back_populates='design_id')

    def __repr__(self):
        return "<Design(name='%s', date='%s')>" %(self.name,self.date)

class Device(Base):
    __tablename__='device'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    device_type = Column(String(50))
    num_JJs = Column(Integer)
    JJ_radius_nom = Column(Float)
    pads = Column(String(50))
    card = Column(Integer)
    card1 = Column(Integer)
    card2 = Column(Integer)
    channel1 = Column(Integer)
    channel2 = Column(Integer)
    description = Column(String(500))

    design_id = relationship("Design", secondary=design_devices, back_populates='device_id')

    def __repr__(self):
#        return "<Device(device_name=%s, device_type='%s', num_JJs='%d', JJ_radius_nom='%f')>" %(self.name, self.device_type, self.num_JJs, self. JJ_radius_nom)
        return "<Device(device_name=%s, device_type='%s')>" %(self.name, self.device_type)

class JJ_Measurement(Base):
    'This takes in name of the device and string of tuples (device type, number of devices, junction radius in um, pads, channels)'
    __tablename__ = 'jj_measurement'
    id = Column(Integer, primary_key = True)
    date = Column(String(50)) #date measurement was taken
    time = Column(String(50)) #time measurement was taken
    chip_id = Column(Integer, ForeignKey('chip.id'))
    chip_name = Column(String(50))
    design_id = Column(Integer, ForeignKey('design.id'))
    design_name = Column(String(50))
    device_name = Column(String(50))
    num_JJs = Column(Integer)
    JJ_radius_nom = Column(Float)
    data_directory = Column(String(500)) #directory with data

    #Default jj_measurements
    Ic_pos = Column(Float) #The critical current positive side of IV curve
    Ic_neg = Column(Float) #The critical current negative side of IV curve
    Iret_pos = Column(Float) #The return critical current postive side of IV curve which depending on the damping below should show some slight hysteresis (i.e. slight difference between Ic and Iret)
    Iret_neg = Column(Float) #The return critical current negative side of IV curve which depending on the damping below should show some slight hysteresis (i.e. slight difference between Ic and Iret)
    Imax = Column(Float) #Max current before heating
    Rn = Column(Float) #Normal resistance which should be near the superconducting band gap. Due to heating we can measure the normal resistance slightly below the superconduting band gap.
    Iret_Ic_ratio = Column(Float) #This is an approximation of Beta which is the damping of the circuit. Ideally [underdamped] 0.9 < Beta > 1.0 [overdamped]. If the circuit is overdamped then it will not work at higher frequencies (~100GHz)
    Ic_Rn_product = Column(Float)
    Rn_Area_product = Column(Float)
    Inverse_sqrtRn = Column(Float)
    sqrtIc = Column(Float)
    R_roomTemp = Column(Float) #room temperature R
    tedindex=Column(Integer)
    
    Jc_nom = Column(DECIMAL(13,3)) #The critical current density Jc = Ic/Area of junction

    def __repr__(self):
        return "<JJ_Measurement(measurement_id='%s',device_name='%s', num_JJs='%d', JJ_radius='%f')>" %(self.id, self.device_name, self.num_JJs, self.JJ_radius_nom)

class Squid_Measurement(Base):
    'Squid Measurement'
    __tablename__ = 'squid_measurement'
    id = Column(Integer, primary_key = True)
    date = Column(String(50)) #date measurement was taken
    time = Column(String(50)) #time measurement was taken
    chip_id = Column(Integer, ForeignKey('chip.id'))
    chip_name = Column(String(50))
    design_id = Column(Integer, ForeignKey('design.id'))
    design_name = Column(String(50))
    device_name = Column(String(50))
    num_JJs = Column(Integer)
    data_directory = Column(String(500)) #directory with data

    #Default squid_measurements
    Ic_pos = Column(Float) #The critical current positive side of IV curve
    Ic_neg = Column(Float) #The critical current negative side of IV curve
    Iret_pos = Column(Float) #The return critical current postive side of IV curve which depending on the damping below should show some slight hysteresis (i.e. slight difference between Ic and Iret)
    Iret_neg = Column(Float) #The return critical current postive side of IV curve which depending on the damping below should show some slight hysteresis (i.e. slight difference between Ic and Iret)
    Imax = Column(Float) #Max current before heating
    Rn = Column(Float) #Normal resistance which should be near the superconducting band gap. Due to heating we can measure the normal resistance slightly below the superconduting band gap.
    Iret_Ic_ratio = Column(Float) #This is an approximation of Beta which is the damping of the circuit. Ideally [underdamped] 0.9 < Beta > 1.0 [overdamped]. If the circuit is overdamped then it will not work at higher frequencies (~100GHz)
    Ic_Rn_product = Column(Float)
    Rn_Area_product = Column(Float)
    Inverse_sqrtRn = Column(Float)
    sqrtIc = Column(Float)
    R_roomTemp = Column(Float) #room temperature R
    Jc_nom = Column(DECIMAL(13,3)) #The critical current density Jc = Ic/Area of junction

    #Addtional squid related measurements
    metal_layers = Column(String(50))
    JJ_radius_nom1 = Column(DECIMAL(13,3))
    JJ_radius_nom2 = Column(DECIMAL(13,3))
    Iflux_period = Column(Float)
    Ic_min_pos = Column(Float)
    Ic_min_neg = Column(Float)
    Delta_Ic_min = Column(Float)
    I_LC_step = Column(Float)
    Iflux_min_Ic = Column(Float)

    def __repr__(self):
        return "<Squid_Measurement(measurement_id='%s',device_name='%s')>" %(self.id, self.device_name)

class Resistor_Measurement(Base):
    'Resistor Measurement'
    __tablename__ = 'resistor_measurement'
    id = Column(Integer, primary_key = True)
    date = Column(String(50)) #date measurement was taken
    time = Column(String(50)) #time measurement was taken
    chip_id = Column(Integer, ForeignKey('chip.id'))
    chip_name = Column(String(50))
    design_id = Column(Integer, ForeignKey('design.id'))
    design_name = Column(String(50))
    device_name = Column(String(50))
    num_Rs = Column(Integer)

    data_directory = Column(String(500)) #directory with data

    #Default resistor_measurements
    R_4k_2000uA = Column(Float)
    R_4k_1000uA = Column(Float)
    R_4k_500uA = Column(Float)

    R_RT_2000uA = Column(Float)
    R_RT_1000uA = Column(Float)
    R_RT_500uA = Column(Float)

    Ravg_4k_2000uA = Column(Float)
    Ravg_4k_1000uA = Column(Float)
    Ravg_4k_500uA = Column(Float)

    sq_correction = Column(Float)
    Rsqs_4k_2000uA = Column(Float)
    Rsqs_4k_1000uA = Column(Float)
    Rsqs_4k_500uA = Column(Float)
    
    #Added as part of database migration for PCM3B testing
    R_RT_IV = Column(Float) #room temperature resistance from the slope of an IV curve

    def __repr__(self):
        return "<Resistor_Measurement(measurement_id='%s',device_name='%s')>" %(self.id, self.device_name)

class Via_Measurement(Base):
    'Via Measurement'
    __tablename__ = 'via_measurement'
    id = Column(Integer, primary_key = True)
    date = Column(String(50)) #date measurement was taken
    time = Column(String(50)) #time measurement was taken
    chip_id = Column(Integer, ForeignKey('chip.id'))
    chip_name = Column(String(50))
    design_id = Column(Integer, ForeignKey('design.id'))
    design_name = Column(String(50))
    device_name = Column(String(50))

    #JJ_radius_nom = Column(DECIMAL(13,3))
    data_directory = Column(String(500)) #directory with data

    #Default via_measurements
    R_4k = Column(Float)
    R_RT = Column(Float)
    Imax=Column(Float)

    def __repr__(self):
        return "<Via_Measurement(measurement_id='%s',device_name='%s')>" %(self.id, self.device_name)
    
class Crossbar_Measurement(Base):
    'Crossbar Measurement'
    __tablename__ = 'crossbar_measurement'
    id = Column(Integer, primary_key = True)
    date = Column(String(50)) #date measurement was taken
    time = Column(String(50)) #time measurement was taken
    chip_id = Column(Integer, ForeignKey('chip.id'))
    chip_name = Column(String(50))
    design_id = Column(Integer, ForeignKey('design.id'))
    design_name = Column(String(50))
    device_name = Column(String(50))
    data_directory = Column(String(500)) #directory with all the .dat files
    
    #Extra crossbar-specific measurements
    #Note: R_10K and R_RT could be either length resistances or cross resistances depending on the type of device
    R_10K = Column(Float) #Resistance just above the critical temperature (~10K)
    R_RT = Column(Float) #Resistance at room temperature
    Tc = Column(Float)
    
    def __repr__(self):
        return "<Crossbar_Measurement(measurement_id='%s',device_name='%s')>" %(self.id, self.device_name)
    

#Back relationships
Wafer.chips = relationship("Chip", order_by=Chip.id, back_populates="wafer")
Chip.wafer = relationship("Wafer", order_by=Chip.id, back_populates="chips")

Design.chips = relationship("Chip", order_by=Chip.id, back_populates="type")
Chip.type = relationship("Design", order_by=Chip.id, back_populates="chips")

JJ_Measurement.chips = relationship("Chip", order_by=JJ_Measurement.id, back_populates="jj_measurements")
Chip.jj_measurements = relationship("JJ_Measurement", order_by=JJ_Measurement.id, back_populates="chips")

JJ_Measurement.designs = relationship("Design", order_by=JJ_Measurement.id, back_populates="jj_measurements")
Design.jj_measurements = relationship("JJ_Measurement", order_by=JJ_Measurement.id, back_populates="designs")

Squid_Measurement.chips = relationship("Chip", order_by=Squid_Measurement.id, back_populates="squid_measurements")
Chip.squid_measurements = relationship("Squid_Measurement", order_by=Squid_Measurement.id, back_populates="chips")

Resistor_Measurement.chips = relationship("Chip", order_by=Resistor_Measurement.id, back_populates="resistor_measurements")
Chip.resistor_measurements = relationship("Resistor_Measurement", order_by=Resistor_Measurement.id, back_populates="chips")

Via_Measurement.chips = relationship("Chip", order_by=Via_Measurement.id, back_populates="via_measurements")
Chip.via_measurements = relationship("Via_Measurement", order_by=Via_Measurement.id, back_populates="chips")

Crossbar_Measurement.chips = relationship("Chip", order_by=Crossbar_Measurement.id, back_populates="crossbar_measurements")
Chip.crossbar_measurements = relationship("Crossbar_Measurement", order_by=Crossbar_Measurement.id, back_populates="chips")

#---------------------
##END BASE CLASSES

#Lets create our Table which is part of MetaData and pass it our 'engine' to connect to the database
Base.metadata.create_all(engine)
#Lets start chatting with the database via a session
Session = sa.orm.sessionmaker(bind=engine)
session = Session()


def show_all_wafers():
    session.commit() #need this to force the database to update
    try:
        w = session.query(Wafer).all()
        print("\nAll Wafers")
        return w

    except sa.orm.exc.NoResultFound:
        print("\n!ERROR! No wafers found.")

def show_all_chips():
    session.commit() #need this to force the database to update
    try:
        c = session.query(Chip).all()
        print("\nAll Chips")
        return c

    except sa.orm.exc.NoResultFound:
        print("\n!ERROR! No chips found.")

def find_chip(chip):
    session.commit() #need this to force the database to update
    'finds the chip by id or name'
    if isinstance(chip,Chip):
        return chip
    elif type(chip) == str:
        try:
            c = (session.query(Chip).filter_by(name=chip).one())
            print("\n Found chip %s" %chip)
            return c
        except sa.orm.exc.NoResultFound:
            print("\n!ERROR! Did not find chip with name: %s" %chip)

    elif type(chip) == int:
        try:
            c = (session.query(Chip).filter_by(id=chip).one())
            print("\n Found chip %s" %chip)
            return c
        except sa.orm.exc.NoResultFound:
            print("\n!ERROR! Did not find chip with id: %s" %chip)
    else:
        print("Must pass in chip as int, string or chip object")
        

def find_device(device,optional_designid=0,output=1):
    session.commit() #need this to force the database to update
    'finds the device by id or name'
    if isinstance(device,Device):
        return device
    elif type(device) == str:
        try:
            d = (session.query(Device).filter_by(name=device).one())
            if output:
                print("\n Found device %s" %device)
            return d
        except sa.orm.exc.NoResultFound:
            print("\n!ERROR! Did not find device with name: %s" %device)

        except sa.orm.exc.MultipleResultsFound:
            if(optional_designid):
                d = (session.query(Device).filter_by(name=device).all())
                for dev in d:
                    if dev.design_id[0].id == optional_designid:
                        return dev
                return -1
            else:
                return -1

    elif type(device) == int:
        try:
            d = (session.query(Chip).filter_by(id=device).one())
            print("\n Found device %s" %device)
            return d
        except sa.orm.exc.NoResultFound:
            print("\n!ERROR! Did not find device with id: %s" %device)
    else:
        print("Must pass in device as a Device object, a string or an int")
        
def find_wafer(wafer):
    session.commit() #need this to force the database to update
    'finds the wafer by id or name'
    if isinstance(wafer,Wafer):
        return wafer
    elif type(wafer) == str:
        try: 
            c = (session.query(Wafer).filter_by(name=wafer).one())
            print("\n Found wafer %s" %wafer)
            return c
        except sa.orm.exc.NoResultFound:
            print("\n!ERROR! Did not find wafer with name: %s" %wafer)
            
    elif type(wafer) == int:
        try: 
            c = (session.query(Wafer).filter_by(id=wafer).one())
            print("\n Found wafer %s" %wafer)
            return c
        except sa.orm.exc.NoResultFound:
            print("\n!ERROR! Did not find wafer with id: %s" %wafer)
    else: 
        print("Must pass in as a Wafer object, a string or an int")
    session.close()
    
def find_design(design):
    session.commit()
    if type(design) == str:
        try:
            d = session.query(Design).filter_by(name=design).one()
            print("\n Found Design %s" %design)
            return d
        except sa.orm.exc.NoResultFound:
            print("\n!ERROR! Did not find design: %s" %design)
            
    elif type(design) == int:
        try: 
            d = (session.query(Design).filter_by(id=design).one())
            print("\n Found design %s" %design)
            return d
        except sa.orm.exc.NoResultFound:
            print("\n!ERROR! Did not find design: %s" %design)
    else: 
        print("Must pass in wafer name as string or id as int")
    session.close()

def show_all_designs():
    session.commit() #need this to force the database to update
    try:
        d = session.query(Design).all()
        print("\nAll Designs")
        return d

    except sa.orm.exc.NoResultFound:
        print("\n!ERROR! No designs found.")

def show_all_devices():
    session.commit() #need this to force the database to update
    try:
        d = session.query(Device).all()
        print("\nAll Devices")
        return d

    except sa.orm.exc.NoResultFound:
        print("\n!ERROR! No devices found.")

def show_chips_from_wafer(wafer):
    session.commit() #need this to force the database to update
    if type(wafer) == str:
        try:
            c = (session.query(Wafer).filter_by(name=wafer).one()).chips
            print("\nChips associated with wafer %s" %wafer)
            return c
        except sa.orm.exc.NoResultFound:
            print("\n!ERROR! Did not find wafer: %s" %wafer)

    elif type(wafer) == int:
        try:
            w = (session.query(Wafer).filter_by(id=wafer).one())
            c = w.chips
            print("\nChips associated with wafer %s" %w.name)
            return c
        except sa.orm.exc.NoResultFound:
            print("\n!ERROR! Did not find wafer: %s" %wafer)
    else:
        print("Must pass in wafer name as string or id as int")

def show_devices_from_chip(chip):
    session.commit() #need this to force the database to update
    if type(chip) == str:
        try:
            c = (session.query(Chip).filter_by(name=chip).one())
            design = session.query(Design).get(c.design_id)
            #devices = design.device_id
            devices = session.query(Device).filter(Device.design_id.any(id=design.id)).order_by(Device.id).all()
            print("\nChip %s:%s uses design %s:%s and has the following device associations " %(c.id, c.name, design.id, design.name))
            return devices
        except sa.orm.exc.NoResultFound:
            print("\n!ERROR! Did not find wafer: %s" %chip)
        except sa.orm.exc.MultipleResultsFound:
            c = session.query(Design).get(c.design_id)(session.query(Chip).filter_by(name=chip).all())
            print("\n!ERROR! Multiple chips with same name. Please use the 'id' from the list below")
            return c
    elif type(chip) == int:
        try:
            c = (session.query(Chip).filter_by(id=chip).one())
            design = session.query(Design).get(c.design_id)
            devices = design.device_id
            print("\nChip %s:%s uses design %s:%s and has the following device associations " %(c.id, c.name, design.id, design.name))
            return devices
        except sa.orm.exc.NoResultFound:
            print("\n!ERROR! Did not find chip: %s" %chip)
    else: 
        try:
            chipname=chip.name
            design = session.query(Design).get(chip.design_id)
            #devices = design.device_id
            devices = session.query(Device).filter(Device.design_id.any(id=design.id)).order_by(Device.id).all()
            print("\nChip %s:%s uses design %s:%s and has the following device associations " %(chip.id, chip.name, design.id, design.name))
            return devices
        except sa.orm.exc.NoResultFound:
            print("\n!ERROR! Did not find chip: %s" %chip)
        except sa.orm.exc.MultipleResultsFound:
            c = session.query(Design).get(chip.design_id)(session.query(Chip).filter_by(name=chipname).all())
            print("\n!ERROR! Multiple chips with same name. Please use the 'id' from the list below")
            return c    
        except:
            print("Must pass in chip as string, int or chip object")
def show_measurements_from_chip(chip):
    session.commit()

    if type(chip) == str:
        try:
            m = session.query(JJ_Measurement).filter_by(chip_name=chip).all()
            return m
        except sa.orm.exc.NoResultFound:
            return []

# returns the actual measurement, to be handled in the return
def get_measurements_from_device(chip, device):
    session.commit()
    try:
         m = session.query(JJ_Measurement).filter_by(chip_name=chip.name, device_name=device.name).one()
         return [m]
    except sa.orm.exc.MultipleResultsFound:
         mults = session.query(JJ_Measurement).filter_by(chip_name=chip.name, device_name=device.name).all()
        
         return mults
    except sa.orm.exc.NoResultFound:
        return -1
    
def get_measurement_from_device_recent(Chip, Device):
    session.commit()
    if type(Chip)==str and type(Device)==str:    
        meas=session.query(JJ_Measurement).filter_by(chip_name=Chip,device_name=Device).all()[-1]
    else:
        meas=session.query(JJ_Measurement).filter_by(chip_name=Chip.name,device_name=Device.name).all()[-1]
    session.close()
    return meas
    
def show_via_measurements_from_device(chip,device):
    session.commit()
    if type(chip) == str:
        c = (session.query(Chip).filter_by(name=chip).one())
    elif type(chip) == int:
        c = (session.query(Chip).filter_by(id=chip).one())
    else:
        raise Exception("Invalid Input")
    
    if type(device) == str:
        dev = (session.query(Device).filter_by(name=device).one())
    elif type(device) == int:
        dev = (session.query(Device).filter_by(id=device).one())
    else:
        raise Exception("Invalid Input")
    try:
        meas=session.query(Via_Measurement).filter_by(chip_name=c.name,device_name=dev.name).one()
    except sa.orm.exc.MultipleResultsFound:
         mults= session.query(Via_Measurement).filter_by(chip_name=c.name,device_name=dev.name).all()
         maxtime=0
         meas=0
         for m in mults:
             if time.mktime(time.strptime(m.date+"/"+m.time,"%Y/%m/%d/%H:%M:%S"))>maxtime:
                 meas=m  
         return meas
    except sa.orm.exc.NoResultFound:
        return -1
    session.close()
    return meas

def show_crossbar_measurements_from_device(Chip,Device):
    session.commit()
    if type(Chip)==str and type(Device)==str:    
        meas=session.query(Crossbar_Measurement).filter_by(chip_name=Chip,device_name=Device).all()[-1]
    else:
        meas=session.query(Crossbar_Measurement).filter_by(chip_name=Chip.name,device_name=Device.name).all()[-1]
    session.close()
    return meas

# inted for use with plotting all
def show_measurements_from_device(chip, device):
    session.commit()

    try:
        m = session.query(JJ_Measurement).filter_by(chip_name=chip.name, device_name=device.name).one()
        if m.Rn is None:
            return [m.Ic_pos, 0]
        return [m.Ic_pos, m.Rn]
    except sa.orm.exc.MultipleResultsFound:
        m = session.query(JJ_Measurement).filter_by(chip_name=chip.name, device_name=device.name).all()
        print("\nError! Too many results found. But I will find an average for you;)")
        avg_ic = 0
        ic_ct=0
        avg_rn = 0
        rn_ct=0
        for i in range(0,len(m)):
            if type(m[i].Ic_pos)==None:
                print("No value found, nothing will be added")
            else:
                avg_ic = avg_ic + m[i].Ic_pos
                ic_ct+=1
            if type(m[i].Rn)==None:
                print("No value found, nothing will be added")
            else:
                avg_rn = avg_rn + m[i].Rn
                rn_ct+=1
        try:
            avg_ic = avg_ic/ic_ct
            avg_rn = avg_rn/rn_ct
        except ZeroDivisionError:
            print("Not enough results found, adding a 0")
            return [0,0]
        
        return [avg_ic, avg_rn]
    except sa.orm.exc.NoResultFound:
        print("\nError! No measurement found. I will add a 0")
        return [0, 0]
    
def show_squid_measurements_from_device(chip, device):
    session.commit()
    try:
        m = session.query(Squid_Measurement).filter_by(chip_name=chip.name, device_name=device.name).one()
        return m
    except sa.orm.exc.MultipleResultsFound:
        m = session.query(JJ_Measurement).filter_by(chip_name=chip.name, device_name=device.name).all()
        return m
    except sa.orm.exc.NoResultFound:
        print("No results found!")
        return None
    
def show_squid_measurement_from_device_recent(Chip, Device):
    session.commit()
    if type(Chip)==str and type(Device)==str:    
        meas=session.query(Squid_Measurement).filter_by(chip_name=Chip,device_name=Device).all()[-1]
    else:
        meas=session.query(Squid_Measurement).filter_by(chip_name=Chip.name,device_name=Device.name).all()[-1]
    session.close()
    return meas

def show_JJ_measurements_from_wafer(wafer, design='all'):
    session.commit() #need this to force the database to update
    jj_measurements = []
    chips_for_design = []
    w = find_wafer(wafer)
    print(w)
    chips = show_chips_from_wafer(w.id)

    if design == 'all': #returns all the measurement associated with the wafer
        for i, chip in enumerate(chips):
            c = find_chip(chips[i].id) #get the chip from database
            jj_measurements.append(session.query(JJ_Measurement).filter_by(chip_name=c.name).all())
            chips_for_design.append(c)

    else: #Searching for chips from wafer for a particular design name
        for i, chip in enumerate(chips):
            c = find_chip(chips[i].id) #get the chip from database
            design_name = session.query(Design).join(Chip).filter(Chip.id==c.id).one() #grabs the design name for the chip
            if design_name.name.find(design) != -1: #Append only chips with the proper design name
                jj_measurements.append(session.query(JJ_Measurement).filter_by(chip_name=c.name).all())
                chips_for_design.append(c)

    session.close()
    return jj_measurements, chips_for_design


def get_data_directory(chip,typeofdata=JJ_Measurement):
    session.commit()
    if(type(chip)==Chip):
        #doesn't work
        chip_name = chip.name
    else:
        chip_name = chip
    if type(typeofdata)==str:
        if typeofdata[0] in ["C","c"]:
            typeofdata=Crossbar_Measurement
        elif typeofdata[0] in ["S","s"]:
            typeofdata=Squid_Measurement
        elif typeofdata[0] in ["R","r"]:
            typeofdata=Resistor_Measurement
        elif typeofdata[0] in ["V","v"]:
            typeofdata=Via_Measurement
        else:
            typeofdata=JJ_Measurement
    try:
        m = session.query(typeofdata).filter_by(chip_name=chip_name).one()
        return [m.data_directory]
    except sa.orm.exc.MultipleResultsFound:
        ms = session.query(typeofdata).filter_by(chip_name=chip_name).all()
        ms_toreturn = []
        for m in ms:
            if not m.data_directory in ms_toreturn:
                ms_toreturn.append(m.data_directory)
        return ms_toreturn
    except sa.orm.exc.NoResultFound:
        return -1
def create_chip():
    chip_name = str(input("Chip name?  ")).upper()
    wafer_name = str(input('Wafer name?  ')).upper()
    design_name = str(input('Design name?  ')).upper()

    print('\nCreating... \nChip "%s" \nWafer "%s" \nDesign "%s"' %(chip_name, wafer_name, design_name))

def device_def(chip_id):
    'pass in chip name returns the device definition as list of tuples'

    try:
        c = session.query(Chip).filter(Chip.id==chip_id).one()
        d = session.query(Design).get(c.design_id).device_id
        print("\nFound chip: %s" %c.name)
        return d

    except sa.orm.exc.NoResultFound:
        print("\n!ERROR! Did not find chip_id:%s" %chip_id)

def calc_Jc(Ic, JJ_radius):
    'returns value of critical current density Jc based on Ic and JJ radius'

    A = np.pi*(JJ_radius)**2

    return Ic/A

def predict_Ic(Jc, JJ_radius):
    'returns value of predicted Ic'
    A = np.pi*(JJ_radius)**2

    return Jc*A

def sweep_def(Jc, JJ_radius):
    'creates sweep range for one device'
    Ic = predict_Ic(Jc, JJ_radius)

    print("Predicted Ic:%e"%Ic)
    I_min = -Ic*Ic_range_scale
    I_max = -I_min
    return I_min, I_max

def sweep_def_SQUID_smaller_range(Jc, JJ_radius):
    'creates sweep range for one device'
    Ic =  predict_Ic(Jc, JJ_radius)
    Ic *=2
    #***changed for SQUID measurements***
    # mult. by 20 for first 7, then by 3 for rest of devices
    print("Predicted Ic:%e"%Ic)
    I_min = -Ic*Ic_range_scale
    I_max = -I_min
    return I_min, I_max

def sweep_def_SQUID_bigger_range(Jc, JJ_radius):
    'creates sweep range for one device'
    Ic = predict_Ic(Jc, JJ_radius)

    #***changed for SQUID measurements***
    # mult. by 20 for first 7, then by 3 for rest of devices
    Ic *= 15

    print("Predicted Ic:%e"%Ic)
    I_min = -Ic*Ic_range_scale
    I_max = -I_min
    return I_min, I_max

def calc_JJ_measurements(Ic_list, Rn, Imax, JJ_radius):
    '''
    This will calculate the JJ measurements based on the values of Ic, Iret, Rn, and Imax
    Returns a list with all the values Ic_pos, Ic_neg, Iret_pos, Iret_neg, Imax, Rn, Iret_Ic_ratio, Ic_Rn_product, Rn_Area_product, Inverse_sqrtRn, sqrtIc, Jc_nom
    '''
    Ic_pos=float(Ic_list[1]); Ic_neg=float(Ic_list[3]); Iret_pos=float(Ic_list[2]); Iret_neg=float(Ic_list[0])
    Iret = Iret_pos
    Ic = Ic_pos
    A = np.pi*JJ_radius**2 #area of JJ
    Iret_Ic_ratio = Iret/Ic; Ic_Rn_product = Ic*Rn; Rn_Area_product = Rn*A; Inverse_sqrtRn = abs(Rn)**(-1/2); sqrtIc = abs(Ic)**(1/2); Jc_nom = Ic/A
    data = [Ic_pos, Ic_neg, Iret_pos, Iret_neg, Imax, Rn, Iret_Ic_ratio, Ic_Rn_product, Rn_Area_product, Inverse_sqrtRn, sqrtIc, Jc_nom]
    return data
#TODO list: add design to device, calculate the values to input to database with function above, move chip.id and design.id to 2 & 3 column

def save_JJ_Measurements(chip, Ic_list, Rn, Imax, data_directory, device):
    '''
    Saves 4 Ic values from Ic_list to the measurements of the particular chip
    Extracts the device details from the passed in device object and assigns
    the measurement to the chip from the passed in chip id or name
    '''
    session.commit() #need this to force the database to update
    date = time.strftime("%Y/%m/%d") #get the date
    current_time = time.strftime("%H:%M:%S") #get the time
    c = find_chip(chip) #get the chip from database
    JJ_radius = device.JJ_radius_nom #Need to for the calculations below

    data = calc_JJ_measurements(Ic_list, Rn, Imax, JJ_radius) #calculates relevant values to save to the database
    design_name = session.query(Design).get(c.design_id).name
    print(design_name)
    #Writes all the data into the database returned from the line above
    c.jj_measurements.append(JJ_Measurement(date=date, time=current_time, chip_name = c.name, design_id = c.design_id, design_name = design_name, device_name=device.name, num_JJs = device.num_JJs,\
                                            JJ_radius_nom = device.JJ_radius_nom, data_directory = data_directory,\
                                            Ic_pos=float(data[0]), Ic_neg=float(data[1]),Iret_pos=float(data[2]),\
                                            Iret_neg=float(data[3]), Imax=float(data[4]), Rn=float(data[5]), Iret_Ic_ratio=float(data[6]), Ic_Rn_product=float(data[7]), Rn_Area_product=float(data[8]), Inverse_sqrtRn=float(data[9]), sqrtIc=float(data[10]),\
                                            Jc_nom=float(data[11])))
    session.commit()
    print("Data successfully saved to database")
    
def save_Fix_Ic(chip, device, Iclist): #Iclist = [Icneg, Icpos, Iretpos, Iretneg]
    session.commit()
    date = time.strftime("%Y/%m/%d")
    current_time = time.strftime("%H:%M:%S")
    c = find_chip(chip)
    device = find_device(device)
    
    Ic_pos = float(Iclist[0]) #The critical current positive side of IV curve
    Ic_neg = float(Iclist[1]) #The critical current negative side of IV curve
    Iret_pos = float(Iclist[2]) #The return critical current postive side of IV curve which depending on the damping below should show some slight hysteresis (i.e. slight difference between Ic and Iret)
    Iret_neg = float(Iclist[3])
    measurement = get_measurement_from_device_recent(c,device)
    
    measurement.date = date
    measurement.time = current_time
    measurement.Ic_pos = Ic_pos
    measurement.Ic_neg = Ic_neg
    measurement.Iret_pos = Iret_pos
    measurement.Iret_neg = Iret_neg
    
    session.commit()
    print("Data successfully saved to database")

def save_Squid_Measurements(chip, Ic_list, data_directory, device):
    '''
    Saves 4 Ic values from Ic_list to the measurements of the particular chip
    Extracts the device details from the passed in device object and assigns
    the measurement to the chip from the passed in chip id or name
    '''
    session.commit() #need this to force the database to update
    date = time.strftime("%Y/%m/%d") #get the date
    current_time = time.strftime("%H:%M:%S") #get the time
    c = find_chip(chip) #get the chip from database
    JJ_radius = device.JJ_radius_nom #Need to for the calculations below

    design_name = session.query(Design).get(c.design_id).name
    print(design_name)

    Ic_pos=float(Ic_list[1]); Ic_neg=float(Ic_list[3]); Iret_pos=float(Ic_list[2]); Iret_neg=float(Ic_list[0])

    #Writes all the data into the database returned from the line above
    c.squid_measurements.append(Squid_Measurement(date=date, time=current_time, chip_name = c.name, design_id = c.design_id, design_name = design_name, device_name=device.name, num_JJs = device.num_JJs,\
                                            data_directory = data_directory,\
                                            Ic_pos = Ic_pos, Ic_neg = Ic_neg,\
                                            Iret_neg = Iret_neg, Iret_pos = Iret_pos))

    session.commit()
    print("Data successfully saved to database")

def save_Resistance_Measurements_warm(chip, Resistance_list, data_directory, device):
    '''
    Saves 4 Ic values from Ic_list to the measurements of the particular chip
    Extracts the device details from the passed in device object and assigns
    the measurement to the chip from the passed in chip id or name
    '''
    session.commit() #need this to force the database to update
    date = time.strftime("%Y/%m/%d") #get the date
    current_time = time.strftime("%H:%M:%S") #get the time
    c = find_chip(chip) #get the chip from database

    design_name = session.query(Design).get(c.design_id).name
    print(design_name)

    R_RT_500uA = float(Resistance_list[0]); R_RT_1000uA = float(Resistance_list[1]); R_RT_2000uA = float(Resistance_list[2])

    #Writes all the data into the database returned from the line above
    c.resistor_measurements.append(Resistor_Measurement(date=date, time=current_time, chip_name = c.name, design_id = c.design_id, design_name = design_name, device_name=device.name,\
                                            data_directory = data_directory,\
                                            R_RT_2000uA = R_RT_2000uA, R_RT_1000uA = R_RT_1000uA,\
                                            R_RT_500uA = R_RT_500uA))

    session.commit()

    print("Data successfully saved to database")

def save_Resistance_Measurements_cold(chip, Resistance_list, data_directory, device):
    '''
    Saves 4 Ic values from Ic_list to the measurements of the particular chip
    Extracts the device details from the passed in device object and assigns
    the measurement to the chip from the passed in chip id or name
    '''
    session.commit() #need this to force the database to update
    date = time.strftime("%Y/%m/%d") #get the date

    c = find_chip(chip) #get the chip from database

    design_name = session.query(Design).get(c.design_id).name
    print(design_name)

    measurement = session.query(Resistor_Measurement).filter_by(chip_name=c.name, device_name=device.name).one()

    # get relevant info
    chip = measurement.chip_name
    device = measurement.device_name
    date = measurement.date

    R_4k_500uA = float(Resistance_list[0]); R_4k_1000uA = float(Resistance_list[1]); R_4k_2000uA = float(Resistance_list[2])

    measurement.R_4k_500uA = R_4k_500uA
    measurement.R_4k_1000uA = R_4k_1000uA
    measurement.R_4k_2000uA = R_4k_2000uA

    session.commit()

    print("Data successfully saved to database")

def save_Via_Measurements_warm(chip, resistance, data_directory, device):
    '''
    Saves 4 Ic values from Ic_list to the measurements of the particular chip
    Extracts the device details from the passed in device object and assigns
    the measurement to the chip from the passed in chip id or name
    '''
    session.commit() #need this to force the database to update
    date = time.strftime("%Y/%m/%d") #get the date
    current_time = time.strftime("%H:%M:%S") #get the time
    c = find_chip(chip) #get the chip from database
    design_name = session.query(Design).get(c.design_id).name
    R_RT = float(resistance)

    #Writes all the data into the database returned from the line above
    c.via_measurements.append(Via_Measurement(date=date, time=current_time, chip_name = c.name, design_id = c.design_id, design_name = design_name, device_name=device.name,\
                                            data_directory = data_directory,\
                                            R_RT = R_RT))

    session.commit()

    print("Data successfully saved to database")

def save_Via_Measurements_cold(chip, resistance, data_directory, device):
    '''
    Saves 4 Ic values from Ic_list to the measurements of the particular chip
    Extracts the device details from the passed in device object and assigns
    the measurement to the chip from the passed in chip id or name
    '''
    session.commit() #need this to force the database to update
    date = time.strftime("%Y/%m/%d") #get the date
    c = find_chip(chip) #get the chip from database
    design_name = session.query(Design).get(c.design_id).name

    measurement = session.query(Via_Measurement).filter_by(chip_name=c.name, device_name=device.name).one()

    # get relevant info
    chip = measurement.chip_name
    device = measurement.device_name
    date = measurement.date

    R_4k = float(resistance)
    measurement.R_4k = R_4k

    session.commit()
    print("Data successfully saved to database")
    
###########################################
#Save to db functions for PCM3B testing
###########################################
def save_Resistance_Measurements_PCM3B_warm(chip, resistance, data_directory, device):
    
    session.commit()
    date = time.strftime("%Y/%m/%d")
    current_time = time.strftime("%H:%M:%S")
    c = find_chip(chip)
    R_RT_IV = float(resistance[0])
    measurement = session.query(Resistor_Measurement).filter_by(chip_name=c.name, device_name=device.name).one_or_none()

    if measurement is None:
        
        design_name = session.query(Design).get(c.design_id).name
        c.resistor_measurements.append(Resistor_Measurement(date=date, time=current_time, chip_name = c.name, \
                                                        design_id = c.design_id, design_name = design_name, \
                                                        device_name=device.name, \
                                                        data_directory=data_directory, R_RT_IV=R_RT_IV))
    else:
        measurement.R_RT_IV = R_RT_IV
        measurement.date = date
        measurement.time = current_time
        measurement.data_directory = data_directory

    session.commit()
    print("Data successfully saved to database")
    
def save_Resistance_Measurements_PCM3B_cold(chip, resistance, data_directory, device):
    
    session.commit() #Forces the database to update
    date = time.strftime("%Y/%m/%d")
    current_time = time.strftime("%H:%M:%S")
    c = find_chip(chip)
    R_4k_500uA = float(resistance[0]); R_4k_1000uA = float(resistance[1]); R_4k_2000uA = float(resistance[2])
    measurement = session.query(Resistor_Measurement).filter_by(chip_name=c.name, device_name=device.name).one_or_none()

    if measurement is None:
        design_name = session.query(Design).get(c.design_id).name
        c.resistor_measurements.append(Resistor_Measurement(date=date, time=current_time, chip_name = c.name, \
                                                        design_id = c.design_id, design_name = design_name, \
                                                        device_name=device.name, \
                                                        data_directory=data_directory, R_4k_500uA=R_4k_500uA, \
                                                        R_4k_1000uA=R_4k_1000uA, R_4k_2000uA=R_4k_2000uA))
    else:
        measurement.date = date
        measurement.time = current_time
        measurement.data_directory = data_directory
        measurement.R_4k_500uA = R_4k_500uA
        measurement.R_4k_1000uA = R_4k_1000uA
        measurement.R_4k_2000uA = R_4k_2000uA
    
    session.commit()
    print("Data successfully saved to database")

def save_Resistance_Measurements_PCMRS(chip, resistance, data_directory, device):
    session.commit()
    date = time.strftime("%Y/%m/%d")
    current_time = time.strftime("%H:%M:%S")
    c = find_chip(chip)
    measurement = session.query(Resistor_Measurement).filter_by(chip_name=c.name, device_name=device.name).one_or_none()

    if measurement is None:
        design_name = session.query(Design).get(c.design_id).name
        c.resistor_measurements.append(Resistor_Measurement(date=date, time=current_time, chip_name = c.name, \
                                                        design_id = c.design_id, design_name = design_name, \
                                                        device_name=device.name, \
                                                        data_directory=data_directory, \
                                                        R_4k_1000uA=resistance))
    else:
        measurement.date = date
        measurement.time = current_time
        measurement.data_directory = data_directory    
        measurement.R_4k_1000uA = resistance
    
    session.commit()
    print("Data successfully saved to database")

def save_Via_Measurements_PCM3B_cold(chip, resistance, Imaxs, data_directory, device):
    
    session.commit()
    date = time.strftime("%Y/%m/%d")
    current_time = time.strftime("%H:%M:%S")
    c = find_chip(chip)
    R_4k = float(resistance[0])
    Imax=float(Imaxs[0])
    measurement = session.query(Via_Measurement).filter_by(chip_name=c.name, device_name=device.name).one_or_none()
    
    if measurement is None:
        design_name = session.query(Design).get(c.design_id).name
        c.via_measurements.append(Via_Measurement(date=date, time=current_time, chip_name = c.name, \
                                              design_id=c.design_id, design_name=design_name, \
                                              device_name=device.name, data_directory=data_directory, \
                                              R_4k=R_4k, Imax=Imax))
    else:
        measurement.date = date
        measurement.time = current_time
        measurement.data_directory = data_directory    
        measurement.R_4k = R_4k
        measurement.Imax = Imax
    
    session.commit()
    print("Data successfully saved to database")


def save_Crossbar_Measurements_PCM3B_warm(chip, resistance, data_directory, device):

    session.commit()
    date = time.strftime("%Y/%m/%d")
    current_time = time.strftime("%H:%M:%S")
    c = find_chip(chip)
    R_RT = float(resistance[0]) #Note:This could be either RL or Rcross depending on the device type
    measurement = session.query(Crossbar_Measurement).filter_by(chip_name=c.name, device_name=device.name).one_or_none()

    if measurement is None:
        design_name = session.query(Design).get(c.design_id).name
        c.crossbar_measurements.append(Crossbar_Measurement(date=date, time=current_time, chip_name = c.name, \
                                                        design_id=c.design_id, design_name = design_name, \
                                                        device_name=device.name, data_directory=data_directory,
                                                        R_RT=R_RT))
    else:
        measurement.date = date
        measurement.time = current_time
        measurement.data_directory = data_directory  
        measurement.R_RT = R_RT

    session.commit()
    print("Data successfully saved to database")
    
def save_Crossbar_Measurements_PCM3B_cold(chip, resistance, data_directory, device):
    
    session.commit()
    date = time.strftime("%Y/%m/%d")
    current_time = time.strftime("%H:%M:%S")
    c = find_chip(chip)
    R_10K = float(resistance[0])
    measurement = session.query(Crossbar_Measurement).filter_by(chip_name=c.name, device_name=device.name).one_or_none()
    
    if measurement is None:
        design_name = session.query(Design).get(c.design_id).name
        c.crossbar_measurements.append(Crossbar_Measurement(date=date, time=current_time, chip_name = c.name, \
                                                        design_id=c.design_id, design_name = design_name, \
                                                        device_name=device.name, data_directory=data_directory,
                                                        R_10K=R_10K))
    else:
        measurement.date = date
        measurement.time = current_time
        measurement.data_directory = data_directory  
        measurement.R_10K = R_10K
    
    session.commit()
    print("Data successfully saved to database")
    
def save_Crossbar_Tc(chip, TcIn, data_directory, device):
    
    session.commit()
    date = time.strftime("%Y/%m/%d")
    current_time = time.strftime("%H:%M:%S")
    c = find_chip(chip)
    Tc = float(TcIn)
    measurement = session.query(Crossbar_Measurement).filter_by(chip_name=c.name, device_name=device.name).one_or_none()
    
    if measurement is None:
        design_name = session.query(Design).get(c.design_id).name
        c.crossbar_measurements.append(Crossbar_Measurement(date=date, time=current_time, chip_name = c.name, \
                                                        design_id=c.design_id, design_name = design_name, \
                                                        device_name=device.name, data_directory=data_directory,
                                                        Tc=Tc))
    else:
        measurement.date = date
        measurement.time = current_time
        measurement.data_directory = data_directory 
        measurement.Tc = Tc
    
    session.commit()
    print("Data successfully saved to database")
    
##########################################    
#Save to db functions for SQUID testing
##########################################
def save_SQUID_no_flux(chip, Iclist, data_directory, device):
        
    session.commit()
    date = time.strftime("%Y/%m/%d")
    current_time = time.strftime("%H:%M:%S")
    c = find_chip(chip)
    Ic_neg = float(Iclist[0])
    Ic_pos = float(Iclist[1])
    Iret_pos = float(Iclist[2])
    Iret_neg = float(Iclist[3])
    #Get the most recent measurement
    measurements = session.query(Squid_Measurement).filter_by(chip_name=c.name, device_name=device.name).order_by(Squid_Measurement.id).all()
    if len(measurements) == 0:
        measurement = None
    else:
        measurement = measurements[-1]
    
    #If no measurement is found OR most recent measurements already has Ic data, create a new measurement
    if measurement is None or not(measurement.Ic_neg == None and measurement.Ic_pos == None and measurement.Ic_pos == None and measurement.Iret_neg == None):
        new = True
        design_name = session.query(Design).get(c.design_id).name
        c.squid_measurements.append(Squid_Measurement(date=date, time =current_time, chip_name=c.name, \
                                                      design_id=c.design_id, design_name=design_name, \
                                                      device_name=device.name, data_directory=data_directory,
                                                      Ic_neg=Ic_neg, Ic_pos=Ic_pos, Iret_pos=Iret_pos, Iret_neg=Iret_neg))
    else: #otherwise update most recent measurement
        new = False
        measurement.date = date
        measurement.time = current_time
        #measurement.data_directory = data_directory 
        measurement.Ic_neg = Ic_neg
        measurement.Ic_pos = Ic_pos
        measurement.Iret_pos = Iret_pos
        measurement.Iret_neg = Iret_neg
    
    session.commit()
    print("Data successfully saved to database")
    return new, measurement
    
def save_SQUID_periodicity(chip, period, Iflux_min_Ic, data_directory, device):
    session.commit()
    date = time.strftime("%Y/%m/%d")
    current_time = time.strftime("%H:%M:%S")
    c = find_chip(chip)
    period=float(period)
    #Get the most recent measurement
    measurements = session.query(Squid_Measurement).filter_by(chip_name=c.name, device_name=device.name).order_by(Squid_Measurement.id).all()
    if len(measurements) == 0:
        measurement = None
    else:
        measurement = measurements[-1]
    
    #If no measurement is found OR most recent measurements already has period data, create a new measurement
    if measurement is None or measurement.Iflux_period != None:
        new_meas = True
        design_name = session.query(Design).get(c.design_id).name
        c.squid_measurements.append(Squid_Measurement(date=date, time =current_time, chip_name=c.name, \
                                                      design_id=c.design_id, design_name=design_name, \
                                                      device_name=device.name, data_directory=data_directory,
                                                      Iflux_period=period, Iflux_min_Ic=float(Iflux_min_Ic)))
    else: #otherwise update most recent measurement
        new_meas = False
        measurement.date = date
        measurement.time = current_time
        #measurement.data_directory = data_directory 
        measurement.Iflux_period = period
        measurement.Iflux_min_Ic = float(Iflux_min_Ic)
    
    session.commit()
    print("Data successfully saved to database")
    return new_meas, measurement
    
def save_SQUID_with_flux(chipname, I_LC_step, data_directory, device):
    session.commit()
    date = time.strftime("%Y/%m/%d")
    current_time = time.strftime("%H:%M:%S")
    c = find_chip(chipname)
    I_LC_step=float(I_LC_step)
    #Get the most recent measurement
    measurements = session.query(Squid_Measurement).filter_by(chip_name=c.name, device_name=device.name).order_by(Squid_Measurement.id).all()
    if len(measurements) == 0:
        measurement = None
    else:
        measurement = measurements[-1]
    
    #If no measurement is found OR most recent measurements already has LC_step data, create a new measurement
    if measurement is None or measurement.I_LC_step != None:
        new = True
        design_name = session.query(Design).get(c.design_id).name
        c.squid_measurements.append(Squid_Measurement(date=date, time =current_time, chip_name=c.name, \
                                                      design_id=c.design_id, design_name=design_name, \
                                                      device_name=device.name, data_directory=data_directory,
                                                      I_LC_step=I_LC_step))
    else: #otherwise update most recent measurement
        new = False
        measurement.date = date
        measurement.time = current_time
        #measurement.data_directory = data_directory 
        measurement.I_LC_step = I_LC_step
    
    session.commit()
    print("Data successfully saved to database")
    return new, measurement

def save_SQUID_LC(chip, Vresstep, device):
    session.commit()
    Vresstep = float(Vresstep)
    
    measurements = session.query(Squid_Measurement).filter_by(chip_name=chip, device_name=device.name).order_by(Squid_Measurement.id).all()
    measurement = measurements[-1]
        
    measurement.I_LC_step = Vresstep
    
    session.commit()
    print("Data successfully saved to database")
    
def save_SQUID_Rn(chip, Rn, device):
    
    session.commit()
    Rn = float(Rn)
    
    measurements = session.query(Squid_Measurement).filter_by(chip_name=chip, device_name=device.name).order_by(Squid_Measurement.id).all()
    measurement = measurements[-1]
        
    measurement.Rn = Rn
    
    session.commit()
    print("Data successfully saved to database")
    
#==============================================
# functions for saving during the sweeps

def calc_JJ_measurements_after(Ic_list, Rn, Imax, JJ_radius):
    '''
    This will calculate the JJ measurements based Ics, Rn, Imax, and Radius
    Returns a list with all the values Ic_pos, Ic_neg, Iret_pos, Iret_neg, Imax, Rn, Iret_Ic_ratio, Ic_Rn_product, Rn_Area_product, Inverse_sqrtRn, sqrtIc, Jc_nom
    '''
    Ic_pos=float(Ic_list[0]); Iret_pos=float(Ic_list[1]);

    Iret = Iret_pos
    Ic = Ic_pos
    A = np.pi*JJ_radius**2 #area of JJ
    Ic_Rn_product = Ic*Rn; Rn_Area_product = Rn*A; Jc_nom = Ic/A
    try:
        Iret_Ic_ratio = Iret/Ic
        Inverse_sqrtRn = abs(Rn)**(-1/2); sqrtIc = abs(Ic)**(1/2);
    except:
        Iret_Ic_ratio = 1e-09
        Inverse_sqrtRn = 1e-09; sqrtIc = 1e-09;
            
    data = [Iret_Ic_ratio, Ic_Rn_product, Rn_Area_product, Inverse_sqrtRn, sqrtIc, Jc_nom]
    return data


def save_JJ_Measurements_Ic(chip, Ic_list, data_directory, device):
    '''
    Saves 4 Ic values from Ic_list to the measurements of the particular chip
    Extracts the device details from the passed in device object and assigns
    the measurement to the chip from the passed in chip id or name

    returns measurment id, for measure Rn to use and pass into the calc_JJ_measuremnts
    '''
    session.commit() #need this to force the database to update
    date = time.strftime("%Y/%m/%d") #get the date
    current_time = time.strftime("%H:%M:%S") #get the time
    c = find_chip(chip) #get the chip from database

    data = Ic_list
    design_name = session.query(Design).get(c.design_id).name
    print(design_name)
    #Writes all the data into the database returned from the line above
    if len(data)>2:
        this_JJ_Measurement = JJ_Measurement(date=date, time=current_time, chip_name = c.name, design_id = c.design_id, design_name = design_name, device_name=device.name, num_JJs = device.num_JJs,\
                                            JJ_radius_nom = device.JJ_radius_nom, data_directory = data_directory,\
                                            Ic_pos=float(data[1]), Ic_neg=float(data[3]),Iret_pos=float(data[2]),\
                                            Iret_neg=float(data[0]))
    else:
        this_JJ_Measurement = JJ_Measurement(date=date, time=current_time, chip_name = c.name, design_id = c.design_id, design_name = design_name, device_name=device.name, num_JJs = device.num_JJs,\
                                            JJ_radius_nom = device.JJ_radius_nom, data_directory = data_directory,\
                                            Ic_pos=float(data[0]),Iret_pos=float(data[1]))

    c.jj_measurements.append(this_JJ_Measurement)
    session.commit()
    print("Data successfully saved to database")

    return this_JJ_Measurement.id
def save_Ted_mistake(chip,measid,tedindex):
    session.commit() #need this to force the database to update

    measurement = session.query(JJ_Measurement).filter_by(id=measid).one()

    measurement.tedindex=tedindex

    session.commit()
    print("Data successfully saved to database")
def save_JJ_Measurements_Rn(chip, Rn, Imax, measurement_id, device,optionalindex=0):
    '''
    Saves 4 Ic values from Ic_list to the measurements of the particular chip
    Extracts the device details from the passed in device object and assigns
    the measurement to the chip from the passed in chip id or name
    '''
    session.commit() #need this to force the database to update

    measurement = session.query(JJ_Measurement).filter_by(id=measurement_id).one()

    date = time.strftime("%Y/%m/%d") #get the date
    current_time = time.strftime("%H:%M:%S") #get the time
    c = find_chip(chip) #get the chip from database

    Ic_list = []

    Ic_list.append(measurement.Ic_pos)
    Ic_list.append(measurement.Iret_pos)

    if type(device) == str:
        print(device)
        try:
            device = session.query(Device).filter_by(name=device).one()
        except sa.orm.exc.MultipleResultsFound:
            design = c.design_id
            devices = session.query(Device).filter_by(name=device).all()
            for dev in devices:
                if dev.design_id[0].id==design:
                    device = dev

    JJ_radius = device.JJ_radius_nom #Need to for the calculations below

    data = calc_JJ_measurements_after(Ic_list,Rn, Imax, JJ_radius) #calculates relevant values to save to the database
    design_name = session.query(Design).get(c.design_id).name


    #Writes all the data into the database returned from the line above
    measurement.Imax = float(Imax)
    measurement.Rn = float(Rn)

    measurement.Iret_Ic_ratio=float(data[0])
    measurement.Ic_Rn_product=float(data[1])
    measurement.Rn_Area_product=float(data[2])
    measurement.Inverse_sqrtRn=float(data[3])
    measurement.sqrtIc=float(data[4])
    measurement.Jc_nom=float(data[5])
    if optionalindex!=0:
        measurement.tedindex=optionalindex

    session.commit()
    print("Data successfully saved to database")

def chip_Jc(chip):
    '''
    Queries the database for wafer.Jc_approx
    '''
    c = find_chip(chip) #get the chip from database
    Jc = session.query(Wafer).get(c.wafer_id).Jc_approx*10000000 #Rest of program expect Jc to be in A/m^2, not kA/cm^2, so we multiply by 10^7
    print(Jc)
    return Jc

def copy_design(design_id):
    session.commit()
    '''
    designs = show_all_designs()
    
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
    '''
    try:
        og_design = session.query(Design).filter_by(id=design_id).one()
        og_devices = og_design.device_id

        design = Design(name=og_design.name + ' COPY')
        session.add(design)
        for i in range(0,len(og_devices)):
            og_dev = og_devices[i]
            card = og_dev.card
            card1 = og_dev.card1
            card2 = og_dev.card2
            channel1 = og_dev.channel1
            channel2 = og_dev.channel2
            name = og_dev.name + ' COPY'
            pads = og_dev.pads
            device_type = og_dev.device_type

            dev = Device(name=name, card=card, card1=card1, card2=card2, channel1=channel1, channel2=channel2, pads=pads, device_type=device_type)

            design.device_id.append(dev)
            session.add(dev)

        session.add(design)
        session.commit()

        rv = 0

    except sa.orm.exc.MultipleResultsFound:
        rv = -1
    except sa.orm.exc.NoResultFound:
        rv = -1

    return rv
def get_design_name(chip):
    return  session.query(Design.name).filter_by(id=chip.design_id).all()[0][0]
    
def get_session():
    return session

def end_session():
    session.close()
    return

