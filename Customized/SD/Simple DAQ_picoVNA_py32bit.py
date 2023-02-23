# -*- coding: utf-8 -*-
"""
Created on Tues Feb 8 16:17:58 2022

@author: Shilling Du
@date: Feb 8, 2022
"""
# manually delete r'C:\Users\<username>\AppData\Local\Temp\2\gen_py'


import numpy as np
from datetime import datetime
import time, sys, os, pyvisa
import matplotlib as mpl
import matplotlib.pyplot as plt

folder_path = os.getcwd()
if folder_path not in sys.path:
    sys.path.append(folder_path) # easier to open driver files as long as Simple_DAQ.py is in the same folder with drivers
from Instrument_Drivers.PicoVNA108 import get_picoVNA_smith
from Instrument_Drivers.SR830 import SR830_set_frequency, SR830_set_amplitude
from Instrument_Drivers.keithley import keithley2400_set_sour_voltage_V, keithley2000_get_voltage_V, keithley2400_initialize, keithley2400_output_on
from Instrument_Drivers.hp34461A import hp34461a_get_ohm_2pt,hp34461a_get_voltage
rm = pyvisa.ResourceManager()

'''---------------------INPUT BEFORE RUN---------------------'''

keithley2400_gpib = 'GPIB0::25::INSTR'
keithley2000_gpib = 'GPIB0::18::INSTR'
hp34461a = 'GPIB0::17::INSTR'
data_dir = r'C:\Users\ICET\Desktop\Data\SD\20230126_SD_006b\DC_field_transmission\02182023_wiggle_field'
my_note = "2023.02.18 Icet basetemp_scan 0V when field off"
# tell me about your exp, start a new line by \n

title = "_" + "long_avg_0V" # some unique feature you want to add in title

# customized, here I have 4 constant value for each VNA sweep, thus I defined 4 constant in the following function my_form

port ='S21'

def my_form(smith, **kwargs):
    lens = len(smith.freqs)
    dataToSave = []
    dataToSave += [smith.freqs]
    dataToSave += [smith.log_mag]
    dataToSave += [smith.phase_rad]
    dataToSave += [smith.real]
    dataToSave += [smith.imag]
    for key in kwargs:
        dataToSave += [np.full(lens, kwargs[key])]
    data = np.column_stack(dataToSave)
    return data


span = 250
#(start freq, end freq, power, 1/bandwidth, points to sweep, address), you could skip if you done this manually already
#time.sleep(200)

'''---------------------Start run---------------------'''
# list = ['VNA_freqs', 'VNA_log_mag', 'VNA_phase_rad', 'VNA_real', 'VNA_imag', 'vg','timestamp','r_RuOx']
list = ['VNA_freqs', 'VNA_log_mag', 'VNA_phase_rad', 'VNA_real', 'VNA_imag', 'vg_sur','vg','timestamp']

def get_sweep(start,stop,step_size):
    num_steps = int(np.floor(abs(float(start) - float(stop)) / float(step_size))) + 1
    return np.linspace(float(start), float(stop), num_steps)

def run_single(v_sur,order):
    # keithley2400_set_sour_voltage_V(keithley2400_gpib, v_sur)
    time.sleep(10)
    # r_ruox = hp34461a_get_ohm_2pt(hp34461a)
    # v_get = keithley2000_get_voltage_V(keithley2000_gpib)
    v_get = hp34461a_get_voltage(hp34461a)
    timestamp = time.time()
    avg = f"\n average for {span} times"
    print(f"{datetime.now().strftime('%Y.%m.%d')}", " ", f"{datetime.now().strftime('%H:%M:%S')}", "  ",
          order, " . started")
    vs = get_picoVNA_smith(port=port, f_min=2000, f_max=8000, number_of_points=1001, power=3, bandwidth=1000,
                           Average=span)
    print(f"VNA data for {v_sur}V recorded, measured to be {v_get}V")
    # data = my_form(vs, v_sur, timestamp, r_ruox)
    data = my_form(smith=vs, v_sur=v_sur, v_get=v_get, timestamp=timestamp)
    file_name = f"SD_006b_V_B_{v_sur}V.{order}"
    axis = ''
    for x in list:
        axis += f"{x}_{order}\t\t\t"
    read_frequency = "\n VNA is set at frequency range:" + f"{np.min(vs.freqs) / 1E9:0.6f},{np.max(vs.freqs) / 1E9:0.6f} GHz"
    # os.makedirs(data_dir + '\\' + datetime.now().strftime('%Y%m%d'), exist_ok=True)
    file_real_path = data_dir + '\\' + datetime.now().strftime('%Y%m%d') + title + "\\" + file_name
    while os.path.exists(file_real_path):
        order = order + 1
        file_name = ''.join(file_name.split('.')[:-1]) + f'.{order}'
        file_real_path = data_dir + '\\' + datetime.now().strftime('%Y%m%d') + title + "\\" + file_name
    os.makedirs(data_dir + '\\' + datetime.now().strftime('%Y%m%d') + title, exist_ok=True)
    np.savetxt(file_real_path, data, delimiter='\t',
               header=f"{datetime.now().strftime('%Y%m%d')}" + " " + f"{datetime.now().strftime('%H%M%S')}" + '\n' + \
                      my_note + '\n' + avg + '\n' + f"{axis}")

def dry_sweep(start, stop, step_size=0.005):
    for sweep in get_sweep(start=start, stop=stop, step_size=step_size):
        v_sur = sweep
        keithley2400_set_sour_voltage_V(keithley2400_gpib, v_sur)
        time.sleep(1)
        read = hp34461a_get_voltage(hp34461a)
        print("v_sur=", v_sur, ", measured to be", read)
    return v_sur

def wet_sweep(start, stop, step_size, order, last_v):
    for sweep in get_sweep(start=start, stop=stop, step_size=step_size):
        v_sur = sweep
        dry_sweep(last_v, v_sur)
        order += 1
        run_single(v_sur, order)
        last_v = v_sur

# last_v = dry_sweep(0,0.35)
order = 0
for i in range(0,10):
    v_sur = 0.5
    order += 1
    run_single(v_sur, order)
# dry_sweep(0.35,1.4)
# for i in range(0,11):
#     v_sur = 1.4
#     order += 1
#     run_single(v_sur, order)
# dry_sweep(1.4,0)

# keithley2400_set_sour_voltage_V(keithley2400_gpib,0)
print('done')