# -*- coding: utf-8 -*-
"""
Created on Tues Feb 22

@author: Shilling Du
@date: Feb 22, 2022
"""

import numpy as np
from datetime import datetime
import time, sys, os, pyvisa
import matplotlib as mpl
import matplotlib.pyplot as plt

folder_path = os.getcwd()
if folder_path not in sys.path:
    sys.path.append(folder_path) # easier to open driver files as long as Simple_DAQ.py is in the same folder with drivers
from PicoVNA108 import get_picoVNA_smith


rm = pyvisa.ResourceManager()

'''---------------------INPUT BEFORE RUN---------------------'''

SR830_gpib = 'GPIB0::5::INSTR'
data_dir = r"C:\Users\ICET\OneDrive - Washington University in St. Louis\wustl\2022spring\data\20220602_SD_004a_ICET\scanPeak"
my_note = "2022.06.05 Icet basetemp_finerecord"
# tell me about your exp, start a new line by \n
title = "_" + "total" # some unique feature you want to add in title

# customized, here I have 4 constant value for each VNA sweep, thus I defined 4 constant in the following function my_form

port ='S21'

def my_form(smith, constant1):
    lens = len(smith.freqs)
    data = np.column_stack((smith.freqs, smith.log_mag, smith.phase_rad, smith.real, smith.imag,
                             np.full(lens, constant1)))
    return data


span = 5
#(start freq, end freq, power, 1/bandwidth, points to sweep, address), you could skip if you done this manually already
#time.sleep(200)

'''---------------------Start run---------------------'''
total = []
for i in range(0,61):
    timestamp = time.time()
    vs = get_picoVNA_smith(port=port,f_min=4000+i*50-26,f_max=4000+i*50+26,number_of_points=1001,power=3,bandwidth=1000,Average=span)
    print(f"VNA data for {4000+i*50} MHz recorded")
    data = my_form(vs, timestamp)
    total.append(data)
    time.sleep(0.1)

file_name = f"SD_004a_ICET_basetemp.001"
axis = f"VNA_freqs_{i}\t\t\t" + f"VNA_log_mag_{i}\t\t\t" + f"VNA_phase_rad_{i}\t\t\t" + f"VNA_real_{i}\t\t\t" + f"VNA_imag_{i}\t\t\t" + \
           f"timestamp_{i}\t\t\t"
os.makedirs(data_dir + '\\' + datetime.now().strftime('%Y%m%d')+ title, exist_ok=True)
np.savetxt(data_dir + '\\' + datetime.now().strftime('%Y%m%d')+ title + "/" + file_name, total, delimiter='\t',
               header = f"{datetime.now().strftime('%Y%m%d')}"+" "+f"{datetime.now().strftime('%H%M%S')}"+'\n'+ \
                   my_note + read_frequency + avg + '\n' + f"{axis}")
