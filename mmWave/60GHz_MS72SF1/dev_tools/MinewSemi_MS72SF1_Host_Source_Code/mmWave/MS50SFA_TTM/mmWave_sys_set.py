import tkinter as tk
import tkinter.ttk as ttk
import os
import configparser
import time

import MS50SFA_TTM.MS50SFA_read_and_write as MS50SFA_WR
import MS50SFA_TTM.Format_conversion as Format_conversion
import system.sys_data as sys_data


file_path = ".\MS72SFx_config.ini"
if os.path.exists(file_path):
    print("文件存在")
    try:
        MS72SFx_config = configparser.ConfigParser()
        MS72SFx_config.read(file_path, encoding="utf-8")
    except:
        print("文件格式错误！")

else:
    print("文件不存在")


class mmWave_sys_set_ui(object):
    def __init__(self, frame_1, uart, uart_ui):
        self.uart = uart
        self.uart_ui = uart_ui
        self.mmWave_Send_data = sys_data.SYS_mmWave_write

        
        tk.Label(frame_1, text="AT+HEIGHT=XXX\n").grid(column=2,row=2,sticky='w')
        tk.Label(frame_1, text="配置雷达安装高度(250-320)").grid(column=0,row=2,sticky='w')
        this_combobox_value = []
        for i in range (250, 320+1, 1):
            this_combobox_value.append(str(i) + " cm")
        self.set_HEIGHT_combobox = ttk.Combobox(frame_1, values=this_combobox_value, width=12)
        self.set_HEIGHT_combobox.grid(column=1,row=2)
        self.set_HEIGHT_combobox.current(20)
        ttk.Button(frame_1, text="set", width=4, command=self.set_HEIGHT).grid(column=3,row=2)

        tk.Label(frame_1, text="AT+HEIGHTD=XXX\n").grid(column=2,row=3,sticky='w')
        tk.Label(frame_1, text="配置模块扫描高度(小于HEIGHT)").grid(column=0,row=3,sticky='w')
        self.set_HEIGHTD_Entry = ttk.Entry(frame_1, width=15)
        self.set_HEIGHTD_Entry.grid(column=1,row=3)
        self.set_HEIGHTD_Entry.insert(0, "270")
        ttk.Button(frame_1, text="set", width=4, command=self.set_HEIGHTD).grid(column=3,row=3)

        tk.Label(frame_1, text="AT+DEBUG=X\n").grid(column=2,row=8,sticky='w')
        tk.Label(frame_1, text="协议").grid(column=0,row=8,sticky='w')
        this_combobox_value = ["字符串模式0", "字符串模式1", "测试模式", "工作模式"]
        self.set_DEBUG_combobox = ttk.Combobox(frame_1, values=this_combobox_value, width=12)
        self.set_DEBUG_combobox.grid(column=1,row=8)
        self.set_DEBUG_combobox.current(0)
        # ttk.Button(frame_1, text="read", width=4, command=self.read_adv_power).grid(column=2,row=8)
        ttk.Button(frame_1, text="set", width=4, command=self.set_DEBUG).grid(column=3,row=8)

        tk.Label(frame_1, text="AT+TIME=XX\n").grid(column=2,row=9,sticky='w')
        tk.Label(frame_1, text="配置间隔(100-10000)").grid(column=0,row=9,sticky='w')
        this_combobox_value = []
        for i in range (1, 100+1, 1):
            this_combobox_value.append(str(i * 100) + " ms")
        self.set_TIME_combobox = ttk.Combobox(frame_1, values=this_combobox_value, width=12)
        self.set_TIME_combobox.grid(column=1,row=9)
        self.set_TIME_combobox.current(0)
        ttk.Button(frame_1, text="set", width=4, command=self.set_TIME).grid(column=3,row=9)

        tk.Label(frame_1, text="AT+HEATIME=XX\n").grid(column=2,row=10,sticky='w')
        tk.Label(frame_1, text="简易协议上报间隔(10-999)").grid(column=0,row=10,sticky='w')
        this_combobox_value = []
        for i in range (10, 999+1, 1):
            this_combobox_value.append(str(i) + " S")
        self.set_HEATIME_combobox = ttk.Combobox(frame_1, values=this_combobox_value, width=12)
        self.set_HEATIME_combobox.grid(column=1,row=10)
        self.set_HEATIME_combobox.current(50)
        ttk.Button(frame_1, text="set", width=4, command=self.set_HEATIME).grid(column=3,row=10)


        tk.Label(frame_1, text="AT+RANGE=XXX\n").grid(column=2,row=11,sticky='w')
        tk.Label(frame_1, text="配置雷达到边界距离(100--2000)").grid(column=0,row=11,sticky='w')
        this_combobox_value = []
        for i in range (100, 2000+1, 1):
            this_combobox_value.append(str(i) + " cm")
        self.set_RANGE_combobox = ttk.Combobox(frame_1, values=this_combobox_value, width=12)
        self.set_RANGE_combobox.grid(column=1,row=11)
        self.set_RANGE_combobox.current(200)
        ttk.Button(frame_1, text="set", width=4, command=self.set_RANGE).grid(column=3,row=11)
        

        tk.Label(frame_1, text="AT+XNegaD=XXX\n").grid(column=2,row=12,sticky='w')
        tk.Label(frame_1, text="配置X负向边界(0-300)").grid(column=0,row=12,sticky='w')
        this_combobox_value = []
        for i in range (0, 300+1, 1):
            this_combobox_value.append(str(i) + " cm")
        self.set_XNegaD_combobox = ttk.Combobox(frame_1, values=this_combobox_value, width=12)
        self.set_XNegaD_combobox.grid(column=1,row=12)
        self.set_XNegaD_combobox.current(300)
        ttk.Button(frame_1, text="set", width=4, command=self.set_XNegaD).grid(column=3,row=12)

        tk.Label(frame_1, text="AT+XPosiD=XXX\n").grid(column=2,row=13,sticky='w')
        tk.Label(frame_1, text="配置X正向边界(0-300)").grid(column=0,row=13,sticky='w')
        this_combobox_value = []
        for i in range (0, 300+1, 1):
            this_combobox_value.append(str(i) + " cm")
        self.set_XPosiD_combobox = ttk.Combobox(frame_1, values=this_combobox_value, width=12)
        self.set_XPosiD_combobox.grid(column=1,row=13)
        self.set_XPosiD_combobox.current(300)
        ttk.Button(frame_1, text="set", width=4, command=self.set_XPosiD).grid(column=3,row=13)

        tk.Label(frame_1, text="AT+YNegaD=XXX\n").grid(column=2,row=14,sticky='w')
        tk.Label(frame_1, text="配置Y负向边界(0-300)").grid(column=0,row=14,sticky='w')
        this_combobox_value = []
        for i in range (0, 300+1, 1):
            this_combobox_value.append(str(i) + " cm")
        self.set_YNegaD_combobox = ttk.Combobox(frame_1, values=this_combobox_value, width=12)
        self.set_YNegaD_combobox.grid(column=1,row=14)
        self.set_YNegaD_combobox.current(300)
        ttk.Button(frame_1, text="set", width=4, command=self.set_YNegaD).grid(column=3,row=14)

        tk.Label(frame_1, text="AT+YPosiD=XXX\n").grid(column=2,row=15,sticky='w')
        tk.Label(frame_1, text="配置Y正向边界(0-300)").grid(column=0,row=15,sticky='w')
        this_combobox_value = []
        for i in range (0, 300+1, 1):
            this_combobox_value.append(str(i) + " cm")
        self.set_YPosiD_combobox = ttk.Combobox(frame_1, values=this_combobox_value, width=12)
        self.set_YPosiD_combobox.grid(column=1,row=15)
        self.set_YPosiD_combobox.current(300)
        ttk.Button(frame_1, text="set", width=4, command=self.set_YPosiD).grid(column=3,row=15)

    def read_all(self):
        self.read_adv_name()
        self.read_adv_interval()
        self.read_adv_power()
        self.read_factory_ID()
        self.read_service_UUID()
        self.read_UUID()
        self.read_Major()
        self.read_Minor()

    def clear(self):
        self.set_adv_name_Entry.delete(0, tk.END)
        self.set_adv_interval_combobox.set("")
        self.set_adv_power_combobox.set("")
        self.set_factory_ID_Entry.delete(0, tk.END)
        self.set_service_UUID_Entry.delete(0, tk.END)
        self.set_UUID_Entry.delete(0, tk.END)
        self.set_Major_Entry.delete(0, tk.END)
        self.set_Minor_Entry.delete(0, tk.END)

    def set_HEIGHT(self):
        data1 = self.set_HEIGHT_combobox.get()
        
        self.mmWave_Send_data.name = "配置雷达安装高度"
        self.mmWave_Send_data.command = "AT+HEIGHT="
        self.mmWave_Send_data.data = get_mmWave_data_from_str(data1, 'INT')
        self.mmWave_Send_data.send_min = 250
        self.mmWave_Send_data.send_max = 320
        self.mmWave_Send_data.data_type = "INT"
        self.mmWave_Send_data.rev_type = "ASCII"
        self.mmWave_Send_data.command_end = "\n"

        mmWave_Send_data_Parameter_validity_check(self.mmWave_Send_data, self.uart, self.uart_ui)
        
    def set_HEIGHTD(self):
        
        data1 = self.set_HEIGHT_combobox.get()
        self.mmWave_Send_data.send_max = get_mmWave_data_from_str(data1, 'INT')

        data1 = self.set_HEIGHTD_Entry.get()


        self.mmWave_Send_data.name = "配置模块扫描高度"
        self.mmWave_Send_data.command = "AT+HEIGHTD="
        self.mmWave_Send_data.data = get_mmWave_data_from_str(data1, 'INT')
        self.mmWave_Send_data.send_min = 250
        # self.mmWave_Send_data.send_max = 320
        self.mmWave_Send_data.data_type = "INT"
        self.mmWave_Send_data.rev_type = "ASCII"
        self.mmWave_Send_data.command_end = "\n"

        mmWave_Send_data_Parameter_validity_check(self.mmWave_Send_data, self.uart, self.uart_ui)

    def set_DEBUG(self):
        # data1 = self.set_DEBUG_combobox.get()
        data1 = self.set_DEBUG_combobox.current()

        self.mmWave_Send_data.name = "切换协议"
        self.mmWave_Send_data.command = "AT+DEBUG="
        self.mmWave_Send_data.data = data1
        self.mmWave_Send_data.send_min = 0
        self.mmWave_Send_data.send_max = 3
        self.mmWave_Send_data.data_type = "INT"
        self.mmWave_Send_data.rev_type = "ASCII"
        self.mmWave_Send_data.command_end = "\n"

        mmWave_Send_data_Parameter_validity_check(self.mmWave_Send_data, self.uart, self.uart_ui)
    
    def set_TIME(self):
        data1 = self.set_TIME_combobox.get()

        self.mmWave_Send_data.name = "配置间隔"
        self.mmWave_Send_data.command = "AT+TIME="
        self.mmWave_Send_data.data = get_mmWave_data_from_str(data1, 'INT')
        self.mmWave_Send_data.send_min = 100
        self.mmWave_Send_data.send_max = 10000
        self.mmWave_Send_data.data_type = "INT"
        self.mmWave_Send_data.rev_type = "ASCII"
        self.mmWave_Send_data.command_end = "\n"

        mmWave_Send_data_Parameter_validity_check(self.mmWave_Send_data, self.uart, self.uart_ui)
    
    def set_HEATIME(self):
        data1 = self.set_HEATIME_combobox.get()
        
        self.mmWave_Send_data.name = "简易协议上报间隔"
        self.mmWave_Send_data.command = "AT+HEATIME="
        self.mmWave_Send_data.data = get_mmWave_data_from_str(data1, 'INT')
        self.mmWave_Send_data.send_min = 10
        self.mmWave_Send_data.send_max = 999
        self.mmWave_Send_data.data_type = "INT"
        self.mmWave_Send_data.rev_type = "ASCII"
        self.mmWave_Send_data.command_end = "\n"

        mmWave_Send_data_Parameter_validity_check(self.mmWave_Send_data, self.uart, self.uart_ui)
    
    def set_RANGE(self):
        data1 = self.set_RANGE_combobox.get()

        self.mmWave_Send_data.name = "配置雷达到边界距离"
        self.mmWave_Send_data.command = "AT+RANGE="
        self.mmWave_Send_data.data = get_mmWave_data_from_str(data1, 'INT')
        self.mmWave_Send_data.send_min = 100
        self.mmWave_Send_data.send_max = 2000
        self.mmWave_Send_data.data_type = "INT"
        self.mmWave_Send_data.rev_type = "ASCII"
        self.mmWave_Send_data.command_end = "\n"

        mmWave_Send_data_Parameter_validity_check(self.mmWave_Send_data, self.uart, self.uart_ui)
    
    def set_XNegaD(self):
        data1 = self.set_XNegaD_combobox.get()
        
        self.mmWave_Send_data.name = "配置 X 负向边界"
        self.mmWave_Send_data.command = "AT+XNegaD="
        self.mmWave_Send_data.data = 0 - get_mmWave_data_from_str(data1, 'INT')
        self.mmWave_Send_data.send_min = -300
        self.mmWave_Send_data.send_max = 0
        self.mmWave_Send_data.data_type = "INT"
        self.mmWave_Send_data.rev_type = "ASCII"
        self.mmWave_Send_data.command_end = "\n"

        mmWave_Send_data_Parameter_validity_check(self.mmWave_Send_data, self.uart, self.uart_ui)
    
    def set_XPosiD(self):
        data1 = self.set_XPosiD_combobox.get()
        
        self.mmWave_Send_data.name = "配置 X 正向边界"
        self.mmWave_Send_data.command = "AT+XPosiD="
        self.mmWave_Send_data.data = get_mmWave_data_from_str(data1, 'INT')
        self.mmWave_Send_data.send_min = 0
        self.mmWave_Send_data.send_max = 300
        self.mmWave_Send_data.data_type = "INT"
        self.mmWave_Send_data.rev_type = "ASCII"
        self.mmWave_Send_data.command_end = "\n"

        mmWave_Send_data_Parameter_validity_check(self.mmWave_Send_data, self.uart, self.uart_ui)
    
    def set_YNegaD(self):
        data1 = self.set_YNegaD_combobox.get()
        
        self.mmWave_Send_data.name = "配置 Y 负向边界"
        self.mmWave_Send_data.command = "AT+YNegaD="
        self.mmWave_Send_data.data = 0 - get_mmWave_data_from_str(data1, 'INT')
        self.mmWave_Send_data.send_min = -300
        self.mmWave_Send_data.send_max = 0
        self.mmWave_Send_data.data_type = "INT"
        self.mmWave_Send_data.rev_type = "ASCII"
        self.mmWave_Send_data.command_end = "\n"

        mmWave_Send_data_Parameter_validity_check(self.mmWave_Send_data, self.uart, self.uart_ui)
    
    def set_YPosiD(self):
        data1 = self.set_YPosiD_combobox.get()
        
        self.mmWave_Send_data.name = "配置 Y 正向边界"
        self.mmWave_Send_data.command = "AT+YPosiD="
        self.mmWave_Send_data.data = get_mmWave_data_from_str(data1, 'INT')
        self.mmWave_Send_data.send_min = 0
        self.mmWave_Send_data.send_max = 300
        self.mmWave_Send_data.data_type = "INT"
        self.mmWave_Send_data.rev_type = "ASCII"
        self.mmWave_Send_data.command_end = "\n"

        mmWave_Send_data_Parameter_validity_check(self.mmWave_Send_data, self.uart, self.uart_ui)
        

