# Written by Yiwei Le 3/12/2024
import sys, os, time, threading, tkinter
import numpy as np
from decimal import Decimal
import matplotlib.pyplot as plt

def read_data(data_path):
    f=open(data_path)
    vx = []
    vy = []
    freq = []
    v_in = []
    t = []
    while True:
        line = f.readline()
        try:
            a = line.split()
            if a == []:
                break
            vx.append(float(a[0]))
            vy.append(float(a[1]))
            freq.append(float(a[2]))
            v_in.append(float(a[3]))
            v_in.append(float(a[4]))
            t.append(float(a[len(a)-1]))
        except ValueError:
            line = f.readline()
    return vx, vy, freq, v_in, t

def cal_std(n,data_path):
    while True:
        for i in range(n):
            print('error'+str(i)+' = '+ str(np.std(read_data(data_path)[i])/np.sqrt(len(read_data(data_path)[i])-1)))
        time.sleep(10)

'''''--------------------------------------------run-------------------------------'''
data_path = r'C:\Users\ICET\Desktop\Data\lyw\20240318\data\20240318\1w_bt.001'
cal_std(4, data_path)