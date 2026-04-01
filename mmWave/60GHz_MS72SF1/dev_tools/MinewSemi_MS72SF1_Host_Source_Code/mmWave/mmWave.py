import tkinter as tk
import tkinter.ttk as ttk
# import logging
import threading
import os
import sys
from PIL  import Image, ImageTk
from datetime import datetime
import time

# current_path = os.path.abspath(__file__)  # 获取当前文件的绝对路径
# parent_path = os.path.dirname(os.path.dirname(current_path))  # 获取上一级目录的绝对路径
# sys.path.append(parent_path)  # 将上一级目录添加到系统路径中

#import my_uart2024
import trx_display as trx_display_ui
# import common.uart.uart_ctl as uart_ctl
# import common.uart.uart_ui as uart_ui
from common.uart.uart_ctl import UartInfo as uart_ctl
from common.uart.uart_ui import Uart_ui as uart_ui

import MS50SFA_TTM.mmWave_ui as mmWave_ui_ca
import MS50SFA_TTM.MS50SFA_connect_ui as MS50SFA_connect_ui_ca
import MS50SFA_TTM.mmWave_sys_set as mmWave_sys_set_ca
import MS50SFA_TTM.mmWave_sys_set as mmWave_button_ui_ca
import MS50SFA_TTM.mmWave_curve as mmWave_curve_ca
import MS50SFA_TTM.mmWave_curve_copy as mmWave_curve_person_ca

import MS50SFA_TTM.Format_conversion as MS50SFA_ui_read
import system.ico_is as ico_display

import psutil
from tkinter import messagebox


# def logging_init():
#     logging.basicConfig(
#         filename="D:\work\itool\window\\te.log", # 指定输出文件
#         level = logging.DEBUG,
#         format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    
#     return True
    

def Read_scan_All_at_type(type):
    print("enter Get_All")
    if uart_ctl_1.fd == -1:
        print("uart not open !")
        return -5
    
    MS50SFA_connect_ui_4.clear()  # 连接
    
    root.update()
    # time.sleep(1)
    if 'uart_ui_1.this_rev_Text' in locals():
        uart_ui_1.this_rev_Text.insert("end", "**************************\r\n")
        # 方法一：获取当前时间并格式化为指定字符串格式
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uart_ui_1.this_rev_Text.insert("end", current_time + "\r\n")
    
    # 寄存器读取
    MS50SFA_connect_ui_4.read_all()
    
    
    if 'uart_ui_1.this_rev_Text' in locals():
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uart_ui_1.this_rev_Text.insert("end", current_time + "\r\n")
        uart_ui_1.this_rev_Text.see("end")

def Get_All():
    Read_scan_All_at_type(0)
type(3)

def Clear_All():
    MS50SFA_connect_ui_4.clear()  # 连接


def on_tab_change(event):
    this_index = notebook.index("current")
    # print("当前选中的标签页索引:", this_index)

def load_image(image_path):
    # 使用Pillow打开图片
    img = Image.open(image_path)
    # 将图片转换成Tkinter可以处理的格式
    return ImageTk.PhotoImage(img)

def quit_application():
    global uart_ctl_1
    global mmWave_1
    global mmWave_curve_ui_2
    if messagebox.askokcancel("退出", "确定退出吗？"):
        uart_ctl_1.close_window()
        mmWave_1.close_window()
        mmWave_curve_ui_2.close_window()
        mmWave_curve_person_ui_2.close_window()
        
        
        print("exit main ok!")
        root.destroy()
        print("exit main all item!")
        
