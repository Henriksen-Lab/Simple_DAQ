import time
from Instrument_Drivers.vna_analysis import *
from Instrument_Drivers.SR830 import *
from Instrument_Drivers.keithley import *
from Instrument_Drivers.hp34461A import *
# from Instrument_Drivers.PicoVNA108 import *
from Instrument_Drivers.Agilent_infiniVision import *
from Instrument_Drivers.keysightN6700c import *
from Instrument_Drivers.transfer_heater_PID import *
from Instrument_Drivers.noise_probe_PID import *
from Instrument_Drivers.E4405B import *
from Instrument_Drivers.DC205 import *
from Instrument_Drivers.SR124 import *
from Instrument_Drivers.keithley2230G_30_1 import *
from Instrument_Drivers.Keysight_U2741A import *
global instrument_dict
instrument_dict = {'get':{},
                   'set':{},
                   'vna':['vna', 'PicoVNA108', 'E4405B'],
                   'pid_noise':['keithley', 'SR830', 'hp34461A']} #the instrument for temp acq

instrument_dict['get'].update({'keithley2000': ['ohm_4pt', 'ohm_2pt', 'volt']})
instrument_dict['get'].update({'keithley2400': ['ohm_4pt', 'ohm_2pt', 'sur_current', 'sur_volt']})
instrument_dict['get'].update({'keithley2230': ['Ch1_fetch_volt', 'Ch1_fetch_curr', 'Ch2_fetch_volt', 'Ch2_fetch_curr', 'Ch3_fetch_volt', 'Ch3_fetch_curr']})
instrument_dict['get'].update({'SR830': ['x', 'y', 'R', 'theta', 'freq','amplitude']})
instrument_dict['get'].update({'hp34461A': ['volt', 'ohm_4pt']})
instrument_dict['get'].update({'PicoVNA108': ['S21', 'S12', 'S11', 'S22']})
instrument_dict['get'].update({'vna': ['please input the VNA_settings']})
instrument_dict['get'].update({'Agilent infiniiVision': ['counter']})
instrument_dict['get'].update({'E4405B': ['please input the VNA_settings']})
instrument_dict['get'].update({'DC205': ['sur_volt']})
instrument_dict['get'].update({'SR124': ['sur_AC_Vrms', 'sur_AC_freq', 'sur_DC_bias']})
instrument_dict['get'].update({'U2741A': ['volt', 'ohm_4pt']})

instrument_dict['set'].update({'keithley2400': ['current', 'voltage']})
instrument_dict['set'].update({'keithley2230': ['Ch1_volt', 'Ch2_volt', 'Ch3_volt']})
instrument_dict['set'].update({'SR830': ['amplitude', 'freqency','harmonic']})
instrument_dict['set'].update({'keysight N6700c': ['volt @ channel 2']})
instrument_dict['set'].update({'DC205': ['voltage']})
instrument_dict['set'].update({'SR124': ['AC_Vrms', 'AC_freq', 'DC_bias']})

global read_write_lock
read_write_lock = False

