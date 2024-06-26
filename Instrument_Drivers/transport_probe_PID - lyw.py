# Written by Yiwei Le 9/26/2023
import sys, os, time, threading, tkinter
import numpy as np
from decimal import Decimal
import matplotlib.pyplot as plt

folder_path = os.getcwd()
if folder_path not in sys.path:
    sys.path.append(
        folder_path)  # easier to open driver files as long as Simple_DAQ.py is in the same folder with drivers
from Instrument_Drivers.thermometer.SiDiode import get_T_SiDiode#!!!!
from Instrument_Drivers.thermometer.Cernox import get_T_cernox_3
from Instrument_Drivers.hp34461A import hp34461a_get_ohm_4pt#!!!!
from Instrument_Drivers.hp34461A import hp34461a_get_voltage
from Instrument_Drivers.keithley2230G_30_1 import *
from Instrument_Drivers.keithley import keithley2000_get_ohm_4pt
'''-------------------------------------------------------Main------------------------------------------------------'''

def output_cal(setpoint_value, now_value, time_interval, kp, ki, kd, lastErr, lastErr_2):
    err = float(setpoint_value) - float(now_value)
    output =  kp * (err - lastErr) + ki * err * time_interval + kd * (err - 2 * lastErr + lastErr_2) / time_interval
    output = min(max(output, 0), 1)
    return (output, err, lastErr)

def run_r_vs_T():
    address = 'GPIB::17::INSTR'#!!!!
    address2 = 'GPIB::1::INSTR'
    err = 0.0 #initial error(0)
    lastErr = 0. #initial err(-1)
    lastErr_2 = 0.0 #initial err(-2)
    now_value = get_T_cernox_3(hp34461a_get_ohm_4pt(address)) #current temp #!!!!
    time_interval = 1 #change input voltage every ...s
    kp = [0, 0.2, 0.2, 0.4, 0.4, 7, 7, 15, 15, 25, 25, 25, 25, 25, 25, 25, 25]
    ki = [0, 1, 1.5, 1.5, 15, 15, 15, 15, 20, 25, 25, 25, 25, 25, 25, 25, 25] # ki for 5-100 K#!!!!
    kd = [0, 0.5, 1, 3.5, 4.5, 4.5, 4.5, 4.5, 5, 5, 5, 5, 5, 5, 5, 5, 5]  # kd for 20-100 K#!!!!
    V_in = [0, 0.8, 1, 1.6, 2.5, 3, 4, 4.25, 4.5, 4.75, 5.25, 6, 7.5, 8.5, 9, 10]  # input voltage for 5-100 K#!!!!
    setpoint = [0, 5, 7.5, 10, 15, 20, 30, 40, 50 ,60, 70, 80, 100, 120, 150, 200] # !!!!
    timestamp = [] #record time of set temp change
    set_temp = [] #record set temp
    reach_temp = []
    data_path_init = r'C:\Users\ICET\Desktop\Data\lyw\20240424\r_vs_t_temp'#!!!
    for i in range(0,len(setpoint)):
        time_temp = []
        reach_temp_total = []
        reach_temp_temp = []
        timestamp.append(time.time())
        setpoint_value = setpoint[i]
        set_temp.append(setpoint_value)
        j = 0  # record time
        print('!!!!')
        print(setpoint_value)
        if i < 6:
            Time_wait = 1800
        elif i < 10:
            Time_wait = 3600
        elif i < 13:
            Time_wait = 5400
        else :
            Time_wait = 9000
        while j < Time_wait:
            values = output_cal(setpoint_value, now_value, time_interval, kp[i], ki[i], kd[i], lastErr, lastErr_2)
            p = values[0]
            lastErr = values[1]
            lastErr_2 = values[2]
            keithley2230_CH1_Set_voltage(address2, V_in[i]*p)
            time.sleep(time_interval)
            now_value = get_T_cernox_3(hp34461a_get_ohm_4pt(address))
            print(p, lastErr, lastErr_2, now_value)
            j += 1
            reach_temp_total.append(now_value)
            time_temp.append(time.time())
            if j > Time_wait*0.75:
                reach_temp_temp.append(now_value)
        data_path=data_path_init+'_'+str(setpoint_value)+'.txt'
        with open(data_path,'w') as f:
            f.write('{:<20}{:<20}\n'.format('temp','time'))
            for i in range(0,len(reach_temp_total)):
                f.write('{:<20}{:<20}\n'.format(reach_temp_total[i], time_temp[i]))
            f.close()
        reach_temp.append(sum(reach_temp_temp)/len(reach_temp_temp))
        timestamp.append(time.time())
    keithley2230_CH1_Set_voltage(address2, 0)
    print(set_temp)
    print(reach_temp)
    print(timestamp)

def run_one_temp():
    address = 'GPIB::17::INSTR'
    #address = 'GPIB::18::INSTR'
    address2 = 'GPIB::1::INSTR'
    err = 0.0  # initial error(0)
    lastErr = 0.0  # initial err(-1)
    lastErr_2 = 0.0  # initial err(-2)
    now_value = get_T_cernox_3(hp34461a_get_ohm_4pt(address))  # current temp
    time_interval = 1  # change input voltage every ...s
    n = 0
    kp = [0, 0.4, 7, 7, 15, 15, 25, 25, 25, 25, 25, 25, 25, 25]
    ki = [0, 1.5, 15, 15, 15, 20, 25, 25, 25, 25, 25, 25, 25, 25] #ki for 5-100 K
    kd = [0, 3.5, 4.5, 4.5, 4.5, 5, 5, 5, 5, 5, 5, 5, 5, 5]  # kd for 20-100 K
    V_in = [0, 1.6, 2.5, 4, 4.25, 4.5, 4.75, 5.25, 6, 7.5, 8.5, 9, 10]
    setpoint = [0, 10, 20, 30, 40, 50, 60, 70, 80, 100, 120, 150, 200]
    setpoint_value = setpoint[n]
    while True:
        values = output_cal(setpoint_value, now_value, time_interval, kp[n], ki[n], kd[n], lastErr, lastErr_2)
        p = values[0]
        lastErr = values[1]
        lastErr_2 = values[2]
        keithley2230_CH1_Set_voltage(address2, V_in[n] * p)
        time.sleep(time_interval)
        now_value = get_T_cernox_3(hp34461a_get_ohm_4pt(address))
        #now_value = get_T_cernox_3(keithley2000_get_ohm_4pt(address))
        print(p, lastErr, lastErr_2, now_value)


