import tkinter as tk
import tkinter.ttk as ttk
import time
import threading
import queue

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

from PIL  import Image, ImageTk

import MS50SFA_TTM.MS50SFA_read_and_write as MS50SFA_WR
import MS50SFA_TTM.Format_conversion as Format_conversion
import system.sys_data as sys_data
import MS50SFA_TTM.mmWave_sys_set as mmWave_sys_set

class mmWave_ui(object):
    def __init__(self, frame_1, uart, uart_ui, window, canvas, person_data_q):
        self.uart = uart
        self.uart_ui = uart_ui
        self.local_filter_flag = 0
        self.select_updata_singel_option = None

        self.frame_1 = frame_1
        self.mmWave_start_flag = 0
        self.this_color = frame_1["background"]
        self.window = window
        self.man_exit_flag = 0

        self.person_data_q = person_data_q
        
        # self.mmWave_q = queue.Queue()  # 创建一个先进先出队列
        self.mmWave_coordinate_q = queue.Queue()  # 创建一个先进先出队列

        self.SYS_mmWave_total_data = sys_data.SYS_mmWave_total_data
        self.SYS_mmWave_total_data.Current_number_of_people = 0
        self.SYS_mmWave_total_data.Person_ID_dict_Current = {}
        self.SYS_mmWave_total_data.Person_ID_dict_last = {}
        self.SYS_mmWave_total_data.Person_ID_dict_history = {}

        self.mmWave_Thread_hand = None

        # 获取Canvas组件
        self.canvas = canvas
        # line1 = self.canvas.create_line(30,30,30,630,630,630,fill="black")
        # 设置纵坐标
        coordinate_x = []
        x_start = 30
        y_start = 30
        for i in range(13):
            y_offset = y_start + i*50
            coordinate_x.append(x_start)
            coordinate_x.append(y_offset)

            coordinate_x.append(x_start + 5)
            coordinate_x.append(y_offset)

            coordinate_x.append(x_start)
            coordinate_x.append(y_offset)

        line1 = self.canvas.create_line(coordinate_x,fill="black")

        #设置横坐标
        coordinate_x = []
        x_start = 30
        y_start = 630
        for i in range(13):
            x_offset = x_start + i*50
            coordinate_x.append(x_offset)
            coordinate_x.append(y_start)

            coordinate_x.append(x_offset)
            coordinate_x.append(y_start - 5)

            coordinate_x.append(x_offset)
            coordinate_x.append(y_start)
        line2 = self.canvas.create_line(coordinate_x,fill="black")

        x_start = 30
        y_start = 30
        line3 = self.canvas.create_line(x_start+300,y_start, x_start+300,y_start+600,fill="#C0C0C0")

        line31 = self.canvas.create_line(x_start+100,y_start, x_start+100,y_start+600,fill="#C6C6C6",dash=(1,1))
        line32 = self.canvas.create_line(x_start+200,y_start, x_start+200,y_start+600,fill="#C6C6C6",dash=(1,1))
        line33 = self.canvas.create_line(x_start+400,y_start, x_start+400,y_start+600,fill="#C6C6C6",dash=(1,1))
        line34 = self.canvas.create_line(x_start+500,y_start, x_start+500,y_start+600,fill="#C6C6C6",dash=(1,1))


        line4 = self.canvas.create_line(x_start,y_start+300, x_start+600,y_start+300,fill="#C0C0C0")
        line41 = self.canvas.create_line(x_start,y_start+100, x_start+600,y_start+100,fill="#C6C6C6",dash=(1,1))
        line42 = self.canvas.create_line(x_start,y_start+200, x_start+600,y_start+200,fill="#C6C6C6",dash=(1,1))
        line43 = self.canvas.create_line(x_start,y_start+400, x_start+600,y_start+400,fill="#C6C6C6",dash=(1,1))
        line44 = self.canvas.create_line(x_start,y_start+500, x_start+600,y_start+500,fill="#C6C6C6",dash=(1,1))

        str0 = self.canvas.create_text(20,10,text="(y)", fill="black")
        str1 = self.canvas.create_text(20,30,text="3", fill="black")
        str2 = self.canvas.create_text(20,130,text="2", fill="black")
        str3 = self.canvas.create_text(20,230,text="1", fill="black")
        str4 = self.canvas.create_text(20,330,text="0", fill="black")
        str5 = self.canvas.create_text(20,430,text="-1", fill="black")
        str6 = self.canvas.create_text(20,530,text="-2", fill="black")
        str7 = self.canvas.create_text(20,630,text="-3", fill="black")

        str20 = self.canvas.create_text(650,640,text="(x)", fill="black")
        str21 = self.canvas.create_text(630,640,text="3", fill="black")
        str22 = self.canvas.create_text(530,640,text="2", fill="black")
        str23 = self.canvas.create_text(430,640,text="1", fill="black")
        str24 = self.canvas.create_text(330,640,text="0", fill="black")
        str25 = self.canvas.create_text(230,640,text="-1", fill="black")
        str26 = self.canvas.create_text(130,640,text="-2", fill="black")
        # str27 = self.canvas.create_text(20,20,text="-3", fill="black")
        # ttk.Button(window, text="添加", width=12, command=self.add_point_chart).place(x=700,y=20)
        # ttk.Button(window, text="删除", width=12, command=self.del_point_chart).place(x=700,y=50)
        
        self.display_coordinate_Label = tk.Label(window, text="",justify="left")  # width=25, height=45
        self.display_coordinate_Label.place(x=700, y=20)  # 100

        self.Show_number_of_people_Label = tk.Label(window, text="0",justify="left",font=("Arial", 26, "bold"),bg="white")  # width=25, height=45
        self.Show_number_of_people_Label.place(x=650, y=30)
        
        uart.thread_1 = self.mmWave_thread_start

    def add_point_chart(self):
        print("add_point_chart")
        point_cloud = [(100, 50), (200, 50), (500, 260)]
        print("开始绘制点", type(point_cloud))
        print(point_cloud)
        print("完成绘制点")
        self.canvas.fillStyle = 'red'
        # 绘制点云
        draw_point_cloud(self.canvas, point_cloud, "red")
    
    def del_point_chart(self):
        point_cloud = [(100, 50), (200, 50), (500, 260)]
        draw_point_cloud(self.canvas, point_cloud, self.this_color)
        print("del_point_chart")

    def mmWave_thread_start(self, option):
        print("mmWave_thread_start is start", option)
        if option == 1:
            self.uart.uart_data_ana_function = self.scan_data_processing_function
            if self.mmWave_Thread_hand is None:
                self.man_exit_flag = 0
                self.mmWave_Thread_hand = threading.Thread(target=self.this_mmWave_scan_Thread)
                self.mmWave_Thread_hand.start()
            else:
                print("显示线程已经启动了！")
        else:
            self.close_window()

    def close_window(self):
        print("mmWave close_window")
        
        if self.mmWave_Thread_hand is not None:
            self.man_exit_flag = 1
            self.mmWave_Thread_hand.join()
            self.mmWave_Thread_hand = None
    
    def mmWave_start_option(self, data):
        self.mmWave_start_flag = data
        print("mmWave_start_option", data)

        if data == 1:
            self.uart.uart_data_ana_function = self.scan_data_processing_function
            print("开始扫描了")
        else:
            self.uart.uart_data_ana_function = None
    
    def scan_data_processing_function(self, rev_data):
        # print("scan_data_processing_function = ", rev_data)
        try:
            return self.mmWave_Frame_protocol_parsing(rev_data)
        except:
            print("scan_data_processing_function, err")

    def mmWave_Frame_protocol_parsing(self, data):
        len1 = len(data)
        if len1 < 64:
            print("错误帧长度！")
            return -1
        new_SYS_mmWave_Frame = sys_data.SYS_mmWave_Frame  # 定义结构图存储器
        new_SYS_mmWave_Frame.Frame_header = data[:16]
        d1 = data[16:24]
        new_SYS_mmWave_Frame.total_length = hex_string_to_int(d1)
        d1 = data[24:32]
        new_SYS_mmWave_Frame.current_frame_count = hex_string_to_int(d1)
        d1 = data[32:40]
        new_SYS_mmWave_Frame.TLV1 = hex_string_to_int(d1)
        d1 = data[40:48]
        new_SYS_mmWave_Frame.constant = hex_string_to_int(d1)
        d1 = data[48:56]
        new_SYS_mmWave_Frame.TLV2 = hex_string_to_int(d1)
        d1 = data[56:64]
        d2 = hex_string_to_int(d1)
        d3 = int(d2 / 32)
        new_SYS_mmWave_Frame.length_of_personnel_data = d3

        Effective_data = data[64:]
        # Effective_data_length = new_SYS_mmWave_Frame.total_length * 2 - 64

        self.SYS_mmWave_total_data.Current_number_of_people = d3
        # print("Current_number_of_people = ", d3)
        self.mmWave_coordinate_q.put(Effective_data)  #Debug响应速度，这里终止UI显示
        
        return 0
        
    def this_mmWave_scan_Thread(self):
        color_list = ["red", "green", "blue", "purple", "pink", "orange", "gray", "yellow", "black", "white"]
        self.mmWave_start_flag = 1

        dict_last = {}
        oval_id_list = []
        while(1):
            if self.man_exit_flag == 1:
                print("exit this_mmWave_scan_Thread 1, uart fd = ", self.uart.fd, 
                      "exit flag = ", self.man_exit_flag)
                
                try:
                    for item in oval_id_list:
                        del_ovals_one(self.canvas, item)
                except:
                    print("del_ovals_one err")
                return
            
            try:
                if self.mmWave_coordinate_q.empty() is False:
                    if 1:
                        # 方案2，不清空队列，显示最后一个。也是最新的点
                        while(1):
                            rev_str = self.mmWave_coordinate_q.get()
                            
                            if self.mmWave_coordinate_q.empty() is True:
                                break
                    else:
                        # 方案1，清空队列，只显示第一个
                        rev_str = self.mmWave_coordinate_q.get()
                        self.mmWave_coordinate_q.queue.clear()
                    

                    len_rev_str = len(rev_str)
                    Current_number_of_people = 0
                    result_str = ""

                    # 删除所有点
                    for item in oval_id_list:
                        del_ovals_one(self.canvas, item)
                    oval_id_list = []
                    while(1):
                        if len_rev_str < 64:
                            break
                        
                        new_id, str1, struc1 = get_str_and_struc_form_str(rev_str[:64])
                        
                        # 显示的字符串更新         
                        result_str += str1
                        
                        # 删除上次点
                        
                        # 绘制点云
                        id = draw_point_one(self.canvas, [(struc1.x, struc1.y)], color_list[Current_number_of_people])
                        oval_id_list.append(id)
                        
                        # 人数统计
                        Current_number_of_people += 1

                        # 去除已分析数据及长度，准备分析下一个
                        rev_str = rev_str[64:]
                        len_rev_str -= 64

                        
                    self.display_coordinate_Label["text"] = result_str
                    self.Show_number_of_people_Label["text"] = Current_number_of_people
                    self.person_data_q.put(Current_number_of_people)

            except:
                print("异常, this_mmWave_scan_Thread")
                # return
            
            time.sleep(0.09)
    

