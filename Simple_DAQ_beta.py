# -*- coding: utf-8 -*-
"""
@author: Shilling Du
@date: Aug 10, 2022
"""
import sys, os, time, threading
from tkinter import ttk
import tkinter as tk
import queue
from tkinter.filedialog import askdirectory, askopenfilename
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

folder_path = os.getcwd()
if folder_path not in sys.path:
    sys.path.append(folder_path) # easier to open driver files as long as Simple_DAQ.py is in the same folder with drivers
from DataManager import *
from Instrument_Drivers.Instrument_dict import instrument_dict
import pickle

global instrument_dict
# Size
sizex = 1500
sizey = 925

# Colors
background_color = 'white'
frame_background_color = '#FCFCFC'
border_color = 'turquoise'
highlight_border_color = 'salmon'
box_color = '#E7F6F2'
box_color_2 = 'whitesmoke'
box_color_3 = 'azure2'

# Padding
frame_ipadx = 5
frame_ipady = 5
frame_padx = 10
frame_pady = 10

q = queue.Queue()
reply = None
reply_1 = None
start_time = time.time()
last_datalength = 0



def background():
    global q, reply, profile, reply_1
    rm = pyvisa.ResourceManager()
    instr_list = rm.list_resources()
    def msg_handler(msg):
        global reply, reply_1
        if 'query' in msg.keys():
            if msg['query'] == 'refresh_visa':
                reply = {'reply': 'display_visa_list', 'visa_list': instr_list}
            elif msg['query'] == 'run_measurement':
                choose_config(profile)
                # print('not stuck')
        if 'plot' in msg.keys():
            # print('data request sent')
            x_1,y_1,x_2,y_2 = return_axis(
                x1=msg['x1'],
                y1=msg['y1'],
                x2=msg['x2'],
                y2=msg['y2'],
                selector=msg['selector']
                )
            reply_1 = {'plot':{'x1':x_1,'y1':y_1,'x2':x_2,'y2':y_2,'flag':True}}
            # print('data sent')
    while True:
        msg = q.get()
        # print(msg)
        msg_handler(msg)



def pop_window(measurements=8):
    global q, reply, profile,start_time
    # Window
    window = tk.Tk()
    window.title('Specify your measurement below')
    window.geometry(f'{sizex}x{sizey}')
    window.configure(bg=background_color)

    window.columnconfigure(0, weight=1)
    window.columnconfigure(1, weight=4)
    window.rowconfigure(0, weight=1)
    window.rowconfigure(1, weight=4)

    # Frames
    class StyleFrame(tk.Frame):
        def __init__(self, master, label, width, height, row=None, column=None, rowspan=1, columnspan=1):
            super().__init__(
                master, width=width, height=height,
                bg=frame_background_color,
                highlightbackground=border_color,
                highlightcolor=border_color,
                highlightthickness=1.5,
                bd=6
            )
            if row is not None:
                self.grid(
                    row=row, column=column,
                    rowspan=rowspan, columnspan=columnspan,
                    ipadx=frame_ipadx, ipady=frame_ipady,
                    padx=frame_padx, pady=frame_pady
                )
                self.grid_propagate(False)

            self.rowconfigure(0, weight=5)
            self.rowconfigure(1, weight=95)

            self.label = tk.Label(
                self,
                text=label,
                height=1,
                bg=background_color
            )

            self.label.grid(column=0, row=0, sticky='w')

    class EntryBox(tk.Frame):
        def __init__(self, master, label, width=160, height=60, columnspan=1,initial_value='',box_color= box_color):
            super().__init__(
                master, width=width, height=height,
                bg=box_color,
                bd=3
            )
            self.grid_propagate(False)

            self.rowconfigure(0, weight=1)
            self.rowconfigure(1, weight=1)

            self.label = tk.Label(
                self,
                text=label,
                height=1,
                bg=box_color
            )
            self.label.grid(column=0, row=0, sticky='w',columnspan=columnspan)

            self.entry = tk.Entry(
                self,
                width=width
            )
            self.entry.grid(column=0, row=1, sticky='ew',columnspan=columnspan)
            self.entry.insert(0, initial_value)

    class EntryBoxH(tk.Frame):
        def __init__(self, master, label, width=160, height=50, initial_value='', box_color = box_color):
            super().__init__(
                master, width=width, height=height,
                bg=box_color,
                bd=3
            )
            self.grid_propagate(False)

            self.rowconfigure(0, weight=1)
            self.rowconfigure(1, weight=1)

            self.label = tk.Label(
                self,
                text=label,
                height=1,
                bg=box_color
            )
            self.label.grid(column=0, row=0)

            self.entry = tk.Entry(
                self
            )
            self.entry.grid(column=1, row=0, sticky='e')
            self.entry.insert(0, initial_value)

    class Boolean(tk.Frame):
        def __init__(self, master, label, width=160, height=60, box_color = box_color):
            super().__init__(
                master, width=width, height=height,
                bg=box_color,
                bd=3
            )
            self.grid_propagate(False)

            self.rowconfigure(0, weight=1)
            self.rowconfigure(1, weight=1)

            self.label = tk.Label(
                self,
                text=label,
                height=1,
                bg=box_color
            )
            self.label.grid(column=0, row=0, sticky='w')

            self.combotext = tk.StringVar()
            self.combobox = ttk.Combobox(
                self,
                textvariable=self.combotext,
                width = 5
            )
            self.combobox['values'] = ['No', 'Yes']
            self.combobox.current(0)
            self.combobox.grid(column=1, row=0, sticky='e')
            self.combobox.current(0)

    class Combobox(tk.Frame):
        def __init__(self, master, label, values=[None], width=160, height=60, box_color = box_color):
            super().__init__(
                master, width=width, height=height,
                bg=box_color,
                bd=3
            )
            self.grid_propagate(False)

            self.rowconfigure(0, weight=1)
            self.rowconfigure(1, weight=1)

            self.label = tk.Label(
                self,
                text=label,
                height=1,
                bg=box_color
            )
            self.label.grid(column=0, row=0, sticky='w')

            self.combotext = tk.StringVar()
            self.combobox = ttk.Combobox(
                self,
                textvariable=self.combotext
            )
            self.combobox['values'] = values
            self.combobox.current(0)
            self.combobox.grid(column=0, row=1, sticky='we')

    instrument_list = []

    # Single instrument frame
    class InstrumentFrame(tk.Frame):
        def __init__(self, instrument_frame, label, width, height, row, column, rowspan=1, columnspan=1):
            super().__init__(
                instrument_frame, width=width, height=height,
                bg=box_color,
                highlightbackground=border_color,
                highlightcolor=highlight_border_color,
                highlightthickness=1.5,
                bd=6
            )
            instrument_list.append(self)
            self.grid(
                row=row, column=column,
                rowspan=rowspan, columnspan=columnspan,
                ipadx=frame_ipadx, ipady=frame_ipady,
                padx=frame_padx, pady=frame_pady,
                sticky='w'
            )
            self.grid_propagate(False)

            self.rowconfigure(0, weight=1)
            self.rowconfigure(1, weight=9)
            self.rowconfigure(2, weight=2)

            self.label = tk.Label(
                self,
                text=label,
                height=1,
                bg=box_color
            )
            self.label.grid(row=0,columnspan=2)
            self.content = tk.Frame(
                self, width=width, height=height,
                bg=box_color
            )
            self.content.grid(row=1, sticky='nw')

            self.variable_name = EntryBox(self.content, 'Variable name')
            self.variable_name.grid(row=1, sticky='e')

            self.visa_address = Combobox(self.content, 'Visa address', values=['Refreshing...'])

            def event_visa_address_refresh(event):
                if self.visa_address.combobox.get() == 'Refresh':
                    update_visa_list()

            self.visa_address.combobox.bind('<<ComboboxSelected>>', event_visa_address_refresh)
            self.visa_address.grid(row=2)

            global instrument_dict
            instr_list_name = ['None']
            for name in instrument_dict['get'].keys():
                if name not in instrument_dict['vna']:
                    instr_list_name.append(name)
            instr_list_vna = ['None'] + instrument_dict['vna']

            if label == 'VNA':
                self.instrument_name = Combobox(self.content, 'Instrument_name', values=instr_list_vna)
            else:
                self.instrument_name = Combobox(self.content, 'Instrument_name', values=instr_list_name)
            self.instrument_name.grid(row=3)

            self.function_selection = Combobox(self.content, 'Function_selection')
            self.function_selection.grid(row=4)

            def update_function_selection(event):
                global instrument_dict
                func_list = ['None']
                for name in instrument_dict['get'].keys():
                    if self.instrument_name.combobox.get() == name:
                        func_list = instrument_dict['get'][name]
                self.function_selection.combobox.config(values=func_list)
                self.function_selection.combobox.current(0)
            self.instrument_name.combobox.bind('<<ComboboxSelected>>', update_function_selection)


