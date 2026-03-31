import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import tkinter as tk
from tkinter import ttk
 
def draw_plot(time_list, data_list):
    # 将时间字符串转换为datetime对象
    time_list = [datetime.strptime(t, '%Y-%m-%d %H:%M:%S') for t in time_list]
    # 创建折线图
    plt.plot(time_list, data_list)
    # 设置x轴的时间格式
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    # 使x轴的刻度根据需要自动调整
    plt.gcf().autofmt_xdate()
    # 显示图表
    plt.show()
 
def main():
    # 示例数据
    time_list = ['2023-01-01 00:00:00', '2023-01-01 01:00:00', '2023-01-01 02:00:00']
    data_list = [10, 20, 15]
 
    # 绘制折线图
    draw_plot(time_list, data_list)
 
if __name__ == "__main__":
    main()
    