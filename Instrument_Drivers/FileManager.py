import numpy as np
from scipy import interpolate
import os, sys, time
from datetime import datetime

file = r"C:\Users\ICET\Desktop\Data\Simple_DAQ_test\constant volt\data\20220818\test_1_constant_vol.001"

class MainData():
    def __init__(self,data_path=None, sweep_path=None, pid_path=None, fridge_log_path=None):
        self.all_data = {}
        self.Mynote = ''
        if data_path != None and data_path != 'Please enter or choose':
            self.read_data_file(file_path=data_path, label='data')
        if sweep_path != None and sweep_path != 'Please enter or choose':
            self.read_data_file(file_path=sweep_path, label='sweep')
        if pid_path != None and pid_path != 'Please enter or choose':
            self.read_data_file(file_path=pid_path, label='pid')
        if fridge_log_path != None and fridge_log_path != 'Please enter or choose':
            self.read_fridge_log(file_path=fridge_log_path, label='fridge_log')
        self.match_timestamp()


    def read_data_file(self, file_path, label):
        self.all_data.update({label:{}})
        order = 0
        for root, dirs, files in os.walk(file_path):
            for name in sorted(files):
                if 'Simple_DAQ_config' not in name:
                    order +=1
                    if order == 1:
                        # dummy way of getting axis
                        file = os.path.join(root, name)
                        with open(file, 'rb') as f:
                            file_content = f.readlines()
                        for i in range(0, len(file_content)):
                            if b'#' not in file_content[i]:
                                break
                        note = ''
                        for x in file_content[:i-2]:
                            note += x[2:].decode('utf-8')
                        if label == 'data' and note!= '':
                            self.Mynote = note
                        print(file_content[i-1][1:])
                        axis = str(file_content[i-1][1:].decode('utf-8')).split()
                        data_in_file = np.loadtxt(os.path.join(root, name))
                        for i in range(0, len(axis)):
                            self.all_data[label][axis[i]] = list(data_in_file[:,i])
                        print(order, '. ', os.path.join(root, name))
                        print('done')
                    else:
                        data_in_file = np.loadtxt(os.path.join(root, name))
                        for i in range(0, len(axis)):
                            [self.all_data[label][axis[i]].append(x) for x in list(data_in_file[:,i])]
                        print(order, '. ', os.path.join(root, name))
                        print('done')
                        # for key in self.all_data[label].keys():
                        #     print(key, len(self.all_data[label][key]))

    def read_fridge_log(self,file_path,label):
        time = []
        temp = []
        for root, dirs, files in os.walk(file_path):
            for name in files:
                print(os.path.join(root, name))
                x, y = get_fridge_temperature(os.path.join(root, name))
                [time.append(xx) for xx in x]
                [temp.append(yy) for yy in y]
                print('done')
        time = np.array(time)
        temp = np.array(temp)
        self.all_data.update({label:{}})
        self.all_data[label]['timestamp'] = time
        self.all_data[label]['temp'] = temp


    def match_timestamp(self):
        print("matching started")
        for name in self.all_data['data'].keys():
            if 'timestamp' in name:
                self.data_timestamp = name

        for key in self.all_data.keys():
            if key != 'data':
                for name in self.all_data[key].keys():
                    if 'timestamp' in name:
                        self.match_timestamp = name
                for name in self.all_data[key].keys():
                    if 'timestamp' not in name:
                        # print(len(self.all_data[key][self.match_timestamp]))
                        # print(len(self.all_data[key][name]))
                        func = interpolate.interp1d(
                            self.all_data[key][self.match_timestamp],
                            self.all_data[key][name],
                            kind='nearest-up',
                            bounds_error=False,
                            fill_value="extrapolate")
                        self.all_data['data'][key+'_'+name] = func(self.all_data['data'][self.data_timestamp])
        print("matching completed")

    def all_data_save(self,filename,path):
        self.axis = ''
        self.dataToSave = []
        for name in self.all_data['data'].keys():
            self.axis += f"{name}\t\t\t\t"
            self.dataToSave += [self.all_data['data'][name]]
        self.dataToSave = np.column_stack(self.dataToSave)
        os.makedirs(path, exist_ok=True)
        file_name = filename + "_sum"
        np.savetxt(path + "\\" + file_name,
                   self.dataToSave,
                   delimiter='\t',
                   header= self.Mynote + '\n' + f"{self.axis}"
                   )
        print(f"{datetime.now().strftime('%Y.%m.%d')}", " ", f"{datetime.now().strftime('%H:%M:%S')}", "  ", file_name)
        print('data saved')

def get_fridge_temperature(log_name):
    folder_path = os.getcwd()
    if folder_path not in sys.path:
        sys.path.append(folder_path)
    temp = np.loadtxt(log_name, delimiter=',', usecols=2)
    date, clock = np.loadtxt(log_name, dtype='str', delimiter=',', usecols=(0, 1), unpack=True)
    timearray = [time.strptime(x[1:7]+'20'+x[-2:]+','+y, '%d-%m-%Y,%H:%M:%S') for x, y in zip(date, clock)]
    # for the format we get from fridge log, the '20' is to change 09-02-22 into 09-02-2022, for reading purpose
    timestamp = [time.mktime(x) for x in timearray]
    return timestamp, temp