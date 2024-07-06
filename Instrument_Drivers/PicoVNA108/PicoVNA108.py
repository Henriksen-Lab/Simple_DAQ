import socket
import subprocess
import pickle
import os, time
import numpy as np


def start_32_bit_program():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.join(current_directory,'pywin32-env','dist', "PicoVNA108_server.exe")
    subprocess.Popen([exe_path])

def recv_full_message(client_socket, length):
    data = b''
    while len(data) < length:
        packet = client_socket.recv(length - len(data))
        if not packet:
            break
        data += packet
    return data

def call_32bit_program(params):
    start_32_bit_program()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 65432))
    client_socket.send(pickle.dumps(params))

    response_length = int.from_bytes(client_socket.recv(4), 'big')
    response = recv_full_message(client_socket, response_length)
    data = pickle.loads(response)
    client_socket.close()
    if 'error' in data:
        raise Exception(data['error'])
    return data

class Smith():
    def __init__(self,real,imag,logmag,phase,freq):
        self.real = np.array(real)
        self.imag = np.array(imag)
        self.log_mag = np.array(logmag)
        self.phase_rad = np.array(phase)
        self.freqs = np.array(freq)

def get_picoVNA_smith(port='S21',f_min=0.3,f_max=8500,number_of_points=1001,power=0,bandwidth=1000,Average=1,picoVNA="PicoControl3.PicoVNA_3"):
    params = {
    'port': port,
    'f_min': f_min,
    'f_max': f_max,
    'number_of_points': number_of_points,
    'power': power,
    'bandwidth': bandwidth,
    'Average': Average,
    'picoVNA':"PicoControl3.PicoVNA_3"
    }
    dict = call_32bit_program(params)
    data = Smith(dict['real'],dict['imag'],dict['log_mag'],dict['phase_rad'],dict['freqs'])
    return data

start = time.time()
print(get_picoVNA_smith(Average=1).log_mag)
print(time.time()-start)
