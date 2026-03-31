import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
 
# 初始化tkinter窗口
root = tk.Tk()
root.title("Tkinter Matplotlib Line Chart")
 
# 创建一个Figure对象和一个Axes对象
fig = Figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot(111)
 
# 创建一个折线图
x = [1, 2, 3, 4, 5]
y = [1, 2, 3, 4, 5]
ax.plot(x, y, label='Line 1')
ax.legend()
 
# 在tkinter中展示matplotlib图形
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
 
# 启动tkinter事件循环
root.mainloop()
