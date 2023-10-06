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
    Time_wait = 1800 #change set temperature every ...s

    kp = 0.2
    ki = [4, 4, 4, 10, 10, 10, 10] #ki for 20-80 K
    kd = [2.5, 2.5, 2.5, 5, 5, 7.5, 7.5] #kd for 20-80 K
    V_in = [3.25, 5, 6, 7, 7, 7, 7] #input voltage for 20-80 K
    timestamp = [] #record time of set temp change
    set_temp = [] #record set temp
    for i in range(0,7):
        timestamp.append(time.time())
        setpoint_value = 10*i+20
        set_temp.append(setpoint_value)
        j = 0  # record time
        print('!!!!')
        print(setpoint_value)
        while j < Time_wait:
            values = output_cal(setpoint_value, now_value, time_interval, kp, ki[i], kd[i], lastErr, lastErr_2)
            p = values[0]
            lastErr = values[1]
            lastErr_2 = values[2]
            keithley2230_CH1_Set_voltage(address2, V_in[i]*p)
            time.sleep(time_interval)
            now_value = get_T_cernox_3(hp34461a_get_ohm_4pt(address))
            print(p, lastErr, lastErr_2, now_value)
            j += 1
        timestamp.append(time.time())
    keithley2230_CH1_Set_voltage(address2, 0)
    print(set_temp)
    print(timestamp)

def run_one_temp():
    address = 'GPIB::17::INSTR'
    address2 = 'GPIB::1::INSTR'
    err = 0.0  # initial error(0)
    lastErr = 0.  # initial err(-1)
    lastErr_2 = 0.0  # initial err(-2)
    now_value = get_T_cernox_3(hp34461a_get_ohm_4pt(address))  # current temp
    time_interval = 1  # change input voltage every ...s
    kp = 0.2
    ki = 4
    kd = 2.5
    setpoint_value = 28
    while True:
        values = output_cal(setpoint_value, now_value, time_interval, kp, ki, kd, lastErr, lastErr_2)
        p = values[0]
        lastErr = values[1]
        lastErr_2 = values[2]
        keithley2230_CH1_Set_voltage(address2, 5 * p)
        time.sleep(time_interval)
        now_value = get_T_cernox_3(hp34461a_get_ohm_4pt(address))
        print(p, lastErr, lastErr_2, now_value)

'''-------------------------------------------------------Run------------------------------------------------------'''
run_one_temp()
