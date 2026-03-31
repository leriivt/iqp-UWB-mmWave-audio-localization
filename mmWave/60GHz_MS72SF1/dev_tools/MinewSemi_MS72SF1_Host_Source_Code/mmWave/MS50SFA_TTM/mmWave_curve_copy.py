import tkinter as tk
import tkinter.ttk as ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import time
import copy


class mmWave_curve_person_ui(object):
    def __init__(self, frame_1, uart, uart_ui, window, this_data):
        self.uart = uart 
        self.uart_ui = uart_ui
        
        self.this_data = this_data

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

        # 创建数据
        self.x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.y = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        self.ax.bar(self.x, self.y)
        self.ax.set_xlim(self.x[0], self.x[-1])
        self.ax.set_ylim(0, 10)
    
        self.canvas.draw()  # 绘制曲线

        tk.Label(window, text="人数分布图", bg="white").place(x=400,y=360)
        ttk.Button(window, text="分析全部", width=8, command=self.add_point_chart).place(x=740,y=620)

    def close_window(self):
        print("close_window copy")
        # plt.close()

    def add_point_chart(self):
        print("add_point_chart")

        this_data = self.this_data.y_values
        # this_data = copy.deepcopy(self.this_data)
        # print(self.this_data.y_values)
        person_statistics_dict = {}
        for item in this_data:
            if item in person_statistics_dict:
                person_statistics_dict[item] += 1
            else:
                person_statistics_dict[item] = 1
        
        # print(person_statistics_dict)

        # 统计人数
        self.x = []
        self.y = []
        data_totle_count = 0
        max_person = 0
        min_person = 0
        for item in person_statistics_dict:
            self.x.append(item)
            person_count = person_statistics_dict[item]
            data_totle_count += person_count
            self.y.append(person_count)

            if person_count > max_person:
                max_person = person_count

        # 计算比例
        for i in range(0, len(self.y), 1):
            temp = self.y[i]
            temp = temp / data_totle_count * 100
            self.y[i] = temp

        self.ax.clear()
        # 设置坐标
        # self.ax.set_xlim(self.x[0], self.x[-1])
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 100)
        
        self.ax.bar(self.x, self.y)
        self.canvas.draw()
