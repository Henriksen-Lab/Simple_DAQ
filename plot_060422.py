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
from math import exp
from math import log as ln
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
        self.timestamp = np.array(read_data[:, 7])
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

def get_RuOx_temp(r):
    t = exp(4.5647 - 37.205*(ln(r) - 6.91109) + 203.58*(ln(r) - 6.91109)**2 - 702.37*(ln(r) - 6.91109)**3 +
           1420*(ln(r) -6.91109)**4 - 1708.8*(ln(r) - 6.91109)**5 + 1204.6*(ln(r) - 6.91109)**6 - 458.84*(ln(r) - 6.91109)**7 + 72.825*(ln(r) - 6.91109)**8)
    return t

def update_temp(data):
    data.temp = []
    [data.temp.append(get_RuOx_temp(-x * 1E7)) for x in data.SR830_x]
    return data
'''------------------------input before run------------------------'''

folder_path = r'C:\Users\ICET\OneDrive - Washington University in St. Louis\wustl\2022spring\data\20220602_SD_004a_ICET\coolingdown'
data = load_data_from_folder(folder_path)
update_temp(data)

'''------------------------load files to class: data, and get temp at each timestamp------------------------'''

'''------------------------plot------------------------'''
fg = plt.figure()
gs = fg.add_gridspec(1,2,width_ratios=[1,0.1])
ax = fg.add_subplot(gs[0])

ax.set_xlabel('Freq(Hz)')
ax.set_ylabel('temp')
ax.scatter(data.VNA_freqs, data.temp, c=data.VNA_log_mag, s=1)
ax.set_ylim([0,50])
cax = fg.add_subplot(gs[1])
norm = mpl.colors.Normalize(vmin=np.min(data.VNA_log_mag), vmax=np.max(data.VNA_log_mag))
cb = plt.colorbar(cm.ScalarMappable(norm=norm), cax=cax,
                  ticks=np.linspace(np.min(data.VNA_log_mag), np.max(data.VNA_log_mag), 10),
                  label='Transmission(dB)')


'''# plot another line that share the same x axis
ax1 = ax.twiny()
ax1.set_xlabel('RuOX resistance(ohm)')
ax1.plot(get_RuOx_temp(data.SR830_x * 1E7), data.timestamp,'.r')

'''
plt.show()