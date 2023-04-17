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
from keithley_2400 import set_voltage_V, get_ohm_4pt_2000

rm = pyvisa.ResourceManager()

'''---------------------INPUT BEFORE RUN---------------------'''

SR830_gpib_1 = 'GPIB0::5::INSTR'
SR830_gpib_2 = 'GPIB0::6::INSTR'
keithley2400_gpib = 'GPIB0::25::INSTR'
keithley2000_gpib = 'GPIB0::18::INSTR'
data_dir = r"C:\Users\ICET\OneDrive - Washington University in St. Louis\wustl\2022spring\data\20220609_cooling_RuOx_Cali" # the path you want to save all your datas

my_note = "2022.06.12 ICET RuOx calibration, keithley 2000 for RuOx Resistance, keithley 2400 for heater voltage, Lockins for cernox on noise probe "
# tell me about your exp, start a new line by \n
title = "_heater" # some unique feature you want to add in title
order = 2
list = ['timestamp', 'V_T_x', 'V_T_y', 'I_T_x' ,'I_T_y', 'R_RuOx', 'V_heater']
axis =""
for x in list:
    axis += f"{x}_{order}\t\t\t"
# customized

'''---------------------Start run---------------------'''

target_value_V = 4
step_size_V = 0.01
delaytime = 5

num_steps = int(np.floor(abs(target_value_V) / (step_size_V))) + 1

timestamp =[]
V_T_x =[]
V_T_y =[]
I_T_x =[]
I_T_y =[]
R_RuOx =[]
V_heater =[]
for val in np.linspace(0, target_value_V, num_steps):
    set_voltage_V(keithley2400_gpib, val)
    print("sweep voltage to: ", val)
    time.sleep(delaytime)

    for i in range(0,10):
        time.sleep(0.5)
        timestamp += [time.time()]

        V_x_temp = SR830_get_x(SR830_gpib_1)
        V_T_x += [V_x_temp]
        print("V_x: ",V_x_temp )

        V_T_y += [SR830_get_y(SR830_gpib_1)]
        I_T_x += [SR830_get_x(SR830_gpib_2)]
        I_T_y += [SR830_get_y(SR830_gpib_2)]

        r_temp = get_ohm_4pt_2000(keithley2000_gpib)
        print("RuOx reads: ", r_temp)
        R_RuOx += [r_temp]

        V_heater += [val]
    print("ok")
data = np.column_stack((timestamp, V_T_x, V_T_y, I_T_x ,I_T_y, R_RuOx, V_heater))
file_name = f"RuOx_cali.{order}"
# file_name = f"SDCPW_Background_at_Nb_{int(x*1E6)}ohm.{i}"
os.makedirs(data_dir + '\\' + datetime.now().strftime('%Y%m%d') + title, exist_ok=True)
np.savetxt(data_dir + '\\' + datetime.now().strftime('%Y%m%d') + title + "/" + file_name, data, delimiter='\t', \
           header=f"{datetime.now().strftime('%Y%m%d')}" + " " + f"{datetime.now().strftime('%H%M%S')}" + '\n' + \
                  my_note + f"{axis}")




