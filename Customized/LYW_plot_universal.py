# -*- coding: utf-8 -*-
"""
@author: Shilling Du
@date: Feb 16, 2022
"""

import time, datetime, sys, os, string
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.pyplot import text
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

global global_legend
global_legend = []

def plot_fig(name = 'temp', folder_path = None, save = False):
    print('plot')
    plt.tight_layout()
    if not save:
        plt.show()
    else:
        folder_path = folder_path
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
linewidth = 1
mpl.rcParams['axes.linewidth'] = linewidth
mpl.rcParams['axes.labelweight'] = 'normal'
mpl.rcParams['lines.linewidth'] = 0.5
mpl.rcParams['xtick.major.width'] = linewidth
mpl.rcParams['xtick.major.size'] = 1
mpl.rcParams['ytick.major.width'] = linewidth
mpl.rcParams['ytick.major.size'] = 1
mpl.rcParams['legend.fontsize'] = 4

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
                file_name_dict.update({name: {}})
                file_name_dict[name].update({'path': os.path.join(root, name),
                                             'time': os.path.getctime(os.path.join(root, name)),
                                             'dir': root,
                                             })
    # Reorder the file name dict with the modified time, if want to use the created time order, change the getmtime -> getctime
    ordered_file_name_dict = OrderedDict(sorted(file_name_dict.items(),
                                                key=lambda x: getitem(x[1], 'time')))
    return ordered_file_name_dict



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

def add_column(file_path,column_name='new_para',value=0):
    data = load_data_from_file(file_path)
    folder_path = os.path.dirname(file_path)
    random_name = list(data.keys())[0]
    data.update({column_name:np.full(len(data[random_name]),value)})
    save_data(folder_path, data)

def calc_average(x,y,type=None):
    yy = np.nanmean(y)
    return np.average(x),yy
  
def filter_nan(x,y):
    mask = [np.logical_and(np.isfinite(x),np.isfinite(y))]
    mask = tuple(mask)
    return x[mask], y[mask]
  
def omega3_fit_func(x, a, b):
    return 1/(a * np.sqrt(1+b*(2*np.pi*x)**2))

def linear_func(x, A, B):
    y = A * x +B
    return y



"""------------------Plot configs-----------------------------------"""
def plot_single_sweep(data, sweep_tag_1, plot_tag_x, plot_tag_y, save=False, yerrbar=False, continuous=False):
    global global_legend
    # filter mask for single sweep
    data[sweep_tag_1] = np.array([round(x, 3) for x in
                         data[sweep_tag_1]])  # round sweep para, avoiding multiple value at same sweep value
    sweep1 = data[sweep_tag_1]  # sweep para
    sweep_1 = list(dict.fromkeys(sweep1))  # sweep para list
    mask = {}  # mask dictionary
    for ssweep1 in sweep_1:
        mask.update({ssweep1: sweep1 == ssweep1})
    # Plot
    if not continuous:
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
        yy = data[plot_tag_y][current_mask]
        x += [np.average(xx)]
        y += [np.average(yy)]
#       yerr += [np.std(yy)]
        plt.xlabel(plot_tag_x)
        plt.ylabel(plot_tag_y)
        
    #prepare for save data, just in case
    axis = plot_tag_x +'\t\t\t\t' + plot_tag_y + '\t\t\t\t'
    data.update({f'avg_{plot_tag_x}_x':x})
    data.update({f'avg_{plot_tag_y}_y': y})
    data.update({f'avg_{plot_tag_y}_yerr': yerr})
    file_path = folder_path + '\\' + plot_tag_x +'_vs_' + plot_tag_y
    
    if yerrbar:
        print('error bar')
        # plt.errorbar(x, y, yerr, ls='--', marker='o', ms=5, mfc='none')
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

    if save:
        np.savetxt(file_path, dataToSave, delimiter='\t',
               header= axis
               )
    plot_fig()



