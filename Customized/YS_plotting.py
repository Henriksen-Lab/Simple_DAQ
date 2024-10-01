import sys
import numpy as np
import matplotlib.pyplot as plt

ploter_path = r"C:\Users\Crow108\Documents\GitHub\Simple_DAQ\Customized\SD_plot"
# ploter_path = r'C:\Users\simpl\OneDrive - Washington University in St. Louis (1)\wustl\HLab\Project_MLGM\Paper\SD_plot'
if ploter_path not in sys.path:
    sys.path.append(ploter_path)
from SD_plot_universal import *

date='20240730'
temp='18.67'
current_directory = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(current_directory,date)
data_path = os.path.join(folder_path,temp)
# print(folder_path)

'''Get data in one array'''
data = load_data_from_folder(data_path)

x,y,z  = get_xyz(data,plot_tag_x='VNA_freqs', plot_tag_y='timestamp', plot_tag_z='VNA_log_mag',avgtype='logmag',normalized=None,digit=5)
plot_fill_matrix(x,y,z,cmap='coolwarm',ax=None)
plt.show()
