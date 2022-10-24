# -*- coding: utf-8 -*-
"""
@author: Shilling Du
@date: Aug 10, 2022
"""

import numpy as np
from datetime import datetime
import time, sys, os, pyvisa

folder_path = os.getcwd()
if folder_path not in sys.path:
    sys.path.append(
        folder_path)  # easier to open driver files as long as Simple_DAQ.py is in the same folder with drivers
from Instrument_Drivers.vna_analysis import *
from Instrument_Drivers.SR830 import *
from Instrument_Drivers.keithley import *
from Instrument_Drivers.hp34461A import *
from Instrument_Drivers.PicoVNA108 import *
from Instrument_Drivers.Agilent_infiniVision import *
from Instrument_Drivers.keysightN6700c import *
from Instrument_Drivers.transfer_heater_PID import *
from Instrument_Drivers.noise_probe_PID import *

global daq_flag

class Mydata:
    def __init__(self):
        self.variable_name_list = []
        self.last_data_length = 0
        self.last_sweep_length = 0
        self.last_pid_length = 0
        self.sweep_order = '001'
        self.pid_order = '001'
        self.data = {}
        self.sweep = {}
        self.sweep_on_flag = True


    def add_instrument(self, instrument_info):
        self.variable_name_list = instrument_info['variable_name']
        for i in range(0, len(self.variable_name_list)):
            self.data.update({self.variable_name_list[i]: {}})
            self.data[self.variable_name_list[i]].update({'data':[]})
            self.data[self.variable_name_list[i]]['instrument_address'] = instrument_info['instrument_address'][i]
            self.data[self.variable_name_list[i]]['instrument_name'] = instrument_info['instrument_name'][i]
            self.data[self.variable_name_list[i]]['function'] = instrument_info['function'][i]
        self.data['timestamp'] = {'data': [], 'instrument_address': '', 'instrument_name': 'time', 'function': ''}
        self.f_min = float(instrument_info['f_min'])
        self.f_max = float(instrument_info['f_max'])
        self.points = int(instrument_info['points'])
        self.power = float(instrument_info['power'])
        self.bandwidth = float(instrument_info['bandwidth'])
        self.average = int(instrument_info['average'])

    def add_sweep(self, sweep_info):
        self.sweep_list = sweep_info['variable_name']
        for i in range(0, len(self.sweep_list)):
            self.sweep.update({self.sweep_list[i]: {}})
            self.sweep[self.sweep_list[i]].update({'data': []})
            self.sweep[self.sweep_list[i]]['instrument_address'] = sweep_info['instrument_address'][i]
            self.sweep[self.sweep_list[i]]['instrument_name'] = sweep_info['instrument_name'][i]
            self.sweep[self.sweep_list[i]]['function'] = sweep_info['function'][i]
            self.sweep[self.sweep_list[i]]['sweep_bottom_limit'] = sweep_info['sweep_bottom_limit'][i]
            self.sweep[self.sweep_list[i]]['sweep_up_limit'] = sweep_info['sweep_up_limit'][i]
            self.sweep[self.sweep_list[i]]['sweep_step_size'] = sweep_info['sweep_step_size'][i]
            self.sweep[self.sweep_list[i]]['sweep_delay'] = sweep_info['sweep_delay'][i]
            self.sweep[self.sweep_list[i]]['sweep_up_and_down_flag'] = sweep_info['sweep_up_and_down_flag'][i]
        self.sweep['timestamp'] = {'data': [], 'instrument_address': '', 'instrument_name': 'time', 'function': ''}

    def add_pid(self, pid_info):
        self.pid = pid_info
        self.pid.update({'temp':{'data':[]}})
        self.pid.update({'time':{'data':[]}})

    def add_file(self, file_info):
        self.file_name = file_info['file_name']
        self.file_order = file_info['file_order']
        self.file_path = file_info['file_path']
        self.Mynote = file_info['mynote']
        self.data_interval = file_info['data_interval']
        self.data_size = file_info['data_size']

    def data_update(self):
        if 'vna_data' in self.data.keys():
            for name in self.data.keys():
                if self.data[name]['instrument_name'] == 'PicoVNA108':
                    # expecting func choosing from S11, S12, S21,S22
                    self.data_VNA = get_picoVNA_smith(
                        port=self.data[name]['function'],
                        f_min=self.f_min,
                        f_max=self.f_max,
                        number_of_points=self.points,
                        power=self.power,
                        bandwidth=self.bandwidth,
                        Average=self.average
                    )
                elif self.data[name]['instrument_name'] == 'vna':
                    change_vna_settings(
                        vna_start_freq_GHz=self.f_min,
                        vna_end_freq_GHz=self.f_max,
                        vna_power_dBm=self.power,
                        dwell_sec=1 / self.bandwidth,
                        num_freq=self.points,
                        vna_gpib=self.data[name]['instrument_address']
                    )
                    self.data_VNA = self.data[name]['instrument_address']
            self.data['VNA_freqs']['data'] = self.data_VNA.freqs
            self.data['VNA_log_mag']['data'] = self.data_VNA.log_mag
            self.data['VNA_phase_rad']['data'] = self.data_VNA.phase_rad
            self.data['VNA_real']['data'] = self.data_VNA.real
            self.data['VNA_imag']['data'] = self.data_VNA.imag
            self.vna_data_length = len(self.data_VNA.freqs)
            for name in self.data.keys():
                if name != 'vna_data':
                    for i in range(0, self.vna_data_length):
                        self.data[name]['data'] += [get_value(
                            address=self.data[name]['instrument_address'],
                            name=self.data[name]['instrument_name'],
                            func=self.data[name]['function'])
                        ]
        else:
            for name in self.data.keys():
                self.data[name]['data'] += [get_value(
                    address=self.data[name]['instrument_address'],
                    name=self.data[name]['instrument_name'],
                    func=self.data[name]['function'])
                ]
                # print(name,': ',self.data[name]['instrument_address'],self.data[name]['instrument_name'],self.data[name]['function'])
                # print(name,get_value(
                #     address=self.data[name]['instrument_address'],
                #     name=self.data[name]['instrument_name'],
                #     func=self.data[name]['function']))
    def file_order_update(self):
        order = int(self.file_order)
        order += 1
        self.file_order = str(order).zfill(3)

    def sweep_order_update(self):
        order = int(self.sweep_order)
        order += 1
        self.sweep_order = str(order).zfill(3)

    def pid_order_update(self):
        order = int(self.pid_order)
        order += 1
        self.pid_order = str(order).zfill(3)

    def data_save(self):
        self.axis = ''
        self.dataToSave = []
        for name in self.data.keys():
            if name != 'vna_data':
                self.axis += f"{name}_{self.file_order}\t\t\t\t"
                self.dataToSave += [self.data[name]['data'][self.last_data_length:]]
        try:
            self.dataToSave = np.column_stack(self.dataToSave)
        except:
            final_data_len = []
            for data_column in self.dataToSave:
                final_data_len.append(len(data_column))
            final_len = min(final_data_len)
            for i in range(0,len(self.dataToSave)):
                self.dataToSave[i] =  self.dataToSave[i][:final_len]
            self.dataToSave = np.column_stack(self.dataToSave)

        os.makedirs(self.file_path + '\\data' + '\\' + datetime.now().strftime('%Y%m%d'), exist_ok=True)
        file_name = self.file_name + f".{self.file_order}"
        file_real_path = self.file_path + '\\data' + '\\' + datetime.now().strftime('%Y%m%d') + "\\" + file_name
        if self.last_data_length == 0:
            while os.path.exists(file_real_path):
                self.file_order_update()
                file_name = self.file_name + f".{self.file_order}"
                file_real_path = self.file_path + '\\data' + '\\' + datetime.now().strftime('%Y%m%d') + "\\" + file_name
        if not os.path.exists(file_real_path):
            np.savetxt(file_real_path,
                       self.dataToSave,
                       delimiter='\t',
                       header=f"{datetime.now().strftime('%Y.%m.%d')}" + " " + f"{datetime.now().strftime('%H:%M:%S')}" +
                              '\n' + self.Mynote + '\n' + f"{self.axis}"
                       )
            print(f"{datetime.now().strftime('%Y.%m.%d')}", " ", f"{datetime.now().strftime('%H:%M:%S')}", "  ",
                  file_name)
            print('data file created')
        else:
            with open(file_real_path, "ab") as f:
                np.savetxt(f, self.dataToSave, delimiter='\t')
            print(f"{datetime.now().strftime('%Y.%m.%d')}", " ", f"{datetime.now().strftime('%H:%M:%S')}", "  ",
                      file_name)
            print('data file updated')
        self.last_data_length = len(self.data['timestamp']['data'])



    def sweep_update(self, value):
        self.sweep['timestamp']['data'] += [time.time()]
        for i in range(0, len(self.sweep_list)):
            self.sweep[self.sweep_list[i]]['data'] += [value[i]]

    def sweep_save(self):
        self.sweep_axis = ''
        self.SweepToSave = []
        for name in self.sweep.keys():
            self.sweep_axis += f"{name}_sweep\t\t\t\t"
            self.SweepToSave += [self.sweep[name]['data'][self.last_sweep_length:]]
        self.SweepToSave = np.column_stack(self.SweepToSave)
        os.makedirs(self.file_path + '\\sweep' + '\\' + datetime.now().strftime('%Y%m%d'), exist_ok=True)
        file_name = self.file_name + f"_sweep.{self.sweep_order}"
        file_real_path = self.file_path + '\\sweep' + '\\' + datetime.now().strftime('%Y%m%d') + "\\" + file_name
        if self.last_sweep_length == 0:
            while os.path.exists(file_real_path):
                self.sweep_order_update()
                file_name = self.file_name + f"_sweep.{self.sweep_order}"
                file_real_path = self.file_path + '\\sweep' + '\\' + datetime.now().strftime(
                    '%Y%m%d') + "\\" + file_name
        if not os.path.exists(file_real_path):
            np.savetxt(file_real_path,
                       self.SweepToSave,
                       delimiter='\t',
                       header=f"{datetime.now().strftime('%Y.%m.%d')}" + " " + f"{datetime.now().strftime('%H:%M:%S')}" +
                              '\n' + self.Mynote + '\n' + f"{self.sweep_axis}"
                       )
            print(f"{datetime.now().strftime('%Y.%m.%d')}", " ", f"{datetime.now().strftime('%H:%M:%S')}", "  ",
                  file_name)
            print('sweep file created')
        else:
            with open(file_real_path, "ab") as f:
                np.savetxt(f, self.SweepToSave, delimiter='\t')
            print(f"{datetime.now().strftime('%Y.%m.%d')}", " ", f"{datetime.now().strftime('%H:%M:%S')}", "  ",
                      file_name)
            print('sweep file updated')
        self.last_sweep_length = len(self.sweep['timestamp']['data'])

        self.sweep_order_update()

    def sweep_single(self):
        global daq_flag
        start = self.sweep[data.sweep_list[0]]['sweep_bottom_limit']
        stop = self.sweep[data.sweep_list[0]]['sweep_up_limit']
        step_size = self.sweep[data.sweep_list[0]]['sweep_step_size']
        delay = self.sweep[data.sweep_list[0]]['sweep_delay']
        name = self.sweep[data.sweep_list[0]]['instrument_name']
        address = self.sweep[data.sweep_list[0]]['instrument_address']
        func = self.sweep[data.sweep_list[0]]['function']
        flag = self.sweep[data.sweep_list[0]]['sweep_up_and_down_flag']
        num_steps = int(np.floor(abs(float(start) - float(stop)) / float(step_size))) + 1
        for val in np.linspace(float(start), float(stop), num_steps):
            if not daq_flag:
                break
            set_value(address=address, name=name, func=func, value=val)
            time.sleep(delay)
            self.sweep_update(value=[val])
        if flag:
            for val in np.linspace(float(stop), float(start), num_steps):
                if not daq_flag:
                    break
                set_value(address=address, name=name, func=func, value=val)
                time.sleep(delay)
                self.sweep_update(value=[val])
        self.sweep_save()
        self.sweep_on_flag = False

    def sweep_double(self):
        global daq_flag
        start = []
        stop = []
        step_size = []
        delay = []
        name = []
        address = []
        func = []
        flag = []
        for i in range(0, len(self.sweep_list)):
            start += [self.sweep[data.sweep_list[i]]['sweep_bottom_limit']]
            stop += [self.sweep[data.sweep_list[i]]['sweep_up_limit']]
            step_size += [self.sweep[data.sweep_list[i]]['sweep_step_size']]
            delay += [self.sweep[data.sweep_list[i]]['sweep_delay']]
            name += [self.sweep[data.sweep_list[i]]['instrument_name']]
            address += [self.sweep[data.sweep_list[i]]['instrument_address']]
            func += [self.sweep[data.sweep_list[i]]['function']]
            flag += [self.sweep[data.sweep_list[i]]['sweep_up_and_down_flag']]
        num_steps = int(np.floor(abs(start[0] - stop[0]) / (step_size[0]))) + 1
        num_steps_1 = int(np.floor(abs(start[1] - stop[1]) / (step_size[1]))) + 1
        print(num_steps, num_steps_1)
        for val in np.linspace(start[0], stop[0], num_steps):
            set_value(address=address[0], name=name[0], func=func[0], value=val)
            for val_1 in np.linspace(start[1], stop[1], num_steps_1):
                if not daq_flag:
                    break
                set_value(address=address[1], name=name[1], func=func[1], value=val_1)
                time.sleep(delay[1])
                self.sweep_update(value=[val, val_1])
            if flag[1]:
                for val_1 in np.linspace(stop[1], start[1], num_steps_1):
                    if not daq_flag:
                        break
                    set_value(address=address[1], name=name[1], func=func[1], value=val_1)
                    time.sleep(delay[1])
                    self.sweep_update(value=[val, val_1])
            if not daq_flag:
                break
            time.sleep(delay[0])
        if flag[0]:
            for val in np.linspace(stop[0], start[0], num_steps):
                set_value(address=address[0], name=name[0], func=func[0], value=val)
                for val_1 in np.linspace(start[1], stop[1], num_steps_1):
                    if not daq_flag:
                        break
                    set_value(address=address[1], name=name[1], func=func[1], value=val_1)
                    time.sleep(delay[1])
                    self.sweep_update(value=[val, val_1])
                if flag[1]:
                    for val_1 in np.linspace(stop[1], start[1], num_steps_1):
                        if not daq_flag:
                            break
                        set_value(address=address[1], name=name[1], func=func[1], value=val_1)
                        time.sleep(delay[1])
                        self.sweep_update(value=[val, val_1])
                if not daq_flag:
                    break
                time.sleep(delay[0])
        self.sweep_save()
        self.sweep_on_flag = False


    def pid_save(self):
        self.pid_axis_list = ['temp','time']
        self.pid_axis = ""
        self.PidToSave = []
        for name in self.pid_axis_list:
            self.pid_axis += f"{name}_pid\t\t\t\t"
            self.PidToSave += [self.pid[name]['data'][self.last_pid_length:]]
        self.PidToSave = np.column_stack(self.PidToSave)
        os.makedirs(self.file_path + '\\pid' + '\\' + datetime.now().strftime('%Y%m%d'), exist_ok=True)
        file_name = self.file_name + f"_pid.{self.pid_order}"
        file_real_path = self.file_path + '\\pid' + '\\' + datetime.now().strftime('%Y%m%d') + "\\" + file_name
        if self.last_pid_length == 0:
            while os.path.exists(file_real_path):
                self.pid_order_update()
                file_name = self.file_name + f"_pid.{self.pid_order}"
                file_real_path = self.file_path + '\\pid' + '\\' + datetime.now().strftime('%Y%m%d') + "\\" + file_name
        if not os.path.exists(file_real_path):
            np.savetxt(file_real_path,
                       self.PidToSave,
                       delimiter='\t',
                       header=f"{datetime.now().strftime('%Y.%m.%d')}" + " " + f"{datetime.now().strftime('%H:%M:%S')}" +
                              '\n' + self.Mynote + '\n' + f"{self.pid_axis}"
                       )
            print(f"{datetime.now().strftime('%Y.%m.%d')}", " ", f"{datetime.now().strftime('%H:%M:%S')}", "  ",
                  file_name)
            print('PID file created')
        else:
            with open(file_real_path, "ab") as f:
                np.savetxt(f, self.PidToSave, delimiter='\t')
            print(f"{datetime.now().strftime('%Y.%m.%d')}", " ", f"{datetime.now().strftime('%H:%M:%S')}", "  ",
                      file_name)
            print('PID file updated')
        self.last_pid_length = len(self.pid['timestamp']['data'])

        self.pid_order_update()

    def pid_get_reading_noise(self):
        global daq_flag
        noise_pid.reading = get_value(address=self.pid['instrument_address'],
                                      name=self.pid['instrument_name'],
                                      func=self.pid['function'])
        temp_initial = noise_pid_get(noise_pid.reading)
        setpoint = self.pid['setpoint']
        sweep_up_flag = True
        while noise_pid.update_flag:
            noise_pid.reading = get_value(address=self.pid['instrument_address'],
                                            name=self.pid['instrument_name'],
                                            func=self.pid['function'])
            temp = noise_pid_get(noise_pid.reading)
            self.pid['temp']['data'] += [temp]
            self.pid['time']['data'] += [time.time()]
            noise_pid_set(noise_pid.reading,
                    target_temp=setpoint,
                    step_size=self.pid['step_size'],
                    lowkp=self.pid['Lowkp'],
                    lowki=self.pid['Lowki'],
                    lowkd=self.pid['Lowkd'],
                    highkp=self.pid['highkp'],
                    highki=self.pid['highki'],
                    highkd=self.pid['highkd'])
            if not daq_flag:
                break
            time.sleep(self.data_interval)
            if self.pid['sweep_up_and_down_flag']:
                if temp >= setpoint and sweep_up_flag:
                    setpoint = temp_initial
                    temp_initial = temp
                    sweep_up_flag = False
                elif temp <= setpoint and not sweep_up_flag :
                    noise_pid.update_flag = False
                    self.pid_save()
            else:
                if temp >= setpoint and sweep_up_flag:
                    noise_pid.update_flag = False
                    self.pid_save()
        self.pid_save()
    def pid_get_reading_transfer(self):
        temp = transfer_pid_get(arduino_address=self.pid['arduino_address'])
        temp_initial = temp
        setpoint = self.pid['setpoint']
        sweep_up_flag = True
        i = 0
        while noise_pid.update_flag:
            i +=1
            temp = transfer_pid.reading
            self.pid['temp']['data'] += [temp]
            self.pid['time']['data'] += [time.time()]
            transfer_pid_set(arduino_address=self.pid['arduino_address'],
                             kp=self.pid['kp'],
                             ki=self.pid['ki'],
                             kd=self.pid['kd'],
                             set_point=setpoint)
            time.sleep(self.data_interval)
            if self.pid['sweep_up_and_down_flag']:
                if temp >= setpoint and sweep_up_flag:
                    setpoint = temp_initial
                    temp_initial = temp
                    sweep_up_flag = False
                elif temp <= setpoint and not sweep_up_flag :
                    transfer_pid.update_flag = False
            else:
                if temp >= setpoint and sweep_up_flag:
                    transfer_pid.update_flag = False

    def pid_sweep_continuous(self):
        # print_dict(self.pid)
        while self.pid['sweep_continuous']:
            self.pid_sweep_single()
        self.pid_sweep_single()

    def pid_sweep_single(self):
        if self.pid['pid_variable_name'] == 'ICET noise setup':
            print('ICET noise PID started')
            noise_pid.update_flag = True
            t3 = threading.Thread(target=self.pid_get_reading_noise)
            t3.start()
            noise_pid.pid_run()
        elif self.pid['pid_variable_name'] == 'NV transfer setup':
            print('NV PID started')
            transfer_pid.update_flag = True
            t4 = threading.Thread(target=self.pid_get_reading_transfer)
            t4.start()
            transfer_pid.run()

