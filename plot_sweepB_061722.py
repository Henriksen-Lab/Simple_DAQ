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
        self.V_mag = np.array(read_data[:, 5])
        self.timestamp = np.array(read_data[:, 6])


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
            #readout[:, 1] -= np.mean(readout[:, 1]) # level the data
            [matrix.append(x) for x in readout]
            print('done')
    matrix = np.array(matrix)
    data = My_data(matrix)
    return data

'''------------------------input before run------------------------'''

folder_path = r'C:\Users\ICET\OneDrive - Washington University in St. Louis\wustl\2022spring\data\20220617_SD_004a\SweepField\20220623_sweepfield_DC'
data = load_data_from_folder(folder_path)

'''------------------------plot------------------------'''
fg = plt.figure()
gs = fg.add_gridspec(1,2,width_ratios=[1,0.1])
ax = fg.add_subplot(gs[0])

ax.set_xlabel('Freq(Hz)')
ax.set_ylabel('V_mag(V)')
ax.scatter(data.VNA_freqs, data.V_mag, c=data.VNA_log_mag, s=0.05, cmap='magma')
#ax.set_ylim([0,5])
cax = fg.add_subplot(gs[1])
norm = mpl.colors.Normalize(vmin=np.min(data.VNA_log_mag), vmax=np.max(data.VNA_log_mag))
cb = plt.colorbar(cm.ScalarMappable(norm=norm, cmap='magma'), cax=cax,
                  ticks=np.linspace(np.min(data.VNA_log_mag), np.max(data.VNA_log_mag), 10),
                  label='Transmission(dB)')

plt.show()