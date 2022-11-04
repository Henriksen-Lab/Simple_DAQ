# -*- coding: utf-8 -*-
"""
@author: Shilling Du
@date: Feb 16, 2022
"""

import time, datetime, sys, os, string
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
from collections import OrderedDict
from operator import getitem
import re
from io import StringIO

def my_data_dict(read_data, axis):
    dict = {}
    for i in range(len(axis)):
        dict.update({axis[i]:np.array(read_data[:, i])})
    return dict

def load_data_from_file(name):
    readout = np.loadtxt(name)
    # dummy way of getting axis
    file = name
    with open(file, 'rb') as f:
        file_content = f.readlines()
    for i in range(0, len(file_content)):
        if b'#' not in file_content[i]:
            break
    axis = str(file_content[i - 1][1:].decode('utf-8')).split()
    axis = ['_'.join(x.split('_')[:-1]) for x in axis]
    data = my_data_dict(readout, axis)
    return data

def load_data_from_folder(folder_path):
    matrix =[]
    order = 0
    ordered_file_name_dict = get_ordered_file_name_dict(folder_path)
    for name in ordered_file_name_dict.keys():
        order +=1
        file = ordered_file_name_dict[name]['path']
        if order == 1:
            # dummy way of getting axis
            with open(file, 'rb') as f:
                file_content = f.readlines()
            for i in range(0, len(file_content)):
                if b'#' not in file_content[i]:
                    break
            axis = str(file_content[i - 1][1:].decode('utf-8')).split()
            axis = ['_'.join(x.split('_')[:-1]) for x in axis]
        print(' ', order ,". ", name)
        readout = np.loadtxt(file)
        [matrix.append(x) for x in readout]
        print('done')
    matrix = np.array(matrix)
    data = my_data_dict(matrix, axis)
    return data

def get_ordered_file_name_dict(folder_path):
    file_name_dict = {}
    for root, dirs, files in os.walk(folder_path, topdown=False):
        # go through every file inside the folder, even inside subfolders
        for name in files:
            file_name_dict.update({name: {}})
            file_name_dict[name].update({'path': os.path.join(root, name),
                                         'time': os.path.getmtime(os.path.join(root, name)),
                                         'dir': root,
                                         })
    # Reorder the file name dict with the modified time, if want to use the created time order, change the getmtime -> getctime
    ordered_file_name_dict = OrderedDict(sorted(file_name_dict.items(),
                                                key=lambda x: getitem(x[1], 'time')))
    return ordered_file_name_dict

def calc_average(x,y):
    return np.average(x),np.average(y)

def calc_average_spectrum(x,y):
    x_sweep = list(dict.fromkeys(x))
    y_sweep = []
    for each_x in x_sweep:
        each_y = np.average(y[x == each_x])
        y_sweep += [each_y]
    print('     Avg = ', len(y[x == x_sweep[0]]), ' times')
    return np.array(x_sweep),np.array(y_sweep)
'''------------------------input before run------------------------'''

# folder_path = r'C:\Users\ICET\Desktop\Data\SD\20221020_SD_004d\Spectrum\temp\data'
# file_path = r"C:\Users\ICET\Desktop\Data\SD\20221020_SD_004d\Spectrum\temp\data\20221103\Vmag_f_temp_fine.001"
folder_path = r'C:\Users\ICET\Desktop\Data\SD\20221020_SD_004d\Spectrum\Q\data\20221104'
# folder_path = r"C:\Users\ICET\Desktop\Data\SD\20221020_SD_004d\Spectrum\I_2\vna\20221104_sweepfield_Peak4_75kHz"
data = load_data_from_folder(folder_path)
print(data.keys())

# data = load_data_from_file(file_path)
# folder_path = r'C:\Users\ICET\Desktop\Data\SD\20221020_SD_004d\with_amp\20221028_sweepfield_DC_Peak2'
# dcData = load_data_from_folder(folder_path)
# print(dcData.keys())

'''------------------------filter------------------------'''
sweep1 = data['amp']
sweep2 = data['f']
sweep_1 = list(dict.fromkeys(sweep1))
sweep_2 = list(dict.fromkeys(sweep2))
mask = {}
for ssweep1 in sweep_1:
    mask.update({ssweep1:{}})
    for ssweep2 in sweep_2:
        mask[ssweep1].update({ssweep2 : np.logical_and(sweep1 == ssweep1, sweep2 == ssweep2)})

# sweep1 = data['v_sur']
# sweep_1 = list(dict.fromkeys(sweep1))
# mask = {}
# for ssweep1 in sweep_1:
#     mask.update({ssweep1: sweep1 == ssweep1})

