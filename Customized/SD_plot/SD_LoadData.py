# -*- coding: utf-8 -*-
"""
@author: Shilling Du
@date: Feb 16, 2022
"""

import time, datetime, sys, os, string
import re
from io import StringIO
import numpy as np
from collections import OrderedDict
from operator import getitem
from scipy import interpolate
import copy


def my_data_dict(data, read_data, axis):
    if len(list(data)) == 0:
        for i in range(len(axis)):
            data.update({axis[i]: np.array(read_data[:, i])})
    else:
        for col in range(read_data.shape[1]):
            if axis[col] in data.keys():
                data[axis[col]] = np.append(data[axis[col]], np.array(read_data[:, col]))
            else:
                data.update({axis[col]: np.array(read_data[:, col])})
        length = [len(item) for key, item in data.items()]
        if min(length) != max(length):
            for key in data.keys():
                if len(data[key]) < max(length):
                    data[key] = np.append(np.zeros(max(length) - len(data[key])), data[key])
    return data

def add_data(data,newdict):
    axis = newdict.keys()
    if len(list(data)) == 0:
        for column in axis:
            data.update({column: np.array(newdict[column])})
    else:
        for column in axis:
            if column in data.keys():
                data[column] = np.append(data[column], np.array(newdict[column]))
            else:
                data.update({column: np.array(newdict[column])})
        length = [len(item) for key, item in data.items()]
        if min(length) != max(length):
            for key in data.keys():
                if len(data[key]) < max(length):
                    data[key] = np.append(np.zeros(max(length) - len(data[key])), data[key])
    return data


def load_matrix_axis_from_file(file):
    matrix = []
    # dummy way of getting axis
    with open(file, 'rb') as f:
        file_content = f.readlines()
    for i in range(0, len(file_content)):
        if b'#' not in file_content[i]:
            break
    axis = str(file_content[i - 1][1:].decode('utf-8')).split()
    axis = ['_'.join(x.split('_')[:-1]) for x in axis]
    readout = np.loadtxt(file)
    [matrix.append(x) for x in readout]
    matrix = np.array(matrix)
    return matrix, axis

def load_data_from_file(name):
    data = {}
    matrix, axis = load_matrix_axis_from_file(file=name)
    data = my_data_dict(data, matrix, axis)
    return data

def load_data_CZlab(path):
    with open(path, 'r') as f:
        data = f.read()
    result = re.search(r"(BEGIN)(.*)(END)", data, flags=re.DOTALL)
    data = result.groups()[1]
    with StringIO(data) as data_io:
        data = np.genfromtxt(data_io)
    return data

def load_data_s2p(path):
    data = {}
    matrix = []

    with open(path, encoding="utf8") as f:
        lines = (line for line in f if not line.startswith('#') and not line.startswith('!'))
        readout = np.loadtxt(lines)
    [matrix.append(x) for x in readout]
    matrix = np.array(matrix)
    if matrix.shape[1] == 9:
        axis = ['freq', 'S11_mag', 'S11_angle', 'S21_mag', 'S21_angle', 'S12_mag', 'S12_angle', 'S22_mag', 'S22_angle']
    elif matrix.shape[1] == 3:
        axis = ['freq', 'S21_mag', 'S21_angle']
    data = my_data_dict(data, matrix, axis)
    tags = ['S11','S21','S12','S22']
    for tag in tags:
        if f'{tag}_mag' in data.keys():
            mag = np.array(data[f'{tag}_mag'])
            data.update({f'{tag}_logmag': 20*np.log10(mag)})
    return data

def load_data_from_folder(folder_path):
    order = 0
    ordered_file_name_dict = get_ordered_file_name_dict(folder_path)
    data = {}
    for name in ordered_file_name_dict.keys():
        if ".DS_Store" not in name:
            order += 1
            file = ordered_file_name_dict[name]['path']
            matrix, axis = load_matrix_axis_from_file(file)
            print(' ', order, ". ", ordered_file_name_dict[name]['name'])
            data = my_data_dict(data, matrix, axis)
            print('done')
    return data