global read_write_lock
read_write_lock = False

def get_value(address='', name='', func=''):
    global read_write_lock
    while read_write_lock:
        time.sleep(0.001)
    read_write_lock = True
    if name == 'time':
        value = time.time()
    elif name == 'keithley':
        if func == '2000ohm_4pt':
            value = keithley2000_get_ohm_4pt(address)
        elif func == '2400ohm_4pt':
            value = keithley2400_get_ohm_4pt(address)
        elif func == '2000ohm_2pt':
            value = keithley2000_get_ohm_2pt(address)
        elif func == '2400ohm_2pt':
            value = keithley2400_get_ohm_2pt(address)
        elif func == '2000volt':
            value = keithley2000_get_voltage_V(address)
        elif func == '2400amp':
            value = keithley2400_get_sour_currrent_A(address)
    elif name == 'SR830':
        if func == 'x':
            value = SR830_get_x(address)
        elif func == 'y':
            value = SR830_get_y(address)
        elif func == 'R':
            value = SR830_get_R(address)
        elif func == 'theta':
            value = SR830_get_Theta(address)
        elif func == 'freq':
            value = SR830_get_frequency(address)
    elif name == 'hp34461A':
        if func == 'volt':
            value = hp34461a_get_voltage(address)
        elif func == 'ohm_4pt':
            value = hp34461a_get_ohm_4pt(address)
    elif name == 'Agilent infiniiVision':
        if func == 'counter':
            value = infiniVision_get_counter(address)
    else:
        value = 0
        print('Please input correct instrument name or function name')
    read_write_lock = False
    return value