def run_one_temp_SiDiode_on_stage():
    address = 'GPIB::17::INSTR'
    address2 = 'GPIB::1::INSTR'
    err = 0.0  # initial error(0)
    lastErr = 0.0  # initial err(-1)
    lastErr_2 = 0.0  # initial err(-2)
    now_value = get_T_SiDiode(hp34461a_get_voltage(address))  # current temp
    time_interval = 0.5 # change input voltage every ...s
    n = 13
    kp = [0, 20, 20, 20, 20, 20, 25, 25, 25, 25, 25, 25, 25, 25]
    ki = [0, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100] #ki for 5-100 K
    kd = [0, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 25, 25, 25]  # kd for 20-100 K
    V_in = [0, 8, 9, 10, 10.5, 11, 11.5, 15, 15, 15, 15, 16.5, 19.5, 22]
    setpoint = [0, 15, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 150, 200]
    a = [0, 0.5, 0.5, 0.7, 0.6, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.6, 0.5, 0.5]
    setpoint_value = setpoint[n]
    print(setpoint_value)
    while True:
        values = output_cal(setpoint_value, now_value, time_interval, kp[n], ki[n], kd[n], lastErr, lastErr_2)
        p = max(values[0],a[n])
        lastErr = values[1]
        lastErr_2 = values[2]
        keithley2230_CH1_Set_voltage(address2, V_in[n] * p)
        time.sleep(time_interval)
        now_value = get_T_SiDiode(hp34461a_get_voltage(address))
        #now_value = get_T_cernox_3(keithley2000_get_ohm_4pt(address))
        print(p, lastErr, lastErr_2, now_value)

def run_r_vs_T_SiDiode_on_stage():
    address = 'GPIB::17::INSTR'#!!!!
    address2 = 'GPIB::1::INSTR'
    err = 0.0 #initial error(0)
    lastErr = 0. #initial err(-1)
    lastErr_2 = 0.0 #initial err(-2)
    now_value = get_T_SiDiode(hp34461a_get_voltage(address)) #current temp #!!!!
    time_interval = 0.5 #change input voltage every ...s
    kp = [0, 20, 20, 20, 20, 20, 25, 25, 25, 25, 25, 25, 25, 25]
    ki = [0, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100]  # ki for 5-100 K
    kd = [0, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 20, 25, 25, 25]  # kd for 20-100 K
    V_in = [0, 8, 9, 10, 10.5, 11, 11.5, 15, 15, 15, 15, 16.5, 19.5, 22]
    setpoint = [0, 15, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 150, 200]
    a = [0, 0.5, 0.5, 0.7, 0.6, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.6, 0.5, 0.5]
    timestamp = [] #record time of set temp change
    set_temp = [] #record set temp
    reach_temp = []
    data_path_init = r'C:\Users\ICET\Desktop\Data\lyw\20240626\r_vs_t_temp'#!!!
    for i in range(0,len(setpoint)):
        time_temp = []
        reach_temp_total = []
        reach_temp_temp = []
        timestamp.append(time.time())
        setpoint_value = setpoint[i]
        set_temp.append(setpoint_value)
        j = 0  # record time
        print('!!!!')
        print(setpoint_value)
        if i < 6:
            Time_wait = 1800
        elif i < 10:
            Time_wait = 3600
        elif i < 13:
            Time_wait = 5400
        else :
            Time_wait = 9000
        while j < Time_wait:
            values = output_cal(setpoint_value, now_value, time_interval, kp[i], ki[i], kd[i], lastErr, lastErr_2)
            p = max(values[0], a[i])
            lastErr = values[1]
            lastErr_2 = values[2]
            keithley2230_CH1_Set_voltage(address2, V_in[i]*p)
            time.sleep(time_interval)
            now_value = get_T_SiDiode(hp34461a_get_voltage(address))
            print(p, lastErr, lastErr_2, now_value)
            j += 1
            reach_temp_total.append(now_value)
            time_temp.append(time.time())
            if j > Time_wait*0.75:
                reach_temp_temp.append(now_value)
        data_path=data_path_init+'_'+str(setpoint_value)+'.txt'
        with open(data_path,'w') as f:
            f.write('{:<20}{:<20}\n'.format('temp','time'))
            for i in range(0,len(reach_temp_total)):
                f.write('{:<20}{:<20}\n'.format(reach_temp_total[i], time_temp[i]))
            f.close()
        reach_temp.append(sum(reach_temp_temp)/len(reach_temp_temp))
        timestamp.append(time.time())
    keithley2230_CH1_Set_voltage(address2, 0)
    print(set_temp)
    print(reach_temp)
    print(timestamp)
'''-------------------------------------------------------Run------------------------------------------------------'''
run_r_vs_T_SiDiode_on_stage()
#run_one_temp_SiDiode_on_stage()