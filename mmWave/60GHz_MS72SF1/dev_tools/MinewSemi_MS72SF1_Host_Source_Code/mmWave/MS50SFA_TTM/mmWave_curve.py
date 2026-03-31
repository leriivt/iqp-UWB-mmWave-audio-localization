import tkinter as tk
import tkinter.ttk as ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


import numpy as np
import threading
import time

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import queue

import system.get_screen_dpi as this_dpi


class mmWave_curve_ui(object):
    def __init__(self, frame_1, uart, uart_ui, window):
        self.uart = uart
        self.uart_ui = uart_ui

        self.man_exit_flag = 0
        self.auto_max_show_count = 0
        
        self.draw_count = 0  # 添加曲线数量统计
        self.person_data_q = queue.Queue()  # 创建一个先进先出队列
        
        if 1:
            # 创建柱状图
            fig = Figure(figsize=(8,3), dpi=100)
            self.ax = fig.add_subplot(111)

            # 添加一组曲线
            # self.ax.plot([1,2,4,3,5,7,6])
            
            # 将柱状图嵌入到Tkinter窗口中
            self.canvas = FigureCanvasTkAgg(fig, frame_1)
            self.canvas.get_tk_widget().pack()
        else:
            # 创建柱状图
            fig, self.ax = plt.subplots(figsize=(8, 3), dpi=100)
            # 将柱状图嵌入到Tkinter窗口中
            self.canvas = FigureCanvasTkAgg(fig, master=frame_1)
            # self.canvas.draw()
            self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
        
        # 假设有一些数据点
        self.x_times = []  # ['2023-01-01 08:00', '2023-01-01 09:00', '2023-01-01 10:00']
        self.y_values = []  # [20, 25, 21]
        self.times = [datetime.strptime(t, '%Y-%m-%d %H:%M') for t in self.x_times]
        
        self.line, = self.ax.plot(self.times, self.y_values)
        # 设置x轴的时间格式
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%M:%S'))
        # 设定x轴的时间范围
        # self.ax.set_xlim(times[0], times[-1])
        self.ax.set_ylim(0, 10)
        self.ax.yaxis.set_label_position('right')  # 将纵坐标标签放置在右侧
        self.ax.yaxis.tick_right()  # 将纵坐标的刻度放置在右侧
        
        # 使图表与tkinter窗口交互
        fig.autofmt_xdate()
    
        tk.Label(window, text="时间分布图", bg="white").place(x=400,y=25)
        ttk.Button(window, text="显示全部", width=8, command=self.add_point_chart).place(x=740,y=270)

        self.point_chart_Thread_hand = None
        uart.thread_2 = self.point_chart_thread_start
        

    def close_window(self):
        print("mmWave curve close_window")
        
        if self.point_chart_Thread_hand is not None:
            self.man_exit_flag = 1
            self.point_chart_Thread_hand.join()
            self.point_chart_Thread_hand = None

        plt.close()


    def add_point_chart(self):
        self.auto_max_show_count = 60*2
        self.ax.set_xlim(self.times[0], self.times[-1])
        self.canvas.draw()  # 重绘图像


    def update_plt(self, data):
 
        # self.person_statistics_dict[data] += 1  # 人数统计

        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        self.x_times.append(current_time)
        self.y_values.append(data)

        if self.draw_count > 1000:
            self.x_times.pop(0)
            self.y_values.pop(0)

        self.times = [datetime.strptime(t, '%Y-%m-%d %H:%M:%S') for t in self.x_times]
        self.line.set_data(self.times, self.y_values)

        get_count = len(self.times)
        if self.auto_max_show_count > 0:
            self.auto_max_show_count -= 1
            self.ax.set_xlim(self.times[0], self.times[-1])
        elif get_count > 1:
            sigle_show_num = 1*5
            if get_count < sigle_show_num:
                self.ax.set_xlim(self.times[0], self.times[-1])
            else:
                self.ax.set_xlim(self.times[-sigle_show_num], self.times[-1])
            
        
        if get_count == 60:
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        elif get_count == 3600:
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        self.canvas.draw()  # 重绘图像

    def update_plot(self, x, y):
        self.line.set_data(x, y)
        self.canvas.draw()  # 重绘图像

    def point_chart_thread_start(self, option):
        print("point_chart_thread_start is start", option)

        if option == 1:
            if self.point_chart_Thread_hand is None:
                self.point_chart_Thread_hand = threading.Thread(target=self.point_chart_Thread)
                self.man_exit_flag = 0
                self.point_chart_Thread_hand.start()
        else:
            # self.man_exit_flag = 1
            self.close_window()


    def point_chart_Thread(self):
        display_persion_to_bar = 0
        self.draw_count = 0
        while(1):
            if self.man_exit_flag == 1:
                print("sys exit point_chart_Thread 100")
                return
            
            try:
                if self.person_data_q.empty() is False:
                    while(1):
                        rev_str = self.person_data_q.get()

                        # if display_persion_to_bar != rev_str:
                        #     display_persion_to_bar = rev_str
                        
                        if self.person_data_q.empty() is True:
                            break
                    
                    # self.person_data_q.queue.clear()
                    
                    self.update_plt(rev_str)
                    self.draw_count += 1
                    # print("draw_char count = ", self.draw_count)
            
            except:
                print("异常, point_chart_Thread")
                # return
            
            time.sleep(1)
