# -*- coding: utf-8 -*-
"""
Created on Mon April 7 2023

@author: Shilling Du
"""

import numpy as np
import serial, time



def dc205_set_sour_voltage_V(address, target_value_V):
    flag = False
    if 'ASRL' in address:
        address = 'COM' + address.split('::')[0][4:]
    try:
        dc205 = serial.Serial(port=address, baudrate=115200, timeout=0.5)
        flag = dc205.is_open
        range = 0
        output_flag = True
        if abs(target_value_V) < 1.01:
            range = 0
        if abs(target_value_V) < 10.1:
            range = 1
        elif abs(target_value_V) < 101:
            range = 2
        else:
            output_flag = False
            print('DC205 can not output more than 100V')

        dc205.write(bytes(f'RNGE?\r\n', 'utf-8'))
        time.sleep(0.03)
        out = ''
        while dc205.inWaiting() > 0:
            out += dc205.read().decode("ascii")
        if out != '':
            range_now = int(out)
        else:
            range_now = 0
        if range_now < range:
            dc205.write(bytes(f'SOUT OFF\r\n', 'utf-8'))
            dc205.write(bytes(f'RNGE {range}\r\n', 'utf-8'))
        if output_flag:
            dc205.write(bytes(f'SOUT ON\r\n', 'utf-8'))
            value = format(target_value_V, '.4e')
            command = f'VOLT {value}\r\n'
            dc205.write(bytes(command, 'utf-8'))
            dc205.flushOutput()
    finally:
        if flag:
            dc205.close()

def dc205_get_sour_voltage_V(address):
    flag = False
    if 'ASRL' in address:
        address = 'COM' + address.split('::')[0][4:]
    try:
        dc205 = serial.Serial(port=address, baudrate=115200, timeout=0.5)
        flag = dc205.is_open
        command = f'VOLT?\r\n'
        dc205.write(bytes(command, 'utf-8'))
        time.sleep(0.03)
        out = ''
        read = 0
        while dc205.inWaiting() > 0:
            out += dc205.read().decode("ascii")
        if out != '':
            read = float(out)
    finally:
        if flag:
            dc205.close()
    return read

# address = 'COM3'
