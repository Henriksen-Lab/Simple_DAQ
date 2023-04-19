import pyvisa, queue
import sys, os, time, threading
from tkinter import ttk
import tkinter as tk
import serial
from UI_manager.DataManager import get_value,set_value
from Instrument_Drivers.Instrument_dict import instrument_dict
from Instrument_Drivers.SR830 import *

global instrument_dict, onetime_dict
onetime_dict = {'get':{},
                'set':{},
                'combobox':{}}
onetime_dict['get'].update({'SR830':{'time_constant','sensitivity','harmonic'}})
onetime_dict['set'].update({'SR830':{'time_constant','sensitivity','harmonic'}})
onetime_dict['combobox'].update({'SR830':{}})
onetime_dict['combobox']['SR830'].update({'time_constant': SR830_timeconstant,
                                          'sensitivity': SR830_sensitivity})

# Size
sizex = 1500
sizey = 400

# Colors
background_color = 'white'
frame_background_color = '#FCFCFC'
border_color = 'turquoise'
highlight_border_color = 'salmon'
box_color = '#E7F6F2'

# Padding
frame_ipadx = 5
frame_ipady = 5
frame_padx = 10
frame_pady = 10

q = queue.Queue()
reply = None


def background():
    global q, reply
    rm = pyvisa.ResourceManager()
    instr_list = rm.list_resources()
    def msg_handler(msg):
        global reply
        if msg['query'] == 'refresh_visa':
            reply = {'reply': 'display_visa_list', 'visa_list': instr_list}

    while True:
        msg = q.get()
        msg_handler(msg)

