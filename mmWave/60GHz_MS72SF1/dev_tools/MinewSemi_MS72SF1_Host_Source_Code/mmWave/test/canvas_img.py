import tkinter as tk
from PIL import Image, ImageTk
 
def main():
    # 创建Tkinter窗口
    root = tk.Tk()
    root.title("Canvas Background Image")
 
    # 创建Canvas对象
    canvas = tk.Canvas(root, width=600, height=600)
    canvas.pack()
 
    # 加载背景图片
    image = Image.open("D:\work\itool\mmWave\img\ditu2.png")  # 替换为你的图片路径
    image = ImageTk.PhotoImage(image)
 
    # 在Canvas上添加背景图片
    canvas.create_image(0, 0, image=image, anchor='nw')
 
    # 开始Tkinter事件循环
    root.mainloop()
 
if __name__ == '__main__':
    main()
