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

    SR830_handle = rm.open_resource(address)
    try:
        string_data = SR830_handle.query(f"OUTP? 1")
        numerical_data = float(string_data)
        return numerical_data
    finally:
        SR830_handle.close()

def SR830_get_y(address):
    SR830_handle = rm.open_resource(address)
    try:
        string_data = SR830_handle.query(f"OUTP? 2")
        numerical_data = float(string_data)
        return numerical_data
    finally:
        SR830_handle.close()

def SR830_get_R(address):

    SR830_handle = rm.open_resource(address)
    try:
        string_data = SR830_handle.query(f"OUTP? 3")
        numerical_data = float(string_data)
        return numerical_data
    finally:
        SR830_handle.close()

def SR830_get_Theta(address):
    SR830_handle = rm.open_resource(address)
    try:
        string_data = SR830_handle.query(f"OUTP? 4")
        numerical_data = float(string_data)
        return numerical_data
    finally:
        SR830_handle.close()

def SR830_set_frequency(address, frequency):
    '''
    Set frequency of the local oscillator
    Input:
        frequency (float) : frequency in Hz
    '''
    SR830_handle = rm.open_resource(address)
    SR830_handle.write(f"FREQ {float(frequency)}")
    SR830_handle.close()

def SR830_set_harmonic(address, harm):
    SR830_handle = rm.open_resource(address)
    SR830_handle.write(f"HARM {int(harm)}")
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

def SR830_get_harmonic(address):
    SR830_handle = rm.open_resource(address)
    SR830_handle.write(f"OUTX 1")
    read = int(SR830_handle.query("HARM?"))
    SR830_handle.close()
    return read

def SR830_set_amplitude(address, amplitude):
    '''
    Set frequency of the local oscillator
    Input:
        amplitude (float) : amplitude in V
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

#print(SR830_get_x('GPIB20::5::INSTR'))