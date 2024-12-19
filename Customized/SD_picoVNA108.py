# -*- coding: utf-8 -*-
"""
Created on Tues Feb 8 16:17:58 2022

@author: Shilling Du
@date: Feb 8, 2022
"""

# use Python 32bit for PicoVNA108


import numpy as np
from datetime import datetime
import time, sys, os, pyvisa, subprocess
# import matplotlib as mpl
# import matplotlib.pyplot as plt

current_directory = os.path.dirname(os.path.abspath(__file__))
main_directory = os.path.dirname(current_directory) 
if main_directory not in sys.path:
    sys.path.append(main_directory)
from Instrument_Drivers.PicoVNA108 import get_picoVNA_smith
from Instrument_Drivers.Instrument_dict import *
rm = pyvisa.ResourceManager()

# subprocess.call(['sh','SD_pywin32error.sh'])
# this command delete r'C:\Users\<username>\AppData\Local\Temp\2\gen_py' to solve a potential pywin32 error that usually happens after you use the PICOVNA 3 program
global msmt_flag, my_note
msmt_flag = None
my_note = ''

def my_form(kwargs):
    if 'smith' in kwargs.keys():
        lens = len(kwargs['smith'].freqs)
    else:
        lens = 1
    list = []
    dataToSave = []
    for key in kwargs:
        if key=='smith':
            smith = kwargs[key]
            dataToSave += [smith.freqs]
            dataToSave += [smith.log_mag]
            dataToSave += [smith.phase_rad]
            dataToSave += [smith.real]
            dataToSave += [smith.imag]
            list += ['VNA_freqs', 'VNA_log_mag', 'VNA_phase_rad', 'VNA_real', 'VNA_imag']
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

def run_single(sweep,order,f_min,f_max,average=250,power=-5,name=None,number_of_points=1001,bandwidth=1000):
    global my_note
    save_my_note = my_note
    set(sweep)
    value = read()
    avg = f"\n average for {average} times"
    print(f"{datetime.now().strftime('%Y.%m.%d')}", " ", f"{datetime.now().strftime('%H:%M:%S')}", "  ",
          order, " . started")
    msg = 'VNA data for'
    for key, item in value.items():
        msg += f" {key}={item}, "
    time.sleep(0.5)
    vs = get_picoVNA_smith(port=port, f_min=f_min, f_max=f_max, number_of_points=number_of_points, power=power, bandwidth=bandwidth, Average=average)
    time.sleep(0.5)
    print(msg+' recorded')
    value.update({'smith':vs})
    data, axis = my_form(value)
    if name is not None:
        file_name = f"{name}.{order}"
    else:
        file_name = f"{title}.{order}"
    file_real_path = data_dir + '\\' + datetime.now().strftime('%Y%m%d') + "\\" + file_name
    while os.path.exists(file_real_path):
        order = order + 1
        file_name = ''.join(file_name.split('.')[:-1]) + f'.{order}'
        file_real_path = data_dir + '\\' + datetime.now().strftime('%Y%m%d') + "\\" + file_name
    os.makedirs(data_dir + '\\' + datetime.now().strftime('%Y%m%d'), exist_ok=True)
    save_my_note += avg + ', power=' + f'{power}' + ', bandwidth=' + f'{bandwidth}' + '\n'
    np.savetxt(file_real_path, data, delimiter='\t',
               header=f"{datetime.now().strftime('%Y%m%d')}" + " " + f"{datetime.now().strftime('%H%M%S')}" + '\n' + \
                      save_my_note + f"{axis}")
    

def dry_sweep(start, stop, step_size=0.01, delay=0.9):
    print(f"{datetime.now().strftime('%Y.%m.%d')}", " ", f"{datetime.now().strftime('%H:%M:%S')} ", 'Sweep started from:')
    read()
    for sweep in get_sweep(start=start, stop=stop, step_size=step_size):
        sweep = round(sweep,ndigits=4)
        set(sweep,delay=delay)
        value = read(printable=False)
        data, axis = my_form(value)
        os.makedirs(data_dir + '\\' + datetime.now().strftime('%Y%m%d') + "\\" +title, exist_ok=True)
        dry_sweep_real_path = data_dir + '\\' + datetime.now().strftime('%Y%m%d') + "\\" + title + "\\" + title + '_dry_sweep'
        if not os.path.exists(dry_sweep_real_path):
            np.savetxt(dry_sweep_real_path,data,delimiter='\t',
                       header=f"{datetime.now().strftime('%Y.%m.%d')}" + " " + f"{datetime.now().strftime('%H:%M:%S')}" +
                              '\n' + f"{axis}")
        else:
            with open(dry_sweep_real_path, "ab") as f:
                np.savetxt(f, data, delimiter='\t')
    print(f"{datetime.now().strftime('%Y.%m.%d')}", " ", f"{datetime.now().strftime('%H:%M:%S')} ", 'Sweep ended at :')
    read()
    return sweep

