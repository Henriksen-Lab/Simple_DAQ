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
from Instrument_Drivers.Instrument_dict import *
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
            for key, value in instrument_info.items():
                self.data[self.variable_name_list[i]][key] = value[i]
        self.data['timestamp'] = {'data': [], 'instrument_address': '', 'instrument_name': 'time', 'function': ''}

    def add_vna(self, vna_info):
        self.vna_list = vna_info['variable_name']
        for i in range(0, len(self.vna_list)):
            self.data.update({self.vna_list[i]: {}})
            self.data[self.vna_list[i]].update({'data':[]})
            for key, value in vna_info.items():
                if key in ['f_min', 'f_max', 'power', 'bandwidth']:
                    self.data[self.vna[i]][key] = float(value[i])
                elif key in ['points', 'average']:
                    self.data[self.vna[i]][key] = int(value[i])
                else:
                    self.data[self.vna[i]][key] = value[i]

    def add_sweep(self, sweep_info):
        self.sweep_list = sweep_info['variable_name']
        for i in range(0, len(self.sweep_list)):
            self.sweep.update({self.sweep_list[i]: {}})
            self.sweep[self.sweep_list[i]].update({'data': []})
            for key, value in sweep_info.items():
                self.sweep[self.sweep_list[i]][key] = value[i]
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
        vna_exist = False
        for name in self.data.keys():
            if self.data[name]['instrument_name'] in instrument_dict['vna']:
                vna_exist = True
                if self.data[name]['instrument_name'] == 'PicoVNA108':
                    # expecting func choosing from S11, S12, S21,S22
                    self.data_VNA = get_value(address='',
                                              name='PicoVNA108',
                                              func=self.data[name]['function'],
                                              f_min=self.data[name]['f_min'],
                                              f_max=self.data[name]['f_max'],
                                              number_of_points=self.data[name]['points'],
                                              power=self.data[name]['power'],
                                              bandwidth=self.data[name]['bandwidth'],
                                              Average=self.data[name]['average']
                                              )
                elif self.data[name]['instrument_name'] == 'vna':
                    set_value(value=0, address='', name='vna', func='',
                              vna_start_freq_GHz=self.data[name]['f_min'],
                              vna_end_freq_GHz=self.data[name]['f_max'],
                              vna_power_dBm=self.data[name]['power'],
                              dwell_sec=1 / self.data[name]['bandwidth'],
                              num_freq=self.data[name]['points'],
                              vna_gpib=self.data[name]['instrument_address']
                              )
                    self.data_VNA = get_value(address=self.data[name]['instrument_address'], name='vna', func='')
                elif self.data[name]['instrument_name'] == 'E4405B':
                    self.data_VNA = get_value(address=self.data[name]['instrument_address'], name='E4405B', func='',
                                              f_min=self.data[name]['f_min'],
                                              f_max=self.data[name]['f_max'])

                vna_attributes = [(attr, getattr(self.data_VNA, attr)) for attr in dir(self.data_VNA)
                                  if not attr.startswith('__') and not callable(getattr(self.data_VNA, attr))]

                for name, value in vna_attributes:
                    newname = 'VNA_' + name
                    self.data.update({newname: {'data': value}})
                self.vna_data_length = len(self.data_VNA.freqs)
        if vna_exist:
            for name in self.data.keys():
                if (self.data[name]['instrument_name'] not in instrument_dict['vna']) and \
                        (name not in ['VNA_freqs','VNA_log_mag','VNA_phase_rad','VNA_real','VNA_imag']):
                    value = get_value(address=self.data[name]['instrument_address'],
                                      name=self.data[name]['instrument_name'],
                                      func=self.data[name]['function'])
                    self.data[name]['data'] = np.full(self.vna_data_length, value)
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
                self.dataToSave[i] = self.dataToSave[i][:final_len]
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
        if 'vna_data' not in  self.data.keys():
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


    def sweep_universal(self):
        global daq_flag
        delay = []
        delayback = []
        name = []
        address = []
        func = []
        flag = []
        sweep_up = []
        sweep_down = []
        for i in range(0, len(self.sweep_list)):
            delay += [self.sweep[data.sweep_list[i]]['sweep_delay']]
            name += [self.sweep[data.sweep_list[i]]['instrument_name']]
            address += [self.sweep[data.sweep_list[i]]['instrument_address']]
            func += [self.sweep[data.sweep_list[i]]['function']]
            flag += [self.sweep[data.sweep_list[i]]['sweep_up_and_down_flag']]
            if self.sweep[data.sweep_list[i]]['sweep_up_and_down_flag']:
                delayback += [self.sweep[data.sweep_list[i]]['sweepback_delay']]
                stepback_size = self.sweep[data.sweep_list[i]]['sweepback_step_size']
            else:
                delayback += [self.sweep[data.sweep_list[i]]['sweep_delay']]
                stepback_size = self.sweep[data.sweep_list[i]]['sweep_step_size']
            start = self.sweep[data.sweep_list[i]]['sweep_bottom_limit']
            stop = self.sweep[data.sweep_list[i]]['sweep_up_limit']
            step_size = self.sweep[data.sweep_list[i]]['sweep_step_size']
            if self.sweep[data.sweep_list[i]]['log_scale_flag']:
                num_steps_up = int(np.floor(abs(np.log10(start) - np.log10(stop)) / np.log10(step_size))) + 1
                num_steps_down = int(np.floor(abs(np.log10(start) - np.log10(stop)) / np.log10(stepback_size))) + 1
                sweep_up += [np.logspace(float(np.log10(start)), float(np.log10(stop)), num_steps_up)]
                sweep_down += [np.logspace(float(np.log10(stop)), float(np.log10(start)), num_steps_down)]
            else:
                num_steps_up = int(np.floor(abs(start - stop) / (step_size))) + 1
                num_steps_down = int(np.floor(abs(start - stop) / (stepback_size))) + 1
                sweep_up += [np.linspace(float(start), float(stop), num_steps_up)]
                sweep_down += [np.linspace(float(stop), float(start), num_steps_down)]

        def loop(i,value):
            if i < len(sweep_up):
                for val in sweep_up[i]:
                    if not daq_flag:
                        break
                    set_value(address=address[i], name=name[i], func=func[i], value=val)
                    time.sleep(delay[i])
                    value[i] = val
                    loop(i+1,value)
                    self.sweep_update(value=value)
                if flag[i]:
                    for val in sweep_down[i]:
                        if not daq_flag:
                            break
                        set_value(address=address[i], name=name[i], func=func[i], value=val)
                        time.sleep(delayback[i])
                        value[i] = val
                        loop(i+1,value)
                        self.sweep_update(value=value)
            else:
                pass
        loop(0, np.zeros(len(sweep_up)))

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
            temp = get_value(address='', name='noise pid', func='',
                             reading=noise_pid.reading)
            self.pid['temp']['data'] += [temp]
            self.pid['time']['data'] += [time.time()]
            set_value(value=noise_pid.reading, address='', name='noise pid', func='',
                      target_temp=setpoint,
                      step_size=self.pid['step_size'],
                      lowkp=self.pid['Lowkp'],
                      lowki=self.pid['Lowki'],
                      lowkd=self.pid['Lowkd'],
                      highkp=self.pid['highkp'],
                      highki=self.pid['highki'],
                      highkd=self.pid['highkd']
                      )
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
        temp = get_value(address=self.pid['arduino_address'], name='transfer pid', func='')
        temp_initial = temp
        setpoint = self.pid['setpoint']
        sweep_up_flag = True
        i = 0
        while noise_pid.update_flag:
            i +=1
            temp = transfer_pid.reading
            self.pid['temp']['data'] += [temp]
            self.pid['time']['data'] += [time.time()]
            set_value(value=setpoint, address=self.pid['arduino_address'], name='transfer pid', func='',
                      kp=self.pid['kp'],
                      ki=self.pid['ki'],
                      kd=self.pid['kd'],)
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