if __name__ == "__main__":
    print("hello word !")
    # logging_init()
    
    # 创建主窗口
    root = tk.Tk()
    root.title("MINEWSEMI 毫米波Demo")  # 设置窗口标题
    root.geometry("890x900+20+20")
    # root.geometry("890x900-2220+60")  # 用于Debug

    ico_name = ico_display.get_ico()
    # print("ico name = ", ico_name)
    root.iconbitmap(ico_name)
    # 设置窗口关闭响应函数
    root.protocol("WM_DELETE_WINDOW", quit_application)
    # root.resizable(False,False)

    # 显示logo和
    # this_image_logo = load_image("D:\work\itool\mmWave\img\MINEWSEMI_logo_300.png")
    this_image_logo = load_image(ico_display.get_logo_img())
    label_logo = tk.Label(root, image=this_image_logo)
    label_logo.place(x=550, y=10)  # 使标签显示在窗口上
    # 显示产品
    # this_image_product = load_image("D:\work\itool\mmWave\img\MINEWSEMI_product_300.png")
    this_image_product = load_image(ico_display.get_product_img())
    label_product = tk.Label(root, image=this_image_product)
    label_product.place(x=550, y=90)  # 使标签显示在窗口上
    

    # 创建一个 Notebook 对象
    notebook = ttk.Notebook(root, width=860, height=700)
    notebook.place(x=10, y=120)
    notebook.bind("<<NotebookTabChanged>>", on_tab_change)
    
    # 创建第一个页面
    frame1 = ttk.Frame(notebook)
    # frame1.bind("<FocusIn>", lambda event: on_tab_changed(event))
    notebook.add(frame1, text="坐标显示 (Coordinate Display)")
    
    frame3 = ttk.Frame(notebook)
    # frame1.bind("<FocusIn>", lambda event: on_tab_changed(event))
    notebook.add(frame3, text="曲线查看 (Curve View)")
    # 创建第2个页面
    frame2 = ttk.Frame(notebook)
    # frame1.bind("<FocusIn>", lambda event: on_tab_changed(event))
    notebook.add(frame2, text="参数设置 (Parameter Settings)")

    # trx 指令显示Frame控件
    frame_uart = tk.Frame(frame2, width=350, height=800)
    frame_uart.place(x=500, y=0)  # 使标签显示在窗口上
    trx_display_1 = trx_display_ui.TRX_display_ui(frame_uart)

    # UART Frame控件
    frame_uart = tk.Frame(root, width=500, height=40, bg="lightblue")
    frame_uart.place(x=10, y=10)  # 使标签显示在窗口上
    uart_ui_1 = uart_ui(frame_uart, frame2)
    uart_ctl_1 = uart_ctl(-1, 0, 0, uart_ui_1)

    uart_ui_1.this_rev_Text = trx_display_1.this_rev_Text
    uart_ui_1.window = root

    # 创建一个Frame控件
    frame_MS50SFA_TTM_Ctrl = tk.LabelFrame(frame2, text="连接 (Connection)", width=500, height=500, relief="raised")
    frame_MS50SFA_TTM_Ctrl.place(x=10, y=10)
    MS50SFA_connect_ui_4 = MS50SFA_connect_ui_ca.MS50SFA_Connect_ui(frame_MS50SFA_TTM_Ctrl, uart_ctl_1, uart_ui_1)

    # 创建一个 Notebook 对象
    notebook_mmWave = ttk.Notebook(frame2, width=460, height=500)
    notebook_mmWave.place(x=10, y=240)
    notebook_mmWave.bind("<<NotebookTabChanged>>", on_tab_change)
    
    # 创建第1个页面
    frame1_mmWave = ttk.Frame(notebook)
    notebook_mmWave.add(frame1_mmWave, text="设置 (Parameter Setting)")
    # 创建第2个页面
    frame2_mmWave = ttk.Frame(notebook)
    notebook_mmWave.add(frame2_mmWave, text="单项 (Single Setting)")

    frame_MS50SFA_TTM_Ctrl = tk.LabelFrame(frame2_mmWave, text="MS72SF2 初始化 (Initialization)", width=500, height=500, relief="raised")
    frame_MS50SFA_TTM_Ctrl.place(x=10, y=10)
    mmWave_sys_set_ui_2 = mmWave_sys_set_ca.mmWave_sys_set_ui(frame_MS50SFA_TTM_Ctrl, uart_ctl_1, uart_ui_1)

    frame_mmWave_autoSet_Ctrl = tk.LabelFrame(frame1_mmWave, text="MS72SF2 初始化设置 (Initialization Settings)", width=430, height=400, relief="raised")
    frame_mmWave_autoSet_Ctrl.place(x=10, y=10)
    mmWave_autoSet_ui_2 = mmWave_sys_set_ca.mmWave_autoSet_ui(frame_mmWave_autoSet_Ctrl, uart_ctl_1, uart_ui_1)
    
    frame_mmWave_curve_panel = tk.LabelFrame(frame3, text="", width=430, height=400, relief="ridge")  # 时间分布图
    frame_mmWave_curve_panel.place(x=10, y=10)
    mmWave_curve_ui_2 = mmWave_curve_ca.mmWave_curve_ui(frame_mmWave_curve_panel, uart_ctl_1, uart_ui_1, frame3)
    
    frame_mmWave_curve_person_panel = tk.LabelFrame(frame3, text="", width=430, height=400, relief="ridge")  # flat sunken raised ridge
    frame_mmWave_curve_person_panel.place(x=10, y=350)
    mmWave_curve_person_ui_2 = mmWave_curve_person_ca.mmWave_curve_person_ui(frame_mmWave_curve_person_panel, uart_ctl_1, uart_ui_1, frame3, mmWave_curve_ui_2)
    

    #创建毫米波模块
    frame_MS50SFA_TTM_set = tk.LabelFrame(frame1, text="", width=670, height=670, relief="flat", bg="white")  # mmWave  flat
    frame_MS50SFA_TTM_set.place(x=10, y=10)
    
    # 创建Canvas组件
    canvas = tk.Canvas(frame_MS50SFA_TTM_set, width=670, height=670, bg="white")
    # canvas.pack()
    canvas.place(x=-2,y=-2)

    # 加载背景图片
    image = Image.open(".\mmWave_map.png")  # 替换为你的图片路径
    image = ImageTk.PhotoImage(image)
    
    # 在Canvas上添加背景图片
    canvas.create_image(30, 30, image=image, anchor='nw')
    print("加载图片完成")
    mmWave_1 = mmWave_ui_ca.mmWave_ui(frame_MS50SFA_TTM_set, uart_ctl_1, uart_ui_1, frame1, canvas, mmWave_curve_ui_2.person_data_q)

    frame_mmWave_button_Ctrl = tk.LabelFrame(frame2, text="MS72SF2 控制 (Control)", width=50, height=500, relief="raised")
    frame_mmWave_button_Ctrl.place(x=10, y=90)
    mmWave_button_ui_2 = mmWave_sys_set_ca.mmWave_button_ui(frame_mmWave_button_Ctrl, uart_ctl_1, uart_ui_1, mmWave_1.mmWave_start_option)
    
    print("进入了主循环")
    # 进入主事件循环
    root.mainloop()

    print("退出了主循环")


print("主程序全部关闭了！")
