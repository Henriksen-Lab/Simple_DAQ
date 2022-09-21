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



