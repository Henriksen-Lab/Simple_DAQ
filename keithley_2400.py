 # -*- coding: utf-8 -*-
"""
Created on Tue Sep  1 22:18:28 2020

@author: Crow108
@revised: Shilling Du 02092020 11:24 added function get_ohm_4pt
"""

import numpy as np
import pyvisa

rm = pyvisa.ResourceManager()

def ramp_from_prev_value(address, target_value_mA, step_size_mA=0.01):    
    try:
        keithley = rm.open_resource(address)            
        last_value_mA = float( keithley.query("sour:curr?") )*1000
        
        num_steps = int(np.floor( abs((last_value_mA - target_value_mA))/ (step_size_mA))) +1
        # arange excludes last point; so use linspace
        for val in np.linspace(last_value_mA, target_value_mA, num_steps):
            keithley.write(f"sour:curr {np.round(val*1E-3,6)}")
    finally:     
        keithley.close()            
        
def get_currrent_mA(address):
    try:
        keithley = rm.open_resource(address)            
        last_value_mA = float( keithley.query("sour:curr?") )*1000
    finally:     
        keithley.close()       
    return last_value_mA

def get_ohm_4pt(address):
    try:
        keithley = rm.open_resource(address)
        keithley.write("*RST")
        keithley.write("SYST:BEEP:STAT OFF") # mute the equip from making beeps
        keithley.write("*cls")
        keithley.write("SENS:FUNC 'RES'") # measure Resistance
        keithley.write("RES:MODE AUTO") # mode: auto
        keithley.write("SYST:RSEN ON")  # set to 4 wire sensing
        keithley.write("SENS:RES:RANG:AUTO 1") # Auto range
        keithley.write("FORM:ELEM RES") # only output R
        keithley.write("OUTP ON")
        string_data = keithley.query("READ?")
        keithley.write("OUTP OFF")
        numerical_data = float(string_data)

    finally:     
        keithley.close()       
    return numerical_data