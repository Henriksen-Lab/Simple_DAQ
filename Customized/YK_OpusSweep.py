# -*- coding: utf-8 -*-


import numpy as np
from datetime import datetime
import time, sys, os, pyvisa, subprocess
# import matplotlib as mpl
# import matplotlib.pyplot as plt

current_directory = os.path.dirname(os.path.abspath(__file__))
main_directory = os.path.dirname(current_directory) 
if main_directory not in sys.path:
    sys.path.append(main_directory)
from Instrument_Drivers.Opus import get_opus_data
from Instrument_Drivers.Instrument_dict import *
rm = pyvisa.ResourceManager()


my_note = ''

def my_form(kwargs):
    if 'Opus' in kwargs.keys():
        lens = len(kwargs['Opus'].x)
    else:
        lens = 1
    list = []
    dataToSave = []
    for key in kwargs:
        if key=='Opus':
            data = kwargs[key]
            dataToSave += [data.x]
            dataToSave += [data.y]
            list += ['Opus_Wavenum', 'Opus_Intensity']
        else:
            dataToSave += [np.full(lens, kwargs[key])]
            list += [key]
    data = np.column_stack(dataToSave)
    axis = ''
    for x in list:
        axis += f"{x}_{order}\t\t\t"
    return data, axis


'''---------------------Run funcs---------------------'''
def get_sweep(start,stop,step_size):
    num_steps = int((abs(float(start) - float(stop)) / float(step_size))) + 1
    list = np.linspace(float(start), float(stop), num_steps)
    return np.append(list,stop)

def run_single(sweep,order,name=None):
    msg = f'TG{sweep[0]:0.3f}_BG{sweep[1]:0.3f}'
    msg = msg.replace('.','p')
    msg = msg.replace('-','m')
    savefile_name = name + '_' + msg + f'.{order}' + '.dpt'
    print(f"{datetime.now().strftime('%Y.%m.%d')}", " ", f"{datetime.now().strftime('%H:%M:%S')}", f'TG = {sweep[0]:0.3f} V, BG = {sweep[1]:0.3f} V', "", "started")
    vs = get_opus_data()
    value = {}
    value.update({'Opus':vs})
    data, axis = my_form(value)
    # Just to prevent you overwite the file with order already exist
    file_real_path = Save_folder + '\\' + savefile_name
    os.makedirs(Save_folder, exist_ok=True)
    while os.path.exists(file_real_path):
        order = order + 1
        savefile_name = name + '_' + msg + f'.{order}' + '.dpt'
        file_real_path = Save_folder + '\\' + savefile_name
    #
    np.savetxt(file_real_path, data, delimiter='\t',
               header=f"{datetime.now().strftime('%Y%m%d')}" + " " + f"{datetime.now().strftime('%H%M%S')}" + '\n' + f"{axis}")
    print(savefile_name + '' + ' recorded')

def dry_sweep(start, stop, step_size, delay=0.9, flag=None):
    # print(f"{datetime.now().strftime('%Y.%m.%d')}", " ", f"{datetime.now().strftime('%H:%M:%S')} ", 'Sweep started from:')
    sweep = get_sweep(start, stop, step_size)
    for each in sweep:
        set(each,delay=delay,flag=flag)
    # print(f"{datetime.now().strftime('%Y.%m.%d')}", " ", f"{datetime.now().strftime('%H:%M:%S')} ", 'Sweep ended at :')
    return each

def wet_sweep(TG, BG, TG_Step_size, BG_Step_size, TG_Sweep_rate, BG_Sweep_rate, Scan_per_Set, order ,dry_delay=0.9, wet_delay=0.01):
    last_v = read()
    TG_sweep = get_sweep(start=last_v[0],stop=TG,step_size=TG_Step_size)
    BG_sweep = get_sweep(start=last_v[1],stop=BG,step_size=BG_Step_size)
    for each_TG in TG_sweep:
        last_v[0] = dry_sweep(last_v[0], each_TG, step_size=TG_Sweep_rate,flag='TG', delay=dry_delay)
        time.sleep(wet_delay)
    for each_BG in BG_sweep:
        last_v[1] = dry_sweep(last_v[1], each_BG, step_size=BG_Sweep_rate,flag='BG', delay=dry_delay)
        time.sleep(wet_delay)
    for i in range(Scan_per_Set):
        run_single([TG,BG], order=order, name= name)
        # print(TG,BG,order)
        order += 1
    return order


