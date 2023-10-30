# Written by Shilling Du 7/25/2022
import sys, os, time, threading, tkinter
import numpy as np
# import matplotlib.pyplot as plt
from datetime import datetime
from decimal import Decimal

folder_path = os.getcwd()
if folder_path not in sys.path:
    sys.path.append(
        folder_path)  # easier to open driver files as long as Simple_DAQ.py is in the same folder with drivers
from Instrument_Drivers.transfer_heater_arduino_comm import *

class MyPID:
    def __init__(self):
        self.setpoint = 30
        self.arduino_address = 'COM10'
        #Initialize the variables
        self.time_interval = 1
        self.reading = 0
        self.timenow =0
        self.timelog = []
        self.templog = []
        self.setpoint_read = 0
        self.Output_read = 0
        self.pid_value = ''
        self.pid_read = ''
        self.update_flag = True
    def read(self):
        self.reading = float(arduino_read_temp(arduino_name=self.arduino_address))
        self.timenow = float(time.time())
        self.setpoint_read = float(arduino_read_set(arduino_name=self.arduino_address))
        self.Output_read = float(arduino_read_output(arduino_name=self.arduino_address))
        self.pid_read = str(arduino_read_pid(arduino_name=self.arduino_address))
        self.timelog += [self.timenow]
        self.templog += [self.reading]

    def write(self):
        if self.setpoint != 0:
            arduino_set(arduino_name=self.arduino_address, t=self.setpoint)

    def write_pid(self):
        if self.pid_value != '':
            arduino_set_pid(arduino_name=self.arduino_address, pid=self.pid_value)

    def run(self):
        while self.update_flag:
            self.write()
            self.write_pid()
            self.read()
      # #      print(time.asctime(time.localtime(time.time())), "\nTemp =", self.reading, "C", ", Set point =",
      # #            self.setpoint_read, "C")
      #       print(f"Setpoint = {self.setpoint_read}C, Output = {self.Output_read}%, PID value = {self.pid_read}")
      #       plt.title(f"Setpoint = {self.setpoint_read}C, Output = {self.Output_read}%, PID value = {self.pid_read}")
      #       plt.plot(self.timenow - t_now, self.reading, '.r')
      #       plt.xlim([0, self.timenow - t_now + 1])
      #       plt.pause(0.5)
      #       time.sleep(self.time_interval)
      #       np.savetxt(
      #           self.dir +'\\'+ 'temp.txt',
      #           np.column_stack(([a - self.timelog[0] for a in self.timelog], self.templog)), delimiter='\t',
      #           header=f"\Setpoint = {self.setpoint_read}C, Output = {self.Output_read}%, PID value = {self.pid_read}"+ '\n'
      #                  +datetime.now().strftime('%Y%m%d') + '\n' + "time\t\t\ttemp\t\t\t")
      #       print("data saved")

transfer_pid = MyPID()
def transfer_pid_get(arduino_address='COM10'):
    transfer_pid.arduino_address = arduino_address
    transfer_pid.read()
    return transfer_pid.reading

def transfer_pid_set(arduino_address='COM10',kp=1,ki=0,kd=0,set_point=30):
    transfer_pid.arduino_address = arduino_address
    transfer_pid.setpoint = set_point
    transfer_pid.write()
    transfer_pid.pid_value = 'k'+ str(kp)+'p'
    transfer_pid.write_pid()
    transfer_pid.pid_value = 'k' + str(ki) + 'i'
    transfer_pid.write_pid()
    transfer_pid.pid_value = 'k' + str(kd) + 'd'
    transfer_pid.write_pid()