class mmWave_button_ui(object):
    def __init__(self, frame_1, uart, uart_ui, mmWave_start_option):
        self.uart = uart
        self.uart_ui = uart_ui
        self.mmWave_Send_data = sys_data.SYS_mmWave_write
        self.mmWave_start_option = mmWave_start_option

        self.set_start_MS72SF_BUTTON = ttk.Button(frame_1, text="开始", width=12, command=self.set_start_MS72SF)
        self.set_start_MS72SF_BUTTON.grid(column=0,row=0)
        ttk.Button(frame_1, text="结束", width=12, command=self.set_stop_MS72SF).grid(column=1,row=0,pady=5)

        ttk.Button(frame_1, text="恢复默认设置", width=12, command=self.set_Restore_default_Settings_MS72SF).grid(column=2,row=1,padx=25)
        ttk.Button(frame_1, text="模块复位", width=12, command=self.set_reset_MS72SF).grid(column=1,row=1,padx=20,pady=5)
        ttk.Button(frame_1, text="度版本号及参数", width=12, command=self.set_read_ver_MS72SF).grid(column=0,row=1,padx=20)

        ttk.Button(frame_1, text="学习", width=12, command=self.set_study_MS72SF).grid(column=0,row=2,pady=5)

    def set_start_MS72SF(self):
        self.set_start_MS72SF_BUTTON["state"] = "disable"
        self.mmWave_Send_data.name = "开始"
        self.mmWave_Send_data.command = "AT+START"
        self.mmWave_Send_data.data = ""
        self.mmWave_Send_data.send_min = 0
        self.mmWave_Send_data.send_max = 0
        self.mmWave_Send_data.data_type = None
        self.mmWave_Send_data.rev_type = "ASCII"
        self.mmWave_Send_data.command_end = "\n"

        res = mmWave_Send_data_Parameter_validity_check(self.mmWave_Send_data, self.uart, self.uart_ui)
        if res != -1 and res != -2:
            if res[:8] == "AT+START":
                print("开始成功了")
            if res[:16] == "0102030405060708":
                print("开始成功了 2222222")
        self.mmWave_start_option(1)

    def set_stop_MS72SF(self):
        self.mmWave_Send_data.name = "结束"
        self.mmWave_Send_data.command = "AT+STOP"
        self.mmWave_Send_data.data = ""
        self.mmWave_Send_data.send_min = 0
        self.mmWave_Send_data.send_max = 0
        self.mmWave_Send_data.data_type = None
        self.mmWave_Send_data.rev_type = "ASCII"
        self.mmWave_Send_data.command_end = "\n"

        res = mmWave_Send_data_Parameter_validity_check(self.mmWave_Send_data, self.uart, self.uart_ui)
        if res != -1 and res != -2 and res[:8] == "AT+START":
            print("结束成功了")
        self.mmWave_start_option(0)
        self.set_start_MS72SF_BUTTON["state"] = "enable"

    def set_reset_MS72SF(self):
        self.mmWave_Send_data.name = "模块复位"
        self.mmWave_Send_data.command = "AT+RESET"
        self.mmWave_Send_data.data = ""
        self.mmWave_Send_data.send_min = 0
        self.mmWave_Send_data.send_max = 0
        self.mmWave_Send_data.data_type = None
        self.mmWave_Send_data.rev_type = "ASCII"
        self.mmWave_Send_data.command_end = "\n"

        mmWave_Send_data_Parameter_validity_check(self.mmWave_Send_data, self.uart, self.uart_ui)
    
    def set_study_MS72SF(self):
        self.mmWave_Send_data.name = "学习"
        self.mmWave_Send_data.command = "AT+STUDY"
        self.mmWave_Send_data.data = ""
        self.mmWave_Send_data.send_min = 0
        self.mmWave_Send_data.send_max = 0
        self.mmWave_Send_data.data_type = None
        self.mmWave_Send_data.rev_type = "ASCII"
        self.mmWave_Send_data.command_end = "\n"

        mmWave_Send_data_Parameter_validity_check(self.mmWave_Send_data, self.uart, self.uart_ui)
    
    def set_read_ver_MS72SF(self):
        self.mmWave_Send_data.name = "读版本号及参数"
        self.mmWave_Send_data.command = "AT+READ"
        self.mmWave_Send_data.data = ""
        self.mmWave_Send_data.send_min = 0
        self.mmWave_Send_data.send_max = 0
        self.mmWave_Send_data.data_type = None
        self.mmWave_Send_data.rev_type = "ASCII"
        self.mmWave_Send_data.command_end = "\n"

        mmWave_Send_data_Parameter_validity_check(self.mmWave_Send_data, self.uart, self.uart_ui)
    
    def set_Restore_default_Settings_MS72SF(self):
        self.mmWave_Send_data.name = "恢复默认设置"
        self.mmWave_Send_data.command = "AT+RESTORE"
        self.mmWave_Send_data.data = ""
        self.mmWave_Send_data.send_min = 0
        self.mmWave_Send_data.send_max = 0
        self.mmWave_Send_data.data_type = None
        self.mmWave_Send_data.rev_type = "ASCII"
        self.mmWave_Send_data.command_end = "\n"

        mmWave_Send_data_Parameter_validity_check(self.mmWave_Send_data, self.uart, self.uart_ui)
    

