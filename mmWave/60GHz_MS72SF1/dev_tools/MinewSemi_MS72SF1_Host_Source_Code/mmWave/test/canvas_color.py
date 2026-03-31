import tkinter as tk
 
def create_ovals(canvas, points, colors):
    for i in range(len(points)):
        x1, y1, x2, y2 = points[i]
        canvas.create_oval(x1, y1, x2, y2, fill=colors[i])
 
root = tk.Tk()
canvas = tk.Canvas(root, width=400, height=400)
canvas.pack()
 
points = [(10, 10, 100, 100), (150, 150, 250, 250), (50, 200, 150, 300)]
colors = ['red', 'blue', 'green']
 
create_ovals(canvas, points, colors)
 
root.mainloop()