# dcData['I_mag'] = np.abs(dcData['I_mag'])/1.3

'''------------------------plot 0------------------------'''
# fg = plt.figure()
# legend = []
# for ssweep1 in sweep_1:
#     current_mask = mask[ssweep1]
#     plt.plot(data['VNA_freqs'][current_mask],data['VNA_log_mag'][current_mask], lw=1)
#     legend += [f"v = {ssweep1}"]
# plt.legend(legend)
# # plt.xlim(6.98e9,6.99e9)
# # plt.ylim(,)
# plt.xlabel('freq(Hz)')
# plt.ylabel('S21(dB)')
# plt.show()


'''------------------------plot 1------------------------'''
# fg = plt.figure()
#
# legend =[]
# for i in range(0,len(sweep_2)):
#     x = []
#     y = []
#     for j in range(0,len(sweep_1)):
#         current_mask = mask[sweep_1[j]][sweep_2[i]]
#         # xx, yy = calc_average(data['I_x'][current_mask],data['r_RuOx'][current_mask])
#         xx, yy = calc_average(data['amp'][current_mask], data['r_RuOx'][current_mask])
#         x.append(xx)
#         y.append(yy)
#     plt.plot(x, y, ls='--', marker='o', ms=5, mfc='none')
#     legend += [f'{sweep_2[i]/1000}'+'kHz']
#
# # add plot trace for DC values
# # plt.scatter(dcData['I_mag'], dcData['r_RuOx'],c='r')
# # legend += ['DC']
# # plt.xscale('log')
# # plt.xlim(0.01,1)
# # plt.legend(legend,loc='lower left')
#
# plt.legend(legend)
# plt.xlabel('AC modulation Amplitude(V)')
# plt.ylabel('RuOx resistance(ohm)')
# plt.show()

'''------------------------plot 2------------------------'''
for i in range(0,len(sweep_2)):
    print(f'Modulation at freq = {sweep_2[i]/1000} kHz')
    fg = plt.figure()
    legend = []
    for j in range(0, len(sweep_1)):
        current_mask = mask[sweep_1[j]][sweep_2[i]]
        print(f'    for V= {sweep_1[j]} V')
        x, y = calc_average_spectrum(data['VNA_freqs'][current_mask],data['VNA_log_mag'][current_mask])
        plt.plot(x, y, lw=1)
        legend += [f'V= {sweep_1[j]}V']
    plt.title(f'Modulation at freq = {sweep_2[i]/1000} kHz')
    plt.legend(legend, loc='lower left')
    plt.xlabel('Spectrum analyzer Sweep freq (Hz)')
    # plt.xlim(sweep_2[i]-2000,sweep_2[i]+2000)
    plt.ylabel('Spectrum analyzer output (dBm)')
    plt.show()

'''------------------------plot 3------------------------'''
fg = plt.figure()
legend = []
for i in range(0,len(sweep_2)):
    xx = []
    yy = []
    for j in range(0, len(sweep_1)):
        current_mask = mask[sweep_1[j]][sweep_2[i]]
        x, y = calc_average_spectrum(data['VNA_freqs'][current_mask],data['VNA_log_mag'][current_mask])
        xx += [sweep_1[j]]
        yy += [np.average(y[np.logical_and(x>sweep_2[i]-1000,x<sweep_2[i]+1000)])]
    plt.plot(xx, yy, ls='--', marker='o', ms=5, mfc='none')
    legend += [f'Modulation at freq = {sweep_2[i]/1000} kHz']
plt.title('Amplitude vs modulation')
plt.legend(legend)
plt.xlabel('AC modulation Amplitude(V)')
plt.ylabel('Spectrum analyzer output (dBm)')
plt.show()

'''------------------------plot 4------------------------'''
# fg = plt.figure()
# gs = fg.add_gridspec(1,2,width_ratios=[1,0.1])
# ax = fg.add_subplot(gs[0])
#
# ax.set_xlabel('Freq(Hz)')
# ax.set_ylabel('V_mag(V)')
# ax.scatter(data.VNA_freqs, data.V_mag, c=data.VNA_log_mag, s=0.05, cmap='magma')
# #ax.set_ylim([0,5])
# cax = fg.add_subplot(gs[1])
# norm = mpl.colors.Normalize(vmin=np.min(data.VNA_log_mag), vmax=np.max(data.VNA_log_mag))
# cb = plt.colorbar(cm.ScalarMappable(norm=norm, cmap='magma'), cax=cax,
#                   ticks=np.linspace(np.min(data.VNA_log_mag), np.max(data.VNA_log_mag), 10),
#                   label='Transmission(dB)')
#
# plt.show()