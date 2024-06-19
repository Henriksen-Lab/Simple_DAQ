# -*- coding: utf-8 -*-
"""
@author: Yiwei Le
@date: Apr 11, 2024
"""

import numpy as np
import time

import pyvisa

rm = pyvisa.ResourceManager()
CS580_gain = ['1nA/V','10nA/V','100nA/V','1uA/V','10uA/V','100uA/V','1mA/V','10mA/V','50mA/V']
CS580_onoff = ['off','on']

def CS580_set_gain(address, gain):
    CS580_handle = rm.open_resource(address)
    index = CS580_gain.index(gain)
    try:
        CS580_handle.write(f"SOUT {0}")
        CS580_handle.write(f"INPT {0}")
        CS580_handle.write(f"GAIN {index}")
        CS580_handle.write(f"SOUT {1}")
        CS580_handle.write(f"INPT {1}")
    finally:
        CS580_handle.close()

def CS580_get_gain(address):
    CS580_handle = rm.open_resource(address)
    try:
        read = float(CS580_handle.query('GAIN?'))
        return read
    finally:
        CS580_handle.close()


def CS580_set_input(address, input):
    CS580_handle = rm.open_resource(address)
    index = CS580_gain.index(input)
    try:
        CS580_handle.write(f"INPT {index}")
    finally:
        CS580_handle.close()

def SR830_get_frequency(address):
    SR830_handle = rm.open_resource(address)
    try:
        SR830_handle.write(f"OUTX 1")
        read = float(SR830_handle.query('FREQ?'))
        return read
    finally:
        SR830_handle.close()

def SR830_set_harmonic(address, harm):
    SR830_handle = rm.open_resource(address)
    try:
        SR830_handle.write(f"HARM {int(harm)}")
    finally:
        SR830_handle.close()

def SR830_get_harmonic(address):
    SR830_handle = rm.open_resource(address)
    try:
        SR830_handle.write(f"OUTX 1")
        read = int(SR830_handle.query("HARM?"))
        return read
    finally:
        SR830_handle.close()


def SR830_set_sensitivity(address, sen):
    SR830_handle = rm.open_resource(address)
    index = SR830_sensitivity.index(sen)
    try:
        SR830_handle.write(f"SENS {index}")
    finally:
        SR830_handle.close()

def SR830_get_sensitivity(address):
    SR830_handle = rm.open_resource(address)
    try:
        SR830_handle.write(f"OUTX 1")
        index = int(SR830_handle.query("SENS?"))
        read = SR830_sensitivity[index]
        return read
    finally:
        SR830_handle.close()

def SR830_set_timeconstant(address, time):
    SR830_handle = rm.open_resource(address)
    index = SR830_timeconstant.index(time)
    try:
        SR830_handle.write(f"OFLT {index}")
    finally:
        SR830_handle.close()

def SR830_get_timeconstant(address):
    SR830_handle = rm.open_resource(address)
    try:
        SR830_handle.write(f"OUTX 1")
        index = int(SR830_handle.query("OFLT?"))
        read = SR830_timeconstant[index]
        return read
    finally:
        SR830_handle.close()