def pop_window():
    global q, reply
    # Window
    window = tk.Tk()
    window.title('Visa resourse trouble shooting')
    window.geometry(f'{sizex}x{sizey}')
    window.configure(bg=background_color)
    window.columnconfigure(0, weight=1)
    window.columnconfigure(1, weight=4)
    window.rowconfigure(0, weight=1)
    window.rowconfigure(1, weight=4)

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
        def __init__(self, master, label, width=160, height=60, columnspan=1, initial_value='', box_color=box_color):
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
            self.label.grid(column=0, row=0, sticky='w', columnspan=columnspan)

            self.entry = tk.Entry(
                self,
                width=width
            )
            self.entry.grid(column=0, row=1, sticky='ew', columnspan=columnspan)
            self.entry.insert(0, initial_value)

    class EntryBoxH(tk.Frame):
        def __init__(self, master, label, width=160, height=50, initial_value='', box_color=box_color):
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
        def __init__(self, master, label, width=160, height=60, box_color=box_color):
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
                width=5
            )
            self.combobox['values'] = ['No', 'Yes']
            self.combobox.current(0)
            self.combobox.grid(column=1, row=0, sticky='e')
            self.combobox.current(0)

    class Combobox(tk.Frame):
        def __init__(self, master, label, values=[None], width=160, height=60, box_color=box_color):
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
        def __init__(self, instrument_frame, width, height, row, column, rowspan=1, columnspan=1):
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

            self.content = tk.Frame(
                self, width=width, height=height,
                bg=box_color
            )
            self.content.grid(row=0, sticky='nw')

            self.visa_address = Combobox(self.content, 'Visa address', values=['Refreshing...'])

            def event_visa_address_refresh(event):
                if self.visa_address.combobox.get() == 'Refresh':
                    update_visa_list()

            self.visa_address.combobox.bind('<<ComboboxSelected>>', event_visa_address_refresh)
            self.visa_address.grid(row=1)

            def display_query():
                address = self.visa_address.combobox.get()
                if 'ASRL' in address:
                    address = 'COM' + address.split('::')[0][4:]
                    try:
                        port = serial.Serial(port=address, baudrate=115200, timeout=0.5)
                        command = f'*IDN?\r\n'
                        port.write(bytes(command, 'utf-8'))
                        time.sleep(0.5)
                        out = ''
                        res = 0
                        while port.inWaiting() > 0:
                            out += port.read().decode("ascii")
                        if out != '':
                            res = out
                    except:
                        res = 'error'
                    finally:
                        port.close()
                else:
                    try:
                        rm = pyvisa.ResourceManager()
                        instr = rm.open_resource(address)
                        res = instr.query('*IDN?')
                    except:
                        res = 'error'
                    finally:
                        instr.close()


                self.visa_query.delete('1.0', 'end')
                self.visa_query.insert('1.0', res)

            self.visa_query_button = tk.Button(self.content, text="Query identity", command=display_query)
            self.visa_query_button.grid(row=1 , column=4, sticky='w')

            self.visa_query = tk.Text(master=self.content, height=4, width=40)
            self.visa_query.grid(row=1, column=1, sticky='news', padx=frame_padx, pady=frame_pady, columnspan=3)


            instr_list = ['None']
            global instrument_dict, onetime_dict
            for name in instrument_dict['get'].keys():
                instr_list.append(name)
            for name in instrument_dict['set'].keys():
                if name not in instr_list:
                    instr_list.append(name)
            for name in onetime_dict['get'].keys():
                if name not in instr_list:
                    instr_list.append(name)
            for name in onetime_dict['set'].keys():
                if name not in instr_list:
                    instr_list.append(name)

            self.instrument_name = Combobox(self.content, 'Instrument_name', values=instr_list)
            self.instrument_name.grid(row=2)

            self.function_selection = Combobox(self.content, 'Reading Function selection')
            self.function_selection.grid(row=3)

            def update_function_selection(event):
                global instrument_dict, onetime_dict
                func_list = ['None']
                name = self.instrument_name.combobox.get()
                if name in instrument_dict['get'].keys():
                    func_list = instrument_dict['get'][name]
                if name in onetime_dict['get'].keys():
                    func_list += onetime_dict['get'][name]
                self.function_selection.combobox.config(values=func_list)
                self.function_selection.combobox.current(0)

                func_list = ['None']
                if name in instrument_dict['set'].keys():
                    func_list = instrument_dict['set'][name]
                if name in onetime_dict['set'].keys():
                    func_list += onetime_dict['set'][name]
                self.set_function_selection.combobox.config(values=func_list)
                self.set_function_selection.combobox.current(0)

            self.instrument_name.combobox.bind('<<ComboboxSelected>>', update_function_selection)

            self.set_function_selection = Combobox(self.content, 'Setting Function selection')
            self.set_function_selection.grid(row=4)

            def update_input(event):
                name = self.instrument_name.combobox.get()
                if name in onetime_dict['combobox'].keys():
                    func = self.set_function_selection.combobox.get()
                    if func in onetime_dict['combobox'][name].keys():
                        combobox_config(self)
                    else:
                        entry_config(self)
                else:
                    entry_config(self)

            self.set_function_selection.combobox.bind('<<ComboboxSelected>>', update_input)

            self.visa_read = tk.Text(master=self.content, height=2, width=40)
            self.visa_read.grid(row=2, column=1, sticky='news', padx=frame_padx, pady=frame_pady, columnspan=3)

            def read():
                address = self.visa_address.combobox.get()
                try:
                    value = get_value(address=self.visa_address.combobox.get(),
                                      name=self.instrument_name.combobox.get(),
                                      func=self.function_selection.combobox.get())
                except:
                    value = 'error'

                self.visa_read.delete('1.0', 'end')
                self.visa_read.insert('1.0', value)

            def write():
                global onetime_dict
                name = self.instrument_name.combobox.get()
                func = self.set_function_selection.combobox.get()
                try:
                    if func in onetime_dict['combobox'][name].keys():
                        value = self.visa_write_combobox.combobox.get()
                    else:
                        value = self.visa_write.get('1.0', 'end-1c')
                        value = float(value)
                    set_value(value=value,
                              address=self.visa_address.combobox.get(),
                              name=self.instrument_name.combobox.get(),
                              func=self.set_function_selection.combobox.get())
                    value = str(value) + ', ' + 'output tried'
                    self.visa_write_result.delete('1.0', 'end')
                    self.visa_write_result.insert('1.0', value)
                finally:
                    print('Output Tried')

            self.visa_read_button = tk.Button(self.content, text="Query value", command=read)
            self.visa_read_button.grid(row=2, column=4, sticky='w')

            self.visa_write = tk.Text(master=self.content, height=2, width=40)
            self.visa_write.grid(row=3, column=1, sticky='news', padx=frame_padx, pady=frame_pady, columnspan=3)

            self.visa_write_button = tk.Button(self.content, text='Set value', command=write)
            self.visa_write_button.grid(row=3, column=4, sticky='w')

            self.visa_write_result = tk.Text(master=self.content, height=2, width=40)
            self.visa_write_result.grid(row=4, column=1, sticky='news', padx=frame_padx, pady=frame_pady, columnspan=3)

    def combobox_config(self):
        global onetime_dict
        name = self.instrument_name.combobox.get()
        func = self.set_function_selection.combobox.get()
        selector = onetime_dict['combobox'][name][func]
        if 'visa_write' in dir(self):
            self.visa_write.grid_forget()
            self.visa_write_combobox = Combobox(self.content, f'Set {func}')
            self.visa_write_combobox.grid(row=3, column=1, columnspan=3)
            self.visa_write_combobox.combobox.config(values=selector)
            self.visa_write_combobox.combobox.current(0)
    def entry_config(self):
        if 'visa_write_combobox' in dir(self):
            self.visa_write_combobox.grid_forget()
            self.visa_write = tk.Text(master=self.content, height=2, width=40)
            self.visa_write.grid(row=3, column=1, sticky='news', padx=frame_padx, pady=frame_pady, columnspan=3)



    def update_visa_list():
        q.put({'query': 'refresh_visa'})

    def display_visa_list(visa_list):
        for instrument in instrument_list:
            instrument.visa_address.combobox.config(values=('None',) + visa_list + ('Refresh',))
            instrument.visa_address.combobox.current(0)

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

        visa_frame = StyleFrame(
            window,
            label='Visa sourse',
            width=int(sizex)-80,
            height=int(sizey),
            column=0, row=0
        )
        visa_1 = InstrumentFrame(
            visa_frame,
            width=int(sizex)/2 - 120,
            height=sizey,
            column=0, row=1
        )

        visa_1 = InstrumentFrame(
            visa_frame,
            width=int(sizex/2) - 120,
            height=sizey,
            column=1, row=1
        )

        update_visa_list()
        window.after(50, reply_handler)

    window.after(50, initialize)
    window.mainloop()

pop_window()