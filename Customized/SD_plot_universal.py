# -*- coding: utf-8 -*-
"""
@author: Shilling Du
@date: Feb 16, 2022
"""

import time, datetime, sys, os, string
import matplotlib as mpl
import matplotlib.pyplot as plt

from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib import cm
import numpy as np
from collections import OrderedDict
from operator import getitem
import re
from io import StringIO
import scipy
from scipy.optimize import curve_fit
from scipy import signal
from scipy import interpolate
import pickle
import copy
from Instrument_Drivers.thermometer.Cernox import *

global global_legend, inside_plot_flag
global_legend = []
inside_plot_flag = True
def plot_fig(name = 'temp',folder_path = r'C:\Users\ICET\Desktop\Data\SD\20230317_SD_004_1_wet_magprobe\graph', save = False):
    global inside_plot_flag
    if inside_plot_flag:
        print('plot')
        plt.tight_layout()
        plt.title('')
        if not save:
            plt.show()
        else:
            real_path = os.path.join(folder_path, name)
            plt.savefig(real_path)
  
# Font
font = {'family': "Arial",
  "weight": 'normal',
  "size":5}
mpl.rc("font",**font)
mpl.rcParams['mathtext.fontset'] = 'custom'
mpl.rcParams['mathtext.bf'] = 'sans:italic:bold'

# Linewidth
linewidth = 0.5
mpl.rcParams['axes.linewidth'] = linewidth
mpl.rcParams['axes.labelweight'] = 'normal'
mpl.rcParams['lines.linewidth'] = linewidth
mpl.rcParams['xtick.major.width'] = linewidth
mpl.rcParams['xtick.major.size'] = 1
mpl.rcParams['ytick.major.width'] = linewidth
mpl.rcParams['ytick.major.size'] = 1
mpl.rcParams['legend.fontsize'] = 3
mpl.rcParams['axes.formatter.limits'] = -3, 3
# layout
fig_size = np.asarray([8,5])
fig_size = fig_size / 2.54


def my_data_dict(data, read_data, axis):
    if len(list(data)) == 0:
        for i in range(len(axis)):
            data.update({axis[i]:np.array(read_data[:, i])})
    else:
        for col in range(read_data.shape[1]):
            if axis[col] in data.keys():
                data[axis[col]] = np.append(data[axis[col]], np.array(read_data[:, col]))
            else:
                data.update({axis[col]: np.array(read_data[:, col])})
        length = [len(item) for key, item in data.items()]
        if min(length)!= max(length):
            for key in data.keys():
                if len(data[key])<max(length):
                    data[key] = np.append(np.zeros(max(length)-len(data[key])),data[key])
    return data

def load_data_from_file(name):
    readout = np.loadtxt(name)
    # dummy way of getting axis
    file = name
    data = {}
    with open(file, 'rb') as f:
        file_content = f.readlines()
    for i in range(0, len(file_content)):
        if b'#' not in file_content[i]:
            break
    axis = str(file_content[i - 1][1:].decode('utf-8')).split()
    axis = ['_'.join(x.split('_')[:-1]) for x in axis]
    data = my_data_dict(data, readout, axis)
    return data

def load_data_from_folder(folder_path):
    order = 0
    ordered_file_name_dict = get_ordered_file_name_dict(folder_path)
    data = {}
    for name in ordered_file_name_dict.keys():
        if 'DS' not in name:
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
                path = os.path.join(root, name)
                file_name_dict.update({path: {}})
                file_name_dict[path].update({'path': os.path.join(root, name),
                                             'time': os.path.getctime(os.path.join(root, name)),
                                             'dir': root,
                                             })

    # Reorder the file name dict with the modified time, if want to use the created time order, change the getmtime -> getctime
    ordered_file_name_dict = OrderedDict(sorted(file_name_dict.items(),
                                                key=lambda x: getitem(x[1], 'time')))
    return ordered_file_name_dict

def calc_average(x,y,type=None):
    x = np.array(x)
    y = np.array(y)
    if type == 'logmag':
        yy = np.average(np.power(10, y / 20))
        yy = 20 * np.log10(yy)
    else:
        yy = np.nanmean(y)
    return np.average(x),yy

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
    new_data = copy.deepcopy(data)
    mask = np.logical_and(new_data[tag] >= low_limit, new_data[tag] <= high_limit)
    for key in data.keys():
        new_data[key] = np.array(new_data[key])[mask]
    return new_data

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

