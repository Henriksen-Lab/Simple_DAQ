# -*- coding: utf-8 -*-
"""
@author: Shilling Du
@date: Feb 16, 2022
"""

import time, datetime, sys, os, string
from datetime import datetime as dt
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib import cm

import numpy as np
import scipy
from scipy.optimize import curve_fit

import pickle
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
parent_parent_dir = os.path.dirname(parent_dir)
if parent_parent_dir not in sys.path:
    sys.path.append(parent_parent_dir)
from Instrument_Drivers.thermometer.Cernox import *
from Instrument_Drivers.thermometer.RuOx import *
from SD_FigureFormat import *
from SD_LoadData import *
from SD_Func import *

""" To use this Plotter, below is an example: Example .py
import sys
import numpy as np
ploter_path = r'C:\Users\Henriksen Lab\Documents\GitHub\Simple_DAQ\Customized\SD_plot'
# note, the path of '\Simple_DAQ\Customized\SD_plot' on each local PC might be different, check the path before usage
if ploter_path not in sys.path:
    sys.path.append(ploter_path)
from SD_plot_universal import *

------------------------------------------your code starts here
folder_path = r'/Users/chellybone/Library/CloudStorage/OneDrive-WashingtonUniversityinSt.Louis/wustl/HLab/Project_MLGM/DATA/20230428_SD006b_MagProbe_addhemt/compressibility/sweep2'
data = load_data_from_folder(folder_path)
plot_double_sweep(data,
    sweep_tag_1='VNA_freqs',
    sweep_tag_2='v_sur',
    plot_tag_x='VNA_freqs',
    plot_tag_y='VNA_log_mag',
    avgtype='logmag',
    baseline=1.3,
    offset=0.02,
    inside_plot_flag = True)
"""

folder_path =''
def plot_fig(note='', inside_plot_flag=True, timestamp= None):
    if inside_plot_flag:
        print('Inside func plot')
        if timestamp is None:
            today = dt.now().strftime("%Y%m%d")
        else:
            today = get_ymd(timestamp)
        plt.title(f'{today}\n {note}', fontsize=5, loc='left')
        plt.tight_layout()
        plt.show()


def filter_nan(x, y):
    mask = [np.logical_and(np.isfinite(x), np.isfinite(y))]
    mask = tuple(mask)
    return x[mask], y[mask]


"""------------------Plot configs-----------------------------------"""
def plot_single_sweep(data, sweep_tag_1, plot_tag_x='VNA_freqs', plot_tag_y='VNA_log_mag', avgtype=None, yerrbar=False, inside_plot_flag=True, timestamp=None):
    if timestamp is None:
        if 'timestamp' in data.keys():
            timestamp = min(data['timestamp'])
    # filter mask for single sweep
    sweep1 = data[sweep_tag_1]
    sweep_1 = get_sweep(data,sweep_tag_1)
    sweep_1_info = get_sweep_info(data,sweep_tag_1)
    # Plot
    if inside_plot_flag:
        fg = plt.figure(figsize=fig_size, dpi=300)
    x = []
    y = []
    yerr = []
    for ssweep1 in sorted(sweep_1):
        current_mask = sweep1 == ssweep1
        xx = data[plot_tag_x][current_mask]
        yy = data[plot_tag_y][current_mask]
        x += [calc_average(xx)]
        y += [calc_average(yy,type=avgtype)]
        yerr += [np.std(yy)]
    plt.xlabel(plot_tag_x)
    plt.ylabel(plot_tag_y)
    plt.plot(x, y, ls='-', ms=0.5, mfc='none')
    data.update({f'avg_{plot_tag_x}_x': x})
    data.update({f'avg_{plot_tag_y}_y': y})
    data.update({f'avg_{plot_tag_y}_yerr': yerr})
    if yerrbar:
        y = np.array(y)
        yerr = np.array(yerr)
        plt.fill_between(x, y - yerr, y + yerr, alpha=0.4, ls='--')
    note = f'{plot_tag_y} vs {plot_tag_x}\n sweeping {sweep_tag_1}: {sweep_1_info}'
    plot_fig(note,inside_plot_flag=inside_plot_flag, timestamp=timestamp)
    return data


