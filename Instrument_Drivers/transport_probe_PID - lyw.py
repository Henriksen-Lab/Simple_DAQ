# Written by Yiwei Le 9/26/2023
import sys, os, time, threading, tkinter
import numpy as np
from decimal import Decimal
import matplotlib.pyplot as plt

folder_path = os.getcwd()
if folder_path not in sys.path:
    sys.path.append(
        folder_path)  # easier to open driver files as long as Simple_DAQ.py is in the same folder with drivers
from Instrument_Drivers.thermometer.Cernox import get_T_cernox_3
from Instrument_Drivers.hp34461A import hp34461a_get_ohm_4pt
from Instrument_Drivers.keithley2230G_30_1 import *

'''-------------------------------------------------------Main------------------------------------------------------'''

def output_cal(setpoint_value, now_value, time_interval, kp, ki, kd, lastErr, lastErr_2):
    err = float(setpoint_value) - float(now_value)
    output =  kp * (err - lastErr) + ki * err * time_interval + kd * (err - 2 * lastErr + lastErr_2) / time_interval
    output = min(max(output, 0), 1)
    return (output, err, lastErr)

def run_r_vs_T():
    address = 'GPIB::17::INSTR'
    address2 = 'GPIB::1::INSTR'
    err = 0.0 #initial error(0)
    lastErr = 0. #initial err(-1)
    lastErr_2 = 0.0 #initial err(-2)
    now_value = get_T_cernox_3(hp34461a_get_ohm_4pt(address)) #current temp
    time_interval = 1 #change input voltage every ...s
    Time_wait = 5400 #change set temperature every ...s
    kp = 0.2
    ki = [0, 1, 2, 4, 4, 4, 10, 10, 12.5] #ki for 5-100 K
    ki = [0, 4, 4, 4, 10, 10, 10]  # ki for 20-100 K
    #kd = [0, 0.5, 1.5, 2.5, 2.5, 2.5, 5, 7.5, 10] #kd for 5-100 K
    kd = [0, 2.5, 2.5, 2.5, 20, 22.5, 25, 27.5, 30, 32.5, 35, 37.5, 40, 42.5, 45, 47.5, 50]  # kd for 20-100 K
    #V_in = [0, 0.8, 1.5, 3, 3.25, 4, 5, 7, 8] #input voltage for 5-100 K
    V_in = [0, 3.25, 4.5, 4, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10]  # input voltage for 5-100 K
    #setpoint= [0, 5, 10, 15, 20, 35, 50, 70, 100]
    setpoint = [0, 20, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
    timestamp = [] #record time of set temp change
    set_temp = [] #record set temp
    reach_temp = []
    for i in range(6,17):
        reach_temp_temp = []
        timestamp.append(time.time())
        setpoint_value = setpoint[i]
        set_temp.append(setpoint_value)
        j = 0  # record time
        print('!!!!')
        print(setpoint_value)
        while j < Time_wait:
            values = output_cal(setpoint_value, now_value, time_interval, kp, 10, kd[i], lastErr, lastErr_2)
            p = values[0]
            lastErr = values[1]
            lastErr_2 = values[2]
            keithley2230_CH1_Set_voltage(address2, V_in[i]*p)
            time.sleep(time_interval)
            now_value = get_T_cernox_3(hp34461a_get_ohm_4pt(address))
            print(p, lastErr, lastErr_2, now_value)
            j += 1
            if j > 2700:
                reach_temp_temp.append(now_value)
        reach_temp.append(sum(reach_temp_temp)/len(reach_temp_temp))
        timestamp.append(time.time())
    keithley2230_CH1_Set_voltage(address2, 0)
    print(set_temp)
    print(reach_temp)
    print(timestamp)

def run_one_temp():
    address = 'GPIB::17::INSTR'
    address2 = 'GPIB::1::INSTR'
    err = 0.0  # initial error(0)
    lastErr = 0.0  # initial err(-1)
    lastErr_2 = 0.0  # initial err(-2)
    now_value = get_T_cernox_3(hp34461a_get_ohm_4pt(address))  # current temp
    time_interval = 1  # change input voltage every ...s
    kp = 0.2
    ki = 10
    kd = 35
    setpoint_value = 70
    while True:
        values = output_cal(setpoint_value, now_value, time_interval, kp, ki, kd, lastErr, lastErr_2)
        p = values[0]
        lastErr = values[1]
        lastErr_2 = values[2]
        keithley2230_CH1_Set_voltage(address2, 7.5 * p)
        time.sleep(time_interval)
        now_value = get_T_cernox_3(hp34461a_get_ohm_4pt(address))
        print(p, lastErr, lastErr_2, now_value)

'''-------------------------------------------------------Run------------------------------------------------------'''
run_one_temp()
#run_r_vs_T()