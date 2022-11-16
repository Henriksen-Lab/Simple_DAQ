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
            if '.' in name:
                file_name_dict.update({name: {}})
                file_name_dict[name].update({'path': os.path.join(root, name),
                                             'time': os.path.getctime(os.path.join(root, name)),
                                             'dir': root,
                                             })
    # Reorder the file name dict with the modified time, if want to use the created time order, change the getmtime -> getctime
    ordered_file_name_dict = OrderedDict(sorted(file_name_dict.items(),
                                                key=lambda x: getitem(x[1], 'time')))
    return ordered_file_name_dict

def calc_average(x,y):
    return np.average(x),np.average(y)

def calc_average_spectrum(x,y):
    x = np.array(x)
    y = np.array(y)
    x_sweep = list(dict.fromkeys(x))
    y_sweep = []
    for each_x in x_sweep:
        each_y = np.average(y[x == each_x])
        y_sweep += [each_y]
    # print('     Avg = ', len(y[x == x_sweep[0]]), ' times')
    return np.array(x_sweep),np.array(y_sweep)

def get_color_cycle(NUM_COLORS, cmap = 'gist_rainbow'):
    cm = plt.get_cmap(cmap)
    custom_cycler = [cm(1.*x/NUM_COLORS) for x in range(NUM_COLORS)]
    return custom_cycler

"""------------------Plot configs-----------------------------------"""
def plot_single_sweep(data, sweep_tag_1, plot_tag_x='VNA_freqs', plot_tag_y='VNA_log_mag',save=False):
    # filter mask for single sweep
    data[sweep_tag_1] = np.array([round(x, 5) for x in
                         data[sweep_tag_1]])  # round sweep para, avoiding multiple value at same sweep value
    sweep1 = data[sweep_tag_1]  # sweep para
    sweep_1 = list(dict.fromkeys(sweep1))  # sweep para list
    mask = {}  # mask dictionary
    for ssweep1 in sweep_1:
        mask.update({ssweep1: sweep1 == ssweep1})
    # Plot
    fg = plt.figure()
    legend = []
    i = 0
    # print(sorted(sweep_1))
    x = []
    y = []
    for ssweep1 in sorted(sweep_1):
        current_mask = mask[ssweep1]
        xx, yy = calc_average_spectrum(data[plot_tag_x][current_mask], data[plot_tag_y][current_mask])
        if 'freq' in plot_tag_x:
            x += [float(ssweep1)]
            y += [xx[yy == min(yy)]] # find dip freq
            plt.xlabel('Vg(V)')
            plt.ylabel('Resonance freq(Hz)')
        else:
            x += [np.average(xx)]
            y += [np.average(yy)]
            plt.xlabel(plot_tag_x)
            plt.ylabel(plot_tag_y)
    plt.plot(x, y, ls='--', marker='o', ms=5, mfc='none')
    if 'freq' in plot_tag_x:
        dataToSave = np.column_stack((x,y))
        file_path = folder_path + '\\' + 'f_vs_v'
        if save:
            np.savetxt(file_path, dataToSave, delimiter='\t',
                   header="gate voltage(V) and resonance freq" + '\n' + "Vg\t\t\t\tfreqs\t\t\t\t"
                   )
    plt.show()

def plot_single_sweep_spectrum(data, sweep_tag_1, plot_tag_x='VNA_freqs', plot_tag_y='VNA_log_mag',legendcol=2):
    # filter mask for single sweep
    data[sweep_tag_1] = [round(x, 5) for x in
                         data[sweep_tag_1]]  # round sweep para, avoiding multiple value at same sweep value
    sweep1 = data[sweep_tag_1]  # sweep para
    sweep_1 = list(dict.fromkeys(sweep1))  # sweep para list
    mask = {}  # mask dictionary
    for ssweep1 in sweep_1:
        mask.update({ssweep1: sweep1 == ssweep1})
    # Plot
    fg = plt.figure()
    legend = []
    i = 0
    # print(sorted(sweep_1))
    for ssweep1 in sorted(sweep_1):
        current_mask = mask[ssweep1]
        zero_mask = mask[(sweep_1)[0]]
        x, y = calc_average_spectrum(np.array(data[plot_tag_x])[current_mask], np.array(data[plot_tag_y])[current_mask])
        x0, y0 = calc_average_spectrum(data[plot_tag_x][zero_mask], data[plot_tag_y][zero_mask])
        plt.plot(x, y, lw=0.5, color=get_color_cycle(len(sweep_1))[i])
        legend += [sweep_tag_1 + f" = {ssweep1}"]
        i += 1
    plt.legend(legend, loc='lower left', fontsize=5, ncol=legendcol)
    # plt.xlim(5.185e9, 5.21e9)
    # plt.ylim(-2, 2.5)
    # plt.ylim(-50, -35)
    plt.xlabel('freq(Hz)')
    plt.ylabel('S21(dB)')
    plt.show()

