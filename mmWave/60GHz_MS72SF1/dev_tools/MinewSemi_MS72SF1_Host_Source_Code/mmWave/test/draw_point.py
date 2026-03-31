import tkinter as tk
 
def draw_point_cloud(canvas, points):
    r1 = 0
    for point in points:
        canvas.create_oval(point[0] - r1, point[1] - r1, point[0] + r1, point[1] + r1)
 
def main():
    # 创建Tkinter窗口
    root = tk.Tk()
    root.title("Point Cloud")
 
    # 创建Canvas组件
    canvas = tk.Canvas(root, width=800, height=600)
    canvas.pack()
 
    # 生成点云数据（随机点）
    # point_cloud = [(x, y) for x in range(10, 390, 50) for y in range(10, 390, 50)]
 
    point_cloud = [(100, 50), (200, 50), (500, 260)]
    print("开始绘制点")
    print(point_cloud)
    print("完成绘制点")
    # 绘制点云
    draw_point_cloud(canvas, point_cloud)
 
    # 启动事件循环
    root.mainloop()
 
if __name__ == '__main__':
    main()
