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
from vna_analysis import get_smith_data, change_vna_settings
from SR830 import SR830_get_x, SR830_get_y
from keithley_2400 import get_ohm_4pt

rm = pyvisa.ResourceManager()

'''---------------------INPUT BEFORE RUN---------------------'''

vna_gpib = 'GPIB20::20::INSTR'
SR830_gpib = 'GPIB20::5::INSTR'
keithley_gpib = 'GPIB20::25::INSTR'
data_dir = r"C:\Data\2022\20220209_SDCPW" # the path you want to save all your datas

my_note = "2022.02.09 red fridge cool down \n lockin 1V on 1Mohm for Nb resistance, keithley for RuOx " 
# tell me about your exp, start a new line by \n
title = "_" + "225mA_avgs" # some unique feature you want to add in title

axis = "VNA_freqs\t\t\t" + "VNA_log_mag\t\t\t" + "VNA_phase_rad\t\t\t" + "VNA_real\t\t\t" +"VNA_imag\t\t\t" +\
       "SR830_x\t\t\t" + "SR830_y\t\t\t" + "keithley_R\t\t\t" + "timestamp\t\t\t"
# customized, here I have 4 constant value for each VNA sweep, thus I defined 4 constant in the following function my_form

def my_form(smith, constant1, constant2, constant3, constant4):
    lens = len(smith.freqs)
    data = np.column_stack((smith.freqs, smith.log_mag, smith.phase_rad, smith.real, smith.imag,
                             np.full(lens, constant1), np.full(lens, constant2), np.full(lens, constant3), np.full(lens, constant4)))
    return data


power_list = [0]
#del_time = [150]
del_time = [10,30,100,300,1000] #avg time in sec
change_vna_settings(2, 9, 0, 0.001, 10001,vna_gpib) 
#(start freq, end freq, power, 1/bandwidth, points to sweep, address), you could skip if you done this manually already
#time.sleep(200)

'''---------------------Start run---------------------'''
i = 1
#while True:
for k , span in enumerate(del_time):
    x = -SR830_get_x(SR830_gpib)
    y = -SR830_get_y(SR830_gpib)
    R = get_ohm_4pt(keithley_gpib)
    timestamp = time.time()
    
    vna_handle = rm.open_resource(vna_gpib)
    vna_handle.write(f"SOUR:POW {power_list[0]}")
    vna_handle.write("sens:aver 0")
    vna_handle.write("sens:AVER 1")
    vna_handle.close()
    # print (f"Averaging for {del_time[0]} minutes")
    #time.sleep(del_time[0])
    time.sleep(span)
    avg = f"\n average for {span} sec"
    vs = get_smith_data(vna_gpib)
    
    data = my_form(vs, x, y, R, timestamp)
    
    file_name = f"SDCPW_Background_at_Nb_{int(x*1E6)}ohm.{span}"
    #file_name = f"SDCPW_Background_at_Nb_{int(x*1E6)}ohm.{i}"
    
    read_frequency = "\n VNA is set at frequency range:"+ f"{np.min(vs.freqs) / 1E9:0.6f},{np.max(vs.freqs) / 1E9:0.6f} GHz"
    #os.makedirs(data_dir + '\\' + datetime.now().strftime('%Y%m%d'), exist_ok=True)
    os.makedirs(data_dir + '\\' + datetime.now().strftime('%Y%m%d')+ title, exist_ok=True)
    np.savetxt(data_dir + '\\' + datetime.now().strftime('%Y%m%d')+ title + "/" + file_name, data, delimiter='\t',\
               header = f"{datetime.now().strftime('%Y%m%d')}"+" "+f"{datetime.now().strftime('%H%M%S')}"+'\n'+ \
               my_note + read_frequency + avg + '\n' + f"{axis}")
    
    time.sleep(30)
    i += 1