'''-----------------------------------------talk to fromt panel---------------------------------------------------'''
data = Mydata()

def initialize_profile(profile):
    if 'vna_info' in profile.keys():
        if len(profile['vna_info']['variable_name']) > 0 :
            data.add_vna(profile['vna_info'])
    if len(profile['instrument_info']['variable_name']) > 0:
        intrument_info = {}
        vna_info = {}
        for name in profile['instrument_info']['instrument_name']:
            if name in instrument_dict['vna']:
                i = instrument_dict['vna'].index(name)
                for key, value in profile['instrument_info'].items():
                    vna_info.update({key: value[i]})
                    del(value[i])
                    intrument_info.update({key: value})
                data.add_vna(vna_info)
                data.add_instrument(intrument_info)
            else:
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
        else:
            t2 = threading.Thread(target=data.sweep_universal)
            t2.start()
            layer = len(profile['sweep_info']['variable_name'])
            if layer == 1:
                layer = 'Single'
            elif layer == 2:
                layer = 'Double'
            print(f'{layer} Sweep starting')

            config_no_sweep()
        print('sweep finished')
        data.sweep_on_flag = False
        # sys.exit()
    mainthread = threading.Thread(target=run_main)
    mainthread.start()

def return_axis(selector=None):
    if selector == 'data':
        all_data = data.data
    elif selector == 'sweep':
        all_data = data.sweep
    elif selector == 'pid':
        all_data = data.pid
    else:
        print('Not such data type: ', selector)

    return all_data

def stop_daq():
    print('Data acquistion stopped, please wait until final data saved')
    global daq_flag
    daq_flag = False

def print_dict(a):
    for key in a:
        print(f"{key}: {a[key]}")