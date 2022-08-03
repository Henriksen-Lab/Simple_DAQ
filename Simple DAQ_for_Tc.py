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
from keithley_2400 import get_voltage_V

rm = pyvisa.ResourceManager()

'''---------------------INPUT BEFORE RUN---------------------'''

SR830_gpib = 'GPIB20::5::INSTR'
keithley_gpib = 'GPIB20::19::INSTR'
data_dir = r"C:\Data\2022\20220209_SDCPW" # the path you want to save all your datas

my_note = "2022.04.10 PPMS Kaiwen's film, NbN008 \n lockin 0.02V on 1Kohm for resistance, keithley for Temp " 
# tell me about your exp, start a new line by \n
title = "20220410_KZ_NbN008_Tc" # some unique feature you want to add in title

axis = "timestamp\t\t\t" + "SR830_x\t\t\t" + "SR830_y\t\t\t" + "keithley_R\t\t\t"
# customized

'''---------------------Start run---------------------'''



j = 0
while 1:
    j += 1
    xx = []
    yy = []
    VVoltage = []
    ttimestamp = []
    for i in range(0,10000):
        xx = np.append(-SR830_get_x(SR830_gpib))
        yy = np.append(-SR830_get_y(SR830_gpib))
        VVoltage = np.append(get_voltage_V(keithley_gpib))
        ttimestamp = np.append(time.time())
    data = np.column_stack(ttimestamp,xx,yy,VVoltage)
    file_name = f"20220410_KZ_NbN008_Tc.{j}"
    #file_name = f"SDCPW_Background_at_Nb_{int(x*1E6)}ohm.{i}"
    os.makedirs(data_dir + '\\' + datetime.now().strftime('%Y%m%d')+ title, exist_ok=True)
    np.savetxt(data_dir + '\\' + datetime.now().strftime('%Y%m%d')+ title + "/" + file_name, data, delimiter='\t',\
                    header = f"{datetime.now().strftime('%Y%m%d')}"+" "+f"{datetime.now().strftime('%H%M%S')}"+'\n'+ \
                    my_note + f"{axis}")
    time.sleep(5)
        
        
        
        

    