def plot_double_sweep(data, sweep_tag_1='amp', sweep_tag_2='f', plot_tag_x='amp', plot_tag_y='r_ruox'):
    # filter mask for double sweep
    sweep1 = data[sweep_tag_1]
    sweep2 = data[sweep_tag_2]
    sweep_1 = list(dict.fromkeys(sweep1))
    sweep_2 = list(dict.fromkeys(sweep2))
    mask = {}
    for ssweep1 in sweep_1:
        mask.update({ssweep1:{}})
        for ssweep2 in sweep_2:
            mask[ssweep1].update({ssweep2 : np.logical_and(sweep1 == ssweep1, sweep2 == ssweep2)})
    fg = plt.figure()
    legend =[]
    for i in range(0,len(sweep_2)):
        x = []
        y = []
        for j in range(0,len(sweep_1)):
            current_mask = mask[sweep_1[j]][sweep_2[i]]
            xx, yy = calc_average(data[plot_tag_x][current_mask], data[plot_tag_y][current_mask])
            x.append(xx)
            y.append(yy)
        plt.plot(x, y, ls='--', marker='o', ms=5, mfc='none')
        legend += [f'{sweep_2[i]/1000}'+'kHz']
    plt.legend(legend)
    plt.xlabel('AC modulation Amplitude(V)')
    plt.ylabel('RuOx resistance(ohm)')

    # # add plot trace for DC values
    # dcData = load_data_from_folder(folder_path)
    # dcData['I_mag'] = np.abs(dcData['I_mag'])/1.3
    # plt.scatter(dcData['I_mag'], dcData['r_RuOx'],c='r')
    # legend += ['DC']
    # plt.xscale('log')
    # plt.xlim(0.01,1)
    # plt.legend(legend,loc='lower left')
    plt.show()

def plot_double_sweep_spectrum(data, sweep_tag_1='amp', sweep_tag_2='f', plot_tag_x='VNA_freqs', plot_tag_y='VNA_log_mag'):
    # filter mask for double sweep
    sweep1 = data[sweep_tag_1]
    sweep2 = data[sweep_tag_2]
    sweep_1 = list(dict.fromkeys(sweep1))
    sweep_2 = list(dict.fromkeys(sweep2))
    mask = {}
    for ssweep1 in sweep_1:
        mask.update({ssweep1:{}})
        for ssweep2 in sweep_2:
            mask[ssweep1].update({ssweep2 : np.logical_and(sweep1 == ssweep1, sweep2 == ssweep2)})

    for i in range(0,len(sweep_2)):
        fg = plt.figure()
        legend = []
        for j in range(0, len(sweep_1)):
            current_mask = mask[sweep_1[j]][sweep_2[i]]
            x, y = calc_average_spectrum(data[plot_tag_x][current_mask],data[plot_tag_y][current_mask])
            plt.plot(x, y, lw=0.5, color=get_color_cycle(len(sweep_1))[i])
            legend += [sweep_tag_1 + f'= {sweep_1[i]}']
        plt.legend(legend)
        plt.xlabel('freq(hz)')
        plt.ylabel('Spectrum analyzer output (dBm)')
        plt.show()

