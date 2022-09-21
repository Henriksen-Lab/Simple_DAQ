# -*- coding: utf-8 -*-
"""
@author: Shilling Du
@date: Feb 16, 2022
"""

import time, datetime, sys, os, string
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm
from scipy import interpolate
import numpy as np

def get_temperature(log_name):
    folder_path = os.getcwd()
    if folder_path not in sys.path:
        sys.path.append(folder_path)
    temp = np.loadtxt(log_name, delimiter=',', usecols=2)
    date, clock = np.loadtxt(log_name, dtype='str', delimiter=',', usecols=(0, 1), unpack=True)
    timearray = [time.strptime(x[1:7]+'20'+x[-2:]+','+y, '%d-%m-%Y,%H:%M:%S') for x, y in zip(date, clock)] 
    # for the format we get from fridge log, the '20' is to change 09-02-22 into 09-02-2022, for reading purpose
    timestamp = [time.mktime(x) for x in timearray]
    return timestamp, temp

def time_temp(log_path):
    time = []
    temp = []
    for root,dirs,files in os.walk(log_path):
        for name in files:
            print(os.path.join(root, name))
            x, y = get_temperature(os.path.join(root, name))
            [time.append(xx) for xx in x]
            [temp.append(yy) for yy in y]
            print('done')
    time = np.array(time)
    temp = np.array(temp)
    return time, temp

class My_data():
    def __init__(self, read_data):
      # might want to change it manually according to the my_form in Simple_DAQ.py
        self.VNA_freqs = np.array(read_data[:, 0])
        self.VNA_log_mag = np.array(read_data[:, 1])
        self.VNA_phase_rad = np.array(read_data[:, 2])
        self.VNA_real = np.array(read_data[:, 3])
        self.VNA_imag = np.array(read_data[:, 4])
        self.SR830_x = np.array(read_data[:, 5])
        self.SR830_y = np.array(read_data[:, 6])
        self.keithley_R = np.array(read_data[:, 7])
        self.timestamp = np.array(read_data[:, 8])
        self.temp = []

def load_data_from_file(name):
    readout = np.loadtxt(name)
    data = My_data(readout)
    return data

def load_data_from_folder(folder_path):
    matrix =[]
    for root,dirs,files in os.walk(folder_path): #go through every file inside the folder, even inside subfolders
        for name in files:
            print(os.path.join(root, name))
            readout = np.loadtxt(os.path.join(root, name))
            [matrix.append(x) for x in readout]
            print('done')
    matrix = np.array(matrix)
    data = My_data(matrix)
    return data

def compare_timestamp(folder_path, log_list):
    timestamp, temp = time_temp(log_path)
    data = load_data_from_folder(folder_path)
    #plt.plot(timestamp, temp)
    #plt.show()
    f = interpolate.interp1d(timestamp, temp, kind='nearest', bounds_error=False)
    data.temp = f(data.timestamp)
    return data

'''------------------------input before run------------------------'''
log_path = r'C:\Users\duxin\OneDrive - Washington University in St. Louis\wustl\2022spring\data\20220209_SDCPW\fridge_log'
folder_path = r'C:\Users\duxin\OneDrive - Washington University in St. Louis\wustl\2022spring\data\20220209_SDCPW\vnadata'



'''------------------------load files to class: data, and get temp at each timestamp------------------------'''

data = compare_timestamp(folder_path, log_path)


'''------------------------plot------------------------'''
fg = plt.figure()
gs = fg.add_gridspec(1,2,width_ratios=[1,0.1])
ax = fg.add_subplot(gs[0])

mask = data.temp > 2 
#Im running exp above 3K, when MX thremometer can't read temp, it will output 0, so this is for filtering out 0K data

ax.set_xlabel('Freq(Hz)')
ax.set_ylabel('Temp(K)')
ax.scatter(data.VNA_freqs[mask], data.temp[mask], c=data.VNA_log_mag[mask], s=1.5)
cax = fg.add_subplot(gs[1])
norm = mpl.colors.Normalize(vmin=np.min(data.VNA_log_mag[mask]), vmax=np.max(data.VNA_log_mag[mask]))
cb = plt.colorbar(cm.ScalarMappable(norm=norm),cax=cax,
                  ticks=np.linspace(np.min(data.VNA_log_mag[mask]), np.max(data.VNA_log_mag[mask]), 10),
                  label='Transmission(dB)')

# plot another line that share the same x axis
ax1 = ax.twiny()
ax1.set_xlabel('Nb resistance(ohm)')
ax1.plot(data.SR830_x[mask] * 1E6, data.temp[mask],'.r')


plt.show()