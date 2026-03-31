import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
 
this_data = 0.1
def update_plot():
    global this_data

    # 生成新的数据
    x = np.linspace(0, 2*np.pi, 100) + this_data
    y = np.sin(x) + this_data

    this_data += 0.1
    line.set_data(x, y)
    canvas.draw()  # 重绘图像
 
root = tk.Tk()
root.title("Tkinter Dynamic Line Plot")
 
fig = Figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot(111)
line, = ax.plot([], [], 'r-')  # 初始空折线图
ax.set_xlim(0, 2*np.pi)
ax.set_ylim(-1, 1)
 
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
 
# 创建一个按钮来触发折线图更新
button = tk.Button(root, text="Update Plot", command=update_plot)
button.pack(side=tk.LEFT, padx=5, pady=5)
 
# 启动事件循环
root.mainloop()
