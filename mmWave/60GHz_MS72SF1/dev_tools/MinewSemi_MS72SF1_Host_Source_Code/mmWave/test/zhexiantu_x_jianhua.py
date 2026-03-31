import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
 
# 创建数据
x = np.arange(0, 10, 0.1)
y = np.sin(x)
 
# 创建折线图
fig, ax = plt.subplots()
ax.plot(x, y)
 
# 设置x轴刻度标签的可见性
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.5))
 
# 隐藏部分x轴标签
# 假设我们想要隐藏x轴的0到2之间的标签
for x_label in ax.xaxis.get_majorticklabels():
    if 0 <= x_label.get_position()[0] < 2:
        x_label.set_visible(False)
 
# 显示图表
plt.show()