class mmWave_autoSet_ui(object):
    def __init__(self, frame_1, uart, uart_ui):
        self.uart = uart
        self.uart_ui = uart_ui
        self.mmWave_Send_data = sys_data.SYS_mmWave_write

        self.send_argument_list = []

        tk.Label(frame_1, text="选择参数").place(x=30,y=20)
        sections = MS72SFx_config.sections()
        # this_combobox_value = []
        # for item in sections:
        #     this_combobox_value.append(item)
        self.set_autoSet_combobox = ttk.Combobox(frame_1, values=sections, width=15)
        self.set_autoSet_combobox.place(x=260,y=20)
        self.set_autoSet_combobox.set(str(len(sections)) + " 组参数")
        # self.set_YPosiD_combobox.current(0)
        # 绑定选择事件到函数
        self.set_autoSet_combobox.bind("<<ComboboxSelected>>", self.add_argument_to_listbox)
        
        ttk.Button(frame_1, text="发送全部", width=12, command=self.set_all_MS72SF).place(x=120,y=20)

        # 创建一个Scrollbar和Text组件，并将它们关联
        scrollbar_listbox = tk.Scrollbar(frame_1)
        self.MS72SF_argument_Listbox = tk.Listbox(frame_1,width=50,height=16,yscrollcommand=scrollbar_listbox.set)
        scrollbar_listbox.config(command=self.MS72SF_argument_Listbox.yview)
        self.MS72SF_argument_Listbox.place(x=30,y=60)

    def add_argument_to_listbox(self, event):
        this_sections = self.set_autoSet_combobox.get()
        
        this_option_list = MS72SFx_config.options(this_sections)

        # 显示到列表
        self.MS72SF_argument_Listbox.delete(0, "end")
        self.send_argument_list = []
        for item in this_option_list:
            value = MS72SFx_config.get(this_sections, item)
            print(item, " 设定指令 ", value)
            self.MS72SF_argument_Listbox.insert("end", value)
            self.send_argument_list.append(value)
        

    def set_all_MS72SF(self):
        # 发送指令
        if len(self.send_argument_list) == 0:
            self.uart_ui.this_rev_Text.insert("end", "空列表，不能发送\r\n")
            print("空列表，不能设置")
            return
        
        err_command_list = []
        for item in self.send_argument_list: 
            self.mmWave_Send_data.name = ""
            self.mmWave_Send_data.command = item
            self.mmWave_Send_data.data = ""
            self.mmWave_Send_data.send_min = 0
            self.mmWave_Send_data.send_max = 0
            self.mmWave_Send_data.data_type = None
            self.mmWave_Send_data.rev_type = "ASCII"
            self.mmWave_Send_data.command_end = "\n"
            send_count = 0
            while(1):
                if item[:5] == 'delay':
                    s1 = item[6:]
                    delay_time = float(s1)
                    print("执行一次Delay = ", delay_time, "秒")
                    self.uart_ui.this_rev_Text.insert("end", "执行一次Delay = " + s1 + "秒\r\n")
                    time.sleep(delay_time)
                    break

                res = mmWave_Send_data_Parameter_validity_check(self.mmWave_Send_data, self.uart, self.uart_ui)
                
                if res[:-1] == item:
                    print("设置成功了 2")
                    break

                s1 = item.split('=')
                if len(s1) > 1:
                    s2 = s1[1]
                else:
                    s2 = ""
                test_ok_check = "AT+OK=" + s2
                
                if res == -1:
                    print("uart err")
                    return
                elif  res == -2:
                    print("无返回值")
                    time.sleep(0.5)
                elif res[:-1] == test_ok_check:
                    print("设置成功了")
                    break
                else:
                    print("设置失败了")
                    time.sleep(0.1)

                if send_count >= 4:
                    print("超过重发次数")
                    err_command_list.append(item)
                    time.sleep(0.5)
                    break
                else:
                    send_count += 1

                time.sleep(0.01)

        err_len1 = len(err_command_list)
        if err_len1 == 0:
            self.uart_ui.this_rev_Text.insert("end", "全部指令发送成功\r\n")
        else:
            self.uart_ui.this_rev_Text.insert("end", "有" + str(err_len1) + "条指令发送错误\r\n")

            for item in err_command_list:
                self.uart_ui.this_rev_Text.insert("end", item + "\r\n")
                

