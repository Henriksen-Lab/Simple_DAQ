#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# author: Shilling Du, revised from https://github.com/picotech/picosdk-picovna-python-examples
# Feb 22, 2022

import win32com.client
import numpy as np
import os
# import matplotlib.pyplot as plt
import socket
import pickle

class Smith():
    def __init__(self,real,imag,logmag,phase,freq):
        self.real = np.array(real)
        self.imag = np.array(imag)
        self.log_mag = np.array(logmag)
        self.phase_rad = np.array(phase)
        self.freqs = np.array(freq)

def get_picoVNA(port='S21',f_min=0.3,f_max=8500,number_of_points=1001,power=0,bandwidth=1000,Average=1,
                      picoVNA="PicoControl3.PicoVNA_3"):
    # PPMS PC Iridium deFAULT
    # picoVNA = "PicoControl3.PicoVNA_3_2" # Icet
    picoVNA = win32com.client.gencache.EnsureDispatch(picoVNA)  
    try:
        findVNA = picoVNA.FND()
        cal_path = os.path.expanduser(r'~\Documents\Pico Technology\PicoVNA3\FacCal.cal')
        ans = picoVNA.LoadCal(cal_path) #Crow108 PC
        freq_step = np.ceil((f_max-f_min)/number_of_points*1E5)/1E5
        flag = picoVNA.SetFreqPlan(f_min,freq_step,number_of_points,power,bandwidth)
        #print(flag)
        picoVNA.SetEnhance('Aver',Average)
        picoVNA.Measure('ALL')

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

def handle_client_connection(client_socket):
    try:
        request = client_socket.recv(4096)
        params = pickle.loads(request)
        data = get_picoVNA(**params)
        response = {
            'real': data.real,
            'imag': data.imag,
            'log_mag': data.log_mag,
            'phase_rad': data.phase_rad,
            'freqs': data.freqs
        }
        response_pickle = pickle.dumps(response)
        response_length = len(response_pickle)
        client_socket.sendall(response_length.to_bytes(4, 'big') + response_pickle)
    except Exception as e:
        error_response = pickle.dumps({'error': str(e)})
        error_length = len(error_response)
        client_socket.sendall(error_length.to_bytes(4, 'big') + error_response)
    finally:
        client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse of the address
    server_socket.bind(('localhost', 65432))
    server_socket.listen(5)
    # print("Server listening on port 65432...")
    while True:
        client_socket, addr = server_socket.accept()
        # print(f"Accepted connection from {addr}")
        handle_client_connection(client_socket)

if __name__ == "__main__":
    start_server()

    
# data = get_picoVNA_smith()
# print(data.freqs)
# plt.plot(data.freqs, data.log_mag)
# plt.ylabel("S21 LogMag")
# plt.xlabel("Frequency")
# plt.show()


