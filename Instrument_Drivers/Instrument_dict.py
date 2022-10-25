import time
from Instrument_Drivers.vna_analysis import *
from Instrument_Drivers.SR830 import *
from Instrument_Drivers.keithley import *
from Instrument_Drivers.hp34461A import *
from Instrument_Drivers.PicoVNA108 import *
from Instrument_Drivers.Agilent_infiniVision import *
from Instrument_Drivers.keysightN6700c import *
from Instrument_Drivers.transfer_heater_PID import *
from Instrument_Drivers.noise_probe_PID import *

global instrument_dict
instrument_dict = {'get':{},
                   'set':{},
                   'vna':['vna', 'PicoVNA108'],
                   'pid_noise':['keithley', 'SR830', 'hp34461A']} #the instrument for temp acq

instrument_dict['get'].update({'keithley': ['2000ohm_4pt', '2400ohm_4pt', '2000ohm_2pt', '2400ohm_2pt', '2000volt', '2400amp']})
instrument_dict['get'].update({'SR830': ['x', 'y', 'R', 'theta', 'freq']})
instrument_dict['get'].update({'hp34461A': ['volt', 'ohm_4pt']})
instrument_dict['get'].update({'PicoVNA108': ['S21', 'S12', 'S11', 'S22']})
instrument_dict['get'].update({'vna': ['please input the VNA_settings']})
instrument_dict['get'].update({'Agilent infiniiVision': ['counter']})

instrument_dict['set'].update({'keithley': ['current', 'voltage']})
instrument_dict['set'].update({'SR830': ['amplitude', 'freqency']})
instrument_dict['set'].update({'keysight N6700c': ['volt @ channel 2']})

global read_write_lock
read_write_lock = False

def get_value(address='', name='', func='', **kwargs):
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
    elif name == 'PicoVNA108':
        value = get_picoVNA_smith(
                        port=func,
                        f_min=kwargs['f_min'],
                        f_max=kwargs['f_max'],
                        number_of_points=kwargs['number_of_points'],
                        power=kwargs['power'],
                        bandwidth=kwargs['bandwidth'],
                        Average=kwargs['Average']
                    )
    elif name == 'vna':
        value = get_smith_data(address)
    elif name == 'noise pid':
        value = noise_pid_get(kwargs['reading'])
    elif name == 'transfer pid':
        value = transfer_pid_get(arduino_address=address)
    else:
        value = 0
        print('Please input correct instrument name or function name')
    read_write_lock = False
    return value


def set_value(value, address='', name='', func='', **kwargs):
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
    elif name == 'vna':
        change_vna_settings(
            vna_start_freq_GHz=kwargs['vna_start_freq_GHz'],
            vna_end_freq_GHz=kwargs['vna_end_freq_GHz'],
            vna_power_dBm=kwargs['vna_power_dBm'],
            dwell_sec=kwargs['dwell_sec'],
            num_freq=kwargs['num_freq'],
            vna_gpib=kwargs['vna_gpib']
        )
    elif name == 'noise pid':
        noise_pid_set(value,
                      target_temp=kwargs['target_temp'],
                      step_size=kwargs['step_size'],
                      lowkp=kwargs['lowkp'],
                      lowki=kwargs['lowki'],
                      lowkd=kwargs['lowkd'],
                      highkp=kwargs['highkp'],
                      highki=kwargs['highki'],
                      highkd=kwargs['highkd'])
    elif name == 'transfer pid':
        transfer_pid_set(arduino_address=address,
                         kp=kwargs['kp'],
                         ki=kwargs['ki'],
                         kd=kwargs['kd'],
                         set_point=value)
    else:
        print('Please input correct instrument name or function name')
    read_write_lock = False
    return value

