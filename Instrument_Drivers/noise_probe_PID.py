# Written by Shilling Du 7/11/2022
import sys, os, time, threading, tkinter
import numpy as np
from decimal import Decimal
# import matplotlib.pyplot as plt

folder_path = os.getcwd()
if folder_path not in sys.path:
    sys.path.append(
        folder_path)  # easier to open driver files as long as Simple_DAQ.py is in the same folder with drivers
from Instrument_Drivers.noise_probe_arduino_control import arduino_write
from Instrument_Drivers.thermometer.Cernox import get_T_cernox_2
from datetime import datetime
from Instrument_Drivers.keithley import *

'''-------------------------------------------------------Main------------------------------------------------------'''

class Mypid:

    def __init__(self):
        self.kp = 1.0
        self.ki = 0.1
        self.kd = 0.05
        self.sample_time = 3
        self.error = 0
        self.lastErr = 0
        self.lastErr_2 = 0
        self.limit = (0, 100)
        self.setpoint = 0
        self.readinglog = []
        self.timelog = []
        self.arduino_address =''
        self.reading = 0
        self.update_flag = True

    def write(self):
        arduino_write(self.output, self.arduino_address)
        print("Arduino set to ", self.output)

    def close(self):
        self.output = 0
        self.write()

    def pid_start(self):
        print("PID initializing")
        self.error = float(self.setpoint) - float(self.reading)
        self.lastErr = self.error
        # time_interval = self.sample_time
        # derr = (error - self.lastErr) / time_interval
        # self.output = self.kp * error + self.ki * error* time_interval + self.kd * derr
        # self.output = max(min(self.output, self.limit[1]), self.limit[0])
        self.lastErr_2 = self.error
        self.lastErr = self.error
        self.last_time = time.time()
        self.write()
        print("PID initialized")
        time.sleep(self.sample_time)

    def pid_update(self):
        print("PID updating")
        error = float(self.setpoint) - float(self.reading)
        time_interval = time.time() - self.last_time
        # if abs(self.reading-self.setpoint)>0.5 and self.output==100:
        #   self.errsum=0
        # else:
        #    self.errsum += error * time_interval
        # derr = (error - self.lastErr) / time_interval
        self.output += self.kp * (error - self.lastErr) + self.ki * error * time_interval + self.kd * (
                    error - 2 * self.lastErr + self.lastErr_2) / time_interval
        self.output = max(min(self.output, self.limit[1]), self.limit[0])
        self.lastErr_2 = self.lastErr
        self.lastErr = error
        self.last_time = time.time()
        self.write()
        print("PID updated")
        time.sleep(self.sample_time)

    def manual_tune(self, newkp, newki, newkd):
        self.kp = newkp
        self.ki = newki
        self.kd = newkd

    def pid_run(self):
        self.pid_reset()
        self.pid_start()
        while self.update_flag:
            self.pid_update()

    def pid_reset(self):
        self.LastErr = 0
        self.errsum = 0


noise_pid = Mypid()
'''sweep temp from temp now to the 80K at rate = 1K/10min'''
def noise_pid_set(reading,target_temp = 80,step_size = 0.1,lowkp=20,lowki=0.1,lowkd=15,highkp=337,highki=1.5,highkd=15):
    temp_now = get_T_cernox_2(reading)
    noise_pid.reading = temp_now
    num_steps = int(np.floor(abs(target_temp) / (step_size))) + 1
    for val in np.linspace(float(temp_now), target_temp, num_steps):
        noise_pid.setpoint = val
        if 20 < val <= 70:
            noise_pid.manual_tune(newkp=lowkp, newki=lowki, newkd=lowkd)
        elif val > 70:
            noise_pid.manual_tune(newkp=highkp, newki=highki, newkd=highkd)

def noise_pid_get(reading):
    temp_now = get_T_cernox_2(reading)
    return temp_now