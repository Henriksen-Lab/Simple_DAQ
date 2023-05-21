# -*- coding: utf-8 -*-
"""
Created on Tues Feb 8 16:17:58 2022

@author: Shilling Du
@date: Feb 8, 2022
"""

# use Python 32bit for PicoVNA108


import numpy as np
from datetime import datetime
import time, sys, os, pyvisa, subprocess
import matplotlib as mpl
import matplotlib.pyplot as plt

folder_path = os.getcwd()
if folder_path not in sys.path:
    sys.path.append(folder_path) # easier to open driver files as long as Simple_DAQ.py is in the same folder with drivers
from Instrument_Drivers.PicoVNA108 import get_picoVNA_smith
from Instrument_Drivers.SR830 import SR830_set_frequency, SR830_set_amplitude
from Instrument_Drivers.keithley import *
from Instrument_Drivers.hp34461A import hp34461a_get_ohm_2pt, hp34461a_get_voltage
from Instrument_Drivers.SR830 import SR830_set_frequency,SR830_set_amplitude,SR830_get_frequency,SR830_get_amplitude
from Instrument_Drivers.SR124 import *
rm = pyvisa.ResourceManager()

# subprocess.call(['sh','SD_pywin32error.sh'])
# this command delete r'C:\Users\<username>\AppData\Local\Temp\2\gen_py' to solve a potential pywin32 error that usually happens after you use the PICOVNA 3 program

def my_form(kwargs):
    lens = len(kwargs['smith'].freqs)
    list = []
    dataToSave = []
    for key in kwargs:
        if key=='smith':
            smith = kwargs[key]
            dataToSave += [smith.freqs]
            dataToSave += [smith.log_mag]
            dataToSave += [smith.phase_rad]
            dataToSave += [smith.real]
            dataToSave += [smith.imag]
            list += ['VNA_freqs', 'VNA_log_mag', 'VNA_phase_rad', 'VNA_real', 'VNA_imag']
        else:
            dataToSave += [np.full(lens, kwargs[key])]
            list += [key]
    data = np.column_stack(dataToSave)
    axis = ''
    for x in list:
        axis += f"{x}_{order}\t\t\t"
    return data, axis


'''---------------------Run func---------------------'''
def get_sweep(start,stop,step_size):
    num_steps = int(np.floor(abs(float(start) - float(stop)) / float(step_size))) + 1
    return np.linspace(float(start), float(stop), num_steps)

def run_single(sweep,order,f_min,f_max,span=250):
    set(sweep)
    value = read()
    avg = f"\n average for {span} times"
    print(f"{datetime.now().strftime('%Y.%m.%d')}", " ", f"{datetime.now().strftime('%H:%M:%S')}", "  ",
          order, " . started")
    msg = 'VNA data for'
    for key, item in value.items():
        msg += f" {key}={item}, "
    vs = get_picoVNA_smith(port=port, f_min=f_min, f_max=f_max, number_of_points=1001, power=-5, bandwidth=1000, Average=span)
    print(msg+' recorded')
    value.update({'smith':vs})
    data, axis = my_form(value)
    read_frequency = "\n VNA is set at frequency range:" + f"{np.min(vs.freqs) / 1E9:0.6f},{np.max(vs.freqs) / 1E9:0.6f} GHz"
    file_name = f"SD_006b_hemt_sweep_gate_DCbias.{order}"
    file_real_path = data_dir + '\\' + datetime.now().strftime('%Y%m%d') + title + "\\" + file_name
    while os.path.exists(file_real_path):
        order = order + 1
        file_name = ''.join(file_name.split('.')[:-1]) + f'.{order}'
        file_real_path = data_dir + '\\' + datetime.now().strftime('%Y%m%d') + title + "\\" + file_name
    os.makedirs(data_dir + '\\' + datetime.now().strftime('%Y%m%d') + title, exist_ok=True)
    np.savetxt(file_real_path, data, delimiter='\t',
               header=f"{datetime.now().strftime('%Y%m%d')}" + " " + f"{datetime.now().strftime('%H%M%S')}" + '\n' + \
                      my_note + '\n' + avg + '\n' + f"{axis}")

def dry_sweep(start, stop, step_size=0.01):
    for sweep in get_sweep(start=start, stop=stop, step_size=step_size):
        sweep = round(sweep,ndigits=4)
        set(sweep)
        read()
    return sweep

