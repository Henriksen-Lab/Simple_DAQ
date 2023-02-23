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
import scipy
# from scipy.optimize import curve_fit
# from scipy import signal
# from scipy import interpolate
import pickle

def my_data_dict(data, read_data, axis):
    for i in range(len(axis)):
        if axis[i] not in data.keys():
            data.update({axis[i]:np.array(read_data[:, i])})
        else:
            data[axis[i]]= np.append(data[axis[i]],np.array(read_data[:, i]))
    return data

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
    order = 0
    ordered_file_name_dict = get_ordered_file_name_dict(folder_path)
    data = {}
    for name in ordered_file_name_dict.keys():
        matrix = []
        order += 1
        file = ordered_file_name_dict[name]['path']
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
        matrix = np.array(matrix)
        data = my_data_dict(data, matrix, axis)
        print('done')
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

def calc_average_spectrum(x,y,type='logmag'):
    x = np.array(x)
    y = np.array(y)
    x_sweep = list(dict.fromkeys(x))
    y_sweep = []
    for each_x in x_sweep:
        if type == 'logmag':
            each_y = np.average(np.power(10, y/20)[x == each_x])
            each_y = 20 * np.log10(each_y)
        else:
            each_y = np.average(y[x == each_x])
        y_sweep += [each_y]
    # print('     Avg = ', len(y[x == x_sweep[0]]), ' times')
    return np.array(x_sweep),np.array(y_sweep)

def get_color_cycle(NUM_COLORS, cmap = 'twilight_shifted'):
    cm = plt.get_cmap(cmap)
    custom_cycler = [cm(1.*x/NUM_COLORS) for x in range(NUM_COLORS)]
    return custom_cycler

def save_data(folder_path, data):
    file_path = folder_path + '\\' + 'reformatted_data'
    axis = ''
    dataToSave = []
    for trace in sorted(data.keys()):
        axis += trace + '_001'+ '\t\t\t'
        dataToSave += [np.array(data[trace])]
    dataToSave = np.column_stack(dataToSave)
    np.savetxt(file_path, dataToSave, delimiter='\t',
               header=axis
               )

def limitdata(data,low_limit,high_limit,tag):
    mask = np.logical_and(data[tag] > low_limit, data[tag] < high_limit)
    for key in data.keys():
        data[key] = np.array(data[key])[mask]
    return data

def linecutdata(data,list,tag):
    mask = np.zeros(len(data[tag]))
    for value in list:
        mask = np.logical_or(mask,data[tag]==value)
    for key in data.keys():
        data[key] = np.array(data[key])[mask]
    return data

def calculate_R(data, tag_I='I_x',tag_V='V_x'):
    data.update({'R': data[tag_V] / data[tag_I]})
    data.update({'rho': data[tag_I] / (data[tag_V])})
    return data

def add_column(file_path,column_name='new_para',value=0):
    data = load_data_from_file(file_path)
    folder_path = os.path.dirname(file_path)
    random_name = list(data.keys())[0]
    data.update({column_name:np.full(len(data[random_name]),value)})
    save_data(folder_path, data)

def antisymetric(y):
    y = np.array(y)
    y = (y-y[::-1])/2
    return y

def linear_func(x, A):
    y = A * x
    return y

def convolution_gaussian_func(x,x0,A,sigma):
    x1 = np.linspace(-100,100,100000)
    y1 = A/(x1-x0)
    y2 = np.exp(-0.5*(x1)**2/sigma**2)/(np.sqrt(2 * np.pi) * sigma)
    y = interpolate.interp1d(x1,
                             signal.convolve(y1, y2, 'same') / sum(y2),
                             kind='linear',
                            bounds_error=False,
                            fill_value="extrapolate")
    return y(x)

