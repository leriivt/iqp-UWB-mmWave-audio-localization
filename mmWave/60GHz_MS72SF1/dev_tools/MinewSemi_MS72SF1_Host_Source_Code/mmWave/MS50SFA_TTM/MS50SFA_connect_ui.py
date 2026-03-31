import tkinter as tk
import tkinter.ttk as ttk

import MS50SFA_TTM.MS50SFA_read_and_write as MS50SFA_WR
import MS50SFA_TTM.Format_conversion as Format_conversion
import system.sys_data as sys_data

class MS50SFA_Connect_ui(object):
    def __init__(self, frame_1, uart, uart_ui):
        self.uart = uart
        self.uart_ui = uart_ui
        self.Send_data = sys_data.SYS_mmWave_write
        
        self.Send_data.command_type = "ASCII"
        self.Send_data.data_type = "INT"
        self.Send_data.rev_type = "ASCII"
        self.Send_data.command_end_type = "HEX"

        self.Send_data.command = "TTM:"
        self.Send_data.send_min = 0
        self.Send_data.send_max = 1
        
        # tk.Label(frame_1, text="设置广播模式").grid(column=0,row=0)
        # this_combobox_value = ["透传", "广播"]
        # self.set_adv_mode_combobox = ttk.Combobox(frame_1, values=this_combobox_value, width=12)
        # self.set_adv_mode_combobox.current(1)
        # self.set_adv_mode_combobox.grid(column=1,row=0)
        # ttk.Button(frame_1, text="read", width=4, command=self.read_adv_mode).grid(column=2,row=0)
        # ttk.Button(frame_1, text="set", width=4, command=self.set_adv_mode).grid(column=3,row=0)

        tk.Label(frame_1, text="连接指定MAC").grid(column=0,row=2,padx=20,pady=10)
        self.connect_appoint_MAC_Entry = ttk.Entry(frame_1, width=15)
        self.connect_appoint_MAC_Entry.grid(column=1,row=2,padx=20)
        ttk.Button(frame_1, text="连接", width=4, command=self.connect_appoint_MAC).grid(column=2,row=2,padx=15)
        ttk.Button(frame_1, text="断开", width=4, command=self.set_Disconnect).grid(column=3,row=2,padx=15)
        self.connect_appoint_MAC_Entry.insert(0, "E0ED90D14B41")
        # self.connect_appoint_MAC_Entry.insert(0, "DB298844D9C8")
        # self.connect_appoint_MAC_Entry.insert(0, "E7546091C04C")

        # tk.Label(frame_1, text="设置连接模式").grid(column=0,row=4)
        # this_combobox_value = ["无需密码", "需要密码"]
        # self.set_connection_mode_combobox = ttk.Combobox(frame_1, values=this_combobox_value, width=12)
        # self.set_connection_mode_combobox.current(0)
        # self.set_connection_mode_combobox.grid(column=1,row=4)
        # ttk.Button(frame_1, text="read", width=4, command=self.read_connection_mode).grid(column=2,row=4)
        # ttk.Button(frame_1, text="set", width=4, command=self.set_connection_mode).grid(column=3,row=4)

        # tk.Label(frame_1, text="设置连接密码").grid(column=0, row=5)
        # self.set_connect_password_Entry = ttk.Entry(frame_1, width=15)
        # self.set_connect_password_Entry.grid(column=1, row=5)
        # ttk.Button(frame_1, text="read", width=4, command=self.read_connect_password).grid(column=2, row=5)
        # ttk.Button(frame_1, text="set", width=4, command=self.set_connect_password).grid(column=3, row=5)

        # tk.Label(frame_1, text="设置连接间隔").grid(column=0, row=6)
        # this_combobox_value = []
        # for i in range (1, 101, 1):
        #     this_combobox_value.append(str(i * 10) + " ms")
        # self.set_conntct_interval_combobox = ttk.Combobox(frame_1, values=this_combobox_value, width=12)
        # self.set_conntct_interval_combobox.current(0)
        # self.set_conntct_interval_combobox.grid(column=1, row=6)
        # ttk.Button(frame_1, text="read", width=4, command=self.read_conntct_interval).grid(column=2, row=6)
        # ttk.Button(frame_1, text="set", width=4, command=self.set_conntct_interval).grid(column=3, row=6)

        # self.this_Send_button = ttk.Button(frame_1, text="透传发送", command=self.this_Send_copy)
        # self.this_Send_button.grid(column=0, row=7)
        # self.this_Read_button = ttk.Button(frame_1, text="Read All", command=self.read_all)
        # self.this_Read_button.grid(column=2, row=7)
        
        # self.this_Send_checkbox_var = tk.IntVar()
        # tk.Checkbutton(frame_1, text="hex", variable=self.this_Send_checkbox_var).grid(column=3, row=7)
        # self.this_Send_checkbox_var.set(True)

        # self.this_Send_Entry = ttk.Entry(frame_1, width=38)
        # self.this_Send_Entry.grid(column=0, row=8, columnspan=4, padx=5, pady=5)
        # self.this_Send_Entry.delete(0, "end")
        # self.this_Send_Entry.insert(0, "123456789")
    
    def read_all(self):
        self.read_adv_mode()
        self.read_connection_mode()
        self.read_connect_password()
        self.read_conntct_interval()

    def read_adv_mode(self):
        self.Send_data.name = "查询广播模式"
        self.Send_data.command = "TTM:MOD"
        self.Send_data.data = ""
        self.Send_data.data_type = None
        self.Send_data.rev_type = "INT"
        self.Send_data.rev_min = 0
        self.Send_data.rev_max = 10
        self.Send_data.command_end = "?"

        res2 = MS50SFA_WR.get_data_from_remote(self.Send_data, self.uart, self.uart_ui)
        if res2 != -1 and res2 != -2:
            self.set_adv_mode_combobox.current(int(res2))
    
    def read_connection_mode(self):
        self.Send_data.name = "查询连接模式"
        self.Send_data.command = "TTM:PWE"
        self.Send_data.data = ""
        self.Send_data.data_type = None
        self.Send_data.rev_type = "INT"
        self.Send_data.rev_min = 0
        self.Send_data.rev_max = 10
        self.Send_data.command_end = "?"

        res2 = MS50SFA_WR.get_data_from_remote(self.Send_data, self.uart, self.uart_ui)
        if res2 != -1 and res2 != -2:
            self.set_connection_mode_combobox.current(int(res2))

    
    def read_connect_password(self):
        self.Send_data.name = "查询连接密码"
        self.Send_data.command = "TTM:PWD"
        self.Send_data.data = ""
        self.Send_data.data_type = None
        self.Send_data.rev_type = "ASCII"
        self.Send_data.rev_min = 0
        self.Send_data.rev_max = 10
        self.Send_data.command_end = "?"

        res2 = MS50SFA_WR.get_data_from_remote(self.Send_data, self.uart, self.uart_ui)
        if res2 != -1 and res2 != -2:
            self.set_connect_password_Entry.delete(0, tk.END)
            self.set_connect_password_Entry.insert(0, res2)
        
    
    def read_conntct_interval(self):
        self.Send_data.name = "查询连接间隔"
        self.Send_data.command = "TTM:CIT"
        self.Send_data.data = ""
        self.Send_data.data_type = None
        self.Send_data.rev_type = "INT"
        self.Send_data.rev_min = 0
        self.Send_data.rev_max = 10
        self.Send_data.command_end = "?"

        res2 = MS50SFA_WR.get_data_from_remote(self.Send_data, self.uart, self.uart_ui)
        if res2 != -1 and res2 != -2:
            self.set_conntct_interval_combobox.current(int(res2) - 1)

    
    def clear(self):
        self.set_adv_mode_combobox.set("")
        self.set_connection_mode_combobox.set("")
        self.set_connect_password_Entry.delete(0, tk.END)
        self.set_conntct_interval_combobox.set("")

    def set_adv_mode(self):
        data1 = self.set_adv_mode_combobox.get()
        if "透传" == data1:
            data1 = 0
        elif "广播" == data1:
            data1 = 1
        
        self.Send_data.name = "设置广播模式"
        self.Send_data.command_type = "ASCII"
        self.Send_data.command = "TTM:MOD-"
        self.Send_data.data = data1
        self.Send_data.send_min = 0
        self.Send_data.send_max = 1
        self.Send_data.data_type = "INT"
        self.Send_data.rev_type = "ASCII"
        self.Send_data.command_end_type = "HEX"
        self.Send_data.command_end = "0"

        MINEWSEMI_Send_data_Parameter_validity_check(self.Send_data, self.uart, self.uart_ui)
    
    def connect_appoint_MAC(self):
        data1 = self.connect_appoint_MAC_Entry.get()
        
        self.Send_data.name = "连接指定MAC"
        self.Send_data.command = "TTM:CONN-"
        self.Send_data.data = data1
        self.Send_data.send_min = 1*2
        self.Send_data.send_max = 6*2
        self.Send_data.data_type = "HEX"
        self.Send_data.rev_type = "ASCII"
        self.Send_data.command_end = "0"

        MINEWSEMI_Send_data_Parameter_validity_check(self.Send_data, self.uart, self.uart_ui)
    
    def set_connection_mode(self):
        data1 = self.set_connection_mode_combobox.get()

        if "无需密码" == data1:
            data1 = 0
        elif "需要密码" == data1:
            data1 = 1
        
        self.Send_data.name = "设置连接模式"
        self.Send_data.command = "TTM:PWE-"
        self.Send_data.data = data1
        self.Send_data.send_min = 0
        self.Send_data.send_max = 1
        self.Send_data.data_type = "INT"
        self.Send_data.rev_type = "ASCII"
        self.Send_data.command_end = "0"

        MINEWSEMI_Send_data_Parameter_validity_check(self.Send_data, self.uart, self.uart_ui)
    
    def set_connect_password(self):
        data1 = self.set_connect_password_Entry.get()

        self.Send_data.name = "设置连接密码"
        self.Send_data.command = "TTM:PWD-"
        self.Send_data.data = data1
        self.Send_data.send_min = 1
        self.Send_data.send_max = 8
        self.Send_data.data_type = "ASCII"
        self.Send_data.rev_type = "ASCII"
        self.Send_data.command_end = "0"

        MINEWSEMI_Send_data_Parameter_validity_check(self.Send_data, self.uart, self.uart_ui)
    
    def set_conntct_interval(self):
        data1 = self.set_conntct_interval_combobox.get()
        if data1 == "":
            return
        data2 = data1.split(" ")
        data2 = data2[0]
        data1 = int(data2, 10) / 10
        data1 = int(data1)

        self.Send_data.name = "设置连接间隔"
        self.Send_data.command = "TTM:CIT-"
        self.Send_data.data = data1
        self.Send_data.send_min = 1
        self.Send_data.send_max = 100
        self.Send_data.data_type = "INT"
        self.Send_data.rev_type = "ASCII"
        self.Send_data.command_end = "0"

        MINEWSEMI_Send_data_Parameter_validity_check(self.Send_data, self.uart, self.uart_ui)
    
    def this_Send_copy(self):
        data1 = self.this_Send_Entry.get()
        if self.this_Send_checkbox_var.get() == True:
            self.Send_data.data_type = "HEX"
        else:
            self.Send_data.data_type = "ASCII"
        
        self.Send_data.name = "透传发送"
        self.Send_data.command = ""
        self.Send_data.data = data1
        self.Send_data.send_min = 0
        self.Send_data.send_max = 300
        self.Send_data.rev_type = "ASCII"
        self.Send_data.command_end = "0"

        MINEWSEMI_Send_data_Parameter_validity_check(self.Send_data, self.uart, self.uart_ui)

    def set_Disconnect(self):
        self.Send_data.name = "断开所有连接"
        self.Send_data.command = "TTM:DISC-ALL"
        self.Send_data.data = None
        self.Send_data.send_min = 100
        self.Send_data.send_max = 10000
        self.Send_data.data_type = "INT"
        self.Send_data.rev_type = "ASCII"
        self.Send_data.command_end = "0"

        MINEWSEMI_Send_data_Parameter_validity_check(self.Send_data, self.uart, self.uart_ui)


def MINEWSEMI_Send_data_Parameter_validity_check(data, uart, uart_ui):    
    this_data = data
    
    # 合法性检查
    if this_data.command == "" and this_data.name != "透传发送":
        uart_ui.this_rev_Text.insert("end", "命令为空\r\n")
        return -1
    if this_data.data == "":
        uart_ui.this_rev_Text.insert("end", "data为空\r\n")
        return -2
    
    if this_data.data_type is not None and this_data.data is not None:
        if this_data.data_type == "INT":
            if this_data.data < this_data.send_min or this_data.data > this_data.send_max:
                uart_ui.this_rev_Text.insert("end", "data 超出范围\r\n")
                return -3
            # this_data.data = str(this_data.data)
        elif this_data.data_type == "ASCII" or this_data.name == "透传发送":
            len1 = len(this_data.data)
            if len1 < this_data.send_min or len1 > this_data.send_max:
                uart_ui.this_rev_Text.insert("end", "data 长度不合法\r\n")
                return -3

    MS50SFA_WR.command_Send(this_data, uart, uart_ui)