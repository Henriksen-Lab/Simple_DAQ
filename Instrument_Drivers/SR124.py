# -*- coding: utf-8 -*-
"""
@author: Shilling Du
@date: May 18, 2023
"""

import numpy as np
import serial, time
import pyvisa
rm = pyvisa.ResourceManager()
# print(rm.list_resources())


def SR124_set_amplitude(address, amplitude):
    SR124_handle = rm.open_resource(address)
    try:
        SR124_handle.write(f"SLVL {float(amplitude)}")
    finally:
        SR124_handle.close()

    '''serial ver'''
    # flag = False
    # if 'ASRL' in address:
    #     address = 'COM' + address.split('::')[0][4:]
    # try:
    #     SR124 = serial.Serial(port=address, baudrate=9600, timeout=0.5)
    #     flag = SR124.is_open
    #     SR124.write(bytes(f'SLVL {float(amplitude)}\n', 'utf-8'))
    #     SR124.flushOutput()
    # finally:
    #     if flag:
    #         SR124.close()

def SR124_get_amplitude(address):
    SR124_handle = rm.open_resource(address)
    try:
        read = float(SR124_handle.query('SLVL?'))
        return read
    finally:
        SR124_handle.close()

    '''serial ver'''
    # flag = False
    # if 'ASRL' in address:
    #     address = 'COM' + address.split('::')[0][4:]
    # try:
    #     SR124 = serial.Serial(port=address, baudrate=9600, timeout=0.5)
    #     flag = SR124.is_open
    #     SR124.write(bytes(f'SLVL?\r\n', 'utf-8'))
    #     time.sleep(0.03)
    #     out = ''
    #     read = 0
    #     while SR124.inWaiting() > 0:
    #         out += SR124.read().decode("ascii")
    #     if out != '':
    #         read = float(out)
    #     return read
    # finally:
    #     if flag:
    #         SR124.close()

def SR124_set_frequency(address, frequency):
    SR124_handle = rm.open_resource(address)
    try:
        frequency = round(float(frequency), ndigits=3)
        SR124_handle.write(f"FREQ {float(frequency)}")
    finally:
        SR124_handle.close()

def SR124_get_frequency(address):
    SR124_handle = rm.open_resource(address)
    try:
        read = float(SR124_handle.query('FREQ?'))
        return read
    finally:
        SR124_handle.close()

def SR124_set_DCbias(address, value):
    SR124_handle = rm.open_resource(address)
    try:
        value = round(float(value), ndigits=4)
        SR124_handle.write(f"BIAS {float(value)}")
    finally:
        SR124_handle.close()

def SR124_get_DCbias(address):
    SR124_handle = rm.open_resource(address)
    try:
        read = float(SR124_handle.query("BIAS?"))
        return read
    finally:
        SR124_handle.close()