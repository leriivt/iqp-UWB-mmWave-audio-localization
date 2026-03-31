from tkinter import Tk, Label
from PIL import Image, ImageTk

import tkinter as tk
 
def load_image(image_path):
    # 使用Pillow打开图片
    img = Image.open(image_path)
    # 将图片转换成Tkinter可以处理的格式
    return ImageTk.PhotoImage(img)
 
root = Tk()
root.title("高清图片展示")
 
# 图片文件路径
image_path = "D:\work\itool\mmWave\img\MINEWSEMI-英文+公司名.png"

# 加载图片
image = load_image(image_path)
 
# 创建标签并展示图片
# label = Label(image=image)
# label.pack()
label_logo = tk.Label(root, image=image)
label_logo.place(x=0, y=10)  # 使标签显示在窗口上
 
root.mainloop()