def plot_double_sweep_spectrum_peak(data, sweep_tag_1='amp', sweep_tag_2='f', plot_tag_x='VNA_freqs', plot_tag_y='VNA_log_mag',save=False):
    # filter mask for double sweep
    sweep1 = data[sweep_tag_1]
    sweep2 = data[sweep_tag_2]
    sweep_1 = list(dict.fromkeys(sweep1))
    sweep_2 = list(dict.fromkeys(sweep2))
    mask = {}
    for ssweep1 in sweep_1:
        mask.update({ssweep1:{}})
        for ssweep2 in sweep_2:
            mask[ssweep1].update({ssweep2 : np.logical_and(sweep1 == ssweep1, sweep2 == ssweep2)})

    fg = plt.figure()
    legend = []
    dataToSave = []
    for i in range(0,len(sweep_2)):
        xx = []
        yy = []
        for j in range(0, len(sweep_1)):
            current_mask = mask[sweep_1[j]][sweep_2[i]]
            x, y = calc_average_spectrum(data[plot_tag_x][current_mask],data[plot_tag_y][current_mask])
            xx += [sweep_1[j]]
            yy += [np.average(y[np.logical_and(x > sweep_2[i]-1000,x < sweep_2[i]+1000)])]
        dataToSave += [xx]
        dataToSave += [yy]
        plt.plot(xx, yy, ls='--', marker='o', ms=5, mfc='none')
        legend += [f'Modulation at freq = {sweep_2[i]/1000} kHz']
    dataToSave = np.column_stack(dataToSave)
    file_path = folder_path + '\\' + 'amp_vs_v'
    if save:
        np.savetxt(file_path, dataToSave, delimiter='\t',
                           header="AC modulation Amplitude(V) and Spectrum analyzer output (dBm) for 1: 60KHZ, 2: 75KHz" + '\n' + "v1\t\t\t\t P1\t\t\t\tv2\t\t\t\t P2\t\t\t\t"
                           )
    plt.title('Amplitude vs modulation')
    plt.legend(legend)
    plt.xlabel('AC modulation Amplitude(V)')
    plt.ylabel('Spectrum analyzer output (dBm)')
    plt.show()

def plot_cmap(data,plot_tag_x='VNA_freqs', plot_tag_y='r_ruox', plot_tag_z='VNA_log_mag'):
    fg = plt.figure()
    gs = fg.add_gridspec(1,2,width_ratios=[1,0.1])
    ax = fg.add_subplot(gs[0])
    ax.scatter(data[plot_tag_x], data[plot_tag_y], c=data[plot_tag_z], s=5, cmap='magma', marker='|')
    #ax.set_ylim([0,5])
    cax = fg.add_subplot(gs[1])
    norm = mpl.colors.Normalize(vmin=np.min(data[plot_tag_z]), vmax=np.max(data[plot_tag_z]))
    cb = plt.colorbar(cm.ScalarMappable(norm=norm, cmap='magma'), cax=cax,
                      ticks=np.linspace(np.min(data[plot_tag_z]), np.max(data[plot_tag_z]), 10),
                      label='Transmission(dB)')
    ax.set_xlabel('Freq(Hz)')
    ax.set_ylabel('r_ruOx')
    plt.show()

'''------------------------input before run------------------------'''

# folder_path = r"C:\Users\ICET\Desktop\Data\SD\20221110_SD_006a\sweepV\20221113_sweepV_4GTo8G"
# folder_path = r"C:\Users\ICET\Desktop\Data\SD\20221110_SD_006a\sweepV\20221114_sweepV_5GTo6G"
folder_path = r"C:\Users\ICET\Desktop\Data\SD\20221110_SD_006a\sweepV_fine"
# folder_path = r"C:\Users\ICET\Desktop\Data\SD\20221110_SD_006a\up"

data = load_data_from_folder(folder_path)
print(data.keys())

# mask = np.logical_and(data['VNA_freqs']>5.2e9,data['VNA_freqs']<5.2045e9)
# mask = np.logical_and(data['VNA_freqs']>4e9,data['VNA_freqs']<4.2e9)
mask = np.logical_and(data['VNA_freqs']>5.2e9,data['VNA_freqs']<5.205e9)
for key in data.keys():
    data[key] = np.array(data[key])[mask]

plot_single_sweep_spectrum(data,
                           sweep_tag_1='vg',
                           plot_tag_x='VNA_freqs',
                           plot_tag_y='VNA_log_mag',
                           legendcol=2
                           )

plot_single_sweep(data,
                  sweep_tag_1='vg',
                  plot_tag_x='VNA_freqs',
                  plot_tag_y='VNA_log_mag',
                  save=True
                  )

# plot_single_sweep(data,
#                   sweep_tag_1='vg',
#                   plot_tag_x='vg',
#                   plot_tag_y='r_RuOx'
#                   )
plot_cmap(data,
          plot_tag_x='VNA_freqs',
          plot_tag_y='vg',
          plot_tag_z='VNA_log_mag')