"""------------------Plot configs-----------------------------------"""
def plot_single_sweep(data, sweep_tag_1, plot_tag_x='VNA_freqs', plot_tag_y='VNA_log_mag',save=False,yerrbar=False):
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
    yerr = []
    for ssweep1 in sorted(sweep_1):
        current_mask = mask[ssweep1]
        if 'freq' in plot_tag_x:
            xx, yy = calc_average_spectrum(data[plot_tag_x][current_mask], data[plot_tag_y][current_mask])
            x += [float(ssweep1)]
            y += [xx[yy == min(yy)]] # find dip freq
            yerr += [xx[1]-xx[0]]
            plt.xlabel('Vg(V)')
            plt.ylabel('Resonance freq(Hz)')
        else:
            xx = data[plot_tag_x][current_mask]
            yy = data[plot_tag_y][current_mask]
            x += [np.average(xx)]
            y += [np.average(yy)]
            yerr += [np.std(yy)]
            plt.xlabel(plot_tag_x)
            plt.ylabel(plot_tag_y)
    axis = plot_tag_x +'\t\t\t\t' + plot_tag_y + '\t\t\t\t'
    data.update({f'avg_{plot_tag_x}_x':x})
    data.update({f'avg_{plot_tag_y}_y': y})
    data.update({f'avg_{plot_tag_y}_yerr': yerr})

    if yerrbar:
        print('error bar')
        # plt.errorbar(x, y, yerr, ls='--', marker='o', ms=5, mfc='none')
        y = np.array(y)
        yerr = np.array(yerr)
        dataToSave = np.column_stack((x, y, yerr))
        axis += 'errorbar\t\t\t\t'
        plt.plot(x, y, ls='--', marker='o', ms=2, mfc='none')
        plt.fill_between(x, y-yerr, y+yerr, alpha=0.4, ls='--')
    else:
        dataToSave = np.column_stack((x, y))
        plt.plot(x, y, ls='--', marker='o', ms=2, mfc='none')

    file_path = folder_path + '\\' + plot_tag_x +'_vs_' + plot_tag_y
    if save:
        np.savetxt(file_path, dataToSave, delimiter='\t',
               header= axis
               )
    plt.show()