def plot_double_sweep(data, sweep_tag_1, sweep_tag_2, plot_tag_x, plot_tag_y,
                      baseline=None ,offset = 0, save=False, fit =False):
    # filter mask for double sweep
    sweep1 = data[sweep_tag_1]
    sweep2 = data[sweep_tag_2]
    sweep2 = np.array([round(x, 5) for x in sweep2])  # round sweep para, avoiding multiple value at same sweep value
    sweep_1 = sorted(list(dict.fromkeys(sweep1)))
    sweep_2 = sorted(list(dict.fromkeys(sweep2)))

    mask = {}
    for ssweep1 in sweep_1:
        mask.update({ssweep1:{}})
        for ssweep2 in sweep_2:
            mask[ssweep1].update({ssweep2 : np.logical_and(sweep1 == ssweep1, sweep2 == ssweep2)})
    fg = plt.figure(figsize=fig_size,dpi=300)
    legend =[]
    vg=[]
    slope=[]
    if baseline is not None and baseline!='difference':
        y0 = []
        for j in range(0, len(sweep_1)):
            current_mask = mask[sweep_1[j]][baseline]
            yy = np.average(data[plot_tag_y][current_mask])
            y0.append(yy)
    else:
        y0 = 0
        
    newdata = {}
    I_rms_list = []
    kappa_list = []
    for i in range(0,len(sweep_2)): # main loop
        x = []
        y = []
        for j in range(0,len(sweep_1)): # second loop
            current_mask = mask[sweep_1[j]][sweep_2[i]]
            xx, yy = calc_average(data[plot_tag_x][current_mask], data[plot_tag_y][current_mask])
            x.append(xx)
            y.append(yy)
        x = np.array(x)
        y = np.abs(np.array(y))
        if i==0:
            y_previous = y
            
        # fit:
        if fit:
            x, y = filter_nan(x, y)
            if len(y) > 1:
                '''-------3 omega fit, original func-----'''
                plt.plot(x, y + i * offset, ls='None', marker='o', ms=2, mfc='none', mew=0.5,
                         color=get_color_cycle(len(sweep_2), cmap='coolwarm')[i])
                legend += [f'{format(round(sweep_2[i], 5) * 1E3, ".2f")}mA']
                # p0 = [min(max(1/np.max(y),0),1E12),1E-7]
                # lbound =[0, 1/10]
                # rbound =[3, 100]
                # for value in p0:
                #     index = p0.index(value)
                #     lbound[index] = value * lbound[index]
                #     rbound[index] = value * rbound[index]
                # para, cov = curve_fit(omega3_fit_func, x, y, p0=p0, bounds=(lbound,rbound), maxfev=50000)
                # plt.plot(x, omega3_fit_func(x,*para), ls='--', marker=None, color=get_color_cycle(len(sweep_2), cmap='coolwarm')[i])
                # a = para[0]
                '''-------3 omega fit, original func-----'''
                fit_y = 1 / (y ** 2)
                fit_x = (2 * np.pi * x) ** 2
                para, cov = curve_fit(linear_func, fit_x, fit_y, bounds=([0,0],[1e10,1e10]), maxfev=50000)
                original_para = [np.sqrt(abs(para[1])),para[0]/para[1]]

                # plt.plot(fit_x, fit_y, ls='None', marker='o', ms=2, mfc='none', mew=0.5,
                #          color=get_color_cycle(len(sweep_2), cmap='coolwarm')[i])
                # legend += [f'{format(round(sweep_2[i], 5) * 1E3, ".2f")}mA']
                # plt.plot(fit_x, linear_func(fit_x, *para), ls='--', marker=None,
                #                   color=get_color_cycle(len(sweep_2), cmap='coolwarm')[i])
                plt.plot(x, omega3_fit_func(x, *original_para), ls='--', marker=None,
                         color=get_color_cycle(len(sweep_2), cmap='coolwarm')[i])
                a = original_para [0]
                I_rms = sweep_2[i]
                R_prime = 0.83431
                R = 316.8
                l_over_L = 1/2
                e = 500E-9
                kappa = a* I_rms**3 *R *R_prime *l_over_L / (2 * e)
                kappa_list += [kappa]
                legend += [f'kappa = {format(kappa, ".2f")}']
                I_rms_list += [sweep_2[i]]
        else:
            # difference = np.remainder(y - y_previous + 180, 360)
            difference = y
            if baseline is not None:
                difference = y-y0
            if baseline == 'difference':
                # difference = np.remainder(y - y_previous + 180, 360)
                difference = y-y_previous
            x,difference = filter_nan(x,difference)
            plt.plot(x, difference + i * offset, ls='-', marker='o', ms=0, mfc='none', color=get_color_cycle(len(sweep_2),cmap='coolwarm')[i])
        # legend += [f'{format(round(sweep_2[i], 5)* 1E3, ".2f")}mA']
        # newdata.update({f'{round(sweep_2[i], 2)}': (x, y- y_previous)})
        y_previous = y
    plt.xlim(min(x), max(x) + abs(max(x) - min(x)) / 1.2)
    # plt.xlim(min(fit_x), max(fit_x) + abs(max(fit_x) - min(fit_x)) / 1.2)
    # with open(folder_path + '\\'+ 'temp', 'wb') as f:
    #     pickle.dump(newdata, f)

    plt.legend(legend, loc='upper right', ncol=2)
    plt.xlabel(plot_tag_x)
    plt.ylabel(plot_tag_y)

    if save:
        file_path = folder_path + '\\' + 'slope' + '_vs_' + 'Vg'
        np.savetxt(file_path, np.column_stack((vg,slope)), delimiter='\t')
     
    plot_fig(name = 'temp', folder_path = None, save = False)
    return np.array(I_rms_list), np.array(kappa_list)



'''------------------------input before run------------------------'''
""""""
folder_path = r"C:\Users\ICET\Desktop\Data\lyw\20230420_3\data\20230420"
file_path = r"C:\Users\ICET\Desktop\Data\lyw\20230420_3\data\20230420\3w_vs_i_20K.002"

data = load_data_from_file(file_path)
data = limitdata(data,80,1000,'f')
data = limitdata(data,-1E12,-1E-5,'vx')
#           plot_single_sweep(data,
#             sweep_tag_1='f',
#             plot_tag_x='f',
#             plot_tag_y=ylabel,
#             yerrbar=True,
#             continuous = True
#           )
I_rms, kappa = plot_double_sweep(data,
                                  sweep_tag_1='f',
                                  sweep_tag_2='vix',
                                  plot_tag_x='f',
                                  plot_tag_y='vx',
                                  baseline=None,
                                  offset = 0,
                                  save=False,
                                  fit =True)
    
fg = plt.figure(figsize=fig_size,dpi=300)
plt.plot(I_rms, kappa,ls='--', marker='o', ms=2, mfc='none', mew=0.5)
plt.xlabel('I_rms')
plt.ylabel('$\kappa$')
plt.tight_layout()
plt.show()

  