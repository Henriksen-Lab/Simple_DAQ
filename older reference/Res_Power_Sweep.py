"""
Created on Sat Nov 14 16:42:05 2020

@author: DVK
"""
#A program to return VNA Smith chart in Wisbey's vi format

import numpy as np
from datetime import datetime
import os
import pyvisa

rm = pyvisa.ResourceManager()
vna_gpib='GPIB20::20::INSTR'
vna = rm.open_resource(vna_gpib)

#data_dir = "C:\\Data\\20210112_CPW_Res\\DVK_068_05\\TempSweep"

def wisform(smith):
    outarray = np.column_stack((smith.freqs,smith.log_mag,smith.phase_rad,smith.real,smith.imag))
    return outarray

data_dir = r"C:\Data\2022\20220126_JR_RCRF_cali\18S22"

#
power_list=[0,5]
del_time = [0.1]
#span = [61, 90, 405] #in KHz
#center_freq = [6.582951264, 6.746680516, 7.156077464] # in GHz

#
#power_list = np.linspace(-70,-90,6)
#power_list = np.linspace(-84,-90,4)
#del_time = np.zeros((np.size(power_list)))
#del_time[0:20] = 60; del_time[20::] = 120  
#power_list = np.linspace(10,-65,26)
#del_time=np.zeros(np.size(power_list))
#del_time[0:5]=1; del_time[5:10]=2; del_time[10:15] = 5; del_time[15:20] = 10; del_time[20:25] = 30; del_time[25:26] = 60;
#del_time[:]=240
#print(np.sum(del_time))

for i,power in enumerate(power_list):
    vna.write(f"SOUR:POW {power}")
    vna.write(":AVER 0")
    vna.write(":AVER 1")
    
    print(f"Averaging for {del_time[i]} minutes")
    time.sleep(60*del_time[i])
    vs=get_smith_data(vna_gpib)
    outarray = wisform(vs)
    file_name = f"vna_{np.min(vs.freqs)/1E9:0.6f},{np.max(vs.freqs)/1E9:0.6f}_power{power}dBm.txt"
    os.makedirs(data_dir+'\\'+datetime.now().strftime('%Y%m%d'),exist_ok=True)
    np.savetxt(data_dir+'\\'+datetime.now().strftime('%Y%m%d')+"/"+datetime.now().strftime('%H%M%S')+file_name,outarray, delimiter='\t')
    