#           self.button = ttk.Button(self, text="Add measurement", padding=5)
#           self.button.grid(row=2, padx=13,columnspan=2)

            if label == 'VNA':
                self.content_2 = tk.Frame(
                    self, width=width, height=height,
                    bg=box_color
                )
                self.content_2.grid(row=1, column=1, sticky='nwe')
                self.f_min = EntryBoxH(self.content_2, label='VNA start freq:', initial_value='0.3')
                self.f_min.grid(row=1, column=1, sticky='e')
                self.f_max = EntryBoxH(self.content_2, label='VNA stop freq:', initial_value='8500')
                self.f_max.grid(row=2, column=1, sticky='e')
                self.points = EntryBoxH(self.content_2, label='sweep points:', initial_value='1001')
                self.points.grid(row=3, column=1, sticky='e')
                self.power = EntryBoxH(self.content_2, label='power(dBm):', initial_value='0')
                self.power.grid(row=4, column=1, sticky='e')
                self.bandwidth = EntryBoxH(self.content_2, label='bandwidth(Hz):', initial_value='1000')
                self.bandwidth.grid(row=5, column=1, sticky='e')
                self.average = EntryBoxH(self.content_2, label='average:', initial_value='1')
                self.average.grid(row=6, column=1, sticky='e')

    class ScrollableInstrumentFrame(tk.Frame):
        def __init__(self, master):
            tk.Frame.__init__(self, master, width=int(sizex) - 20, height=int(sizey / 2) - 15)
            self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff", highlightthickness=0)
            self.frame = tk.Frame(self.canvas, background="#ffffff")
            self.hsb = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
            self.canvas.configure(xscrollcommand=self.hsb.set)

            self.hsb.pack(side=tk.BOTTOM, fill="x")
            self.canvas.pack(side=tk.BOTTOM, fill="both", expand=True)
            self.canvas.create_window((16, 8), window=self.frame, anchor="nw", tags="self.frame")

            self.frame.bind("<Configure>", self.onFrameConfigure)
            self.pack_propagate(False)

            self.instrument_frame = StyleFrame(
                self.frame,
                label='Instrument',
                width=int(sizey * 2),
                height=int(sizey / 2)-120
            )
            self.instrument_frame.pack(side=tk.TOP, expand=True)

        def onFrameConfigure(self, event):
            '''Reset the scroll region to encompass the inner frame'''
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    sweep_list = []

    # Sweep frame
    class SweepFrame(tk.Frame):
        def __init__(self, sweep_frame, label, width, height, row, column, rowspan=1, columnspan=1):
            super().__init__(
                sweep_frame, width=width, height=height,
                bg=box_color,
                highlightbackground=border_color,
                highlightcolor=highlight_border_color,
                highlightthickness=1.5,
                bd=6
            )
            sweep_list.append(self)
            self.sweep_back_flag = False
            self.grid(
                row=row, column=column,
                rowspan=rowspan, columnspan=columnspan,
                ipadx=frame_ipadx, ipady=frame_ipady,
                padx=frame_padx, pady=frame_pady,
                sticky='w'
            )
            self.grid_propagate(False)

            self.rowconfigure(0, weight=1)
            self.rowconfigure(1, weight=9)
            self.rowconfigure(2, weight=2)

            self.label = tk.Label(
                self,
                text=label,
                height=1,
                bg=box_color
            )
            self.label.grid(row=0, columnspan=2)
            self.content = tk.Frame(
                self, width=width, height=height,
                bg=box_color
            )
            self.content.grid(row=1, sticky='nw')

            self.sweep_variable_name = EntryBox(self.content, 'Sweep variable name')
            self.sweep_variable_name.grid(row=1, sticky='e')

            self.visa_address = Combobox(self.content, 'Visa address', values=['Refreshing...'])

            def event_visa_address_refresh(event):
                if self.visa_address.combobox.get() == 'Refresh':
                    update_visa_list()

            self.visa_address.combobox.bind('<<ComboboxSelected>>', event_visa_address_refresh)
            self.visa_address.grid(row=2)

            global instrument_dict
            instr_list = ['None'] + list(instrument_dict['set'].keys())
            self.instrument_name = Combobox(self.content, 'Instrument_name', values=instr_list)

            self.instrument_name.grid(row=3)

            self.function_selection = Combobox(self.content, 'Function_selection')
            self.function_selection.grid(row=4)

            def update_function_selection(event):
                global instrument_dict
                func_list = ['None']
                for name in instrument_dict['set'].keys():
                    if self.instrument_name.combobox.get() == name:
                        func_list = instrument_dict['set'][name]
                self.function_selection.combobox.config(values=func_list)
                self.function_selection.combobox.current(0)

            self.instrument_name.combobox.bind('<<ComboboxSelected>>', update_function_selection)

            # self.button = ttk.Button(self, text="Add measurement", padding=5)
            # self.button.grid(row=2, padx=13, columnspan=2)
            self.content_2 = tk.Frame(
                self, width=width, height=height,
                bg=box_color
            )
            self.content_2.grid(row=1, column=1, sticky='nwe')
            self.sweep_bottom_limit = EntryBoxH(self.content_2, label='Start from:', initial_value='0')
            self.sweep_bottom_limit.grid(row=1, column=1, sticky='e')
            self.sweep_up_limit = EntryBoxH(self.content_2, label='Ends at:', initial_value='0')
            self.sweep_up_limit .grid(row=2, column=1, sticky='e')
            self.sweep_step_size = EntryBoxH(self.content_2, label='Sweep step size:', initial_value='1')
            self.sweep_step_size.grid(row=3, column=1, sticky='e')
            self.sweep_delay = EntryBoxH(self.content_2, label='Delay time(sec):', initial_value='1')
            self.sweep_delay.grid(row=4, column=1, sticky='e')
            self.sweep_back = Boolean(self.content_2, label='Sweep back?')
            self.sweep_back.grid(row=5, column=1, sticky='e')
            def sweep_back_flag(event):
                if self.sweep_back.combobox.get() == 'No':
                    self.sweep_back_flag = False
                if self.sweep_back.combobox.get() == 'Yes':
                    self.sweep_back_flag = True
            # maybe put the bottom func to backend would be better
            def compute_time_estimate():
                for sweep in sweep_list:
                    sweep.num_steps = int(np.floor(
                        abs(float(sweep.sweep_bottom_limit.entry.get()) - float(sweep.sweep_up_limit.entry.get())) /
                        (float(sweep.sweep_step_size.entry.get()))))

                compute_numetrical = int(sweep_list[0].num_steps) * (float(sweep_list[0].sweep_delay.entry.get()) +
                                                                     int(sweep_list[1].num_steps) * float(
                            sweep_list[1].sweep_delay.entry.get()))
                for sweep in sweep_list:
                    sweep.sweep_back.combobox.bind('<<ComboboxSelected>>', sweep_back_flag)
                    if sweep.sweep_back_flag:
                        compute_numetrical = compute_numetrical * 2
                return compute_numetrical

            def display_time_estimate():
                time_estimate = compute_time_estimate()
                m, s = divmod(int(time_estimate), 60)
                h, m = divmod(m, 60)
                compute_str = "%02d:%02d:%02d" % (h, m, s)
                for sweep in sweep_list:
                    sweep.time_estimate = tk.Label(
                        sweep.content_2,
                        text=compute_str,
                        height=1,
                        bg=box_color
                    )
                    sweep.time_estimate.grid(row=6, column=1, sticky='e')

            self.button = ttk.Button(self.content_2, text="Time estimate", command=display_time_estimate, padding=5)
            self.button.grid(row=6, column=1, sticky='w')

    pid_list = []
    # PID frame
    class PidFrame(tk.Frame):
        def __init__(self, pid_frame, label, width, height, row, column, rowspan=1, columnspan=1):
            super().__init__(
                pid_frame, width=width, height=height,
                bg=box_color_2,
                highlightbackground=border_color,
                highlightcolor=highlight_border_color,
                highlightthickness=1.5,
                bd=6
            )
            pid_list.append(self)
            self.grid(
                row=row, column=column,
                rowspan=rowspan, columnspan=columnspan,
                ipadx=frame_ipadx, ipady=frame_ipady,
                padx=frame_padx, pady=frame_pady,
                sticky='w'
            )
            self.grid_propagate(False)

            self.rowconfigure(0, weight=1)
            self.rowconfigure(1, weight=9)
            self.rowconfigure(2, weight=2)

            self.label = tk.Label(
                self,
                text=label,
                height=1,
                bg=box_color_2
            )
            self.label.grid(row=0, columnspan=2)
            self.content = tk.Frame(
                self, width=width, height=height,
                bg=box_color_2
            )
            self.content.grid(row=1, sticky='nw')

            self.pid_variable_name = Combobox(self.content, 'PID temp control for', values=
            ['', 'ICET noise setup', 'NV transfer setup'], box_color=box_color_2)
            self.pid_variable_name.grid(row=1, sticky='e')
            none_config(self)
            self.content_2 = tk.Frame(
                self, width=width/2, height=height,
                bg=box_color_2
            )
            self.content_2.grid(row=1, column=1, sticky='nwe')

            def update_parameter_entry(event):
                if self.pid_variable_name.combobox.get() == 'ICET noise setup':
                    noise_config(self)
                elif self.pid_variable_name.combobox.get() == 'NV transfer setup':
                    NV_config(self)
                else:
                    for item in self.content_2.grid_slaves():
                        item.grid_forget()
                    for item in self.content.grid_slaves():
                        if item != self.pid_variable_name:
                            item.grid_forget()
                    none_config(self)

            self.visa_address = Combobox(self.content, 'Visa address', values=['Refreshing...'], box_color=box_color_2)

            self.visa_address.grid(row=5)
            def event_visa_address_refresh(event):
                if self.visa_address.combobox.get() == 'Refresh':
                    update_visa_list()

            self.visa_address.combobox.bind('<<ComboboxSelected>>', event_visa_address_refresh)
            self.pid_variable_name.combobox.bind('<<ComboboxSelected>>', update_parameter_entry)

    file_list = []
    class FileFrame(tk.Frame):
        def __init__(self, file_frame, label, width, height, row, column, rowspan=1, columnspan=1):
            super().__init__(
                file_frame, width=width, height=height,
                bg=box_color_3,
                highlightbackground=border_color,
                highlightcolor=highlight_border_color,
                highlightthickness=1.5,
                bd=6
            )
            file_list.append(self)
            self.grid(
                row=row, column=column,
                rowspan=rowspan, columnspan=columnspan,
                ipadx=frame_ipadx, ipady=frame_ipady,
                padx=frame_padx, pady=frame_pady,
                sticky='w'
            )
            self.grid_propagate(False)

            self.rowconfigure(0, weight=1)
            self.rowconfigure(1, weight=9)
            self.rowconfigure(2, weight=2)

            self.label = tk.Label(
                self,
                text=label,
                height=1,
                bg=box_color_3
            )
            self.label.grid(row=0,column=0,sticky='ew')
            self.content = tk.Frame(
                self, width=width-10, height=height-10,
                bg=box_color_3
            )
            self.content.grid(row=1, column=0, sticky='new')

            self.file_name = EntryBox(self.content, 'File name',width=150, initial_value='name_me_please',box_color=box_color_3)
            self.file_name.grid(row=1, column=0, sticky='w')
            self.file_order = EntryBox(self.content, 'order', width=50, initial_value='001',box_color=box_color_3)
            self.file_order.grid(row=1, column=1, sticky='ew')
            self.dir_entry = EntryBox(self.content, 'Folder path', initial_value='Please enter or choose',width=260,box_color=box_color_3)
            self.dir_entry.grid(row=2, column=0, sticky='ew', columnspan=2)
            def choose_folder():
                select_directory = askdirectory(title="choose where to save your file")
                self.dir_entry.entry.delete(0, 'end')
                self.dir_entry.entry.insert(0, select_directory)
            self.folder_path = ttk.Button(
                self.content,
                text="choose folder",
                command=choose_folder,
                padding=4
            )
            self.folder_path.grid(row=2, column=0, sticky='ne',columnspan=2)
            self.mynote_label = tk.Label(master=self.content, text='My note',bg=box_color_3)
            self.file_size = EntryBox(self.content, 'File size', width=150, initial_value='1000',
                                      box_color=box_color_3)
            self.file_size.grid(row=4, column=0, sticky='w')
            self.data_interval = EntryBox(self.content, 'Data interval(s)', width=50, initial_value='1', box_color=box_color_3)
            self.data_interval.grid(row=4, column=1, sticky='ew')
            self.mynote_label.grid(row=5, column=0, sticky='new', columnspan=2)
            self.mynote = tk.Text(master=self.content,height=5,width=1)
            self.mynote.grid(row=6, column=0, sticky='new',padx=frame_padx,pady=frame_pady, columnspan=2)
            def run():
                global profile, start_time
                start_time = time.time()
                save_config()
                start_measurement()
            def stop():
                stop_daq()
                sys.exit()
            def save_config():
                global profile
                screenshoot()
                config_file = profile['file_info']['file_path'] + '//' + f'{self.file_name.entry.get()}_Simple_DAQ_config'
                with open(config_file,'wb') as f:
                    pickle.dump(profile, f)
            def load_config():
                global profile
                config_file = askopenfilename(title="choose your Simple_DAQ_config file")
                with open(config_file, 'rb') as f:
                    profile = pickle.load(f)
                profile_show()
                # def print_dict(a):
                #     for key in a:
                #         print(f"{key}: {a[key]}")
                # print_dict(profile)

            self.run_button = ttk.Button(self.content, text="Run", command=run, padding=4)
            self.run_button.grid(row=7, column=0, sticky='ew')
            self.stop_button = ttk.Button(self.content, text="Stop", command=stop, padding=4)
            self.stop_button.grid(row=7, column=1, sticky='ew')
            self.Save_config_button = ttk.Button(self.content, text="Save config", command=save_config, padding=4)
            self.Save_config_button.grid(row=8, column=0, sticky='w')
            self.Load_config_button = ttk.Button(self.content, text="Load config", command=load_config, padding=4)
            self.Load_config_button.grid(row=8, column=0, sticky='e')

    def none_config(self):
        self.set_point = EntryBoxH(self.content, label='Set point:(Degree)', initial_value='30', box_color=box_color_2,
                                   height=40)
        self.set_point.grid(row=2, sticky='e')
        self.sweep_back = Boolean(self.content, label='Sweep back?', box_color=box_color_2, height=40)
        self.sweep_back.grid(row=3, sticky='e')
        self.sweep_continuous = Boolean(self.content, label='Continuously?', box_color=box_color_2, height=40)
        self.sweep_continuous.grid(row=4, sticky='e')

    def noise_config(self):
        global instrument_dict
        instr_list_name = ['None'] + instrument_dict['pid_noise']
        self.instrument_name = Combobox(self.content, 'Instrument for Temp', values=instr_list_name,
                                        box_color=box_color_2)
        self.instrument_name.grid(row=6)
        self.function_selection = Combobox(self.content, 'Function_selection', box_color=box_color_2)
        self.function_selection.grid(row=7)
        def update_function_selection(event):
            global instrument_dict
            func_list = []
            for name in instrument_dict['set'].keys():
                if self.instrument_name.combobox.get() == name:
                    func_list = instrument_dict['set'][name]
            self.function_selection.combobox.config(values=func_list)
            self.function_selection.combobox.current(0)
        self.instrument_name.combobox.bind('<<ComboboxSelected>>', update_function_selection)
        for item in self.content_2.grid_slaves():
            item.grid_forget()
        self.Lowkp = EntryBoxH(self.content_2, label='Lowkp:', initial_value='20', box_color=box_color_2, height= 40)
        self.Lowkp.grid(row=1, column=1, sticky='e')
        self.Lowki = EntryBoxH(self.content_2, label='Lowki:', initial_value='0.1', box_color=box_color_2, height= 40)
        self.Lowki.grid(row=2, column=1, sticky='e')
        self.Lowkd = EntryBoxH(self.content_2, label='Lowkd:', initial_value='15', box_color=box_color_2, height= 40)
        self.Lowkd.grid(row=3, column=1, sticky='e')
        self.Highkp = EntryBoxH(self.content_2, label='Highkp:', initial_value='337', box_color=box_color_2, height= 40)
        self.Highkp.grid(row=4, column=1, sticky='e')
        self.Highki = EntryBoxH(self.content_2, label='Highki:', initial_value='1.5', box_color=box_color_2, height= 40)
        self.Highki.grid(row=5, column=1, sticky='e')
        self.Highkd = EntryBoxH(self.content_2, label='Highkd:', initial_value='15', box_color=box_color_2, height= 40)
        self.Highkd.grid(row=6, column=1, sticky='e')
        self.step_size = EntryBoxH(self.content_2, label='Step size:', initial_value='0.1',
                                   box_color=box_color_2, height= 40)
        self.step_size.grid(row=7, column=1, sticky='e')
        self.arduino_address = EntryBox(self.content_2, 'Arduino address:', box_color=box_color_2, initial_value='COM9')
        self.arduino_address.grid(row=8, column=1, sticky='ew')

    def NV_config(self):
        self.instrument_name.grid_forget()
        self.function_selection.grid_forget()
        for item in self.content_2.grid_slaves():
            item.grid_forget()
        self.content_2.grid_remove()
        self.content_2.grid(row=1, column=1, sticky='nwe')
        self.kp = EntryBoxH(self.content_2, label='kp:', initial_value='1.0', box_color=box_color_2)
        self.kp.grid(row=1, column=1, sticky='e')
        self.ki = EntryBoxH(self.content_2, label='ki:', initial_value='0', box_color=box_color_2)
        self.ki.grid(row=2, column=1, sticky='e')
        self.kd = EntryBoxH(self.content_2, label='kd:', initial_value='0', box_color=box_color_2)
        self.kd.grid(row=3, column=1, sticky='e')
        self.arduino_address = EntryBox(self.content_2, 'Arduino address', box_color=box_color_2, initial_value='COM10')
        self.arduino_address.grid(row=4, column=1, sticky='e')

    def screenshoot():
        global profile
        instrument_info = {
            'variable_name': [],
            'instrument_address': [],
            'instrument_name': [],
            'function': [],
            'f_min': 0.3,
            'f_max': 8500,
            'points': 1001,
            'power': 0,
            'bandwidth': 1000,
            'average': 1
        }
        sweep_info = {
            'variable_name': [],
            'instrument_address': [],
            'instrument_name': [],
            'function': [],
            'sweep_bottom_limit': [],
            'sweep_up_limit': [],
            'sweep_step_size': [],
            'sweep_delay': [],
            'sweep_up_and_down_flag': []
        }
        pid_info = {
            'pid_variable_name': None,
            'sweep_continuous': False
        }
        file_info = {
            'file_name': None,
            'file_order': None,
            'file_path': None,
            'Mynote': '',
            'data_size': None,
            'data_interval': None,

        }
        for file in file_list:
            file_info['file_name'] = file.file_name.entry.get()
            file_info['file_order'] = file.file_order.entry.get()
            file_info['file_path'] = file.dir_entry.entry.get()
            file_info['mynote'] = file.mynote.get('1.0', 'end-1c')
            file_info['data_size'] = int(file.file_size.entry.get())
            file_info['data_interval'] = float(file.data_interval.entry.get())
        for instrument in instrument_list:
            if instrument.variable_name.entry.get() != '':
                instrument_info['instrument_name'] += [instrument.instrument_name.combobox.get()]
                if instrument.instrument_name.combobox.get() =='PicoVNA108' or instrument.instrument_name.combobox.get() == 'vna':
                    instrument_info['variable_name'] += ['vna_data']
                    instrument_info['f_min'] = float(instrument.f_min.entry.get())
                    instrument_info['f_max'] = float(instrument.f_max.entry.get())
                    instrument_info['points'] = int(instrument.points.entry.get())
                    instrument_info['power'] = float(instrument.power.entry.get())
                    instrument_info['bandwidth'] = int(instrument.bandwidth.entry.get())
                    instrument_info['average'] = int(instrument.average.entry.get())
                else:
                    instrument_info['variable_name'] += [instrument.variable_name.entry.get()]
                instrument_info['instrument_address'] += [instrument.visa_address.combobox.get()]
                instrument_info['function'] += [instrument.function_selection.combobox.get()]

        def str_to_tuple(str):
            if str =='No':
                return False
            elif str =='Yes':
                return True

        for sweep in sweep_list:
            if sweep.sweep_variable_name.entry.get() != '':
                sweep_info['instrument_name'] += [sweep.instrument_name.combobox.get()]
                sweep_info['variable_name'] += [sweep.sweep_variable_name.entry.get()]
                sweep_info['instrument_address'] += [sweep.visa_address.combobox.get()]
                sweep_info['function'] += [sweep.function_selection.combobox.get()]
                sweep_info['sweep_bottom_limit'] += [float(sweep.sweep_bottom_limit.entry.get())]
                sweep_info['sweep_step_size'] += [float(sweep.sweep_step_size.entry.get())]
                sweep_info['sweep_up_limit'] += [float(sweep.sweep_up_limit.entry.get())]
                sweep_info['sweep_delay'] += [float(sweep.sweep_delay.entry.get())]
                sweep_info['sweep_up_and_down_flag'] += [str_to_tuple(str(sweep.sweep_back.combobox.get()))]
        for pid in pid_list:
            if pid.pid_variable_name.combobox.get() != '':
                pid_info['pid_variable_name'] = pid.pid_variable_name.combobox.get()
                pid_info['Setpoint'] = pid.set_point.entry.get()
                pid_info['sweep_up_and_down_flag'] = str_to_tuple(str(pid.sweep_back.combobox.get()))
                if pid_info['pid_variable_name'] == 'ICET noise setup':
                    pid_info['instrument_name'] = pid.instrument_name.combobox.get()
                    pid_info['instrument_address'] = pid.visa_address.combobox.get()
                    pid_info['function'] = pid.function_selection.combobox.get()
                    pid_info['Lowkp'] = float(pid.Lowkp.entry.get())
                    pid_info['Lowki'] = float(pid.Lowki.entry.get())
                    pid_info['Lowkd'] = float(pid.Lowkd.entry.get())
                    pid_info['Highkp'] = float(pid.Highkp.entry.get())
                    pid_info['Highki'] = float(pid.Highki.entry.get())
                    pid_info['Highkd'] = float(pid.Highkd.entry.get())
                    pid_info['step_size'] = float(pid.step_size.entry.get())
                    pid_info['arduino_address'] = pid.arduino_address.entry.get()
                    pid_info['sweep_continuous'] = str_to_tuple(str(pid.sweep_continuous.combobox.get()))
                elif pid_info['pid_variable_name'] == 'NV transfer setup':
                    pid_info['kp'] = float(pid.kp.entry.get())
                    pid_info['ki'] = float(pid.ki.entry.get())
                    pid_info['kd'] = float(pid.kd.entry.get())
                    pid_info['arduino_address'] = pid.arduino_address.entry.get()
                    pid_info['sweep_continuous'] = str_to_tuple(str(pid.sweep_continuous.combobox.get()))


            # def print_dict(a):
            #     for key in a:
            #         print(f"{key}: {a[key]}")
            # print_dict(instrument_info)
            # print('===========================================================================================')
            # print_dict(sweep_info)
            # print('===========================================================================================')
            # print_dict(pid_info)
            # print('===========================================================================================')
            # print_dict(file_info)

        profile = {'instrument_info': instrument_info,
                   'sweep_info': sweep_info,
                   'pid_info': pid_info,
                   'file_info': file_info
                   }

    def profile_show():
        global profile
        instrument_info = profile['instrument_info']
        sweep_info = profile['sweep_info']
        pid_info = profile['pid_info']
        file_info = profile['file_info']

        file_list[0].file_name.entry.delete(0, 'end')
        file_list[0].file_name.entry.insert(0, file_info['file_name'])
        file_list[0].file_order.entry.delete(0, 'end')
        file_list[0].file_order.entry.insert(0, file_info['file_order'])
        file_list[0].dir_entry.entry.delete(0, 'end')
        file_list[0].dir_entry.entry.insert(0, file_info['file_path'])
        file_list[0].mynote.delete('1.0', 'end')
        file_list[0].mynote.insert('1.0', file_info['mynote'])
        file_list[0].file_size.entry.delete(0, 'end')
        file_list[0].file_size.entry.insert(0, file_info['data_size'])
        file_list[0].data_interval.entry.delete(0, 'end')
        file_list[0].data_interval.entry.insert(0, file_info['data_interval'])

        i = 0
        for name in instrument_info['variable_name']:
            if name == 'vna_data':
                instrument_list[i].f_min.entry.delete(0, 'end')
                instrument_list[i].f_min.entry.insert(0, instrument_info['f_min'])
                instrument_list[i].f_max.entry.delete(0, 'end')
                instrument_list[i].f_max.entry.insert(0, instrument_info['f_max'])
                instrument_list[i].points.entry.delete(0, 'end')
                instrument_list[i].points.entry.insert(0, instrument_info['points'])
                instrument_list[i].power.entry.delete(0, 'end')
                instrument_list[i].power.entry.insert(0, instrument_info['power'])
                instrument_list[i].bandwidth.entry.delete(0, 'end')
                instrument_list[i].bandwidth.entry.insert(0, instrument_info['bandwidth'])
                instrument_list[i].average.entry.delete(0, 'end')
                instrument_list[i].average.entry.insert(0, instrument_info['average'])
                instrument_list[i].variable_name.entry.delete(0, 'end')
                instrument_list[i].variable_name.entry.insert(0, 'vna_data')
                instrument_list[i].visa_address.combobox.set(instrument_info['instrument_address'][i])
                instrument_list[i].function_selection.combobox.set(instrument_info['function'][i])
                instrument_list[i].instrument_name.combobox.set(instrument_info['instrument_name'][i])
            else:
                i += 1
                if 'vna_data' in instrument_info['variable_name']:
                    j = i
                else:
                    j = i-1
                instrument_list[i].variable_name.entry.delete(0, 'end')
                instrument_list[i].variable_name.entry.insert(0, instrument_info['variable_name'][j])
                instrument_list[i].visa_address.combobox.set(instrument_info['instrument_address'][j])
                instrument_list[i].function_selection.combobox.set(instrument_info['function'][j])
                instrument_list[i].instrument_name.combobox.set(instrument_info['instrument_name'][j])

        def tuple_to_str(flag):
            if flag:
                return 'Yes'
            elif not flag:
                return 'No'

        i = 0
        for name in sweep_info['variable_name']:
            sweep_list[i].instrument_name.combobox.set(sweep_info['instrument_name'][i])
            sweep_list[i].sweep_variable_name.entry.delete(0, 'end')
            sweep_list[i].sweep_variable_name.entry.insert(0, sweep_info['variable_name'][i])
            sweep_list[i].visa_address.combobox.set(sweep_info['instrument_address'][i])
            sweep_list[i].function_selection.combobox.set(sweep_info['function'][i])
            sweep_list[i].sweep_bottom_limit.entry.delete(0, 'end')
            sweep_list[i].sweep_bottom_limit.entry.insert(0, sweep_info['sweep_bottom_limit'][i])
            sweep_list[i].sweep_step_size.entry.delete(0, 'end')
            sweep_list[i].sweep_step_size.entry.insert(0, sweep_info['sweep_step_size'][i])
            sweep_list[i].sweep_up_limit.entry.delete(0, 'end')
            sweep_list[i].sweep_up_limit.entry.insert(0, sweep_info['sweep_up_limit'][i])
            sweep_list[i].sweep_delay.entry.delete(0, 'end')
            sweep_list[i].sweep_delay.entry.insert(0, sweep_info['sweep_delay'][i])
            sweep_list[i].sweep_back.combobox.set(tuple_to_str(sweep_info['sweep_up_and_down_flag'][i]))
            i += 1

        if pid_info['pid_variable_name'] != None:
            pid_list[0].pid_variable_name.combobox.set(pid_info['pid_variable_name'])
            pid_list[0].set_point.entry.delete(0, 'end')
            pid_list[0].set_point.entry.insert(0, pid_info['Setpoint'])
            pid_list[0].sweep_back.combobox.set(tuple_to_str(pid_info['sweep_up_and_down_flag']))
            if pid_info['pid_variable_name'] == 'ICET noise setup':
                noise_config(pid_list[0])
                pid_list[0].instrument_name.combobox.set(pid_info['instrument_name'])
                pid_list[0].visa_address.combobox.set(pid_info['instrument_address'])
                pid_list[0].function_selection.combobox.set(pid_info['function'])
                pid_list[0].Lowkp.entry.delete(0, 'end')
                pid_list[0].Lowkp.entry.insert(0, pid_info['Lowkp'])
                pid_list[0].Lowki.entry.delete(0, 'end')
                pid_list[0].Lowki.entry.insert(0, pid_info['Lowki'])
                pid_list[0].Lowkd.entry.delete(0, 'end')
                pid_list[0].Lowkd.entry.insert(0, pid_info['Lowkd'])
                pid_list[0].Highkp.entry.delete(0, 'end')
                pid_list[0].Highkp.entry.insert(0, pid_info['Highkp'])
                pid_list[0].Highki.entry.delete(0, 'end')
                pid_list[0].Highki.entry.insert(0, pid_info['Highki'])
                pid_list[0].Highkd.entry.delete(0, 'end')
                pid_list[0].Highkd.entry.insert(0, pid_info['Highkd'])
                pid_list[0].step_size.entry.delete(0, 'end')
                pid_list[0].step_size.entry.insert(0, pid_info['step_size'])
                pid_list[0].arduino_address.entry.delete(0, 'end')
                pid_list[0].arduino_address.entry.insert(0, pid_info['arduino_address'])
                pid_list[0].sweep_continuous.combobox.set(tuple_to_str(pid_info['sweep_continuous']))
            elif pid_info['pid_variable_name'] == 'NV transfer setup':
                NV_config(pid_list[0])
                pid_list[0].kp.entry.delete(0, 'end')
                pid_list[0].kp.entry.insert(0, pid_info['kp'])
                pid_list[0].ki.entry.delete(0, 'end')
                pid_list[0].ki.entry.insert(0, pid_info['ki'])
                pid_list[0].kd.entry.delete(0, 'end')
                pid_list[0].kd.entry.insert(0, pid_info['kd'])
                pid_list[0].arduino_address.entry.delete(0, 'end')
                pid_list[0].arduino_address.entry.insert(0, pid_info['arduino_address'])
                pid_list[0].sweep_continuous.combobox.set(tuple_to_str(pid_info['sweep_continuous']))



    def update_visa_list():
        q.put({'query': 'refresh_visa'})

    def start_measurement():
        q.put({'query': 'run_measurement'})


    def display_visa_list(visa_list):
        for instrument in instrument_list:
            instrument.visa_address.combobox.config(values=('None',) + visa_list + ('Refresh',))
            instrument.visa_address.combobox.current(0)
        for sweep in sweep_list:
            sweep.visa_address.combobox.config(values=('None',) + visa_list + ('Refresh',))
            sweep.visa_address.combobox.current(0)
        for pid in pid_list:
            pid.visa_address.combobox.config(values=('None',) + visa_list + ('Refresh',))
            pid.visa_address.combobox.current(0)

    def reply_handler():
        global reply
        if reply:
            if reply['reply'] == 'display_visa_list':
                display_visa_list(reply['visa_list'])
            reply = None
        window.after(50, reply_handler)

    def initialize():
        t = threading.Thread(target=background)
        t.daemon = True
        t.start()

        file_frame = StyleFrame(
            window,
            label='File',
            width=int(sizex / 4) - 60,
            height=int(sizey / 2),
            column=0, row=1
        )
        sweep_frame = StyleFrame(
            window,
            label='Sweep',
            width=int(sizex / 4) * 3 + 60,
            height=int(sizey / 2),
            column=1, row=1
        )

        scrollable_instrument_frame = ScrollableInstrumentFrame(window)
        scrollable_instrument_frame.grid(column=0, row=0, columnspan=2)
        instrument_frame = scrollable_instrument_frame.instrument_frame

        vna = InstrumentFrame(
            instrument_frame,
            label='VNA',
            width=int(sizex / 4) - 30,
            height=int(sizey / 2) - 120,
            column=0, row=1, columnspan=2
        )

        for i in range(1, measurements):
            instrument_i = InstrumentFrame(
                instrument_frame,
                label=f'Instrument {i}',
                width=int(sizex / 8),
                height=int(sizey / 2) - 120,
                column=1+i, row=1
            )

        loop_1 = SweepFrame(
            sweep_frame,
            label='Main loop',
            width=int(sizex / 4) - 30,
            height=int(sizey / 2) - 80,
            column=0, row=1
        )
        loop_2 = SweepFrame(
            sweep_frame,
            label='Secondary loop',
            width=int(sizex / 4) - 30,
            height=int(sizey / 2) - 80,
            column=1, row=1
        )
        pid = PidFrame(
            sweep_frame,
            label='PID control',
            width=int(sizex / 4) - 30,
            height=int(sizey / 2) - 80,
            column=2, row=1
        )
        file = FileFrame(
            file_frame,
            label='Save data setup',
            width=int(sizex / 4)-110,
            height=int(sizey / 2),
            column=0, row=1
        )
        update_visa_list()
        window.after(50, reply_handler)

    window.after(50, initialize)
    window.mainloop()

