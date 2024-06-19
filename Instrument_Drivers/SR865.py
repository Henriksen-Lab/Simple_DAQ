                                                                       # -*- coding: utf-8 -*-
"""
@author: Shilling Du
@date: Feb 9, 2022
"""

import numpy as np
import time

import pyvisa
rm = pyvisa.ResourceManager()

SR865_sensitivity = ['2nV/fA','5nV/fA','10nV/fA','20nV/fA','50nV/fA',
                '100nV/fA','200nV/fA','500nV/fA','1uV/pA','2uV/pA',
                '5uV/pA','10uV/pA','20uV/pA','50uV/pA','100uV/pA',
                '200uV/pA','500uV/pA','1mV/nA','2mV/nA','5mV/nA',
                '10mV/nA','20mV/nA','50mV/nA','100mV/nA','200mV/nA',
                '500mV/nA','1V/uA']

SR865_timeconstant = ['10us','30us','100us','300us','1ms',
                     '3ms','10ms','30ms','100ms','300ms',
                      '1s','3s','10s','30s','100s',
                      '300s','1ks','3ks','10ks','30ks']

def SR865_get_x(address):

    SR865_handle = rm.open_resource(address)
    try:
        string_data = SR865_handle.query(f"OUTP? 0")
        numerical_data = float(string_data)
        return numerical_data
    finally:
        SR865_handle.close()

def SR865_get_y(address):
    SR865_handle = rm.open_resource(address)
    try:
        string_data = SR865_handle.query(f"OUTP? 1")
        numerical_data = float(string_data)
        return numerical_data
    finally:
        SR865_handle.close()

def SR865_get_R(address):

    SR865_handle = rm.open_resource(address)
    try:
        string_data = SR865_handle.query(f"OUTP? 2")
        numerical_data = float(string_data)
        return numerical_data
    finally:
        SR865_handle.close()

def SR865_get_Theta(address):
    SR865_handle = rm.open_resource(address)
    try:
        string_data = SR865_handle.query(f"OUTP? 3")
        numerical_data = float(string_data)
        return numerical_data
    finally:
        SR865_handle.close()

def SR865_set_amplitude(address, amplitude):
    SR865_handle = rm.open_resource(address)
    try:
        SR865_handle.write(f"SLVL {float(amplitude)}")
    finally:
        SR865_handle.close()

def SR865_get_amplitude(address):
    SR865_handle = rm.open_resource(address)
    try:
        SR865_handle.write(f"OUTX 1")
        read = float(SR865_handle.query('SLVL?'))
        return read
    finally:
        SR865_handle.close()


def SR865_set_frequency(address, frequency):
    SR865_handle = rm.open_resource(address)
    try:
        SR865_handle.write(f"FREQ {float(frequency)}")
    finally:
        SR865_handle.close()

def SR865_get_frequency(address):
    SR865_handle = rm.open_resource(address)
    try:
        SR865_handle.write(f"OUTX 1")
        read = float(SR865_handle.query('FREQ?'))
        return read
    finally:
        SR865_handle.close()

def SR865_set_harmonic(address, harm):
    SR865_handle = rm.open_resource(address)
    try:
        SR865_handle.write(f"HARM {int(harm)}")
    finally:
        SR865_handle.close()

def SR865_get_harmonic(address):
    SR865_handle = rm.open_resource(address)
    try:
        SR865_handle.write(f"OUTX 1")
        read = int(SR865_handle.query("HARM?"))
        return read
    finally:
        SR865_handle.close()


def SR865_set_sensitivity(address, sen):
    SR865_handle = rm.open_resource(address)
    index = SR865_sensitivity.index(sen)
    try:
        SR865_handle.write(f"SENS {index}")
    finally:
        SR865_handle.close()

def SR865_get_sensitivity(address):
    SR865_handle = rm.open_resource(address)
    try:
        SR865_handle.write(f"OUTX 1")
        index = int(SR865_handle.query("SENS?"))
        read = SR865_sensitivity[index]
        return read
    finally:
        SR865_handle.close()

def SR865_set_timeconstant(address, time):
    SR865_handle = rm.open_resource(address)
    index = SR865_timeconstant.index(time)
    try:
        SR865_handle.write(f"OFLT {index}")
    finally:
        SR865_handle.close()

def SR865_get_timeconstant(address):
    SR865_handle = rm.open_resource(address)
    try:
        SR865_handle.write(f"OUTX 1")
        index = int(SR650_handle.query("OFLT?"))
        read = SR865_timeconstant[index]
        return read
    finally:
        SR865_handle.close()

