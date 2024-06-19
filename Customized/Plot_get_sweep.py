import sys
import numpy as np
ploter_path = r"C:\Users\ICET\Documents\GitHub\Simple_DAQ\Customized\SD_plot"
# note, the path of '\Simple_DAQ\Customized\SD_plot' on each local PC might be different, check the path before usage
if ploter_path not in sys.path:
    sys.path.append(ploter_path)
from SD_plot_universal import *

file_path = r'C:\Users\ICET\Desktop\Data\lyw\20240424\r_vs_t_real.001'
data = load_data_from_file(file_path)

v_p = []
sd_p = []
nn_p = []
v_n = []
sd_n = []
nn_n = []

v = data['vx']
time = data['timestamp'] - min(data['timestamp'])

'''get the changing time: high slope datas'''
new_time,dvdt = compute_slope(time, v)
plt.plot(new_time,dvdt)
change = abs(dvdt)>1e-5
change_time = new_time[change]
sweep_list = change_time

'''Round the time to 20s to avoid overlapping, not necessary'''
# sweep = np.array([20*round(x/20, 0) for x in change_time])  # round to 20s
# sweep_list = [0] + sorted(list(dict.fromkeys(sweep)))

'''Sweep over each time period'''
for i in range(len(sweep_list)):
    if i == len(sweep_list) - 1:
        mask = time > sweep_list[i]
    else:
        mask = (time > sweep_list[i]) & (time<sweep_list[i+1])
    raw = v[mask]
    t = time[mask]
    length = len(raw)
    if length > 50:
        plt.plot(t[int(length/10):-int(length/10)],raw[int(length/10):-int(length/10)])
        filtered = raw[int(length/10):-int(length/10)]
        avg = np.average(filtered)
        std = np.std(filtered)
        n = len(filtered)
        if avg > 1e-5:
            v_p += [avg]
            sd_p += [std]
            nn_p += [n]
        elif avg < -1e-5:
            v_n += [avg]
            sd_n += [std]
            nn_n += [n]
plt.show()
print(len(v_p),len(v_n))
print('v_p=',v_p)
print('sd_p=',sd_p)
print('n_p=',nn_p)
print('v_n=',v_n)
print('sd_n=',sd_n)
print('n_n=',nn_n)





