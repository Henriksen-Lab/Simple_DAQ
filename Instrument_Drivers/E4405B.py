# -*- coding: utf-8 -*-
"""
Created on Tues Nov 1 2022

@author: shilling

"""

import numpy as np
import pyvisa
import matplotlib.pyplot as plt
import time, os
from datetime import datetime

rm = pyvisa.ResourceManager()

def E4405B_get_spectrum(address,start_freq,stop_freq):
    class E4405B_data():
        def __init__(self, freq, logmag):
            self.freqs = freq
            self.log_mag = logmag
    try:
        E4405B = rm.open_resource(address)
        center = (start_freq + stop_freq)/2
        span = abs(start_freq - stop_freq)
        E4405B.write(f"SENS:FREQ:CENT {center}")
        E4405B.write(f"SENS:FREQ:SPAN {span}")
        time.sleep(1)
        string_data = E4405B.query("TRAC:DATA? TRACE1")
        numerical_data = np.array(string_data.split(","), dtype='float')
        freq = np.linspace(start_freq,stop_freq,len(numerical_data))
        data = E4405B_data(freq,numerical_data)
    finally:
        E4405B.close()
    return data

# address = "GPIB0::20::INSTR"
# data = E4405B_get_spectrum(address,1e4,1.1e5)
# dataToSave = np.column_stack((data.freqs,data.log_mag))

# plt.plot(data.freqs,data.log_mag)
# plt.show()
# data_dir = r"C:\Users\ICET\Desktop\Data\SD\20221020_SD_004d\Spectrum"
# file_name = "base_line"
# os.makedirs(data_dir + '\\' + datetime.now().strftime('%Y%m%d'), exist_ok=True)
# np.savetxt(data_dir + '\\' + datetime.now().strftime('%Y%m%d')+ "/" + file_name, dataToSave, delimiter='\t',
#                header = f"{datetime.now().strftime('%Y%m%d')}"+" "+f"{datetime.now().strftime('%H%M%S')}")