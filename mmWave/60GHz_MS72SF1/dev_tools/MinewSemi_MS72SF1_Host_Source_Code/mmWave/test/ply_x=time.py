import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import tkinter as tk
from tkinter import ttk
 
def draw_chart(root):
    # 假设有一些数据点
    times = ['2023-01-01 08:00', '2023-01-01 09:00', '2023-01-01 10:00']
    values = [20, 25, 30]
 
    times = [datetime.strptime(t, '%Y-%m-%d %H:%M') for t in times]
 
    fig, ax = plt.subplots()
    ax.plot(times, values)
 
    # 设置x轴的时间格式
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
 
    # 设定x轴的时间范围
    ax.set_xlim(times[0], times[-1])
 
    # 使图表与tkinter窗口交互
    fig.autofmt_xdate()
 
    # 在tkinter中显示图表
    canvas = plt.backends.backend_tkagg.FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
 
root = tk.Tk()
draw_chart(root)
root.mainloop()