def get_mmWave_data_from_str(data, type):

    try:
        s1 = data.split(' ')
        s2 = s1[0]

        if type == "INT":
            res1 = int(s2, 10)
        elif type == "HEX":
            res1 = s2
        elif type == "ASCII":
            res1 = Format_conversion.hex_to_str(s2)
        
    except:
        res1 = "default"
        print("转换不成功！", data)
    return res1

def mmWave_Send_data_Parameter_validity_check(data, uart, uart_ui):    
    this_data = data
    
    # 合法性检查
    if this_data.command == "":
        uart_ui.this_rev_Text.insert("end", "命令为空\r\n")
        return -1
    
    if this_data.data_type is not None and this_data.data is not None:
        if this_data.data == "":
            uart_ui.this_rev_Text.insert("end", "data为空\r\n")
            return -2
    
        
        if this_data.data_type == "INT":
            if this_data.data < this_data.send_min or this_data.data > this_data.send_max:
                uart_ui.this_rev_Text.insert("end", "data 超出范围\r\n")
                return -3
            this_data.data = str(this_data.data)
        elif this_data.data_type == "ASCII":
            len1 = len(this_data.data)
            if len1 < this_data.send_min or len1 > this_data.send_max:
                uart_ui.this_rev_Text.insert("end", "data 长度不合法\r\n")
                return -3

    return mmWave_command_Send(this_data, uart, uart_ui)