def wet_sweep(start, stop, step_size, order, last_v, f_min, f_max, number_of_points=1001, power=-5, average=250, dry_step_size=0.01, dry_delay=0.9, wet_delay =0.01, duplicate=1):
    for sweep in get_sweep(start=start, stop=stop, step_size=step_size):
        last_v = dry_sweep(last_v, sweep, step_size=dry_step_size, delay=dry_delay)
        time.sleep(wet_delay)
        for i in range(duplicate):
            order += 1
            run_single(sweep, order, f_min=f_min, f_max=f_max, average=average, power=power, number_of_points=number_of_points)
            last_v = sweep
    return last_v

'''---------------------INPUT BEFORE RUN---------------------'''

# keithley2400_gpib = 'GPIB0::25::INSTR'
keithley2000_gpib = 'GPIB0::18::INSTR'
# keithley2230_gpib = 'GPIB0::1::INSTR'
# dc205_address = 'COM3'
SR830 = 'GPIB0::7::INSTR'
# SR124 = 'ASRL5::INSTR'
# multi_Temp = 'USB0::0x0957::0x4918::MY59170002::INSTR'
# multi_Field = 'USB0::0x0957::0x4918::MY60480007::INSTR'
# hp34461a = 'GPIB0::22::INSTR'
keithley2450_gpib = 'GPIB0::28::INSTR'
keithley2230_gpib = 'USB0::0x05E6::0x2230::805226014786970006::INSTR'
port ='S21'

'''---------------------Start your sequence here---------------------'''
# define the program for each sweep
def set(value, delay=0.9):
    global msmt_flag
    if value is not None:
        if msmt_flag =='AC B wiggle':
            SR830_set_frequency(SR830, 10000)
            SR830_set_amplitude(SR830, value)
        if msmt_flag =='DC sweep Gate, 2400':
            keithley2400_set_sour_voltage_V(keithley2400_gpib, value)
        if msmt_flag =='DC sweep Gate, 2450':
            keithley2450_set_sour_voltage_V(keithley2450_gpib, value)
        if msmt_flag == 'DC sweep Gate, 2230':
            keithley2230_CH2_Set_voltage(keithley2230_gpib, value)
            # keithley2230_CH3_Set_voltage(keithley2230_gpib, value)
        if msmt_flag == 'DC sweep Gate, DC205':
            dc205_set_sour_voltage_V(dc205_address, value)
        if msmt_flag =='DC+AC sweep gate':
            SR124_set_amplitude(SR124, value)
        time.sleep(delay)
    time.sleep(0.1)