def filter_nan(x,y):
    mask = [np.logical_and(np.isfinite(x),np.isfinite(y))]
    mask = tuple(mask)
    return x[mask], y[mask]

def insert(fig,image_path,left,bottom,width,height):
    ax = fig.add_axes([left,bottom,width,height])  # left, bottom, width, height
    fig_insert = plt.imread(image_path)
    ax.imshow(fig_insert)
    ax.axis('off')

def get_sweep(data,tag):
    data[tag] = np.array([round(x, 5) for x in data[tag]])  # round sweep para, avoiding multiple value at same sweep value
    sweep = data[tag]
    sweep_list = sorted(list(dict.fromkeys(sweep)))
    return sweep_list

def add_vline(vlines,y,label=''):
    plt.vlines(x=vlines, ymin=min(y), ymax=max(y), color='grey', ls='--')
    for i, x in enumerate(vlines):
        plt.text(x, min(y), f'{label}:{(x/1e9)}', rotation=90, verticalalignment='bottom')

"""------------------Plot configs-----------------------------------"""
def plot_single_sweep(data, sweep_tag_1, plot_tag_x='VNA_freqs', plot_tag_y='VNA_log_mag',save=False,yerrbar=False,continuous=False):
    global global_legend
    # filter mask for single sweep
    data[sweep_tag_1] = np.array([round(x, 5) for x in
                         data[sweep_tag_1]])  # round sweep para, avoiding multiple value at same sweep value
    sweep1 = data[sweep_tag_1]  # sweep para
    sweep_1 = list(dict.fromkeys(sweep1))  # sweep para list
    mask = {}  # mask dictionary
    for ssweep1 in sweep_1:
        mask.update({ssweep1: sweep1 == ssweep1})
    # Plot
    if not continuous:
        fg = plt.figure(figsize=fig_size, dpi=300)
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
        y = np.array(y)
        yerr = np.array(yerr)
        dataToSave = np.column_stack((x, y, yerr))
        axis += 'errorbar\t\t\t\t'
        plt.plot(x, y, ls='-', ms=0.5, mfc='none')
        plt.fill_between(x, y-yerr, y+yerr, alpha=0.4, ls='--')
        global_legend += ['']
    else:
        dataToSave = np.column_stack((x, y))
        plt.plot(x, y, ls='-', ms=0.5, mfc='none')

    file_path = folder_path + '\\' + plot_tag_x +'_vs_' + plot_tag_y
    if save:
        np.savetxt(file_path, dataToSave, delimiter='\t',
               header= axis
               )
    plot_fig()

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
    fg = plt.figure(figsize=fig_size,dpi=300)
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
    fg = plt.figure(figsize=fig_size,dpi=300)
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
    data[sweep_tag_1] = np.array([round(x, 5) for x in
                         data[sweep_tag_1]])  # round sweep para, avoiding multiple value at same sweep value
    data[sweep_tag_2] = np.array([round(x, 5) for x in
                         data[sweep_tag_2]])  # round sweep para, avoiding multiple value at same sweep value
    # filter mask for double sweep
    sweep1 = data[sweep_tag_1]
    sweep2 = data[sweep_tag_2]
    sweep_1 = sorted(list(dict.fromkeys(sweep1)))
    sweep_2 = sorted(list(dict.fromkeys(sweep2)))
    def get_mask(ssweep1,ssweep2):
        return np.array(np.logical_and(sweep1 == ssweep1, sweep2 == ssweep2))
    if inside_plot_flag:
        fg = plt.figure(figsize=fig_size,dpi=300)
    legend =[]
    vg=[]
    slope=[]
    if baseline is not None and baseline!='difference':
        if isinstance(baseline,float) or isinstance(baseline,int):
            y0 = []
            for j in range(0, len(sweep_1)):
                current_mask = get_mask(sweep_1[j], baseline)
                yy = np.average(data[plot_tag_y][current_mask])
                y0.append(yy)
        else:
            y0 = []
            for j in range(0, len(sweep_1)):
                yy = np.average(baseline[plot_tag_y][baseline[sweep_tag_1]==sweep_1[j]])
                y0.append(yy)
    else:
        y0 = 0
    newdata = {}
    for i in range(0,len(sweep_2)):
        x = []
        y = []
        for j in range(0,len(sweep_1)):
            current_mask = get_mask(sweep_1[j], sweep_2[i])
            if 'log_mag' in plot_tag_y:
                # print(type(data[plot_tag_x]), np.shape(data[plot_tag_x]))
                # print(type(data[plot_tag_y]), np.shape(data[plot_tag_y]))
                # print(type(current_mask), current_mask)
                xx, yy = calc_average(data[plot_tag_x][current_mask], data[plot_tag_y][current_mask], type='logmag')
            else:
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
                # difference -= np.average(difference)
            if baseline == 'difference':
                # difference = np.remainder(y - y_previous + 180, 360)
                difference = y-y_previous
            x,difference = filter_nan(x,difference)
            plt.plot(x, difference + i * offset, ls='-', marker='o', ms=0, mfc='none', color=get_color_cycle(len(sweep_2),cmap='coolwarm')[i])
        legend += [f'{round(sweep_2[i], 2)}']
        # newdata.update({f'{round(sweep_2[i], 2)}': (x, y- y_previous)})
        y_previous = y
    plt.xlim(min(x), max(x) + abs(max(x) - min(x)) / 5)
    # with open(folder_path + '\\'+ 'temp', 'wb') as f:
    #     pickle.dump(newdata, f)

    plt.legend(legend)
    plt.xlabel(plot_tag_x)
    plt.ylabel(plot_tag_y)
    
