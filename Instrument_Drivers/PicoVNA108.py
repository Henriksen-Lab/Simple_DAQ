#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# author: Shilling Du, revised from https://github.com/picotech/picosdk-picovna-python-examples
# Feb 22, 2022

import win32com.client
import numpy as np
import matplotlib.pyplot as plt


class Smith():
    def __init__(self,real,imag,logmag,phase,freq):
        self.real = np.array(real)
        self.imag = np.array(imag)
        self.log_mag = np.array(logmag)
        self.phase_rad = np.array(phase)
        self.freqs = np.array(freq)

def get_picoVNA_smith(port='S21',f_min=0.3,f_max=8500,number_of_points=1001,power=0,bandwidth=1000,Average=1):

    picoVNA = win32com.client.gencache.EnsureDispatch("PicoControl3.PicoVNA_3_2")
    try:
        findVNA = picoVNA.FND()
        ans=picoVNA.LoadCal(r'C:\Users\ICET\Documents\Pico Technology\PicoVNA3\FacCal.cal')
        freq_step = np.ceil((f_max-f_min)/number_of_points*1E5)/1E5
        flag = picoVNA.SetFreqPlan(f_min,freq_step,number_of_points,power,bandwidth)
        #print(flag)
        picoVNA.SetEnhance('Aver',Average)

        picoVNA.Measure('ALL');

        raw_logmag = picoVNA.GetData(port,"logmag",0)
        splitdata_logmag = raw_logmag.split(',')
        freq =  np.float64(np.array(splitdata_logmag))[: : 2]
        logmag = np.float64(np.array(splitdata_logmag))[1 : : 2]

        raw_real = picoVNA.GetData(port, "real", 0)
        splitdata_real = raw_real.split(',')
        real = np.float64(np.array(splitdata_real))[1 : : 2]

        raw_imag = picoVNA.GetData(port, "imag", 0)
        splitdata_imag = raw_imag.split(',')
        imag = np.float64(np.array(splitdata_imag))[1:: 2]

        raw_phase = picoVNA.GetData(port, "phase", 0)
        splitdata_phase = raw_phase.split(',')
        phase = np.float64(np.array(splitdata_phase))[1:: 2]

        data = Smith(real,imag,logmag,phase,freq)
        return data
    finally:
        picoVNA.CloseVNA()


'''
data = get_picoVNA_smith()

plt.plot(data.freqs, data.log_mag)
plt.ylabel("S21 LogMag")
plt.xlabel("Frequency")
plt.show()

'''