def read(printable=True,*arg):
    global msmt_flag
    read = {}
    read.update({'timestamp': time.time()})
    if msmt_flag =='Power scan':
        read.update({'power': arg[0]})
    if msmt_flag =='AC B wiggle':
        read.update({'freq': SR830_get_frequency(SR830)})
        read.update({'wiggle_B': SR830_get_amplitude(SR830)})
    if msmt_flag =='DC sweep Gate, 2400':
        read.update({'v_sur': keithley2400_get_sour_voltage_V(keithley2400_gpib)})
    if msmt_flag == 'DC sweep Gate, 2230':
        # read.update({'v_sur': (-1) * keithley2230_CH3_Fetch_voltage(keithley2230_gpib)})
        # read.update({'i_sur': (-1) * keithley2230_CH3_Fetch_current(keithley2230_gpib)})
        read.update({'v_sur': keithley2230_CH2_Fetch_voltage(keithley2230_gpib)})
        read.update({'i_sur': keithley2230_CH2_Fetch_current(keithley2230_gpib)})
    if msmt_flag == 'DC sweep Gate, DC205':
        read.update({'v_sur': dc205_get_sour_voltage_V(dc205_address)})
    if msmt_flag =='DC+AC sweep gate':
        read.update({'vg_bias': SR124_get_DCbias(SR124)})
        read.update({'vg_freq': SR124_get_frequency(SR124)})
        read.update({'vg_Vrms': SR124_get_amplitude(SR124)})
    if msmt_flag == 'Read RuOx':
        read.update({'R_RuOx': hp34461a_get_ohm_4pt(hp34461a)})
    if msmt_flag == 'Read Si diode':
        read.update({'V_diode': keithley2450_get_volt_4pt(keithley2450_gpib)})
        read.update({'V_x':SR830_get_x(SR830)})
        read.update({'V_y':SR830_get_y(SR830)})
    if msmt_flag == 'Read Temp and Field from PPMS':
        read.update({'V_T': U2741A_get_voltage(multi_Temp)})
        read.update({'V_B': U2741A_get_voltage(multi_Field)})
    if msmt_flag == 'DC sweep Gate, 2450':
        read.update({'V_SiDiode': keithley2000_get_diodeV(keithley2000_gpib)})
        read.update({'Vbg':keithley2450_get_sour_voltage_V(keithley2450_gpib)})
        read.update({'I_leak':keithley2450_get_meas_currrent_A(keithley2450_gpib)})
        read.update({'V_x':SR830_get_x(SR830)})
        read.update({'V_y':SR830_get_y(SR830)})
        read.update({'V_heater':keithley2230_CH1_Fetch_voltage(keithley2230_gpib)})
        read.update({'I_heater':keithley2230_CH1_Fetch_current(keithley2230_gpib)})
    if msmt_flag == 'manual':
        # read.update({'Vtg': 0.73})
        pass
    if printable:
        msg = ''
        for key, item in read.items():
            msg += f'{key}={item}, '
        print(msg)
    return read


'''AC wiggle B'''
# msmt_flag ='AC B wiggle'
# data_dir = r'C:\Users\ICET\Desktop\Data\SD\20231107_SD012_ICET\Wiggle_B'
# my_note = "2023.11.07 Icet SD_012 base temp"
#
# # # centers =  [6080, 6220, 6610, 7089] #sd004_1
# # # centers =  [6033, 6335, 6620, 7104] #sd003a
# # # 6107, 6462, 7172, 7577, 7876, 8029] #sd008
# # centers = [3980, 4070, 4340, 4550] #sd009
#
# start_freq_list = [5600]
# stop_freq_list = [7500]
#
# # for center in centers:
# #     start_freq_list += [center-40]
# #     stop_freq_list += [center+20]
#
# last_v = 0.004
# for index in range(len(start_freq_list)):
#     title = f"sweep_B_{start_freq_list[index]}to{stop_freq_list[index]}MHz" # some unique feature you want to add in title
#     order = 0
#     last_v = wet_sweep(start=last_v,
#                        stop=4.504,
#                        step_size=1.5,
#                        order=order,
#                        last_v=last_v,
#                        f_min=start_freq_list[index],
#                        f_max=stop_freq_list[index],
#                        power=-5)
#     last_v = dry_sweep(last_v,0.004)
# SR830_set_frequency(SR830, 17.777)
# print('done')

'''Power scan'''
# msmt_flag ='Power scan'
# data_dir = r'C:\Users\ICET\Desktop\Data\SD\20230612_SD_008_MoRe2'
# my_note = "2023.06.15 Icet sd008_MoRe2 warm up"

# power_list = [-20,-15,-10,-5,0,5]
# for index in range(len(power_list)):
#     title = f"sweep_power_{power_list[index]}dBm" # some unique feature you want to add in title
#     order = 0
#     for i in range(2):
#         run_single(None,order,f_min=5500,f_max=8500,power=power_list[index])
# print('done')

'''DC sweep Gate'''
# # msmt_flag ='DC sweep Gate, 2400'
# msmt_flag ='DC sweep Gate, 2230'
# # msmt_flag ='DC sweep Gate, DC205'
# data_dir = r'C:\Users\ICET\Desktop\Data\SD\20240407_SD013_Compare_ICET\DC_gate_sweep_broad_fine'
# my_note = "2024.04.09 Icet sd013"
# last_v = 0
# order = 0
# title = f"1c" # some unique feature you want to add in title
# last_v = dry_sweep(last_v,0.03)
# last_v = wet_sweep(start=last_v,
#                    stop=0.73,
#                    step_size=0.1,
#                    order=order,
#                    last_v=last_v,
#                    f_min=6.210e3,
#                    f_max=6.710e3,
#                    average=250,
#                    dry_step_size=0.01,
#                    dry_delay=1)
# last_v = dry_sweep(last_v,0)
# print('done')

