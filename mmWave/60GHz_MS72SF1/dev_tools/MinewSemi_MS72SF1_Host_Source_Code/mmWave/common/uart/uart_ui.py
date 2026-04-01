import tkinter as tk
import tkinter.ttk as ttk

#import uart_module as uart_module
import common.uart.uart_module as uart_module

class Uart_ui(object):
    def __init__(self, frame_uart, frame_trx):
        self.window = frame_trx
        
        tk.Label(frame_uart, text="端口 (port)", bg="lightblue").place(x=10, y=10)
        self.this_com_combobox = ttk.Combobox(frame_uart, values="", width=9)
        self.this_com_combobox.place(x=50, y=10)

        tk.Label(frame_uart, text="波特率 (baud rate)", bg="lightblue").place(x=150, y=10)
        btl_combobox_value = ["9600", "19200", "38400", "57600", "115200"]
        self.this_btl_combobox = ttk.Combobox(frame_uart, values=btl_combobox_value, width=9)
        self.this_btl_combobox.current(4)
        self.this_btl_combobox.place(x=197, y=10)

        self.this_open_button = ttk.Button(frame_uart, text="打开 (open)", command=lambda:uart_module.serial_open(self.this_com_combobox, self.this_btl_combobox))
        self.this_open_button.place(x=300, y=7)

        self.this_uart_com_update_button = ttk.Button(frame_uart, text="更新 (update)", command=lambda:uart_module.serial_update(self.this_com_combobox))
        self.this_uart_com_update_button.place(x=400, y=7)
        uart_module.serial_update(self.this_com_combobox)

        self.this_rev_Text = None
        self.window = None