#   plt.xlabel('B(mT)')
#   plt.ylabel('Rxy(ohm)')
#   plot_fig(name = 'Rxy_vs_B')
    y = difference + i * offset
    # vlines = [4.435e9,5.924e9,6.968e9,7.869e9] #sd006c
    # add_vline(vlines,y)
    #
    # vlines = [6.104e9, 6.414e9, 6.642e9, 7.138e9] #sd004
    # add_vline(vlines,y)

    # vlines = [4.420e9, 4.274e9, 6.583e9, 6.992e9] #sd006d
    # add_vline(vlines,y)

    # vlines = [6032.4e6,6335e6,6620e6,7104e6]  # sd003a
    # add_vline(vlines,y)

    # vlines = [6081e6,6225e6,6789e6,7093e6]  # sd004_1_mag_probe, no hemt
    # add_vline(vlines,y)

    plot_fig()

    if plot_Rxy:
        fg = plt.figure(figsize=np.asarray([10,8.5])/2.54,dpi=300)
        plt.scatter(vg, slope, label='data')
        para, cov = curve_fit(convolution_gaussian_func, vg, slope, p0=[0.35,13.5,0.27412054])
        print(para, np.sum(np.diag(cov)))
        x_fit = np.linspace(min(vg),max(vg),100)
        plt.plot(x_fit,convolution_gaussian_func(x_fit, *para), '--', label= 'Fit', c='grey')
        plt.xlabel('Gate Voltage(V)')
        plt.ylabel('Hall resistance(m^3/C)')
        plot_fig(name = 'Vg_vs_RH')

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
        fg = plt.figure(figsize=fig_size,dpi=300)
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

    fg = plt.figure(figsize=fig_size,dpi=300)
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
    fg = plt.figure(figsize=fig_size,dpi=300)
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
            z[y == sweep] -= np.max(z[y == sweep])

    ax.scatter(x, y, c=z, s=100, cmap='coolwarm', marker='|')
    #ax.set_ylim([0,5])
    cax = fg.add_subplot(gs[1])
    norm = mpl.colors.Normalize(vmin=np.min(z), vmax=np.max(z))
    cb = plt.colorbar(cm.ScalarMappable(norm=norm, cmap='coolwarm'), cax=cax,
                      ticks=np.round(np.linspace(np.min(z), np.max(z), 10),3),
                      label=plot_tag_z)
    ax.set_xlabel(plot_tag_x)
    ax.set_ylabel(plot_tag_y)
    plt.show()



'''------------------------input before run------------------------'''

"""For MW spectrum sweeping AC Mag(wiggle_B) field BEGIN"""
# folder_path = r'C:\Users\ICET\Desktop\Data\SD\20230428_SD006b_mag_probe_addhemt\Transport\4pts\data\20230504\B_wiggle\20230504_sweep_B_4000to7200MHz'
# data = load_data_from_folder(folder_path)
# # data = limitdata(data, 5e9, 6e9, tag='VNA_freqs')
# plot_double_sweep(data,
#                   sweep_tag_1='VNA_freqs',
#                   sweep_tag_2='wiggle_B',
#                   plot_tag_x='VNA_freqs',
#                   plot_tag_y='VNA_log_mag',
#                   baseline=3.504,
#                   offset=0.2,
#                   save=False)