# last_v = 0
# order = 0
# title = f"1c_longavg" # some unique feature you want to add in title
# last_v = dry_sweep(last_v,0.575,step_size=0.01, delay=0.9)
# for i in range(5):
#     run_single(sweep=None, order=order, f_min=3000, f_max=8500, average=250, power=-5)
#     order += 1
# last_v = dry_sweep(last_v,1.5,step_size=0.01, delay=0.9)
# for i in range(5):
#     run_single(sweep=None, order=order, f_min=3000, f_max=8500, average=250, power=-5)
#     order += 1
# last_v = dry_sweep(last_v,0)
# print('done')

'''DC+AC sweep gate'''
# msmt_flag ='DC+AC sweep gate'
# data_dir = r'C:\Users\ICET\Desktop\Data\SD\20230612_SD_008_MoRe2'
# my_note = "2023.06.15 Icet sd008_MoRe2 warm up"

# def bias_sweep(start,stop,stepsize=0.001):
#     for bias in get_sweep(start=start, stop=stop, step_size=stepsize):
#         SR124_set_DCbias(SR124, bias)
#     print(f'bias set to {bias}')
#     return bias
#
#
# order = 0
# last_bias = SR124_get_DCbias(SR124)
# last_v = SR124_get_amplitude(SR124)
#
# for bias in get_sweep(0,1.25,0.05):
#     last_bias = bias_sweep(last_bias,bias)
#     title = f"DC_bias_{last_bias}V"  # some unique feature you want to add in title
#     last_v = wet_sweep(start=0.01,
#                        stop=0.71,
#                        step_size=0.05,
#                        order=order,
#                        last_v=last_v,
#                        f_min=4000,
#                        f_max=7200)
#     last_v = dry_sweep(last_v,0.01)
# bias_sweep(last_bias,0)
# print('done')

# dry_sweep(0.7,0.01)

'''Record temp'''
# msmt_flag = 'Read RuOx'
# data_dir = r'C:\Users\ICET\Desktop\Data\SD\20231111_SD012_AfterFIB_ICET\warmup'
# my_note = "2023.12.07 Icet sd012_afterfib warm up"
#
# order = 0
# title = 'warmup'
# while 1:
#     run_single(sweep=None,order=order,f_min=3000,f_max=8500,average=3,power=-5)
#     order += 1

# msmt_flag = 'Read Si diode'
# data_dir = r'C:\Users\Crow108\Documents\Data\SD\20241127_YBCO_test\1_Cooling_down'
# my_note = "sample: AFMR_YBCO_E, VNA1--20dB--3dB-DC bias tee-0dB-Cable-0dB-Ecosorb filter-DC bias Tee-Circulator-HEMT--3dB-VNA2\nsource 0.05V from sr830 on 1Mohm for V_ybco, read Si diode for temp"

# order = 0
# title = 'Coolingdown'
# while 1:
#     run_single(sweep=None,order=order,f_min=1000,f_max=8500,average=10,power=-5)
#     order += 1

'''Take trace_manual'''
# msmt_flag = 'manual'
# data_dir = r'C:\Users\Crow108\Documents\Data\SD\20241127_YBCO_test\0_Calibration_rmtemp'
# my_note = "VNA1-Sample puck(AFMR_YBCO_E)-VNA2 "
# order = 1
# title = "check_sample_puck" # some unique feature you want to add in title
# run_single(sweep=None,order=order,f_min=1000,f_max=8000,average=10,power=-5,number_of_points=1001)
# while 1:
#     run_single(sweep=None,order=order,f_min=3000,f_max=8500,average=3,power=-5)

'''Take temp and field'''
# msmt_flag = 'Read Temp and Field from PPMS'
# data_dir = r'C:\Users\Henriksen Lab\Desktop\Data\KZ\20231027_KZ_AFMFMR001_PPMS'
# my_note = "2023.10.27 Kaiwen's AFMFMR device, RuCl3 kapton tape on thermal Evapped Al CPW(100nm, wet etch) on Intrinsic Si wafer\n T = V_T/10*150 + 150\n B = V_B/10"
# order = 1
# title = "SweepTandB_3kTo8p5G" # some unique feature you want to add in title
# while 1:
#     run_single(sweep=None,order=order,f_min=0.3,f_max=8500,average=5,power=0,number_of_points=1001,bandwidth=300)
#     time.sleep(15)
#     order += 1