def wet_sweep(start, stop, step_size,order, last_v, f_min, f_max):
    for sweep in get_sweep(start=start, stop=stop, step_size=step_size):
        last_v = dry_sweep(last_v, sweep)
        for i in range(10):
            order += 1
            run_single(sweep, order, f_min=f_min, f_max=f_max, span=250)
            last_v = sweep
    return last_v


'''---------------------INPUT BEFORE RUN---------------------'''

keithley2400_gpib = 'GPIB0::25::INSTR'
keithley2000_gpib = 'GPIB0::18::INSTR'
hp34461a = 'GPIB0::17::INSTR'
SR830 = 'GPIB0::5::INSTR'
SR124 = 'ASRL5::INSTR'
data_dir = r'C:\Users\ICET\Desktop\Data\SD\20230428_SD006b_mag_probe_addhemt\compressibility\DC_AC_sweep'
my_note = "2023.05.18 Icet basetemp_scan sd006b_DCbias"
# tell me about your exp, start a new line by \n

title = "_" + "sweep_Vg_DCbias" # some unique feature you want to add in title
# customized, here I have 4 constant value for each VNA sweep, thus I defined 4 constant in the following function my_form

port ='S21'

'''---------------------Start your sequence here---------------------'''
# define the program for each sweep
def set(value):
    '''AC B wiggle'''
    # SR830_set_frequency(SR830, 10000)
    # SR830_set_amplitude(SR830, value)
    '''DC sweep Gate'''
    # keithley2400_set_sour_voltage_V(keithley2400_gpib, value)
    '''DC+AC sweep gate'''
    SR124_set_amplitude(SR124, value)
    time.sleep(1)

def read():
    read = {}
    '''AC B wiggle'''
    # read.update({'freq':SR830_get_frequency(SR830)})
    # read.update({'wiggle_B':SR830_get_amplitude(SR830)})
    '''DC sweep Gate'''
    # read.update({'v_sur': keithley2400_get_sour_voltage_V(keithley2400_gpib)})
    '''DC+AC sweep gate'''
    read.update({'vg_bias': SR124_get_DCbias(SR124)})
    read.update({'vg_freq': SR124_get_frequency(SR124)})
    read.update({'vg_Vrms': SR124_get_amplitude(SR124)})
    msg = ''
    for key, item in read.items():
        msg += f'{key}={item}, '
    print(msg)
    return read


'''AC wiggle B'''
# centers =  [6080, 6220, 6610, 7089] #sd004_1
# centers =  [6033, 6335, 6620, 7104] #sd003a
# start_freq_list = [4000]
# stop_freq_list = [7200]
# for center in centers:
#     start_freq_list += [center-75]
#     stop_freq_list += [center+75]
#
# last_v = 0.004
# for index in range(len(start_freq_list)):
#     title = "_" + f"sweep_B_{start_freq_list[index]}to{stop_freq_list[index]}MHz" # some unique feature you want to add in title
#     order = 0
#     last_v = wet_sweep(start=last_v,
#                        stop=3.504,
#                        step_size=0.5,
#                        order=order,
#                        last_v=last_v,
#                        f_min=start_freq_list[index],
#                        f_max=stop_freq_list[index])
#     last_v = dry_sweep(last_v,0.004)
# print('done')

'''DC sweep Gate'''
# last_v = 0
# order = 0
# last_v = wet_sweep(start=last_v,
#                    stop=2.5,
#                    step_size=0.1,
#                    order=order,
#                    last_v=last_v,
#                    f_min=4000,
#                    f_max=6000)
# last_v = dry_sweep(last_v,0)
# print('done')

'''DC+AC sweep gate'''
def bias_sweep(start,stop,stepsize=0.001):
    for bias in get_sweep(start=start, stop=stop, step_size=stepsize):
        SR124_set_DCbias(SR124, bias)
    print(f'bias set to {bias}')
    return bias


order = 0
last_bias = SR124_get_DCbias(SR124)
last_v = SR124_get_amplitude(SR124)

for bias in get_sweep(0,1.25,0.05):
    last_bias = bias_sweep(last_bias,bias)
    title = "_" + f"DC_bias_{last_bias}V"  # some unique feature you want to add in title
    last_v = wet_sweep(start=0.01,
                       stop=0.71,
                       step_size=0.05,
                       order=order,
                       last_v=last_v,
                       f_min=4000,
                       f_max=7200)
    last_v = dry_sweep(last_v,0.01)
bias_sweep(last_bias,0)
print('done')

# dry_sweep(0.7,0.01)
