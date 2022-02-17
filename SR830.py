# -*- coding: utf-8 -*-
"""
@author: Shilling Du
@date: Feb 9, 2022
"""

import numpy as np
import time

import pyvisa
rm = pyvisa.ResourceManager()

def SR830_get_x(address):
    ovl = SR830_check_ovl(address)
    SR830_handle = rm.open_resource(address)
    SR830_handle.write(f"OUTX? 1")
    try:
        if ovl==True:
            numerical_data = "overload"
        else:
            string_data = SR830_handle.query(f"OUTP? 1")
            numerical_data = float(string_data)
        return numerical_data
    finally:
        SR830_handle.close()

def SR830_get_y(address):
    ovl = SR830_check_ovl(address)
    SR830_handle = rm.open_resource(address)
    SR830_handle.write(f"OUTX 1")
    try:
        if ovl==True:
            numerical_data = "overload"
        else:
            string_data = SR830_handle.query(f"OUTP? 2")
            numerical_data = float(string_data)
        return numerical_data
    finally:
        SR830_handle.close()

def SR830_check_ovl(address):
    SR830_handle = rm.open_resource(address)
    ovl0 = SR830_handle.query(f"LIAS? 0")
    time.sleep(0.02)
    ovl1 = SR830_handle.query(f"LIAS? 1")
    time.sleep(0.02)
    ovl2 = SR830_handle.query(f"LIAS? 2")
    time.sleep(0.02)
    SR830_handle.close()
    if int(ovl0)==1 and int(ovl1)==1 and int(ovl2)==1:
        ovl =True
    else:
        ovl =False
    return ovl

def SR830_set_frequency(address, frequency):
    '''
    Set frequency of the local oscillator
    Input:
        frequency (float) : frequency in Hz
    '''
    SR830_handle = rm.open_resource(address)
    SR830_handle.write(f"FREQ {float(frequency)}")
    SR830_handle.close()

def SR830_get_frequency(address):
    '''
    Get the frequency of the local oscillator
    Output:
        frequency (float) : frequency in Hz
    '''
    SR830_handle = rm.open_resource(address)
    SR830_handle.write(f"OUTX 1")
    read = float(SR830_handle.query('FREQ?'))
    SR830_handle.close()
    return read

def SR830_set_amplitude(address, amplitude):
    '''
    Set frequency of the local oscillator
    Input:
        frequency (float) : frequency in Hz
    '''
    SR830_handle = rm.open_resource(address)
    SR830_handle.write(f"SLVL {float(amplitude)}")
    SR830_handle.close()

def SR830_get_amplitude(address):
    '''
    Get the frequency of the local oscillator
    Output:
        frequency (float) : frequency in Hz
    '''
    SR830_handle = rm.open_resource(address)
    SR830_handle.write(f"OUTX 1")
    read = float(SR830_handle.query('SLVL?'))
    SR830_handle.close()
    return read