def plot_double_sweep(data, sweep_tag_1='amp', sweep_tag_2='f', plot_tag_x='amp', plot_tag_y='r_ruox', avgtype=None,
                      baseline=None, offset=0, save=False, inside_plot_flag = True, timestamp=None):
    if timestamp is None:
        if 'timestamp' in data.keys():
            timestamp = min(data['timestamp'])
    # filter mask for Double sweep
    sweep1 = data[sweep_tag_1]
    sweep_1 = get_sweep(data,sweep_tag_1)
    sweep_1_info = get_sweep_info(data,sweep_tag_1)
    
    sweep2 = data[sweep_tag_2]
    sweep_2 = get_sweep(data,sweep_tag_2)
    sweep_2_info = get_sweep_info(data,sweep_tag_2)

    if sweep_tag_1 == plot_tag_x:
        sweep_tag = sweep_tag_2
        sweep = sweep2
        sweep_list = sweep_2
        note = f'{plot_tag_y} vs {plot_tag_x}\n sweeping {sweep_tag_2}: {sweep_2_info}'
        secondsweep = sweep1
        secondsweep_list = sweep_1
        secondsweep_tag = sweep_tag_1
    elif sweep_tag_2 == plot_tag_x:
        sweep_tag = sweep_tag_1
        sweep = sweep1
        sweep_list = sweep_1
        note = f'{plot_tag_y} vs {plot_tag_x}\n sweeping {sweep_tag_1}: {sweep_1_info}'
        secondsweep = sweep2
        secondsweep_list = sweep_2
        secondsweep_tag = sweep_tag_2
    def get_mask(ssweep, secondssweep):
        return np.array(np.logical_and(sweep == ssweep, secondsweep == secondssweep))

    if inside_plot_flag:
        fg = plt.figure(figsize=fig_size, dpi=300)
    legend = []
    vg = []
    slope = []
    
    if baseline is not None and baseline != 'difference':
        if isinstance(baseline, float) or isinstance(baseline, int): # baseline is constant
            current_mask = sweep == baseline
            x0, y0 = calc_average_spectrum(data[plot_tag_x][current_mask],data[plot_tag_y][current_mask], type=avgtype)
        else: # baseline is a dict
            x0, y0 = calc_average_spectrum(baseline[plot_tag_x], baseline[plot_tag_y], type=avgtype)
    else:
        y0 = 0
        
    newdata = {}
    for i in range(0, len(sweep_list)):
        current_mask = sweep==sweep_list[i]
        x, y = calc_average_spectrum(data[plot_tag_x][current_mask],data[plot_tag_y][current_mask], type=avgtype)
        x = np.array(x)
        y = np.array(y)
        if i == 0:
            y_previous = y
        difference = y
        if baseline is not None:
            difference = y - y0
        if baseline == 'difference':
            difference = y - y_previous
        x, difference = filter_nan(x, difference)
        plt.plot(x, difference + i * offset, ls='-', marker='o', ms=0, mfc='none',c=get_color_cycle(len(sweep_list))[i])
        legend += [f'{round(sweep_list[i], 2)}']
        newdata.update({f'{round(sweep_2[i], 2)}': (x, difference)})
        y_previous = y
    plt.xlim(min(x), max(x) + abs(max(x) - min(x)) / 5)
    if save:
        with open('temp', 'wb') as f:
          pickle.dump(newdata, f)
    plt.legend(legend)
    plt.xlabel(plot_tag_x)
    plt.ylabel(plot_tag_y)
    
    note = f'{plot_tag_y} vs {plot_tag_x}\n sweeping {sweep_tag_1}: {sweep_1_info}'
    plot_fig(note,inside_plot_flag=inside_plot_flag, timestamp=timestamp)
    return data


def plot_cmap(data, plot_tag_x='VNA_freqs', plot_tag_y='r_ruox', plot_tag_z='VNA_log_mag', avgtype=None, inside_plot_flag = True, timestamp=None):
    if timestamp is None:
        if 'timestamp' in data.keys():
            timestamp = min(data['timestamp'])
    if inside_plot_flag:
        fg = plt.figure(figsize=fig_size, dpi=300)
    gs = fg.add_gridspec(1, 2, width_ratios=[0.9, 0.1])
    ax = fg.add_subplot(gs[0])
    
    # filter mask for Double sweep
    sweep1 = data[plot_tag_x]
    sweep_1 = get_sweep(data,plot_tag_x)
    sweep_1_info = get_sweep_info(data,plot_tag_x)
  
    sweep2 = data[plot_tag_y]
    sweep_2 = get_sweep(data,plot_tag_y)
    sweep_2_info = get_sweep_info(data,plot_tag_y)

    x = []
    y = []
    z = []
    for sweep1 in sweep_1:
        for sweep2 in sweep_2:
            x += [sweep1]
            y += [sweep2]
            mask = np.logical_and(data[plot_tag_x] == sweep1, data[plot_tag_y] == sweep2)
            z += [calc_average(data[plot_tag_z][mask], type=avgtype)]
    x = np.array(x)
    y = np.array(y)
    z = np.array(z)

    ax.scatter(x, y, c=z, s=10, marker='|')
    cax = fg.add_subplot(gs[1])
    norm = mpl.colors.Normalize(vmin=np.min(z), vmax=np.max(z))
    cb = plt.colorbar(cm.ScalarMappable(norm=norm, cmap='coolwarm'), cax=cax,
                      ticks=np.round(np.linspace(np.min(z), np.max(z), 10), 3),
                      label=plot_tag_z)
    ax.set_xlabel(plot_tag_x)
    ax.set_ylabel(plot_tag_y)
    note = f'{plot_tag_y} vs {plot_tag_x}\n colormap {plot_tag_z}'
    plot_fig(note,inside_plot_flag=inside_plot_flag, timestamp=timestamp)