def get_str_and_struc_form_str(rev_str):
    get_SYS_mmWave_Personnel_Frame = sys_data.SYS_mmWave_Personnel_Frame

    # 添加数据点到准备绘制图表
    x = hex_string_to_float(rev_str[16:24])
    y = hex_string_to_float(rev_str[24:32])
    z = hex_string_to_float(rev_str[32:40])

    speed_x = hex_string_to_float(rev_str[40:48])
    speed_y = hex_string_to_float(rev_str[48:56])
    speed_z = hex_string_to_float(rev_str[56:64])

    # 计算结果保持到结构体
    get_SYS_mmWave_Personnel_Frame.ID = rev_str[:8]
    get_SYS_mmWave_Personnel_Frame.reserve = rev_str[8:16]
    get_SYS_mmWave_Personnel_Frame.new_id = rev_str[:16]

    get_SYS_mmWave_Personnel_Frame.x = x * 100 + 300
    get_SYS_mmWave_Personnel_Frame.y = 0 - y * 100 + 300  # y * 100 + 300
    get_SYS_mmWave_Personnel_Frame.z = z * 100 + 300
                        
    get_SYS_mmWave_Personnel_Frame.speed_x = speed_x
    get_SYS_mmWave_Personnel_Frame.speed_y = speed_y
    get_SYS_mmWave_Personnel_Frame.speed_z = speed_z

    
    # 分析结果整理到缓存  # str(int(get_SYS_mmWave_Personnel_Frame.ID,2))
    result_str = "ID: " + get_SYS_mmWave_Personnel_Frame.ID + "\n"
    # result_str += "ren: " + get_SYS_mmWave_Personnel_Frame.reserve + "\n"
    result_str += "x = " + "{:0.2f}".format(x)
    result_str += ", " + "{:0.2f}".format(speed_x) + "\n"

    result_str += "y = " + "{:0.2f}".format(y)
    result_str += ", " + "{:0.2f}".format(speed_y) + "\n"

    result_str += "z = " + "{:0.2f}".format(z)
    result_str += ", " + "{:0.2f}".format(speed_z) + "\n"

    result_str += "\n"

    return get_SYS_mmWave_Personnel_Frame.new_id, result_str, get_SYS_mmWave_Personnel_Frame

