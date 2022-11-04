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
from Instrument_Drivers.hp34461A import hp34461a_get_ohm_4pt
rm = pyvisa.ResourceManager()

'''---------------------INPUT BEFORE RUN---------------------'''

SR830_gpib = 'GPIB0::5::INSTR'
keithley2400_gpib = 'GPIB0::24::INSTR'
keithley2000_gpib = 'GPIB0::18::INSTR'
hp34461a = 'GPIB0::17::INSTR'
data_dir = r"C:\Users\ICET\Desktop\Data\SD\20221020_SD_004d\Spectrum\I_2\vna"
my_note = "2022.11.4 Icet basetemp_scan peak when field on, AC"
# tell me about your exp, start a new line by \n

title = "_" + "sweepfield_Peak4_75kHz" # some unique feature you want to add in title

# customized, here I have 4 constant value for each VNA sweep, thus I defined 4 constant in the following function my_form

port ='S21'

def my_form(smith, constant1, constant2, constant3):
    lens = len(smith.freqs)
    data = np.column_stack((smith.freqs, smith.log_mag, smith.phase_rad, smith.real, smith.imag,
                             np.full(lens, constant1), np.full(lens, constant2), np.full(lens, constant3)))
    return data


span = 100
#(start freq, end freq, power, 1/bandwidth, points to sweep, address), you could skip if you done this manually already
#time.sleep(200)

'''---------------------Start run---------------------'''
list = ['VNA_freqs', 'VNA_log_mag', 'VNA_phase_rad', 'VNA_real', 'VNA_imag', 'v_sur','timestamp','r_RuOx']


# for i in range(0,300):
#     v_mag = 1.5-i/100
#     keithley2400_set_sour_voltage_V(keithley2400_gpib, v_mag)
#     v_sur = keithley2000_get_voltage_V(keithley2000_gpib)
SR830_set_frequency(SR830_gpib,75000)

for i in range(1,9):
    v_sur = 0.5 * i
    time.sleep(30)
    SR830_set_amplitude(SR830_gpib,v_sur)
    r_ruox = hp34461a_get_ohm_4pt(hp34461a)
    timestamp = time.time()
    avg = f"\n average for {span} times"
    vs = get_picoVNA_smith(port=port,f_min=6940,f_max=7010,number_of_points=1001,power=3,bandwidth=1000,Average=span)
    print(f"VNA data for {v_sur}V recorded")
    data = my_form(vs, v_sur, timestamp, r_ruox)
    file_name = f"SD_004a_ICET_AC_{v_sur}V.{i}"

    order = i
    axis = ''
    for x in list:
        axis += f"{x}_{order}\t\t\t"

    read_frequency = "\n VNA is set at frequency range:"+ f"{np.min(vs.freqs) / 1E9:0.6f},{np.max(vs.freqs) / 1E9:0.6f} GHz"
     #os.makedirs(data_dir + '\\' + datetime.now().strftime('%Y%m%d'), exist_ok=True)
    os.makedirs(data_dir + '\\' + datetime.now().strftime('%Y%m%d')+ title, exist_ok=True)
    np.savetxt(data_dir + '\\' + datetime.now().strftime('%Y%m%d')+ title + "/" + file_name, data, delimiter='\t',
               header = f"{datetime.now().strftime('%Y%m%d')}"+" "+f"{datetime.now().strftime('%H%M%S')}"+'\n'+ \
                   my_note + '\n' +avg + '\n'+ f"{axis}")

SR830_set_amplitude(SR830_gpib,0)