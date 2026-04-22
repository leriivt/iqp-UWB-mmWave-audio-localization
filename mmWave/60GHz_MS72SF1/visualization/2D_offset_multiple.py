'''
Reads from a CSV containing cloumns for ground truth x,y coordinates and measured x,y coordinates
and plots the error vectors from the measured points to the ground truth points.
'''
import csv
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator

def plot_error_vectors(csv_file, title='Error Vectors from Measured Points to Ground Truth Points'):
    color_map = {'1': 'y', '2': 'k', '3': 'b', '4': 'c', '5': 'm'}
    color_id = []
    gt_x = []
    gt_y = []
    meas_x = []
    meas_y = []

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:

            color_id.append(row['color_id'])
            gt_x.append(float(row['gt_x']))
            gt_y.append(float(row['gt_y']))
            meas_x.append(float(row['xmeas']))
            meas_y.append(float(row['ymeas']))

    color_id = np.array(color_id)
    gt_x = np.array(gt_x)
    print("gt_x:", gt_x)
    gt_y = np.array(gt_y)
    meas_x = np.array(meas_x)
    meas_y = np.array(meas_y)

    plt.figure(figsize=(8, 8))
    plt.grid()
    #plt.quiver(meas_x, meas_y, gt_x - meas_x, gt_y - meas_y, angles='xy', scale_units='xy', scale=1, color='r')
    #plt.quiver(gt_x, gt_y, meas_x - gt_x, meas_y - gt_y, scale_units='xy', color='r')
    plt.quiver(gt_x, gt_y, meas_x - gt_x, meas_y - gt_y, angles='xy', scale_units='xy', scale=1, color='r')
    plt.scatter(gt_x, gt_y, color='g', label='Ground Truth')
    plt.scatter(meas_x, meas_y, c=[color_map.get(id, 'r') for id in color_id], label='Measured')
    plt.scatter(0, 0, marker='*', s=200, color='g', edgecolors='black', linewidths=1, label='Sensor')
    plt.xlabel('X Coordinate (meters)')
    plt.ylabel('Y Coordinate (meters)')
    plt.xlim(-3, 3)
    plt.ylim(-3, 3)
    #plt.title('Error Vectors from Measured Points to Ground Truth Points')
    plt.title(title)
    plt.legend()

    #plt.axis('equal')
    ax = plt.gca()
    ax.xaxis.set_major_locator(MultipleLocator(0.6))
    ax.yaxis.set_major_locator(MultipleLocator(0.6))
    circle = plt.Circle((0, 0), radius=2.5, fill=False, linestyle='--', edgecolor='blue')
    ax.add_patch(circle)

    
    plt.show()


if __name__ == "__main__":
    csv_file = 'test_5.csv'  # Replace with your CSV file path
    plot_error_vectors(csv_file, title='Error Vectors from Ground Truth Points to Measured Points')
    #plot_error_vectors('test_0_actual.csv')
    #plot_error_vectors('test_2.csv', title='Error Vectors from Measured Points to Ground Truth Points (height adj)')
    #plot_error_vectors('test_3.csv', title='Error Vectors from Measured Points to Ground Truth Points (default)')
    #plot_error_vectors('test_4.csv', title='Error Vectors from Measured Points to Ground Truth Points (calib, height adj)')