def set_value(value, address='', name='', func=''):
    global read_write_lock
    while read_write_lock:
        time.sleep(0.001)
    read_write_lock = True
    if name == 'keithley':
        if func == 'current':
            keithley2400_set_sour_currrent_A(address, value)
        elif func == 'voltage':
            keithley2400_set_sour_voltage_V(address, value)
    elif name == 'SR830':
        if func == 'amplitude':
            SR830_set_amplitude(address, value)
        elif func == 'freqency':
            SR830_set_frequency(address, value)
    elif name == 'keysight N6700c':
        if func == 'volt @ channel 2':
            keysight6700c_set_voltage(address, value)
    else:
        print('Please input correct instrument name or function name')
    read_write_lock = False
    return value

'''-----------------------------------------talk to fromt panel---------------------------------------------------'''
data = Mydata()

def initialize_profile(profile):
    if len(profile['instrument_info']['variable_name']) > 0:
        data.add_instrument(profile['instrument_info'])
    if len(profile['sweep_info']['variable_name']) > 0:
        data.add_sweep(profile['sweep_info'])
    if profile['pid_info']['pid_variable_name'] != None:
        data.add_pid(profile['pid_info'])
    else:
        data.pid = profile['pid_info']
    data.add_file(profile['file_info'])

def no_sweep_config():
    global daq_flag
    while data.sweep_on_flag:
        for i in range(0, data.data_size):
            if not daq_flag:
                break
            data.data_update()
            time.sleep(data.data_interval)
        data.data_save()
        if not daq_flag:
            break