'''Take temp and S21 and sweep gate'''
msmt_flag = 'DC sweep Gate, 2450'
data_dir = r'C:\Users\Crow108\OneDrive\Documents\Data\SD\20241216_SDgPD007\4_cool_lowPower\temp'
my_note = "2024.12.17 Icet SDgPD007 basetemp, 0.05V on 1Mohm measure voltage drop on graphene, sweep gate[-0.4V,0.0V], 1mV/1s, put 20dB attenuator at input, also turned down the power from -5dB to -15dB"
order = 0

# heater_V_list = np.linspace(14,0,15)
# print(heater_V_list)

# def Check_stable():
#     print('Start waiting')
#     unstable_flag = True
#     while unstable_flag:
#         old_V = keithley2000_get_diodeV(keithley2000_gpib)
#         time.sleep(60)
#         new_V = keithley2000_get_diodeV(keithley2000_gpib)
#         if abs(old_V-new_V)<1e-4:
#             time.sleep(60)
#             unstable_flag = False
#             print('Stable')

# for each_heater_v in heater_V_list:
#     message = ''
#     now = time.time()
#     keithley2230_CH1_Set_voltage(keithley2230_gpib, float(each_heater_v))

    # Check_stable()
    # title = f"Heatup_1mvs_{each_heater_v:0.0f}V" # some unique feature you want to add in title
    # last_v = keithley2450_get_sour_voltage_V(keithley2450_gpib)
    # last_v = dry_sweep(start=last_v, stop=-0.25, step_size=0.001, delay=1)
    # last_v = wet_sweep(start=last_v,
    #                 stop=-0.05,
    #                 step_size=0.005,
    #                 order=order,
    #                 last_v=last_v,
    #                 f_min=1000,
    #                 f_max=8000,
    #                 number_of_points=1001,
    #                 average=1,
    #                 dry_step_size=0.005,
    #                 dry_delay=1,
    #                 power=-15
    #                 )
    # then = time.time()
    # message += f'cycle: {int(then-now)} sec\n'
    #     # runs += 1
    # print(message)
title = '0'
last_v = keithley2450_get_sour_voltage_V(keithley2450_gpib)
last_v = dry_sweep(start=last_v, stop=0, step_size=0.001, delay=1)

# my_note = '2024.07.14 Icet SDgPD002 basetemp, 0.1V on 1Mohm measure voltage drop on graphene, at -9.1V warm up'
# order = 0
# title = f"Warmup_VDP_compressorOFF_prepare_1" # some unique feature you want to add in title
# # last_v = keithley2450_get_sour_voltage_V(keithley2450_gpib)
# # last_v = dry_sweep(start=last_v, stop=0, step_size=0.01, delay=1)
# # last_v = wet_sweep(start=last_v,
# #                 stop=10,
# #                 step_size=0.1,
# #                 order=order,
# #                 last_v=last_v,
# #                 f_min=1000,
# #                 f_max=8000,
# #                 number_of_points=101,
# #                 average=1,
# #                 dry_step_size=0.01,
# #                 dry_delay=1)
# # last_v = wet_sweep(start=last_v,
# #                 stop=-9,
# #                 step_size=0.1,
# #                 order=order,
# #                 last_v=last_v,
# #                 f_min=1000,
# #                 f_max=8000,
# #                 number_of_points=101,
# #                 average=1,
# #                 dry_step_size=0.01,
# #                 dry_delay=1)
# print('Turn off Compressor now')
# # time.sleep(30)
# title = f"Warmup_VDP_compressorOFF_1" # some unique feature you want to add in title
# while hp34461a_get_ohm_4pt(hp34461a)>1010:
#     run_single(sweep=None,order=order,f_min=1000,f_max=8000,average=3,power=-5,number_of_points=1001)
# # last_v = keithley2450_get_sour_voltage_V(keithley2450_gpib)
# # last_v = dry_sweep(start=last_v, stop=0, step_size=0.01, delay=1)
# print('done')