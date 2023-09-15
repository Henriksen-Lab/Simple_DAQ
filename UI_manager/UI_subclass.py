from tkinter import ttk
import tkinter as tk

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