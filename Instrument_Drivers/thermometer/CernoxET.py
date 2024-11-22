from math import *
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.optimize import fsolve
from Instrument_Drivers.hp34461A import hp34461a_get_voltage
from Instrument_Drivers.keithley import keithley2000_get_voltage_V
from Instrument_Drivers.thermometer.SiDiode import get_T_SiDiode
from Instrument_Drivers.keithley import keithley2000_get_ohm_2pt
import time

with open(r'C:\Users\ICET\Documents\GitHub\Simple_DAQ\Instrument_Drivers\thermometer\X206563.spline.curve', 'r', encoding='utf-8') as file:
    lines = file.readlines()
data=[]
temps=[]
for line in lines:
    numbers_str = line.split()
    data.append(float(numbers_str[0]))
    temps.append(float(numbers_str[1]))


f = interp1d(data, temps, kind='cubic')

def get_T_cernoxCT(r):
    t = f(r)
    return t


def read_temp():
    while True:
        print('stage '+str(get_T_cernoxCT(keithley2000_get_ohm_2pt( 'GPIB::27::INSTR')-11.8)))
        #print('probe '+str(get_T_SiDiode(keithley2000_get_voltage_V( 'GPIB::18::INSTR'))))
        #print(get_T_SiDiode(hp34461a_get_voltage('GPIB::17::INSTR')))
        time.sleep(1)

#read_temp()