def no_sweep_VNA():
    global daq_flag
    while data.sweep_on_flag:
        data.data_update()
        time.sleep(data.data_interval)
        data.data_save()

        if not daq_flag:
            break


def config_no_sweep():
    if 'vna_data' in data.variable_name_list:
        no_sweep_VNA()
    else:
        no_sweep_config()


def config_pid():
    if data.pid['pid_variable_name'] != None:
        t1 = threading.Thread(target=data.pid_sweep_continuous)
        t1.start()
        print(data.pid['pid_variable_name'])


def choose_config(profile):
    global profile_data
    profile_data = profile
    def run_main():
        global profile_data, daq_flag
        profile = profile_data
        initialize_profile(profile)
        print('Measurements loaded')
        daq_flag = True
        data.sweep_on_flag = True
        config_pid()
        if len(profile['sweep_info']['variable_name']) == 0:
            print('Monitor functioning')
            config_no_sweep()
        elif len(profile['sweep_info']['variable_name']) == 1:
            t2 = threading.Thread(target=data.sweep_single)
            t2.start()
            print('Single sweep starting')
            config_no_sweep()
        elif len(profile['sweep_info']['variable_name']) == 2:
            t2 = threading.Thread(target=data.sweep_double)
            t2.start()
            print('Double sweep starting')
            config_no_sweep()
        print('sweep finished')
        data.sweep_on_flag = False
        # sys.exit()
    mainthread = threading.Thread(target=run_main)
    mainthread.start()

def return_axis(x1=None,
                y1=None,
                x2=None,
                y2=None,
                selector=None):
    def get_axis(x,selector):
        if selector == 'data':
            if x in data.data.keys():
                dataToReturn = np.array(data.data[x]['data'])
            else:
                dataToReturn = np.array([None])
        elif selector == 'sweep':
            if x in data.sweep.keys():
                dataToReturn = np.array(data.sweep[x]['data'])
            else:
                dataToReturn = np.array([None])
        elif selector == 'pid':
            if x in data.pid.keys():
                dataToReturn = np.array(data.pid[x]['data'])
            else:
                dataToReturn = np.array([None])
        else:
            dataToReturn = np.array([None])
            print('Not such trace with name: ',x )
        return dataToReturn

    x_1 = get_axis(x1,selector)
    x_2 = get_axis(x2,selector)
    y_1 = get_axis(y1,selector)
    y_2 = get_axis(y2,selector)
    return x_1,y_1,x_2,y_2

def stop_daq():
    print('Data acquistion stopped, please wait until final data saved')
    global daq_flag
    daq_flag = False

def print_dict(a):
    for key in a:
        print(f"{key}: {a[key]}")