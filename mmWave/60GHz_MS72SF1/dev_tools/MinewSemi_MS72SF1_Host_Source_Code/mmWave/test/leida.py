import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
 
def create_radar_chart():
    # 创建一个二维雷达图数据
    data = np.random.rand(4, 1)  # 3个点，4个维度
    print("data = ", data)
    angles = np.linspace(0, 2*np.pi, 4, endpoint=False)
 
    # 创建雷达图
    fig = Figure(figsize=(7, 7))
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=True)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_rlabel_position(0)
    ax.plot(angles, data, 'o-', linewidth=2)
    ax.fill(angles, data, alpha=0.25)
 
    # 在Tkinter中展示
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
 
root = tk.Tk()
root.title("Tkinter with Matplotlib")
create_radar_chart()
root.mainloop()
