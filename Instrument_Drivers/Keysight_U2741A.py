# -*- coding: utf-8 -*-
"""
Created on Sat July 221 2023

@author: shilling

"""

import numpy as np
import pyvisa
import time

rm = pyvisa.ResourceManager()

def U2741A_get_voltage(address):
    try:
        u2741A = rm.open_resource(address)
        string_data = u2741A.query("MEAS:VOLT:DC?")
        numerical_data = float(string_data)
    finally:
        u2741A.close()
    return numerical_data

def U2741A_get_ohm_4pt(address):
    try:
        u2741A = rm.open_resource(address)
        string_data = u2741A.query("MEAS:FRES?")
        numerical_data = float(string_data)
    finally:
        u2741A.close()
    return numerical_data

def u2741A_get_ohm_2pt(address):
    try:
        u2741A = rm.open_resource(address)
        string_data = u2741A.query("MEAS:RES?")
        numerical_data = float(string_data)
    finally:
        u2741A.close()
    return numerical_data