import matplotlib.pyplot as plt
import numpy as np
 
# 创建数据
x = np.linspace(0, 10, 100)
y = np.sin(x)
 
# 创建折线图
fig, ax = plt.subplots()
ax.plot(x, y)
 
# 设置x轴的刻度标签为空字符串，从而隐藏部分坐标
xticks = ax.set_xticks(np.arange(0, 10, 0.5))
xticklabels = ax.set_xticklabels(['' if i % 0.5 == 0 else f'{i:.1f}' for i in xticks])
 
# 显示图表
plt.show()
