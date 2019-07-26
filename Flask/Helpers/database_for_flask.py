# -*- coding: utf-8 -*-
"""
Created on Thu Mar  8 11:56:43 2018

@author: sdk

This is the version of database used for Flask, slightly stripped down,
mostly the same though.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import numpy as np
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, Float, String, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
import time
#import IV_curve as iv
sa.__version__

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= "mysql+pymysql://volt:pass@132.163.82.9/seg_sfq_v0"

db=SQLAlchemy(app)
migrate=Migrate(app,db)
manager=Manager(app)
manager.add_command('db', MigrateCommand)

#setups logging
# import logging
# db_log_file_name = 'Samples_2_database.log'
# db_handler_log_level = logging.INFO
# db_logger_log_level = logging.INFO

# db_handler = logging.FileHandler(db_log_file_name)
# db_handler.setLevel(db_handler_log_level)

# db_logger = logging.getLogger('sqlalchemy')
# db_logger.addHandler(db_handler)
# db_logger.setLevel(db_logger_log_level)

#engine = sa.create_engine("mysql+pymysql://javi:pass@686qvalessio/seg_sfq_v0", echo=False, pool_recycle=30)
engine = sa.create_engine("mysql+pymysql://volt:pass@132.163.82.9/seg_sfq_v0", echo=False, pool_recycle=30)

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
    comment=Column(String(150))
    missing_width = Column(Float) #In um. Only used for wafers with PCMRS chips
   # chips = relationship("Chip", order_by=Chip.id, back_populates="wafer")
    
    def __repr__(self):
        return "<Wafer(name='%s', date='%s, Jc_approx='%s', comment='%s')>" %(self.name, self.date, self.Jc_approx, self.comment)   
    
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
        return "<Chip(name='%s', location='%s', wafer_id='%s', design_id='%s' )>" %(self.name, self.location, self.wafer_id, self.design_id)

#Wafer.chips = relationship("Chip", order_by=Chip.id, back_populates="wafer")    

class Design(Base):
    'This takes in name of the device and string of tuples (device type, number of devices, junction radius in um, pads, channels)'
    __tablename__ = 'design'
    id = Column(Integer, primary_key = True)
    name = Column(String(50))
    date = Column(String(12))
    #devices = Column(String(1000))
    device_id = relationship("Device", secondary=design_devices, back_populates='design_id')

    #chip_id = Column(Integer, ForeignKey('chip.id'))
    
    #chips = relationship("Chip", back_populates="type")
    
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
    Iret_neg = Column(Float) #The return critical current postive side of IV curve which depending on the damping below should show some slight hysteresis (i.e. slight difference between Ic and Iret)
    Imax = Column(Float) #Max current before heating
    Rn = Column(Float) #Normal resistance which should be near the superconducting band gap. Due to heating we can measure the normal resistance slightly below the superconduting band gap. 
    Iret_Ic_ratio = Column(Float) #This is an approximation of Beta which is the damping of the circuit. Ideally [underdamped] 0.9 < Beta > 1.0 [overdamped]. If the circuit is overdamped then it will not work at higher frequencies (~100GHz)
    Ic_Rn_product = Column(Float)
    Rn_Area_product = Column(Float)
    Inverse_sqrtRn = Column(Float)
    sqrtIc = Column(Float)
    tedindex=Column(Integer)
    R_roomTemp = Column(Float) #room temperature R
    Jc_nom = Column(DECIMAL(13,3)) #The critical current density Jc = Ic/Area of junction
    #chip_id = Column(Integer, ForeignKey('chip.id'))
    
    #chips = relationship("Chip", back_populates="type")
    def __repr__(self):
        return "<JJ_Measurement(measurement_id='%s',device_name='%s', num_JJs='%d', JJ_radius='%f')>" %(self.id, self.device_name, self.num_JJs, self.JJ_radius_nom)
  
    def toJson(self):
        r = {}
        r["datetime"] = self.date + ", " + self.time
        r["chip_name"] = self.chip_name
        r["device_name"] = self.device_name
        r["Rn"] = self.Rn
        r["Ic_pos"] = self.Ic_pos * 1000
        r["data_dir"] = self.data_directory
        
        return r        
    

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
    #JJ_radius_nom = Column(DECIMAL(13,3))
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
    #JJ_radius_nom = Column(DECIMAL(13,3))
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
    Imax = Column(Float)
    
#    size = Column(Float)
    
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

##
##END BASE CLASSES
##


#Lets create our Table which is part of MetaData and pass it our 'engine' to connect to the database
Base.metadata.create_all(engine)
#Lets start chatting with the database via a session
Session = sa.orm.sessionmaker(bind=engine)
session = Session()


#def create_session():
#    session = Session()
#    return session


def show_all_wafers():
    session.commit() #need this to force the database to update
    try:
        w = session.query(Wafer).all()
        print("\nAll Wafers")
        return w

    except sa.orm.exc.NoResultFound:
        print("\n!ERROR! No wafers found.")
    session.close()


def show_all_chips():
    session.commit() #need this to force the database to update
    try:
        c = session.query(Chip).all()
        print("\nAll Chips")
        return c

    except sa.orm.exc.NoResultFound:
        print("\n!ERROR! No chips found.")
        
def find_chip(chip):
    'finds the chip by id or name'
    if type(chip) == str:
        try: 
            c = (session.query(Chip).filter_by(name=chip).one())
            print("\n Found chip %s" %chip)
            return c
        except sa.orm.exc.NoResultFound:
            print("\n!ERROR! Did not find chip: %s" %chip)
            
    elif type(chip) == int:
        try: 
            c = (session.query(Chip).filter_by(id=chip).one())
            print("\n Found chip %s" %chip)
            return c
        except sa.orm.exc.NoResultFound:
            print("\n!ERROR! Did not find chip: %s" %chip)
    else: 
        print("Must pass in wafer name as string or id as int")
    session.close()

def find_design(design):
    session.commit()
    if type(design) == int:
        try:

            d = session.query(Design).filter_by(id=design).one()
            return d
        except sa.orm.exc.NoResultFound:
            print("Didn't find design %s" %design)
            return -1
    if type(design) == str:
        try:
            d = session.query(Design).filter_by(name=design).one()
            return d
        except sa.orm.exc.NoResultFound:
            return -1
    
            
def find_device(device,optional_designid=0,output=1):
    session.commit() #need this to force the database to update
    'finds the device by id or name'
    if type(device) == str:
        try: 
            d = (session.query(Device).filter_by(name=device).one())
            if output:
                print("\n Found device %s" %device)
            return d
        except sa.orm.exc.NoResultFound:
            print("\n!ERROR! Did not find device: %s" %device)
            
        except sa.orm.exc.MultipleResultsFound:
            if(optional_designid):
                # doesn't work
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
            print("\n!ERROR! Did not find device: %s" %device)
    else: 
        print("Must pass in wafer name as string or id as int")
    
        
        
def find_wafer(wafer):
    session.commit() #need this to force the database to update
    'finds the wafer by id or name'
    if type(wafer) == str:
        try: 
            c = (session.query(Wafer).filter_by(name=wafer).one())
            print("\n Found wafer %s" %wafer)
            return c
        except sa.orm.exc.NoResultFound:
            print("\n!ERROR! Did not find wafer: %s" %wafer)
            
    elif type(wafer) == int:
        try: 
            c = (session.query(Wafer).filter_by(id=wafer).one())
            print("\n Found wafer %s" %wafer)
            return c
        except sa.orm.exc.NoResultFound:
            print("\n!ERROR! Did not find wafer: %s" %wafer)
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
    session.close()
    
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
    session.close()
    
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
    else: print("Must pass in chip name as string or id as int")
    session.close()
    
def show_all_JJ_measurements():
    session.commit()
    meas = session.query(JJ_Measurement).all()
    return meas
    
def show_JJ_measurements_from_chip(chip, design=0):
    session.commit() #need this to force the database to update
    c = find_chip(chip) #get the chip from database
    jj_measurements = session.query(JJ_Measurement).filter_by(chip_name=c.name).all()
    #print("\n\nMeasurements associated with Chip:")
    #print(jj_measurements)
    session.close()
    return jj_measurements
def get_design_name(chip):
    return  session.query(Design.name).filter_by(id=chip.design_id).all()[0][0]


def find_meas_by_dir(data_dir, device, chip, partial_dir=False):
    session.commit()
    try:
        m = session.query(JJ_Measurement).filter_by(data_directory=data_dir, device_name=device).one()
        return m
    except:
        try: 
            m = session.query(JJ_Measurement).filter_by(device_name=device, chip_name=chip).one()
            return m
        except sa.orm.exc.MultipleResultsFound:
            m = session.query(JJ_Measurement).filter_by(device_name=device, chip_name=chip).all()
            
            if partial_dir:
                for e in m:
                    if data_dir in e.data_directory:
                        return e
            
            return m[-1]
        except sa.orm.exc.NoResultFound:
            return -1
            
        return -1
    
    
def show_JJ_measurements_from_wafer(wafer, design='all'):
    session.commit() #need this to force the database to update
    jj_measurements = []
    chips_for_design = []
    w = find_wafer(wafer)
    print(w)
    chips = show_chips_from_wafer(w.id)
    #print(chips)
    
    if design == 'all': #returns all the measurement associated with the wafer
        for i, chip in enumerate(chips):
            c = find_chip(chips[i].id) #get the chip from database
            jj_measurements.append(session.query(JJ_Measurement).filter_by(chip_name=c.name).all())
            chips_for_design.append(c)
            
    else: #Searching for chips from wafer for a particular design name
        for i, chip in enumerate(chips): 
            c = find_chip(chips[i].id) #get the chip from database
            #print(c.id)
            design_name = session.query(Design).join(Chip).filter(Chip.id==c.id).one() #grabs the design name for the chip
            #print(design_name.name)
            if design_name.name.find(design) != -1: #Append only chips with the proper design name
                jj_measurements.append(session.query(JJ_Measurement).filter_by(chip_name=c.name).all())
                chips_for_design.append(c)
        
    #print("\n\nMeasurements associated with Wafer:")
    #print(jj_measurements)
    session.close()
    return jj_measurements, chips_for_design

def get_data_directory(chip):
    session.commit()
    
    if(type(chip)==Chip):
        #doesn't work
        chip_name = chip.name
    else:
        chip_name = chip
    try:
        m = session.query(JJ_Measurement).filter_by(chip_name=chip_name).one()
        return [m.data_directory]
    except sa.orm.exc.MultipleResultsFound:
        ms = session.query(JJ_Measurement).filter_by(chip_name=chip_name).all()
        ms_toreturn = []
        for m in ms:
            if not m.data_directory in ms_toreturn:
                ms_toreturn.append(m.data_directory)
        return ms_toreturn
    except sa.orm.exc.NoResultFound:
        return -1


def create_chip():
    chip_name = str(input("Chip name?  ")).upper()
    #print(chip_name)
    wafer_name = str(input('Wafer name?  ')).upper()
    #search for wafer name and ask if you would like to create a new one
    design_name = str(input('Design name?  ')).upper()
    #search for wafer name and ask if you would like to create a new one
    
    print('\nCreating... \nChip "%s" \nWafer "%s" \nDesign "%s"' %(chip_name, wafer_name, design_name))


def device_def(chip_id):
    'pass in chip name returns the device definition as list of tuples'
    
    try:
        #d = session.query(Design).join(Chip).filter(Chip.name==chip).one()
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
    I_min = -Ic*1.85
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
    Iret_Ic_ratio = Iret/Ic; Ic_Rn_product = Ic*Rn; Rn_Area_product = Rn*A; Inverse_sqrtRn = Rn**(-1/2); sqrtIc = Ic**(1/2); Jc_nom = Ic/A
    data = [Ic_pos, Ic_neg, Iret_pos, Iret_neg, Imax, Rn, Iret_Ic_ratio, Ic_Rn_product, Rn_Area_product, Inverse_sqrtRn, sqrtIc, Jc_nom]
    return data
#TODO list: add design to device, calculate the values to input to database with function above, move chip.id and design.id to 2 & 3 column
    
def save_JJ_Measurements(chip, Ic_list, Rn, Imax, data_directory, device):
    session.commit() #need this to force the database to update
    '''
    Saves 4 Ic values from Ic_list to the measurements of the particular chip
    Extracts the device details from the passed in device object and assigns
    the measurement to the chip from the passed in chip id or name
    '''
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
    session.close()

def chip_Jc(chip):
    '''
    Queries the database for wafer.Jc_approx
    '''
    c = find_chip(chip) #get the chip from database
    Jc = session.query(Wafer).get(c.wafer_id).Jc_approx
    print(Jc)
    return Jc
    
def get_session():
    return session

def end_session():
    session.close()
    return

#x = session.query(Wafer).filter_by(date='6/1/2017').all()
#print(x)

if __name__=='__main__':
    manager.run() 


#Start a sweep
