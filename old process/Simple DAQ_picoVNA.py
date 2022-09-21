# -*- coding: utf-8 -*-
"""
Created on Tues Feb 22

@author: Shilling Du
@date: Feb 22, 2022
"""

import numpy as np
from datetime import datetime
import time, sys, os, pyvisa

folder_path = os.getcwd()
if folder_path not in sys.path:
    sys.path.append(folder_path) # easier to open driver files as long as Simple_DAQ.py is in the same folder with drivers
from PicoVNA108 import get_picoVNA_smith
from SR830 import SR830_get_x, SR830_get_y
#from keithley_2400 import get_ohm_4pt


rm = pyvisa.ResourceManager()

'''---------------------INPUT BEFORE RUN---------------------'''

SR830_gpib = 'GPIB0::5::INSTR'
data_dir = r"C:\Users\ICET\OneDrive - Washington University in St. Louis\wustl\2022spring\data\20220602_SD_004a_ICET" # the path you want to save all your datas

my_note = "2022.06.02 Icet cool down \n lockin 1V on 1Mohm for RuOx, VNA for transimission"
# tell me about your exp, start a new line by \n
title = "_" + "cooling" # some unique feature you want to add in title

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
i = 11
while True:
    x = -SR830_get_x(SR830_gpib)
    y = -SR830_get_y(SR830_gpib)
    timestamp = time.time()
    avg = f"\n average for {span} times"
    print(f"x y data for {i} recorded")
    vs = get_picoVNA_smith(port=port,f_min=4000,f_max=8500,number_of_points=1001,power=0,bandwidth=1000,Average=span)
    print(f"VNA data for {i} recorded")
    data = my_form(vs, x, y, timestamp)

    file_name = f"SD_004a_ICET.{i}"
    axis = f"VNA_freqs_{i}\t\t\t" + f"VNA_log_mag_{i}\t\t\t" + f"VNA_phase_rad_{i}\t\t\t" + f"VNA_real_{i}\t\t\t" + f"VNA_imag_{i}\t\t\t" + \
           f"SR830_x_{i}\t\t\t" + f"SR830_y_{i}\t\t\t" + f"timestamp_{i}\t\t\t"

    read_frequency = "\n VNA is set at frequency range:"+ f"{np.min(vs.freqs) / 1E9:0.6f},{np.max(vs.freqs) / 1E9:0.6f} GHz"
     #os.makedirs(data_dir + '\\' + datetime.now().strftime('%Y%m%d'), exist_ok=True)
    os.makedirs(data_dir + '\\' + datetime.now().strftime('%Y%m%d')+ title, exist_ok=True)
    np.savetxt(data_dir + '\\' + datetime.now().strftime('%Y%m%d')+ title + "/" + file_name, data, delimiter='\t',
               header = f"{datetime.now().strftime('%Y%m%d')}"+" "+f"{datetime.now().strftime('%H%M%S')}"+'\n'+ \
                   my_note + read_frequency + avg + '\n' + f"{axis}")

    time.sleep(300)
    i += 1