"""For MW spectrum sweeping DC Mag field BEGIN"""
# folder_path = r'C:\Users\ICET\Desktop\Data\SD\20230428_SD006b_mag_probe_addhemt\compressibility\sweep2'
# data = load_data_from_folder(folder_path)
# # data = limitdata(data, 5.0e9, 5.5e9, tag='VNA_freqs')
# print(get_sweep(data,'v_sur'))
# inside_plot_flag = False
# fig_size = [12/2.54,8/2.54]
# fig = plt.figure(figsize=fig_size, dpi=300)
# plot_double_sweep(data,
#                   sweep_tag_1='VNA_freqs',
#                   sweep_tag_2='v_sur',
#                   plot_tag_x='VNA_freqs',
#                   plot_tag_y='VNA_log_mag',
#                   baseline=1.3,
#                   offset=0.02,
#                   save=False,
#                   )
# add_vline([4.764e9,4.845e9,4.950e9,5.047e9,5.17e9,5.194e9,5.285e9],[-0.1,0.55])
# plt.tight_layout()
# plt.show()

"""For MW spectrum sweeping DC Mag field STOP"""

"""For MW spectrum sweeping DC+ AC gate BEGIN"""
# folder_path = r'C:\Users\ICET\Desktop\Data\SD\20230428_SD006b_mag_probe_addhemt\compressibility\DCACsweep_20min'
# save_path = r'C:\Users\ICET\Desktop\Data\SD\20230428_SD006b_mag_probe_addhemt\compressibility\fig_DCACsweep_20min\difference'
# data = load_data_from_folder(folder_path)
# dcbias_list = get_sweep(data, 'vg_bias')
# amp_list = get_sweep(data,'vg_Vrms')
# print(amp_list, dcbias_list)
# inside_plot_flag = False
# baseline = limitdata(data, low_limit=amp_list[0], high_limit=amp_list[0], tag='vg_Vrms')
# baseline = limitdata(baseline, low_limit=dcbias_list[0], high_limit=dcbias_list[0], tag='vg_bias')
# for amp in amp_list:
#     fg = plt.figure(figsize=fig_size, dpi=300)
#     plot_double_sweep(limitdata(data, low_limit=amp, high_limit=amp, tag='vg_Vrms'),
#                       sweep_tag_1='VNA_freqs',
#                       sweep_tag_2='vg_bias',
#                       plot_tag_x='VNA_freqs',
#                       plot_tag_y='VNA_log_mag',
#                       baseline=baseline,
#                       offset=0.05,
#                       save=False)
#     plt.title(f'Vrms = {amp}V, legend for different DC bias')
#     plt.tight_layout()
#     plt.savefig(os.path.join(save_path,f'amplitude_{amp}.png'))
#     plt.close()
# for dcbias in dcbias_list:
#     fg = plt.figure(figsize=fig_size, dpi=300)
#     plot_double_sweep(limitdata(data, low_limit=dcbias, high_limit=dcbias, tag='vg_bias'),
#                       sweep_tag_1='VNA_freqs',
#                       sweep_tag_2='vg_Vrms',
#                       plot_tag_x='VNA_freqs',
#                       plot_tag_y='VNA_log_mag',
#                       baseline=baseline,
#                       offset=0.05,
#                       save=False)
#     plt.title(f'DCbias = {dcbias}V, legend for different V_rms')
#     plt.tight_layout()
#     plt.savefig(os.path.join(save_path,f'bias_{dcbias}.png'))
#     plt.close()
"""For MW spectrum sweeping DC+ AC gate STOP"""

