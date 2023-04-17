# -*- coding: utf-8 -*-
"""
Created on Mon April 7 2023

@author: Shilling Du
"""

import numpy as np
import serial,time

def dc205_set_sour_voltage_V(address, target_value_V):
    try:
        dc205 = serial.Serial(port=address, baudrate=115200, timeout=0.5)
        flag = dc205.is_open
        time.sleep(0.5)  # allow time for serial port to open
        if abs(target_value_V) < 1.01:
            command = 'RNGE RANGE1; '
        elif abs(target_value_V) < 10.1:
            command = 'RNGE RANGE10; '
        elif abs(target_value_V) < 101:
            command = 'RNGE RANGE100; '
        else:
            command = None
            print('DC205 voltage out of range')
        if command is not None:
            command += f'VOLT {target_value_V}\r\n'
            dc205.write(bytes(command, 'utf-8'))
        dc205.flushOutput()
        time.sleep(0.05)
    finally:
        if flag:
            dc205.close()

def dc205_get_sour_voltage_V(address):
    try:
        dc205 = serial.Serial(port=address, baudrate=115200, timeout=0.5)
        flag = dc205.is_open
        time.sleep(0.5)  # allow time for serial port to open
        command = f'VOLT?\r\n'
        dc205.write(bytes(command, 'utf-8'))
        time.sleep(0.05)
        out = ''
        read = 0
        while dc205.inWaiting() > 0:
            out += dc205.read().decode("ascii")
        if out != '':
            read = float(out)
        time.sleep(0.05)
    finally:
        if flag:
            dc205.close()
    return read

address = ''
dc205_set_sour_voltage_V(address, 0.1)