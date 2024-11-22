from math import *
import os, scipy
import numpy as np
from thermometer.Cernox import *

def RuOx_get_T(r):
    temp = exp(4.5647 - 37.205 * (log(r) - 6.91109) + 203.58 * (log(r) - 6.91109) ** 2 - 702.37 * (log(r) - 6.91109) ** 3 +
        1420 * (log(r) - 6.91109) ** 4 - 1708.8 * (log(r) - 6.91109) ** 5 + 1204.6 * (log(r) - 6.91109) ** 6 - 458.84 * (
                    log(r) - 6.91109) ** 7 + 72.825 * (log(r) - 6.91109) ** 8)

    return temp

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

def load_data_from_file(file):
    data = {}
    matrix =[]
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
    data = my_data_dict(data, matrix, axis)
    return data

current_directory = os.path.dirname(os.path.abspath(__file__))
RuOx_file = os.path.join(current_directory,'RuOx.txt') # calibrated using cernox 2
data = load_data_from_file(RuOx_file)
R_cernox = -data['V_T_x']/data['I_T_x']
R_RuOx = data['R_RuOx']
temp = [get_T_cernox_2(r) for r in R_cernox]
RuOx_get_T_interplate = scipy.interpolate.interp1d(R_RuOx, temp, kind='linear')