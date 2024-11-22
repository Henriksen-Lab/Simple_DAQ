from math import *
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.optimize import fsolve
from Instrument_Drivers.hp34461A import hp34461a_get_voltage
from Instrument_Drivers.keithley import keithley2000_get_voltage_V
import time, os

current = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current,'SiDiode.txt'), 'r', encoding='utf-8') as file:
    lines = file.readlines()
    data=[]

for line in lines:
    numbers_str = line.split()
    for i in numbers_str:
        if float(i) <2:
            data.append(float(i))

data = data[1:]
temps = np.linspace(1,450,450)

f = interp1d(data, temps, kind='cubic')

def get_T_SiDiode(voltage):
    t = f(voltage)
    return t

def read_temp():
    while True:
        print('stage '+str(get_T_SiDiode(hp34461a_get_voltage( 'GPIB::17::INSTR'))))
        #print('probe '+str(get_T_SiDiode(keithley2000_get_voltage_V( 'GPIB::18::INSTR'))))
        #print(get_T_SiDiode(hp34461a_get_voltage('GPIB::17::INSTR')))
        time.sleep(1)


#read_temp()
#plt.plot(temps[:100],data[:100])
# plt.xlabel('temperature (K)')
# plt.ylabel('voltage (V)')
# plt.show()