"""For SD006b Rxy BEGIN"""
#folder_path = r"C:\Users\ICET\Desktop\Data\SD\20230126_SD_006b\transport\Hall\data"
#folder_path = r"/Users/chellybone/Library/CloudStorage/OneDrive-WashingtonUniversityinSt.Louis/wustl/2023 Spring/data/20230126_SD_006b_ICET/transport/Hall/data"
#data = load_data_from_folder(folder_path)
#data = limitdata(data, low_limit=20e-9, high_limit=150e-9, tag='I_x')
#data = calculate_R(data, tag_I='I_x',tag_V='V_x')
#data['V_B'] = data['V_B']/1.4*44
#plot_double_sweep(data,
#            sweep_tag_1='V_B',
#            sweep_tag_2='V_gate',
#            plot_tag_x='V_B',
#            plot_tag_y='R',
#            offset=0.0,
#            save=True,
#                 plot_Rxy=True)
"""For SD006b Rxy STOP"""
  
"""For Random MW ploting: """
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



"""For Transport- check contact ploting: """
# inside_plot_flag = False
# folder_path = r"C:\Users\ICET\Desktop\Data\SD\20230428_SD006b_mag_probe_addhemt\Transport\Check_contact\data"
# name_dict = get_ordered_file_name_dict(folder_path)
# fg = plt.figure(figsize=fig_size, dpi=300)
# for key, value in name_dict.items():
#     file_path = value['path']
#     data = load_data_from_file(file_path)
#     global_legend += [key.split('.')[0]]
#     plot_single_sweep(data,
#                       sweep_tag_1='V_sur_read',
#                       plot_tag_x='V_sur_read',
#                       plot_tag_y='V_lead_y',
#                       save=False,
#                       yerrbar=True,
#                       continuous=True)
# plt.legend(global_legend)
# plt.xlabel('Current (uA)')
# plt.ylabel('Voltage (V)')
# plt.title('Check contact V_y vs I')
# plt.tight_layout()
# insert(fg,
#        image_path=r'C:\Users\ICET\Desktop\Data\SD\20230428_SD006b_mag_probe_addhemt\Transport\Check_contact\measure_config.png',
#        left=0.6,
#        bottom=0.6,
#        width=0.2,
#        height=0.2
#        )
# plt.show()
"""For Transport- check contact ploting END """

"""For Transport- 4pts ploting: """
# inside_plot_flag = False
# fg = plt.figure(figsize=fig_size, dpi=300)
# folder_path = r"C:\Users\ICET\Desktop\Data\SD\20230428_SD006b_mag_probe_addhemt\051823_doublecheckTransport\data\20230518"
# data = load_data_from_folder(folder_path)
# data = calculate_R(data, tag_I='Ix_100ohm', tag_V='Vx')
# data['R'] *= 100
# plot_single_sweep(data,
#                   sweep_tag_1='V_g_sur',
#                   plot_tag_x='V_g_sur',
#                   plot_tag_y='R',
#                   save=False,
#                   yerrbar=True,
#                   continuous=True
#                   )
# plt.xlabel('Vg(V)')
# plt.ylabel('R(ohm)')
# insert(fg,
#        image_path=r'C:\Users\ICET\Desktop\Data\SD\20230428_SD006b_mag_probe_addhemt\Transport\4pts\no_drain_addI.jpg',
#        left=0.1,
#        bottom=0.65,
#        width=0.3,
#        height=0.3
#        )
# plt.tight_layout()
# plt.show()

"""For Transport- 4pts END """

"""For ploting cooling down"""
folder_path = r"C:\Users\ICET\Desktop\Data\SD\20230524_SD_MoRe_2_4pts\heating\data"
data = load_data_from_folder(folder_path)
data = calculate_R(data, tag_I='I_100ohm_x', tag_V='V_x')
data['R'] *= 100
data.update({'temp': np.array([float(get_T_cernox_3(x)) for x in data['V_t']])})
# data = limitdata(data,0,11,'temp')
x = []
y = []
yerr = []
for temp in np.linspace(np.max(data['temp']),np.min(data['temp']),1001):
    all_R = []
    spacing = (np.max(data['temp'])-np.min(data['temp']))/1000
    mask = np.logical_and(data['temp']>=temp-spacing/2,data['temp']<=temp+spacing/2)
    all_R = data['R'][mask]
    if len(all_R)>0:
        x += [temp]
        y += [np.average(all_R)]
        yerr += [np.std(all_R)/np.sqrt(len(all_R))]
plt.figure(figsize=fig_size,dpi=300)
plt.errorbar(x,y,yerr)
plt.xlabel('T(K)')
plt.ylabel(r'R($\Omega$)')
plt.title(r'MoRe Resistance vs temp 053123, ICET heating/cooling')
plt.tight_layout()
plt.show()




