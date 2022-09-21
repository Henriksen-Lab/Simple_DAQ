# -*- coding: utf-8 -*-
"""
@author: Shilling Du
@date: Aug 10, 2022
"""

import numpy as np
from datetime import datetime
import time, sys, os, pyvisa
folder_path = os.getcwd()
if folder_path not in sys.path:
    sys.path.append(folder_path) # easier to open driver files as long as Simple_DAQ.py is in the same folder with drivers
from Instrument_Drivers.vna_analysis import *
from Instrument_Drivers.SR830 import *
from Instrument_Drivers.keithley import *
from Instrument_Drivers.hp34461A import *
from Instrument_Drivers.PicoVNA108 import *

class Mydata:
    def __init__(self):
        self.variable_name_list = []
        self.instrument_address_list = []
        self.instrument_name_list = []
        self.func_list = []
        self.timestamp = []
        self.data = dict.fromkeys(self.variable_name_list,[])
        self.data['timestamp'] = []


    def add_instrument(self,instrument_info={
        'variable_name': [],
        'instrument_address': [],
        'instrument_name': [],
        'function':[],
        'f_min':0.3,
        'f_max':8500,
        'points':1001,
        'power':0,
        'bandwidth':1000,
        'average':1
      }):
        self.variable_name_list += [variable_name]
        self.instrument_address_list += [instrument_address]
        self.instrument_name_list += [instrument_name]
        self.func_list += [func]
        
        self.f_min = float(f_min)
        self.f_max = float(f_max)
        self.points = int(points)
        self.power = float(power)
        self.bandwidth = float(bandwidth)
        self.average = int(average)
        print("updated")
        for i in range (0,len(self.variable_name_list)):
            print(i,".   ","Measurement setup for:", self.variable_name_list[i],", at address:", self.instrument_address_list[i]
                  ,", through instrument:",self.instrument_name_list[i],', Func:',self.func_list[i])


    def update(self):
        self.timestamp += [time.time()]
        for i in range(0,len(self.variable_name_list)):
            self.data[i] += [get_variable(address=self.instrument_address_list[i],name=self.instrument_name_list[i],
                                          func=self.func_list[i])]
    def data_save(self,data_dir = os.getcwd(),file_name='name me please',my_note='', order=1):
        axis = f"timestamp_{order}\t\t\t\t"
        for x in self.variable_name_list:
            axis += f"{x}_{order}\t\t\t\t"
        dataToSave = np.r_[[self.timestamp],self.data].T
        os.makedirs(data_dir + '\\data'+ '\\' + datetime.now().strftime('%Y%m%d') , exist_ok=True)
        file_name = file_name +f"_{order}"
        np.savetxt(data_dir + '\\data'+ '\\' + datetime.now().strftime('%Y%m%d') + "/" + file_name, dataToSave,
                   delimiter='\t',
                   header=f"{datetime.now().strftime('%Y%m%d')}" + " " + f"{datetime.now().strftime('%H%M%S')}" + '\n' + my_note + '\n' + f"{axis}")
        self.data=[]

    def read_and_save_for_VNA_involved(self,data_dir = os.getcwd(),file_name='name me please',my_note='', order=1):
        constant_list = [time.time()]
        for i in range(0, len(self.variable_name_list)):
            if self.variable_name_list[i] == 'PicoVNA108':
                # expecting func choosing from S11, S12, S21,S22
                self.data_VNA = get_picoVNA_smith(port=self.func,f_min=self.f_min,f_max=self.f_max,number_of_points=self.points
                                                  ,power=self.power,bandwidth=self.bandwidth,Average=self.average)
            elif self.variable_name_list[i] == 'vna':
                change_vna_settings(vna_start_freq_GHz=self.f_min, vna_end_freq_GHz=self.f_max, vna_power_dBm=self.power,
                                    dwell_sec=1/self.bandwidth, num_freq=self.points, vna_gpib=self.instrument_address_list[i])
                self.data_VNA = get_smith_data(self.instrument_address_list[i])
            else:
                constant_list += [get_variable(address=self.instrument_address_list[i],name=self.instrument_name_list[i],
                                          func=self.func_list[i])]
        self.data = myform(self.data_VNA, constant_list)

        axis = "freqs\t\t\t\t" + "log_mag\t\t\t\t"+"phase_rad\t\t\t\t"+"real\t\t\t\t"+"imag\t\t\t\t"
        axis += f"timestamp\t\t\t\t"
        for x in self.variable_name_list:
            if x!='PicoVNA108' and x!='vna':
                axis += f"{x}\t\t\t\t"
        dataToSave = self.data
        file_name = file_name + f"_{order}"
        os.makedirs(data_dir + '\\data' + '\\' + datetime.now().strftime('%Y%m%d') + '_' , exist_ok=True)
        np.savetxt(data_dir + '\\data' + '\\' + datetime.now().strftime('%Y%m%d') + '_' + "/" + file_name,
                   dataToSave, delimiter='\t', header=f"{datetime.now().strftime('%Y%m%d')}" + " " +
                                                      f"{datetime.now().strftime('%H%M%S')}" + '\n' + my_note + '\n' + f"{axis}")


def myform(smith, constantlist):
    lens = len(smith.freqs)
    for i in range(0,len(constantlist)):
        constantlist[i] = np.full(lens,constantlist[i])
    data = np.column_stack((smith.freqs, smith.log_mag, smith.phase_rad, smith.real, smith.imag, np.array(constantlist).T))
    return data

def get_variable(address='',name='',func=''):
    if name == 'keithley':
        if func == '2000ohm_4pt':
            value = keithley2000_get_ohm_4pt(address)
        elif func == '2400ohm_4pt':
            value = keithley2400_get_ohm_4pt(address)
        elif func == '2000volt':
            value = keithley2000_get_voltage_V(address)

    elif name == 'SR830':
        if func == 'x':
            value = SR830_get_x(address)
        elif func == 'y':
            value = SR830_get_y(address)
        elif func == 'R':
            value = SR830_get_R(address)
        elif func == 'theta':
            value = SR830_get_Theta(address)
        elif func == 'freq':
            value = SR830_get_frequency(address)

    elif name == 'hp34461A':
        if func == 'volt':
            value = hp34461a_get_voltage(address)
        elif func == 'ohm_4pt':
            value = hp34461a_get_ohm_4pt(address)
    else:
        value = 0
        print('Please input correct instrument name or function name')
    return value


# data = Mydata()
#
# #print(data.variable_name_list,data.instrument_address_list,data.instrument_name_list,data.func_list)
#
# data.update()
# data.update()

#data.data_save()
