# -*- coding: utf-8 -*-
"""
@author: Shilling Du
@date: Aug 10, 2022
"""
import sys, os, time, threading, tkinter
from tkinter import ttk
from tkinter.filedialog import askdirectory

folder_path = os.getcwd()
if folder_path not in sys.path:
    sys.path.append(folder_path) # easier to open driver files as long as Simple_DAQ.py is in the same folder with drivers
from DataManager import *



def pop_window(measurements = 8):
    window = tkinter.Tk()
    window.title('Specify your measurement below')
    window.geometry('1500x900')
# a three column entry for VNA measurement
    tkinter.Label(window,text ='variable name', height=2).grid(row=0,column=0,padx=5,pady=5)
    variable_name_1_entry = tkinter.Entry(window)
    variable_name_1_entry.grid(row=1,column=0,padx=5,pady=5)

# Visa address selection
    tkinter.Label(window,text='Visa address', height=2).grid(row=2,column=0,padx=5,pady=5)
    comvalue_1 = tkinter.StringVar()
    comboxlist_1 = ttk.Combobox(window,textvariable=comvalue_1)
    comboxlist_1['values']= visa_list
    comboxlist_1.current(0)
    comboxlist_1.grid(row=3,column=0,padx=5,pady=5)

# Instrument and func selection at same time
    func_list = []
    def combo_together():
        global comboxlist_2, comboxlist_3
        instr_list =['keithley','SR830','hp34461A','PicoVNA108','vna']
        comboxlist_2 = ttk.Combobox(window, values=instr_list)
        tkinter.Label(window, text='Instrument name', height=2).grid(row=4, column=0,padx=5,pady=5)
        comboxlist_2.grid(row=5,column=0,padx=5,pady=5)
        comboxlist_2.bind('<<ComboboxSelected>>', combofill)
        comboxlist_3 = ttk.Combobox(window, values= func_list)
        tkinter.Label(window, text='Function selection', height=2).grid(row=6, column=0,padx=5,pady=5)
        comboxlist_3.grid(row=7,column=0,padx=5,pady=5)

    def combofill(event):
        if comboxlist_2.get() == 'keithley':
            func_list = ['2000ohm_4pt', '2400ohm_4pt', '2000volt']
        elif comboxlist_2.get() == 'SR830':
            func_list = ['x', 'y', 'R', 'theta', 'freq']
        elif comboxlist_2.get() == 'hp34461A':
            func_list = ['volt', 'ohm_4pt']
        elif comboxlist_2.get() == 'PicoVNA108':
            func_list = ['S21', 'S12', 'S11', 'S22']
        elif comboxlist_2.get() == 'vna':
            func_list = ['please input the VNA_settings']
        else:
            func_list = []
        comboxlist_3.config(values=func_list)
    combo_together()

    tkinter.Label(window, text='VNA parameters', height=2).grid(row=0, column=1, padx=5, pady=5, columnspan=2)
    tkinter.Label(window, text='VNA start freq:', height=2).grid(row=1, column=1,padx=5,pady=5)
    f_min_entry = tkinter.Entry(window)
    f_min_entry.insert(0,'0.3')
    f_min_entry.grid(row=1, column=2,padx=5,pady=5)
    tkinter.Label(window, text='VNA stop freq:', height=2).grid(row=2, column=1,padx=5,pady=5)
    f_max_entry = tkinter.Entry(window)
    f_max_entry.insert(0, '8500')
    f_max_entry.grid(row=2, column=2,padx=5,pady=5)
    tkinter.Label(window, text='sweep points:', height=2).grid(row=3, column=1,padx=5,pady=5)
    points_entry = tkinter.Entry(window)
    points_entry.insert(0, '1001')
    points_entry.grid(row=3, column=2,padx=5,pady=5)
    tkinter.Label(window, text='power(dBm):', height=2).grid(row=4, column=1,padx=5,pady=5)
    power_entry = tkinter.Entry(window)
    power_entry.insert(0, '0')
    power_entry.grid(row=4, column=2,padx=5,pady=5)
    tkinter.Label(window, text='bandwidth(Hz):', height=2).grid(row=5, column=1,padx=5,pady=5)
    bandwidth_entry = tkinter.Entry(window)
    bandwidth_entry.insert(0, '1000')
    bandwidth_entry.grid(row=5, column=2,padx=5,pady=5)
    tkinter.Label(window, text='average:', height=2).grid(row=6, column=1,padx=5,pady=5)
    average_entry = tkinter.Entry(window)
    average_entry.insert(0, '1')
    average_entry.grid(row=6, column=2,padx=5,pady=5)
    def add_measurement():
        data.add_measurement(variable_name= variable_name_1_entry.get(),instrument_address=comboxlist_1.get(),
                             instrument_name=comboxlist_2.get(),func=comboxlist_3.get(),f_min=f_min_entry.get(),
                             f_max=f_max_entry.get(),points=points_entry.get(),power=power_entry.get(),
                             bandwidth=bandwidth_entry.get(),average=average_entry.get())
    tkinter.Button(window, text="add VNA measurement", command=add_measurement).grid(row=9, column=0, columnspan=3,padx=5,pady=5)

    def add_seperate_measurement(c=0):
        # a single column
        tkinter.Label(window, text='variable name', height=2).grid(row=0, column=c, padx=5, pady=5)
        globals()[f'variable_name_entry_{c}'] = tkinter.Entry(window)
        globals()[f'variable_name_entry_{c}'].grid(row=1, column=c, padx=5, pady=5)

        # Visa address selection
        tkinter.Label(window, text='Visa address', height=2).grid(row=2, column=c, padx=5, pady=5)
        globals()[f'comvalue_1_{c}'] = tkinter.StringVar()
        globals()[f'comboxlist_1_{c}'] = ttk.Combobox(window, textvariable=globals()[f'comvalue_1_{c}'])
        globals()[f'comboxlist_1_{c}']['values'] = visa_list
        #globals()[f'comboxlist_1_{c}']['values'] = tuple(['please refresh'])
        globals()[f'comboxlist_1_{c}'].current(0)
        globals()[f'comboxlist_1_{c}'].grid(row=3, column=c, padx=5, pady=5)

        # Instrument and func selection at same time
        globals()[f'func_list_{c}'] = []

        def combo_together_1():
            globals()[f'instr_list_{c}'] = ['keithley', 'SR830', 'hp34461A', 'PicoVNA108', 'vna']
            globals()[f'comboxlist_2_{c}'] = ttk.Combobox(window, values=globals()[f'instr_list_{c}'])
            tkinter.Label(window, text='Instrument name', height=2).grid(row=4, column=c, padx=5, pady=5)
            globals()[f'comboxlist_2_{c}'].grid(row=5, column=c, padx=5, pady=5)
            globals()[f'comboxlist_2_{c}'].bind('<<ComboboxSelected>>', combofill_1)
            globals()[f'comboxlist_3_{c}'] = ttk.Combobox(window, values=globals()[f'func_list_{c}'] )
            tkinter.Label(window, text='Function selection', height=2).grid(row=6, column=c, padx=5, pady=5)
            globals()[f'comboxlist_3_{c}'].grid(row=7, column=c, padx=5, pady=5)

        def combofill_1(event):
            if globals()[f'comboxlist_2_{c}'].get() == 'keithley':
                globals()[f'func_list_{c}'] = ['2000ohm_4pt', '2400ohm_4pt', '2000volt']
            elif globals()[f'comboxlist_2_{c}'].get() == 'SR830':
                globals()[f'func_list_{c}'] = ['x', 'y', 'R', 'theta', 'freq']
            elif globals()[f'comboxlist_2_{c}'].get() == 'hp34461A':
                globals()[f'func_list_{c}'] = ['volt', 'ohm_4pt']
            elif globals()[f'comboxlist_2_{c}'].get() == 'PicoVNA108':
                globals()[f'func_list_{c}'] = ['S21', 'S12', 'S11', 'S22']
            elif globals()[f'comboxlist_2_{c}'].get() == 'vna':
                globals()[f'func_list_{c}'] = ['please input the VNA_settings']
            else:
                globals()[f'func_list_{c}'] = []
            globals()[f'comboxlist_3_{c}'].config(values=globals()[f'func_list_{c}'])
        combo_together_1()
        def add_measurement():
            data.add_measurement(variable_name=globals()[f'variable_name_entry_{c}'].get(),
                                 instrument_address=globals()[f'comboxlist_1_{c}'].get(),
                                 instrument_name=globals()[f'comboxlist_2_{c}'].get(),
                                 func=globals()[f'comboxlist_3_{c}'].get(),
                                 f_min=f_min_entry.get(),
                                 f_max=f_max_entry.get(), points=points_entry.get(), power=power_entry.get(),
                                 bandwidth=bandwidth_entry.get(), average=average_entry.get())

        tkinter.Button(window, text="add measurement", command=add_measurement).grid(row=9, column=c, padx=5,
                                                                                     pady=5)

    for i in range(1,measurements):
        add_seperate_measurement(i+2)
    column_total = measurements + 2
    def choose_folder():
        select_directory = askdirectory(title="choose where to save your file")
        dir_entry.delete(0,'end')
        dir_entry.insert(0,select_directory)
    tkinter.Label(window, text='file directory', height=2).grid(row=10, column=0,padx=5,pady=5,columnspan=column_total)
    dir_entry = tkinter.Entry(window)
    dir_entry.insert(0,'please enter the folder path or choose folder')
    dir_entry.grid(row=11, column=0, padx=5,pady=5,sticky='ew', columnspan=column_total-1, rowspan=2)
    tkinter.Button(window, text="choose folder", command=choose_folder).grid(row=11, column=column_total-1, padx=5, pady=5)
    tkinter.Label(window, text='filename', height=2).grid(row=13, column=0,padx=5,pady=5,columnspan=column_total)
    filename_entry = tkinter.Entry(window)
    filename_entry.insert(0, 'name me please')
    filename_entry.grid(row=14, column=0,padx=5,pady=5,columnspan=column_total,sticky='ew')
    tkinter.Label(window, text='my note', height=2).grid(row=15, column=0, padx=5, pady=5, columnspan=column_total)
    note_entry = tkinter.Entry(window)
    note_entry.insert(0, 'Tell me about your measurement set up')
    note_entry.grid(row=16, column=0, padx=5, pady=5, columnspan=column_total, sticky='sewn', rowspan=5, ipady =60)

    def on_click():
        flag = False
        for i in range(0, len(data.variable_name_list)):
            if data.variable_name_list[i] == 'PicoVNA108':
                flag = True
            elif data.variable_name_list[i] == 'vna':
                flag = True

        if not flag:
            order = int(order_entry.get())
            while True:
                for t in range(0,int(data_size_entry.get())):
                    data.update()
                    time.sleep(float(interval_entry.get()))
                data.data_save(data_dir = dir_entry.get(),file_name=filename_entry.get(),my_note=note_entry.get(), order=order)
                order += 1

        elif flag:
            order = int(order_entry.get())
            while True:
                data.read_and_save_for_VNA_involved(data_dir = dir_entry.get(),file_name=filename_entry.get(),my_note=note_entry.get(),order=order)
                time.sleep(float(interval_entry.get()))
                order += 1

    tkinter.Label(window, text='data taking interval in sec: ', height=2).grid(row=22, column=0, padx=5, pady=5)
    interval_entry = tkinter.Entry(window)
    interval_entry.insert(0, '1')
    interval_entry.grid(row=22, column=1, padx=5, pady=5)
    tkinter.Label(window, text='data size', height=2).grid(row=22, column=2, padx=5, pady=5)
    data_size_entry = tkinter.Entry(window)
    data_size_entry.insert(0, '1000')
    data_size_entry.grid(row=22, column=3, padx=5, pady=5)
    tkinter.Label(window, text='start from file.number', height=2).grid(row=22, column=4, padx=5, pady=5)
    order_entry = tkinter.Entry(window)
    order_entry.insert(0, '0')
    order_entry.grid(row=22, column=5, padx=5, pady=5)

    tkinter.Button(window, text="Run", command = on_click).grid(row=23,column=0,columnspan=column_total,padx=5,pady=5)

    window.mainloop()


rm = pyvisa.ResourceManager()
visa_list = tuple(rm.list_resources())
data = Mydata()
pop_window()