def draw_point_cloud(canvas, points, this_fill):
    r1 = 2
    for point in points:
        canvas.create_oval(point[0] - r1, point[1] - r1, point[0] + r1, point[1] + r1, fill=this_fill, outline=this_fill)

def draw_point_one(canvas, points, this_fill):
    r1 = 10
    point = points[0]
    oval_id = canvas.create_oval(point[0] - r1, point[1] - r1, point[0] + r1, point[1] + r1, fill=this_fill, outline=this_fill)
    return oval_id

def del_ovals_one(canvas, oval_id):
    canvas.delete(oval_id)

def hex_string_to_int(hex_str):
    # 将十六进制字符串转换为字节序列
    byte_seq = bytes.fromhex(hex_str)
    
    # 使用大端序读取整数
    return int.from_bytes(byte_seq, 'little')  # big  little


import struct
def hex_string_to_float(hex_str):
    # 将十六进制字符串转换为字节序列
    byte_seq = bytes.fromhex(hex_str)
    
    # 使用struct解包字节序列为浮点数
    float_num = struct.unpack('<f', byte_seq)[0]

    return float_num

def load_image(image_path):
    # 使用Pillow打开图片
    img = Image.open(image_path)
    # 将图片转换成Tkinter可以处理的格式
    return ImageTk.PhotoImage(img)
