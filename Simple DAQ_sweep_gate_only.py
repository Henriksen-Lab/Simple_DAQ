# -*- coding: utf-8 -*-
"""
Created on Tues Feb 8 16:17:58 2022

@author: Shilling Du
@date: Feb 8, 2022
"""

import numpy as np
from datetime import datetime
import time, sys, os, pyvisa

folder_path = os.getcwd()
if folder_path not in sys.path:
    sys.path.append(folder_path) # easier to open driver files as long as Simple_DAQ.py is in the same folder with drivers
    #from vna_analysis import get_smith_data, change_vna_settings
from SR830 import SR830_get_x, SR830_get_y
from keithley_2400 import set_voltage_V, get_voltage_2000, initialize, output_on

rm = pyvisa.ResourceManager()
'''---------------------INPUT BEFORE RUN---------------------'''
SR830_gpib_1 = 'GPIB0::5::INSTR'
SR830_gpib_2 = 'GPIB0::6::INSTR'
keithley2400_gpib = 'GPIB0::25::INSTR'
keithley2000_gpib = 'GPIB0::18::INSTR'

target_value_V = 4.5
step_size_V = 0.00015
delaytime = 1

'''---------------------Start run---------------------'''
num_steps = int(np.floor(abs(target_value_V) / (step_size_V))) + 1

initialize(keithley2400_gpib)
initialize(keithley2000_gpib)
output_on(keithley2400_gpib)
set_voltage_V(keithley2400_gpib, 4.5)
print("reads: ", get_voltage_2000(keithley2000_gpib))
output_on(keithley2400_gpib)
time.sleep(5)
set_voltage_V(keithley2400_gpib, 0)
print("reads: ", get_voltage_2000(keithley2000_gpib))
time.sleep(30)


for val in np.linspace(0, target_value_V, num_steps):
    set_voltage_V(keithley2400_gpib, val)
    print("sweep voltage to: ", val)
    time.sleep(delaytime)
    print("reads: ", get_voltage_2000(keithley2000_gpib))
print("Sweep up ok")

time.sleep(300)

for val in np.linspace(target_value_V, 0, num_steps):
    set_voltage_V(keithley2400_gpib, val)
    print("sweep voltage to: ", val)
    time.sleep(delaytime)
    print("reads: ", get_voltage_2000(keithley2000_gpib))
print("Sweep down ok")

set_voltage_V(keithley2400_gpib, 0)