def get_value(address='', name='', func='', **kwargs):
    global read_write_lock
    while read_write_lock:
        time.sleep(0.001)
    read_write_lock = True
    if name == 'time':
        value = time.time()
    elif name == 'keithley2000':
        if func == 'ohm_4pt':
            value = keithley2000_get_ohm_4pt(address)
        elif func == 'ohm_2pt':
            value = keithley2000_get_ohm_2pt(address)
        elif func == 'volt':
            value = keithley2000_get_voltage_V(address)
    elif name == 'keithley2400':
        if func == 'ohm_4pt':
            value = keithley2400_get_ohm_4pt(address)
        elif func == 'ohm_2pt':
            value = keithley2400_get_ohm_2pt(address)
        elif func == 'sur_current':
            value = keithley2400_get_sour_currrent_A(address)
        elif func == 'sur_volt':
            value = keithley2400_get_sour_voltage_V(address)
    elif name == 'keithley2230':
        if func == 'Ch1_fetch_volt':
            value = keithley2230_CH1_Fetch_voltage(address)
        elif func == 'Ch1_fetch_curr':
            value = keithley2230_CH1_Fetch_current(address)
        elif func == 'Ch2_fetch_volt':
            value = keithley2230_CH2_Fetch_voltage(address)
        elif func == 'Ch2_fetch_curr':
            value = keithley2230_CH2_Fetch_current(address)
        elif func == 'Ch3_fetch_volt':
            value = keithley2230_CH3_Fetch_voltage(address)
        elif func == 'Ch3_fetch_curr':
            value = keithley2230_CH3_Fetch_current(address)
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
        elif func == 'amplitude':
            value = SR830_get_amplitude(address)
        elif func == 'harmonic':
            value = SR830_get_harmonic(address)
        elif func == 'time_constant':
            value = SR830_get_timeconstant(address)
        elif func == 'sensitivity':
            value = SR830_get_sensitivity(address)
    elif name == 'hp34461A':
        if func == 'volt':
            value = hp34461a_get_voltage(address)
        elif func == 'ohm_4pt':
            value = hp34461a_get_ohm_4pt(address)
    elif name == 'Agilent infiniiVision':
        if func == 'counter':
            value = infiniVision_get_counter(address)
    # elif name == 'PicoVNA108':
    #     value = get_picoVNA_smith(
    #                     port=func,
    #                     f_min=kwargs['f_min'],
    #                     f_max=kwargs['f_max'],
    #                     number_of_points=kwargs['number_of_points'],
    #                     power=kwargs['power'],
    #                     bandwidth=kwargs['bandwidth'],
    #                     Average=kwargs['Average']
    #                 )
    elif name == 'vna':
        value = get_smith_data(address)
    elif name == 'E4405B':
        value = E4405B_get_spectrum(address,
                                    start_freq = kwargs['f_min'],
                                    stop_freq = kwargs['f_max'])
    elif name == 'noise pid':
        value = noise_pid_get(kwargs['reading'])
    elif name == 'transfer pid':
        value = transfer_pid_get(arduino_address=address)
    elif name == 'DC205':
        if func == 'sur_volt':
            value = dc205_get_sour_voltage_V(address)
    elif name == 'SR124':
        if func == 'sur_AC_Vrms':
            value = SR124_get_amplitude(address)
        if func == 'sur_AC_freq':
            value = SR124_get_frequency(address)
        if func == 'sur_DC_bias':
            value = SR124_get_DCbias(address)
    elif name == 'U2741A':
        if func == 'volt':
            value = U2741A_get_voltage(address)
        elif func == 'ohm_4pt':
            value = U2741A_get_ohm_4pt(address)
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
    if name == 'keithley2400':
        if func == 'current':
            keithley2400_set_sour_currrent_A(address, value)
        elif func == 'voltage':
            keithley2400_set_sour_voltage_V(address, value)
    elif name == 'keithley2230':
        if func == 'Ch1_volt':
            keithley2230_CH1_Set_voltage(address,value)
        if func == 'Ch2_volt':
            keithley2230_CH2_Set_voltage(address,value)
        if func == 'Ch3_volt':
            keithley2230_CH3_Set_voltage(address, value)
    elif name == 'SR830':
        if func == 'amplitude':
            SR830_set_amplitude(address, value)
        elif func == 'freqency':
            SR830_set_frequency(address, value)
        elif func == 'harmonic':
            SR830_set_harmonic(address, value)
        elif func == 'time_constant':
            SR830_set_timeconstant(address, value)
        elif func == 'sensitivity':
            SR830_set_sensitivity(address, value)
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
    elif name == 'DC205':
        if func == 'voltage':
            dc205_set_sour_voltage_V(address, value)
    elif name == 'SR124':
        if func == 'AC_Vrms':
            SR124_set_amplitude(address, value)
        if func == 'AC_freq':
            SR124_set_frequency(address, value)
        if func == 'DC_bias':
            SR124_set_DCbias(address, value)
    else:
        print('Please input correct instrument name or function name')
    read_write_lock = False
    return value