def mmWave_command_Send(input_data, uart, uart_ui):
    this_data = input_data
    name = this_data.name
    print("write: ", name)
    result_data = -1

    try:
        command_write = this_data.command + this_data.data + this_data.command_end
        uart_ui.this_rev_Text.insert("end", "\r\n" + this_data.name + "\r\n")
        uart_ui.this_rev_Text.insert("end", command_write.replace("\n", "") + "\r\n")

        command_write = command_write.encode('utf-8')
    except:
        print("Assertion error: command_Send, input data is err.", name)
        result_data = -2
    
    if uart.fd != -1:
        try:
            result = uart.serial_Send_command_and_read(command_write, 1)
        except:
            print("Assertion error: command_Send, uart is err.", name)

        # 返回值处理
        try:
            if result != -1 and result != -2:
                # result_str = result.decode('utf-8')[1:-1]
                result_str = result.decode('utf-8')
                result_data = result_str.replace("\n", "")
                uart_ui.this_rev_Text.insert("end", result_data + "\r\n")
                
            elif result == -2:
                print("uart 无需返回值")
            else:
                print("uart 无返回值")
                uart_ui.this_rev_Text.insert("end", "uart 无返回值 ！ \r\n")
                result_data = -2
        except:
            print("Assertion error: command_Send, data analyze err.", name)
            result_data = -2
    else:
        result_data = -1
        uart_ui.this_rev_Text.insert("end", "没有写入, 串口没打开 ！ \r\n")
        print("uart not open !")
        
    uart_ui.this_rev_Text.see("end")
    uart_ui.window.update()
    
    return result_data