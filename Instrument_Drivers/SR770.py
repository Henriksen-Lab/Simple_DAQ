# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 2022

@author: Shilling Du

"""

import numpy as np
import pyvisa
import matplotlib.pyplot as plt
import time, os
from datetime import datetime

rm = pyvisa.ResourceManager()

def SR770_get_noise_spectrum(address):
    class SR770_data():
        def __init__(self, freq, logmag, range):
            self.freqs = freq
            self.log_mag = logmag
            self.range = range
    try:
        SR770 = rm.open_resource(address)
        SR770.write_termination = '\n'
        SR770.write(f"SPAN 19") # set span to 100khz
        SR770.write(f"ARNG 0")  # Auto Range OFF
        time.sleep(5)
        SR770.write(f"ARNG 1")  # Auto Range On
        time.sleep(5)
        range = float(SR770.query("IRNG?"))
        # print(f'range:{range}')
        start_freq = float(SR770.query("STRF?"))
        # print(f'freq:{start_freq}')
        center_freq = float(SR770.query("CTRF?"))
        # print(f'freq:{center_freq}')
        stop_freq = center_freq * 2 - start_freq
        SR770.write(f"AUTS -1")  # Auto scale -1: active trace
        SR770.timeout = 25000
        time.sleep(10)
        string_data = SR770.query("SPEC?-1")
        # print(string_data.split(","))
        numerical_data = np.array([float(x) for x in string_data.split(",")[:-1]])
        freq = np.linspace(start_freq,stop_freq,len(numerical_data))
        data = SR770_data(freq,numerical_data,range)
    finally:
        SR770.close()
    return data



address = "GPIB0::10::INSTR"
data = SR770_get_noise_spectrum(address)
dataToSave = np.column_stack((data.freqs,data.log_mag))
data_dir = r"C:\Users\ICET\Desktop\Data\SD\20230623_CHECK_samplepackage\DC_SR770\Equipments"
file_name = f"DMM34661A_GPIB_ohm2pt_RANG_{data.range}"
# os.makedirs(data_dir + '\\' + datetime.now().strftime('%Y%m%d'), exist_ok=True)
axis = 'freqs_001\t\t\tlog_mag_001\t\t\t'
np.savetxt(data_dir + "\\" + file_name, dataToSave, delimiter='\t',
               header = f"{datetime.now().strftime('%Y%m%d')}"+" "+f"{datetime.now().strftime('%H%M%S')}"+ '\n' + f"{axis}")