# -*- coding: utf-8 -*-
"""
Created on 06302023 Fri

@author: Shilling Du

"""

import numpy as np
import pyvisa
import time

rm = pyvisa.ResourceManager()

def keithley2230_CH1_Set_voltage(address, value):
    try:
        keithley2230 = rm.open_resource(address)
        keithley2230.write('INST:NSEL 1')
        keithley2230.write(f'VOLT {float(value)}')
    finally:
        keithley2230.close()

def keithley2230_CH1_Fetch_voltage(address):
    try:
        keithley2230 = rm.open_resource(address)
        value = keithley2230.query(f'FETC:VOLT? CH1')
        return float(value)
    finally:
        keithley2230.close()

def keithley2230_CH1_Fetch_current(address):
    try:
        keithley2230 = rm.open_resource(address)
        value = keithley2230.query(f'FETC:CURR? CH1')
        return float(value)
    finally:
        keithley2230.close()

def keithley2230_CH2_Set_voltage(address, value):
    try:
        keithley2230 = rm.open_resource(address)
        keithley2230.write('INST:NSEL 2')
        keithley2230.write(f'VOLT {float(value)}')
    finally:
        keithley2230.close()

def keithley2230_CH2_Fetch_voltage(address):
    try:
        keithley2230 = rm.open_resource(address)
        value = keithley2230.query(f'FETC:VOLT? CH2')
        return float(value)
    finally:
        keithley2230.close()

def keithley2230_CH2_Fetch_current(address):
    try:
        keithley2230 = rm.open_resource(address)
        value = keithley2230.query(f'FETC:CURR? CH2')
        return float(value)
    finally:
        keithley2230.close()

def keithley2230_CH3_Set_voltage(address, value):
    try:
        keithley2230 = rm.open_resource(address)
        keithley2230.write('INST:NSEL 3')
        keithley2230.write(f'VOLT {float(value)}')
    finally:
        keithley2230.close()

def keithley2230_CH3_Fetch_voltage(address):
    try:
        keithley2230 = rm.open_resource(address)
        value = keithley2230.query(f'FETC:VOLT? CH3')
        return float(value)
    finally:
        keithley2230.close()

def keithley2230_CH3_Fetch_current(address):
    try:
        keithley2230 = rm.open_resource(address)
        value = keithley2230.query(f'FETC:CURR? CH3')
        return float(value)
    finally:
        keithley2230.close()