def get_ordered_file_name_dict(folder_path):
    file_name_dict = {}
    for root, dirs, files in os.walk(folder_path, topdown=False):
        # go through every file inside the folder, even inside subfolders
        for name in files:
            if '.' in name and ".DS_Store" not in name:
                path = os.path.join(root, name)
                file_name_dict.update({path: {}})
                file_name_dict[path].update({'path': os.path.join(root, name),
                                             'name': name,
                                             'time': os.path.getctime(os.path.join(root, name)),
                                             'dir': root,
                                             })

    # Reorder the file name dict with the modified time
    # if want to use the created time order, change the getmtime -> getctime
    ordered_file_name_dict = OrderedDict(sorted(file_name_dict.items(),
                                                key=lambda x: getitem(x[1], 'time')))
    return ordered_file_name_dict


def calc_average(y, type=None):
    y = np.array(y)
    if type == 'logmag':
        yy = np.average(np.power(10, y / 20))
        yy = 20 * np.log10(yy)
    else:
        yy = np.nanmean(y)
    return yy

def calc_average_spectrum(x, y, type=None):
    x = np.array(x)
    y = np.array(y)
    x_sweep = list(dict.fromkeys(x))
    y_sweep = []
    for each_x in sorted(x_sweep):
        if type == 'logmag':
            each_y = np.average(np.power(10, y / 20)[x == each_x])
            each_y = 20 * np.log10(each_y)
        else:
            each_y = np.average(y[x == each_x])
        y_sweep += [each_y]
    # print('     Avg = ', len(y[x == x_sweep[0]]), ' times')
    return np.array(sorted(x_sweep)), np.array(y_sweep)


def limitdata(data, low_limit, high_limit, tag):
    new_data = copy.deepcopy(data)
    mask = np.logical_and(new_data[tag] >= low_limit, new_data[tag] <= high_limit)
    for key in data.keys():
        new_data[key] = np.array(new_data[key])[mask]
    return new_data


def linecutdata(data, list, tag):
    mask = np.zeros(len(data[tag]))
    for value in list:
        mask = np.logical_or(mask, data[tag] == value)
    for key in data.keys():
        data[key] = np.array(data[key])[mask]
    return data


def calculate_R(data, tag_I='I_x', tag_V='V_x'):
    data.update({'R': data[tag_V] / data[tag_I]})
    data.update({'rho': data[tag_I] / (data[tag_V])})
    return data


def add_column(data, column_name='new_para', value=0):
    random_name = list(data.keys())[0]
    data.update({column_name: np.full(len(data[random_name]), value)})
    return data

def save_data(folder_path, data):
    file_path = folder_path + '\\' + 'reformatted_data'
    axis = ''
    dataToSave = []
    for trace in sorted(data.keys()):
        axis += trace + '_001' + '\t\t\t'
        dataToSave += [np.array(data[trace])]
    dataToSave = np.column_stack(dataToSave)
    np.savetxt(file_path, dataToSave, delimiter='\t',
               header=axis
               )

def get_sweep(data, tag, digit=None):
    if digit is None:
        sweep = np.array(data[tag])
        sweep_list = sorted(list(dict.fromkeys(sweep)))
    else:
        if digit >=0:
            sweep = np.array(
                [round(x, digit) for x in data[tag]])  # round sweep para, avoiding multiple value at same sweep value
        else:
            sweep = np.array(
                [10**(digit)*round(x/10**(digit), 0) for x in data[tag]])  # round sweep para, avoiding multiple value at same sweep value
        sweep_list = sorted(list(dict.fromkeys(sweep)))
        func = interpolate.interp1d(
            sweep,
            data[tag],
            kind='nearest',
            bounds_error=False,
            fill_value="extrapolate")
        sweep_list = func(sweep_list)
    return sweep_list

def get_sweep_info(data, tag, digit=5):
    sweep_list = get_sweep(data, tag, digit)
    i = str(min(sweep_list))
    f = str(max(sweep_list))
    num = len(sweep_list)
    info = f'[{i}, {f}, num = {num}]'
    return info

