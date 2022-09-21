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
    sys.path.append(folder_path)
from vna_analysis import get_smith_data, change_vna_settings
from SR830 import SR830_get_x, SR830_get_y, SR830_set_frequency, SR830_set_amplitude
from keithley_2400 import get_ohm_4pt

rm = pyvisa.ResourceManager()

SR830_gpib = 'GPIB0::5::INSTR'
data_dir = r"C:\Users\ICET\OneDrive - Washington University in St. Louis\wustl\2022spring\data\20220602_SD_004a_ICET\Lockin practice"

my_note = "2022.06.09 lockin on 1nF for Vx, Vy"
title = "_" + "Capacitor"
order = "004"

axis = f"SR830_x_{order}\t\t\t" + f"SR830_y_{order}\t\t\t" + f"SR830_freq_{order}\t\t\t" + f"timestamp_{order}\t\t\t"

x = []
y = []
freq =[]
timestamp =[]

###############################
SR830_set_amplitude(SR830_gpib, 0.004)
time.sleep(5)
SR830_set_amplitude(SR830_gpib, 0.010)
time.sleep(5)
for k in range(0,75):
    if k<10:
        f = k*10+1
    elif k<20:
        f = (k-10)*100+10*10+1
    elif k<40:
        f = (k-20)*500+10*100+10*10+1
    elif k<60:
        f = (k-40)*1000+20*500+10*100+10*10+1
    else:
        f = (k-60)*5000+20*1000+20*500+10*100+10*10+1
    SR830_set_frequency(SR830_gpib, f)
    time.sleep(5)
    for i in range(0,30):
        x += [SR830_get_x(SR830_gpib)]
        y += [SR830_get_y(SR830_gpib)]
        freq += [f]
        timestamp += [time.time()]
        time.sleep(0.3)

data = np.column_stack((x, y,freq,timestamp))
file_name = f"1nF_Voltage_f.{order} "
    #file_name = f"SDCPW_Background_at_Rmtemp.{span}"
    #read_frequency = "\n VNA is set at frequency range:"+ f"{np.min(vs.freqs) / 1E9:0.6f},{np.max(vs.freqs) / 1E9:0.6f} GHz"
os.makedirs(data_dir + '\\' + datetime.now().strftime('%Y%m%d')+ title, exist_ok=True)
np.savetxt(data_dir + '\\' + datetime.now().strftime('%Y%m%d')+ title + "/" + file_name, data, delimiter='\t',\
           header = f"{datetime.now().strftime('%Y%m%d')}"+" "+f"{datetime.now().strftime('%H%M%S')}"+'\n'+ \
           my_note + ', V_f_curve'+'\n' + f"{axis}")
SR830_set_amplitude(SR830_gpib, 0.004)    
SR830_set_frequency(SR830_gpib, 17.777)

'''
axis = "SR830_x\t\t\t" + "SR830_y\t\t\t" + "SR830_amp\t\t\t" + "timestamp\t\t\t"

x = []
y = []
amp =[]
timestamp =[]
SR830_set_amplitude(SR830_gpib, 0.004)
time.sleep(5)
SR830_set_frequency(SR830_gpib, 102000)
time.sleep(5)
for k in range(0,20):
    SR830_set_amplitude(SR830_gpib, 0.01*k+0.004)
    time.sleep(5)
    for i in range(0,30):
        x += [SR830_get_x(SR830_gpib)]
        y += [SR830_get_y(SR830_gpib)]
        amp += [0.01*k+0.004]
        timestamp += [time.time()]
        time.sleep(0.7)

data = np.column_stack((x, y,amp,timestamp))
file_name = f"SD_004a_contacts_I_V.001 "
    #file_name = f"SDCPW_Background_at_Rmtemp.{span}"
    #read_frequency = "\n VNA is set at frequency range:"+ f"{np.min(vs.freqs) / 1E9:0.6f},{np.max(vs.freqs) / 1E9:0.6f} GHz"
os.makedirs(data_dir + '\\' + datetime.now().strftime('%Y%m%d')+ title, exist_ok=True)
np.savetxt(data_dir + '\\' + datetime.now().strftime('%Y%m%d')+ title + "/" + file_name, data, delimiter='\t',\
           header = f"{datetime.now().strftime('%Y%m%d')}"+" "+f"{datetime.now().strftime('%H%M%S')}"+'\n'+ \
           my_note +' I_V_curve'+ '\n' + f"{axis}")
SR830_set_amplitude(SR830_gpib, 0.004)
    '''
    
  
'''  
def my_form(smith, constant1, constant2, constant3, constant4):
    lens = len(smith.freqs)
    data = np.column_stack((smith.freqs, smith.log_mag, smith.phase_rad, smith.real, smith.imag,
                             np.full(lens, constant1), np.full(lens, constant2), np.full(lens, constant3), np.full(lens, constant4)))
    return data

power_list = [0]
del_time = [180]
#del_time = [10,30,100,300,1000,3000]
change_vna_settings(2, 9, 0, 0.001, 10001,vna_gpib)
time.sleep(1)

i = 1
while True:
    span = del_time[0]
#for k , span in enumerate(del_time):
    x = SR830_get_x(SR830_gpib)
    y = SR830_get_y(SR830_gpib)
    R = get_ohm_4pt(keithley_gpib)
#    x = 0; y = 0; R = 0
    timestamp = time.time()
    
    vna_handle = rm.open_resource(vna_gpib)
    vna_handle.write(f"SOUR:POW {power_list[0]}")
    vna_handle.write("sens:aver 0")
    vna_handle.write("sens:AVER 1")
    vna_handle.close()
    time.sleep(span)
    avg = f"\n average for {span} sec"
    vs = get_smith_data(vna_gpib)
    
    data = my_form(vs, x, y, R, timestamp)
    
    #file_name = f"SDCPW_Background_at_Nb_{int(x*1E6)}ohm.{span}"
    file_name = f"SDCPW_RuCl_at_Nb_{int(x*1E6)}ohm.{i}"
    #file_name = f"SDCPW_Background_at_Rmtemp.{span}"
    read_frequency = "\n VNA is set at frequency range:"+ f"{np.min(vs.freqs) / 1E9:0.6f},{np.max(vs.freqs) / 1E9:0.6f} GHz"
    os.makedirs(data_dir + '\\' + datetime.now().strftime('%Y%m%d')+ title, exist_ok=True)
    np.savetxt(data_dir + '\\' + datetime.now().strftime('%Y%m%d')+ title + "/" + file_name, data, delimiter='\t',\
               header = f"{datetime.now().strftime('%Y%m%d')}"+" "+f"{datetime.now().strftime('%H%M%S')}"+'\n'+ \
               my_note + read_frequency + avg + '\n' + f"{axis}")
    
    time.sleep(5)
    i += 1
'''

