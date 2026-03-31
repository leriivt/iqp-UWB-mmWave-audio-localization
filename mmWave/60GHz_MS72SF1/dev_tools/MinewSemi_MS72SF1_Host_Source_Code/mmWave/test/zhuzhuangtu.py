import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Tk
 
def create_bar_chart():
    # 创建数据
    x = [1, 2, 3, 4]
    y = [10, 20, 15, 25]
 
    # 创建窗口
    root = Tk()
    root.wm_title("柱状图")
 
    # 创建柱状图
    fig, ax = plt.subplots()
    ax.bar(x, y)
 
    # 将柱状图嵌入到Tkinter窗口中
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
 
    # 启动Tkinter事件循环
    root.mainloop()
 
create_bar_chart()
