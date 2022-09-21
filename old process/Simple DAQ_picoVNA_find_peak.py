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
from PicoVNA108 import get_picoVNA_smith


rm = pyvisa.ResourceManager()

'''---------------------INPUT BEFORE RUN---------------------'''

SR830_gpib = 'GPIB0::5::INSTR'
data_dir = r"C:\Users\ICET\OneDrive - Washington University in St. Louis\wustl\2022spring\data\20220617_SD_004a\ScanPeaks"
my_note = "2022.06.17 Icet basetemp_scan peak"
# tell me about your exp, start a new line by \n
title = "_" + "base temp" # some unique feature you want to add in title

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
list = ['VNA_freqs', 'VNA_log_mag', 'VNA_phase_rad', 'VNA_real', 'VNA_imag', 'timestamp']
for i in range(1,61):
    timestamp = time.time()
    avg = f"\n average for {span} times"
    vs = get_picoVNA_smith(port=port,f_min=4000+i*50-26,f_max=4000+i*50+26,number_of_points=1001,power=3,bandwidth=1000,Average=span)
    print(f"VNA data for {4000+i*50} MHz recorded")
    data = my_form(vs, timestamp)
    file_name = f"SD_004a_ICET_{4000+i*50}GHZ.{i}"

    order = i
    axis = ''
    for x in list:
        axis += f"{x}_{order}\t\t\t"

    read_frequency = "\n VNA is set at frequency range:"+ f"{np.min(vs.freqs) / 1E9:0.6f},{np.max(vs.freqs) / 1E9:0.6f} GHz"
     #os.makedirs(data_dir + '\\' + datetime.now().strftime('%Y%m%d'), exist_ok=True)
    os.makedirs(data_dir + '\\' + datetime.now().strftime('%Y%m%d')+ title, exist_ok=True)
    np.savetxt(data_dir + '\\' + datetime.now().strftime('%Y%m%d')+ title + "/" + file_name, data, delimiter='\t',
               header = f"{datetime.now().strftime('%Y%m%d')}"+" "+f"{datetime.now().strftime('%H%M%S')}"+'\n'+ \
                   my_note + '\n' + f"{axis}")

    fg = plt.figure()
    plt.plot(vs.freqs, vs.log_mag)
    #plt.ylim(-120,-60)
    plt.xlabel('freq(Hz)')
    plt.ylabel('log_mag(dB)')
    plt.title(f"SD_004a_ICET_{4000+i*50}GHZ")
    fg.savefig(r"C:\Users\ICET\OneDrive - Washington University in St. Louis\wustl\2022spring\data\20220617_SD_004a\ScanPeaks\pic" + f'\SD_004a_ICET_{4000+i*50}GHZ.{i}.jpg', bbox_inches='tight', dpi=150)
    plt.close()
    time.sleep(0.1)