def plot_single_sweep_calc_R(data, sweep_tag_1, plot_tag_x='VNA_freqs',plot_tag_V='V_x', plot_tag_I='I_x', save=False, yerrbar=False):
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
    yerr = []
    for ssweep1 in sorted(sweep_1):
        current_mask = mask[ssweep1]
        xx = data[plot_tag_x][current_mask]
        yy = data[plot_tag_V][current_mask]/data[plot_tag_I][current_mask]
        x += [np.average(xx)]
        y += [np.average(yy)]
        yerr += [np.std(yy)]
        plt.xlabel(plot_tag_x)
        plt.ylabel('R(ohm)')
    axis = plot_tag_x + '\t\t\t\t' + 'R(ohm)' + '\t\t\t\t'
    data.update({f'avg_{plot_tag_x}_x': x})
    data.update({f'avg_R(ohm)_y': y})
    data.update({f'avg_R(ohm)_yerr': yerr})
    # plt.ylim(0, 1e6)
    if yerrbar:
        print('error bar')
        # plt.errorbar(x, y, yerr, ls='--', marker='o', ms=5, mfc='none')
        y = np.array(y)
        yerr = np.array(yerr)
        dataToSave = np.column_stack((x, y, yerr))
        axis += 'errorbar\t\t\t\t'
        plt.plot(x, y, ls='--', marker='o', ms=2, mfc='none')
        plt.fill_between(x, y - yerr, y + yerr, alpha=0.4, ls='--')
    else:
        dataToSave = np.column_stack((x, y))
        plt.plot(x, y, ls='--', marker='o', ms=2, mfc='none')

    file_path = folder_path + '\\' + plot_tag_x + '_vs_' + 'R(ohm)'
    if save:
        np.savetxt(file_path, dataToSave, delimiter='\t',
                   header=axis
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
        x, y = calc_average_spectrum(np.array(data[plot_tag_x])[current_mask], np.array(data[plot_tag_y])[current_mask])
        zero_mask = mask[(sweep_1)[0]]
        # zero_mask = mask[0.6]
        x0, y0 = calc_average_spectrum(data[plot_tag_x][zero_mask], data[plot_tag_y][zero_mask])
        plt.plot(x, y/y0, lw=0.5, color=get_color_cycle(len(sweep_1))[i])
        # plt.plot(x, y, lw=0.5, color=get_color_cycle(len(sweep_1))[i])
        legend += [sweep_tag_1 + f" = {ssweep1}"]
        i += 1
    # plt.legend(legend, loc='lower left', fontsize=8, ncol=legendcol)
    # plt.legend(legend, loc='upper right', fontsize=8, ncol=legendcol)
    # plt.xlim(5.185e9, 5.21e9)
    # plt.ylim(-2, 2.5)
    # plt.ylim(-50, -35)
    plt.xlabel('freq(Hz)')
    plt.ylabel('S21(dB)')
    plt.show()

def plot_double_sweep(data, sweep_tag_1='amp', sweep_tag_2='f', plot_tag_x='amp', plot_tag_y='r_ruox',
                      baseline=None ,offset = 0, save=False, plot_Rxy =False):
    # filter mask for double sweep
    sweep1 = data[sweep_tag_1]
    sweep2 = data[sweep_tag_2]
    sweep_1 = sorted(list(dict.fromkeys(sweep1)))
    sweep_2 = sorted(list(dict.fromkeys(sweep2)))
    print(sweep_2)
    mask = {}
    for ssweep1 in sweep_1:
        mask.update({ssweep1:{}})
        for ssweep2 in sweep_2:
            mask[ssweep1].update({ssweep2 : np.logical_and(sweep1 == ssweep1, sweep2 == ssweep2)})
    fg = plt.figure()
    legend =[]
    vg=[]
    slope=[]
    if baseline is not None:
        y0 = []
        for j in range(0, len(sweep_1)):
            current_mask = mask[sweep_1[j]][baseline]
            yy = np.average(data[plot_tag_y][current_mask])
            y0.append(yy)
    else:
        y0 = 0
    newdata = {}
    for i in range(0,len(sweep_2)):
        x = []
        y = []
        for j in range(0,len(sweep_1)):
            current_mask = mask[sweep_1[j]][sweep_2[i]]
            xx, yy = calc_average(data[plot_tag_x][current_mask], data[plot_tag_y][current_mask])
            x.append(xx)
            y.append(yy)
        x = np.array(x)
        y = np.array(y)
        if i==0:
            y_previous = y
        if plot_Rxy:
            plt.plot(x, antisymetric(y)+i*offset, ls='-', marker='o', ms=0, mfc='none',color=get_color_cycle(len(sweep_2), cmap='coolwarm')[i])
            para, cov = curve_fit(linear_func, x, antisymetric(y))
            vg += [float(sweep_2[i])]
            slope += [para[0]]
        else:
            # difference = np.remainder(y - y_previous + 180, 360)
            difference = y
            if baseline is not None:
                difference = y-y0
            elif baseline == 'difference':
                difference = np.remainder(y - y_previous + 180, 360)
            plt.plot(x, difference + i * offset, ls='-', marker='o', ms=0, mfc='none', color=get_color_cycle(len(sweep_2),cmap='coolwarm')[i])
        legend += [f'{round(sweep_2[i], 2)}']
        newdata.update({f'{round(sweep_2[i], 2)}': (x, y- y_previous)})
        y_previous = y
    plt.xlim(min(x), max(x) + abs(max(x) - min(x)) / 5)
    with open(folder_path + '\\'+ 'temp', 'wb') as f:
        pickle.dump(newdata, f)


    plt.legend(legend, loc='upper right', fontsize=10, ncol=1)
    plt.xlabel(plot_tag_x)
    plt.ylabel(plot_tag_y)
    plt.show()
    if plot_Rxy:
        fg = plt.figure()
        plt.scatter(vg, slope, label='data')
        para, cov = curve_fit(convolution_gaussian_func, vg, slope, p0=[0.35,13.5,0.27412054])
        print(para, np.sum(np.diag(cov)))
        x_fit = np.linspace(min(vg),max(vg),100)
        plt.plot(x_fit,convolution_gaussian_func(x_fit, *para), '-', label= 'Fit')
        plt.xlabel(sweep_tag_2)
        plt.ylabel('slope')
        plt.show()

    if save:
        file_path = folder_path + '\\' + 'slope' + '_vs_' + 'Vg'
        np.savetxt(file_path, np.column_stack((vg,slope)), delimiter='\t')

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

def plot_cmap(data, plot_tag_x='VNA_freqs', plot_tag_y='r_ruox', plot_tag_z='VNA_log_mag', baseline=None):
    fg = plt.figure()
    gs = fg.add_gridspec(1,2,width_ratios=[0.9,0.1])
    ax = fg.add_subplot(gs[0])
    sweep1 = data[plot_tag_x]  # sweep para
    sweep2 = data[plot_tag_y]  # sweep para
    sweep_1 = list(dict.fromkeys(sweep1))  # sweep para list
    sweep_2 = list(dict.fromkeys(sweep2))  # sweep para list
    x = []
    y = []
    z = []
    for sweep1 in sweep_1:
        for sweep2 in sweep_2:
            x += [sweep1]
            y += [sweep2]
            mask = np.logical_and(data[plot_tag_x]==sweep1, data[plot_tag_y]==sweep2)
            z += [np.average(data[plot_tag_z][mask])]
    x = np.array(x)
    y = np.array(y)
    z = np.array(z)
    if baseline is not None:
        z0 = z[y == baseline]
        for sweep in sweep_2:
            z[y == sweep] = (z[y == sweep])-z0

    ax.scatter(x, y, c=z, s=100, cmap='coolwarm', marker='|')
    #ax.set_ylim([0,5])
    cax = fg.add_subplot(gs[1])
    norm = mpl.colors.Normalize(vmin=np.min(z), vmax=np.max(z))
    cb = plt.colorbar(cm.ScalarMappable(norm=norm, cmap='coolwarm'), cax=cax,
                      ticks=np.linspace(np.min(z), np.max(z), 10),
                      label=plot_tag_z)
    ax.set_xlabel(plot_tag_x)
    ax.set_ylabel(plot_tag_y)
    plt.show()



'''------------------------input before run------------------------'''


# folder_path = r"C:\Users\ICET\Desktop\Data\SD\20230126_SD_006b\transport\Hall\data"
folder_path = r'C:\Users\ICET\Desktop\Data\SD\20230126_SD_006b\DC_field_transmission\02182023_wiggle_field\20230218_long_avg_0V'
data = load_data_from_folder(folder_path)
print(data.keys())

# data = limitdata(data, low_limit=3.61e9, high_limit=3.65e9, tag='VNA_freqs')
# data = limitdata(data, low_limit=0.4, high_limit=0.9, tag='vg_sur')
# data.update({'I': np.sqrt(data['I_x'] ** 2 + data['I_y'] ** 2)})
# data = limitdata(data, low_limit=20e-9, high_limit=150e-9, tag='I_x')
# data = calculate_R(data, tag_I='I_x',tag_V='V_x')

# plot_single_sweep_spectrum(data,
#                            sweep_tag_1='vg_sur',
#                            plot_tag_x='VNA_freqs',
#                            plot_tag_y='VNA_log_mag',
#                            legendcol=2
#                            )

# plot_single_sweep(data,
#                   sweep_tag_1='vg_sur',
#                   plot_tag_x='VNA_freqs',
#                   plot_tag_y='VNA_log_mag',
#                   save=False,
#                   yerrbar=False
#                   )
#
# plot_cmap(data,
#           plot_tag_x='VNA_freqs',
#           plot_tag_y='vg_sur',
#           plot_tag_z='VNA_log_mag',
#           baseline=1.4)

#
# plot_single_sweep(data,
#                   sweep_tag_1='V_gate',
#                   plot_tag_x='V_gate',
#                   plot_tag_y='I_x',
#                   save=True,
#                   yerrbar=True
#                   )
#
# plot_single_sweep(data,
#                   sweep_tag_1='V_gate',
#                   plot_tag_x='V_gate',
#                   plot_tag_y='V_x',
#                   save=True,
#                   yerrbar=True
#                   )
# plot_single_sweep_calc_R(data,
#                         sweep_tag_1='V_gate',
#                         plot_tag_x='V_gate',
#                         plot_tag_V='V_x',
#                         plot_tag_I='I_x',
#                         save=True,
#                         yerrbar=True
#                         )

# plot_cmap(data,
#           plot_tag_x='V_gate',
#           plot_tag_y='V_B',
#           plot_tag_z='R',
#           baseline=None)

plot_double_sweep(data,
                  sweep_tag_1='VNA_freqs',
                  sweep_tag_2='vg_sur',
                  plot_tag_x='VNA_freqs',
                  plot_tag_y='VNA_log_mag',
                  baseline=0.0,
                  offset=0.0,
                  save=True)

# plot_double_sweep(data,
#              sweep_tag_1='V_B',
#              sweep_tag_2='V_gate',
#              plot_tag_x='V_B',
#              plot_tag_y='R',
#              offset=0.0,
#              save=True)