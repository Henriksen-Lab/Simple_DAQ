# Display SR830_y_011,SR830_x_011 vs SR830_freq_011
# •ModifyGraph lsize=1,rgb(SR830_y_011)=(0,43690,65535)
# •ModifyGraph rgb(SR830_x_011)=(65535,16385,16385)
# •ModifyGraph mode(SR830_x_011)=4,marker(SR830_x_011)=8,lstyle(SR830_x_011)=1
# •ModifyGraph mode=4,marker(SR830_y_011)=41
# •ModifyGraph marker=41,lstyle(SR830_x_011)=3
# •ModifyGraph lstyle=3
# •Legend/C/N=text0/F=0/A=MC
# •Legend/C/N=text0/J "\\s(SR830_x_011) SR830_x_011\r\\s(SR830_y_011) SR830_y_011\r"
# •Label bottom "F(Hz)"
# •Label left "I(A)"
# •SavePICT/E=-5/B=72 as "011.png"
import numpy as np

def my_form(smith, **kwargs):
    lens = len(smith.freqs)
    dataToSave = []
    dataToSave += [smith.freqs]
    dataToSave += [smith.log_mag]
    dataToSave += [smith.phase_rad]
    dataToSave += [smith.real]
    dataToSave += [smith.imag]
    for key in kwargs:
        dataToSave += [np.full(lens, kwargs[key])]
    data = np.column_stack(dataToSave)
    return data

amp = 1
volt = 2
class smithdata():
    def __init__(self):
        self.freqs = [1,2,3,4,5,6,7,8,9]
        self.log_mag = [1,2,3,4,5,6,7,8,9]
        self.phase_rad = [1,2,3,4,5,6,7,8,9]
        self.real = [1,2,3,4,5,6,7,8,9]
        self.imag = [1,2,3,4,5,6,7,8,9]
print(my_form(smithdata(), amp=amp, volt=volt))