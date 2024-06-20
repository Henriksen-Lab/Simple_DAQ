from math import *
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.optimize import fsolve

with open(r'C:\Users\ICET\Documents\GitHub\Simple_DAQ\Instrument_Drivers\thermometer\SiDiode.txt', 'r', encoding='utf-8') as file:
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

print(get_T_SiDiode(0.5571))
print(get_T_SiDiode(0.5589))