def plot_window():
    global q, reply_1, profile
    # Window
    window = tk.Tk()
    window.title('Realtime ploting')
    window.geometry('800x450')
    window.configure(bg=background_color)
    window.columnconfigure(0, weight=1)
    window.columnconfigure(1, weight=4)
    window.rowconfigure(0, weight=1)
    window.rowconfigure(1, weight=4)

    class Combobox(tk.Frame):
        def __init__(self, master, label, values=[None], width=160, height=60, box_color = box_color):
            super().__init__(
                master, width=width, height=height,
                bg=box_color,
                bd=3
            )
            self.grid_propagate(False)

            self.rowconfigure(0, weight=1)
            self.rowconfigure(1, weight=1)

            self.label = tk.Label(
                self,
                text=label,
                height=1,
                bg=box_color
            )
            self.label.grid(column=0, row=0, sticky='w')

            self.combotext = tk.StringVar()
            self.combobox = ttk.Combobox(
                self,
                textvariable=self.combotext
            )
            self.combobox['values'] = values
            self.combobox.current(0)
            self.combobox.grid(column=0, row=1, sticky='we')

    plot_list = []

    # Single instrument frame
    class InstrumentFrame(tk.Frame):
        def __init__(self, instrument_frame, label, width, height, row, column, rowspan=1, columnspan=1):
            super().__init__(
                instrument_frame, width=width, height=height,
                bg=box_color,
                highlightbackground=border_color,
                highlightcolor=highlight_border_color,
                highlightthickness=1.5,
                bd=6
            )
            plot_list.append(self)
            self.grid(
                row=row, column=column,
                rowspan=rowspan, columnspan=columnspan,
                ipadx=frame_ipadx, ipady=frame_ipady,
                padx=frame_padx, pady=frame_pady,
                sticky='w'
            )
            self.grid_propagate(False)

            self.rowconfigure(0, weight=1)
            self.rowconfigure(1, weight=9)
            self.rowconfigure(2, weight=2)

            self.label = tk.Label(
                self,
                text=label,
                height=1,
                bg=box_color
            )
            self.label.grid(row=0, columnspan=2)
            self.content = tk.Frame(
                self, width=width, height=height,
                bg=box_color
            )
            self.content.grid(row=1, sticky='nw')


            self.x_1 = Combobox(self.content, 'X1', values=['None'])
            self.x_1.grid(row=0)
            self.y_1 = Combobox(self.content, 'Y1, Y1 vs X1 in red', values=['None'])
            self.y_1.grid(row=1)
            self.x_2 = Combobox(self.content, 'X2, Y1 vs X2 in green', values=['None'])
            self.x_2.grid(row=2)
            self.y_2 = Combobox(self.content, 'Y2, Y2 ys X1 in blue', values=['None'])
            self.y_2.grid(row=3)
            self.selector = Combobox(self.content, 'data_selector', values=['data','pid','sweep'])
            self.selector.grid(row=4)
            self.selector.combobox.current(0)

            def event_get_axis(event):
                global profile
                if self.selector.combobox.get() == 'data':
                    axis_list = profile['instrument_info']['variable_name'] + ['timestamp']+ ['None']
                    self.x_1.combobox.config(values=axis_list)
                    self.x_1.combobox.current(0)
                    self.y_1.combobox.config(values=axis_list)
                    self.y_1.combobox.current(0)
                    self.x_2.combobox.config(values=axis_list)
                    self.y_2.combobox.config(values=axis_list)
                elif self.selector.combobox.get() == 'sweep':
                    axis_list = profile['sweep_info']['variable_name'] + ['timestamp']+ ['None']
                    self.x_1.combobox.config(values=axis_list)
                    self.y_1.combobox.config(values=axis_list)
                    self.x_2.combobox.config(values=axis_list)
                    self.y_2.combobox.config(values=axis_list)
                elif self.selector.combobox.get() == 'sweep':
                    axis_list = ['time','temp']+ ['None']
                    self.x_1.combobox.config(values=axis_list)
                    self.y_1.combobox.config(values=axis_list)
                    self.x_2.combobox.config(values=axis_list)
                    self.y_2.combobox.config(values=axis_list)

            self.selector.combobox.bind('<<ComboboxSelected>>', event_get_axis)

            self.update_button = ttk.Button(self.content, text="Start plotting", command=update_plot_axis, padding=4)
            self.update_button.grid(row=5, column=0, sticky='ew')
            def Reset_plot():
                global last_datalength
                last_datalength = min(len(plot_name[0].x1),len(plot_name[0].y1))
            self.reset_button = ttk.Button(self.content, text="Reset plot from now", command=Reset_plot, padding=4)
            self.reset_button.grid(row=6, column=0, sticky='ew')

    plot_name = []
    class PlotFrame(tk.Frame):
        def __init__(self, plot_frame, width, height, row, column, rowspan=1, columnspan=1):
            super().__init__(
                plot_frame, width=width, height=height,
                bg=box_color,
                highlightbackground=border_color,
                highlightcolor=highlight_border_color,
                highlightthickness=1.5,
                bd=6
            )
            plot_name.append(self)
            self.grid(
                row=row, column=column,
                rowspan=rowspan, columnspan=columnspan,
                ipadx=frame_ipadx, ipady=frame_ipady,
                padx=frame_padx, pady=frame_pady,
                sticky='w'
            )
            self.grid_propagate(False)

            self.rowconfigure(0, weight=1)
            self.rowconfigure(1, weight=9)
            self.rowconfigure(2, weight=2)

            fg = plt.figure(figsize=(5, 4), dpi=100)
            gs = fg.add_gridspec(1, 2, width_ratios=[1, 0])
            global ax,ax1,ax2
            ax = fg.add_subplot(gs[0])
            # plot another line that share the same x axis
            ax1 = ax.twinx()
            ax2 = ax.twiny()

            canvas = FigureCanvasTkAgg(fg, master=self)  # A tk.DrawingArea.
            canvas.draw()
            canvas.get_tk_widget().grid()
            self.x1 = np.array([None])
            self.x1_name = ''
            self.x2 = np.array([None])
            self.x2_name = ''
            self.y1 = np.array([None])
            self.y1_name = ''
            self.y2 = np.array([None])
            self.y2_name = ''

            def drawimg():
                global ax,ax1,ax2,start_time, last_datalength
                ax.clear()
                ax1.clear()
                ax2.clear()
                def normalize_timestamp(x,x_name):
                    global start_time
                    if x_name == 'timestamp' and x.any() != None:
                        for i in range(0,len(x)):
                            x[i] = x[i] - start_time
                normalize_timestamp(self.x1, self.x1_name)
                normalize_timestamp(self.x2, self.x2_name)
                normalize_timestamp(self.y1, self.y1_name)
                normalize_timestamp(self.y2, self.y2_name)

                data_length = min(len(self.x1),len(self.y1))
                if self.x1.any() != None and self.y1.any() != None:
                    ax.set_xlabel(self.x1_name)
                    ax.set_ylabel(self.y1_name)
                    ax.plot(self.x1[last_datalength:data_length-1], self.y1[last_datalength:data_length-1], '.r')
                    if self.y2.any() != None:
                        ax1.set_ylabel(self.y2_name)
                        ax1.plot(self.x1[last_datalength:data_length-1], self.y2[last_datalength:data_length-1], '.b')
                    if self.x2.any() != None:
                        ax2.set_xlabel(self.x2_name)
                        ax2.plot(self.x2[last_datalength:data_length-1], self.y1[last_datalength:data_length-1], '.g')
                canvas.draw()
                window.after(1000,drawimg)

            drawimg()


    def plotInWindow(dataToplot = None):
        if dataToplot!= None:
            plot_name[0].x1 = dataToplot['x1']
            plot_name[0].x1_name = plot_list[0].x_1.combobox.get()
            plot_name[0].y1 = dataToplot['y1']
            plot_name[0].y1_name = plot_list[0].y_1.combobox.get()
            plot_name[0].x2 = dataToplot['x2']
            plot_name[0].x2_name = plot_list[0].x_2.combobox.get()
            plot_name[0].y2 = dataToplot['y2']
            plot_name[0].y2_name = plot_list[0].y_2.combobox.get()
            window.after(100, update_plot_axis)


    def update_plot_axis():
        q.put({'plot': 'plot',
               'x1': plot_list[0].x_1.combobox.get(),
               'y1': plot_list[0].y_1.combobox.get(),
               'x2': plot_list[0].x_2.combobox.get(),
               'y2': plot_list[0].y_2.combobox.get(),
               'selector': plot_list[0].selector.combobox.get()
                }
              )
        # print('asking for data')

    def reply_handler():
        global reply_1
        if reply_1 != None:
            if 'plot' in reply_1.keys():
                if reply_1['plot']['flag'] == True:
                    plotInWindow(reply_1['plot'])
        reply_1 = None
        window.after(50, reply_handler)

    def initialize():
        t = threading.Thread(target=pop_window)
        t.daemon = True
        t.start()

        selection_panel = InstrumentFrame(
            window,
            label='Plot display',
            width= 200,
            height= 420,
            column=0, row=0
        )
        plot_frame =PlotFrame(
            window,
            width= 520,
            height= 420,
            column=1, row=0
        )

        window.after(50, reply_handler)

    window.after(50, initialize)
    window.mainloop()

plot_window()