'''---------------------Start your Measurement here---------------------'''
# define the program for each sweep
def set(value, delay=0.9,flag=None):
    global msmt_flag
    if value is not None:
        if msmt_flag == 'Double Gate Sweep, Both Gates use Keithley2400':
            if flag == 'TG':
                keithley2400_set_sour_voltage_V(TG_keithley2400_gpib, value)
            if flag == 'BG':
                keithley2400_set_sour_voltage_V(BG_keithley2400_gpib, value)
        elif msmt_flag == 'Double Gate Sweep, Both Gates use DC205':
            if flag == 'TG':
                dc205_set_sour_voltage_V(TG_DC205, value)
            if flag == 'BG':
                dc205_set_sour_voltage_V(BG_DC205, value)
        time.sleep(delay)
    time.sleep(0.1)

def read():
    global msmt_flag
    if msmt_flag == 'Double Gate Sweep, Both Gates use Keithley2400':
        TG_read = keithley2400_get_sour_voltage_V(TG_keithley2400_gpib)
        BG_read = keithley2400_get_sour_voltage_V(BG_keithley2400_gpib)
        return [TG_read, BG_read]
    elif msmt_flag == 'Double Gate Sweep, Both Gates use DC205':
        TG_read = dc205_get_sour_voltage_V(TG_DC205)
        BG_read = dc205_get_sour_voltage_V(BG_DC205)
        return [TG_read, BG_read]
    
run_flag = True
'''---------------------INPUT BEFORE RUN---------------------'''

# Instruments info
TG_keithley2400_gpib = 'GPIB0::25::INSTR'
BG_keithley2400_gpib = 'GPIB0::24::INSTR'
TG_DC205 = ''
BG_DC205 = ''

# Sweep Params
TG_background = 3.6 # unit: V
BG_background = 0.158 # unit: V
TG_set = [0,1.8] # unit: V
BG_set = [0,0.158] # unit: V
# Scan_per_Set: Num of Opus scans per set of voltages
Scan_per_Set = 5 # Integer
# Sets_per_voltage: Num of loops(background and set) per set of voltages
Sets_per_voltage = 40 # Integer

TG_Sweep_rate = 500E-3 # unit: V/s
TG_Step_size = 100E-3 # unit: V
BG_Sweep_rate = 200E-3 # unit: V/s
BG_Step_size = 20E-3 # unit: V

Save_folder = r'C:\Users\Henriksen Lab\Desktop\IR data\Ttlg09092024\R1\B0T\n0_D0_Diamond_Si_LPF\11042024'
name = 'YK110424'
order = 0

'''Check params'''
if len(TG_set)-len(BG_set)!=0 :
    run_flag = False
    print('The Voltage don\'t match')

'''Double Gate'''
msmt_flag = 'Double Gate Sweep, Both Gates use Keithley2400'
# msmt_flag = 'Double Gate Sweep, Both Gates use DC205'
for i in range(len(TG_set)):
    TG = TG_set[i]
    BG = BG_set[i]
    for j in range(Sets_per_voltage):
        new_order = wet_sweep(TG, BG, TG_Step_size, BG_Step_size, TG_Sweep_rate, BG_Sweep_rate, Scan_per_Set, order, wet_delay=0.01)
        new_order = wet_sweep(TG_background, BG_background, TG_Step_size, BG_Step_size, TG_Sweep_rate, BG_Sweep_rate, Scan_per_Set, order, wet_delay=0.01)
        order = new_order




