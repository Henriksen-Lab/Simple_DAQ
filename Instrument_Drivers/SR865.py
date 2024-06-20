                                                                       # -*- coding: utf-8 -*-
"""
@author: Shilling Du
@date: Feb 9, 2022
"""

import numpy as np
import time

import pyvisa
rm = pyvisa.ResourceManager()

SR865_sensitivity = ['1 V [μA]',
                     '500 mV [nA]',
                     '200 mV [nA]',
                     '100 mV [nA]',
                     '50 mV [nA]',
                     '20 mV [nA]',
                     '10 mV [nA]',
                     '5 mV [nA]',
                     '2 mV [nA]',
                     '1 mV [nA]',
                     '500 μV [pA]',
                     '200 μV [pA]',
                     '100 μV [pA]',
                     '50 μV [pA]',
                     '20 μV [pA]',
                     '10 μV [pA]',
                     '5 μV [pA]',
                     '2 μV [pA]',
                     '1 μV [pA]',
                     '500 nV [fA]',
                     '200 nV [fA]',
                     '100 nV [fA]',
                     '50 nV [fA]',
                     '20 nV [fA]',
                     '10 nV [fA]',
                     '5 nV [fA]',
                     '2 nV [fA]',
                     '1 nV [fA]']


SR865_timeconstant = ['1us','3us','10us','30us','100us','300us','1ms',
                     '3ms','10ms','30ms','100ms','300ms',
                      '1s','3s','10s','30s','100s',
                      '300s','1ks','3ks','10ks','30ks']

def SR865_get_x(address):

    SR865_handle = rm.open_resource(address)
    try:
        string_data = SR865_handle.query(f"OUTP? X")
        numerical_data = float(string_data)
        return numerical_data
    finally:
        SR865_handle.close()

def SR865_get_y(address):
    SR865_handle = rm.open_resource(address)
    try:
        string_data = SR865_handle.query(f"OUTP? Y")
        numerical_data = float(string_data)
        return numerical_data
    finally:
        SR865_handle.close()

def SR865_get_R(address):

    SR865_handle = rm.open_resource(address)
    try:
        string_data = SR865_handle.query(f"OUTP? R")
        numerical_data = float(string_data)
        return numerical_data
    finally:
        SR865_handle.close()

def SR865_get_Theta(address):
    SR865_handle = rm.open_resource(address)
    try:
        string_data = SR865_handle.query(f"OUTP? TH")
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
        read = int(SR865_handle.query("HARM?"))
        return read
    finally:
        SR865_handle.close()


def SR865_set_sensitivity(address, sen):
    SR865_handle = rm.open_resource(address)
    index = SR865_sensitivity.index(sen)
    try:
        SR865_handle.write(f"SCAL {index}")
    finally:
        SR865_handle.close()

def SR865_get_sensitivity(address):
    SR865_handle = rm.open_resource(address)
    try:
        index = int(SR865_handle.query("SCAL?"))
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
        index = int(SR865_handle.query("OFLT?"))
        read = SR865_timeconstant[index]
        return read
    finally:
        SR865_handle.close()

