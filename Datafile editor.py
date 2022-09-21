import sys, os, time, threading
from tkinter import ttk
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename
from Instrument_Drivers.FileManager import *


# Size
sizex = 800
sizey = 350

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


def pop_window():
    # Window
    window = tk.Tk()
    window.title('Datafile editor')
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


    control_list = []
    # Single control frame
    class InstrumentFrame(tk.Frame):
        def __init__(self, control_frame, width, height, row, column, rowspan=1, columnspan=1):
            super().__init__(
                control_frame, width=width, height=height,
                bg=box_color,
                highlightbackground=border_color,
                highlightcolor=highlight_border_color,
                highlightthickness=1.5,
                bd=6
            )
            control_list.append(self)
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

            self.data_dir_entry = EntryBox(self.content, 'Data folder path', initial_value='Please enter or choose', width=260)
            self.data_dir_entry.grid(row=1, column=0, sticky='ew', columnspan=2)

            def choose_data_folder():
                select_directory = askdirectory(title="choose data folder path")
                self.data_dir_entry.entry.delete(0, 'end')
                self.data_dir_entry.entry.insert(0, select_directory)

            self.data_folder_path = ttk.Button(
                self.content,
                text="choose folder",
                command=choose_data_folder,
                padding=4
            )
            self.data_folder_path.grid(row=1, column=0, sticky='ne', columnspan=2)

            self.sweep_dir_entry = EntryBox(self.content, 'Sweep folder path', initial_value='Please enter or choose',
                                           width=260)
            self.sweep_dir_entry.grid(row=2, column=0, sticky='ew', columnspan=2)

            def choose_sweep_folder():
                select_directory = askdirectory(title="choose sweep log path")
                self.sweep_dir_entry.entry.delete(0, 'end')
                self.sweep_dir_entry.entry.insert(0, select_directory)

            self.sweep_folder_path = ttk.Button(
                self.content,
                text="choose folder",
                command=choose_sweep_folder,
                padding=4
            )
            self.sweep_folder_path.grid(row=2, column=0, sticky='ne', columnspan=2)

            self.pid_dir_entry = EntryBox(self.content, 'PID folder path', initial_value='Please enter or choose',
                                           width=260)
            self.pid_dir_entry.grid(row=3, column=0, sticky='ew', columnspan=2)

            def choose_pid_folder():
                select_directory = askdirectory(title="choose pid log path")
                self.pid_dir_entry.entry.delete(0, 'end')
                self.pid_dir_entry.entry.insert(0, select_directory)

            self.pid_folder_path = ttk.Button(
                self.content,
                text="choose folder",
                command=choose_pid_folder,
                padding=4
            )
            self.pid_folder_path.grid(row=3, column=0, sticky='ne', columnspan=2)

            self.fridge_log_dir_entry = EntryBox(self.content, 'Fridge log folder path', initial_value='Please enter or choose',
                                          width=260)
            self.fridge_log_dir_entry.grid(row=4, column=0, sticky='ew', columnspan=2)

            def choose_fridge_log_folder():
                select_directory = askdirectory(title="choose Fridge log path")
                self.fridge_log_dir_entry.entry.delete(0, 'end')
                self.fridge_log_dir_entry.entry.insert(0, select_directory)

            self.fridge_log_folder_path = ttk.Button(
                self.content,
                text="choose folder",
                command=choose_fridge_log_folder,
                padding=4
            )
            self.fridge_log_folder_path.grid(row=4, column=0, sticky='ne', columnspan=2)

    file_list_1 = []
    class FileFrame(tk.Frame):
        def __init__(self, file_frame, label, width, height, row, column, rowspan=1, columnspan=1):
            super().__init__(
                file_frame, width=width, height=height,
                bg=box_color,
                highlightbackground=border_color,
                highlightcolor=highlight_border_color,
                highlightthickness=1.5,
                bd=6
            )
            file_list_1.append(self)
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
            self.label.grid(row=0,column=0,sticky='ew')
            self.content = tk.Frame(
                self, width=width-10, height=height-10,
                bg=box_color
            )
            self.content.grid(row=1, column=0, sticky='new')

            self.file_name = EntryBox(self.content, 'File name',width=260, initial_value='name_me_please',box_color=box_color)
            self.file_name.grid(row=1, column=0, sticky='w', columnspan=2)
            self.dir_entry = EntryBox(self.content, 'Folder path', initial_value='Please enter or choose',width=260,box_color=box_color)
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

            def convert():
                all_data = MainData(data_path=control_list[0].data_dir_entry.entry.get(),
                                    sweep_path=control_list[0].sweep_dir_entry.entry.get(),
                                    pid_path=control_list[0].pid_dir_entry.entry.get(),
                                    fridge_log_path=control_list[0].fridge_log_dir_entry.entry.get())
                all_data.all_data_save(filename=file_list_1[0].file_name.entry.get(),
                                       path=file_list_1[0].dir_entry.entry.get())

            self.run_button = ttk.Button(self.content, text="Convert", command=convert, padding=4)
            self.run_button.grid(row=3, column=0, sticky='ew',columnspan=2)


    def initialize():
        control = StyleFrame(
            window,
            label='Visa sourse',
            width=int(sizex)-80,
            height=int(sizey),
            column=0, row=0
        )
        control_1 = InstrumentFrame(
            control,
            width=int(sizex)/2 - 120,
            height=sizey,
            column=0, row=1
        )
        file = FileFrame(
            control,
            label='Output setting',
            width=int(sizex)/2 - 120,
            height=sizey,
            column=1, row=1
        )

    window.after(50, initialize)
    window.mainloop()

pop_window()