'''
Reads from a CSV containing cloumns for ground truth x,y coordinates and measured x,y coordinates
and plots the error vectors from the measured points to the ground truth points.
'''
import csv
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator

def plot_error_vectors(csv_file, title='Error Vectors from Measured Points to Ground Truth Points'):
    gt_x = []
    gt_y = []
    meas_x = []
    meas_y = []

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            gt_x.append(float(row['gt_x']))
            gt_y.append(float(row['gt_y']))
            meas_x.append(float(row['meas_x']))
            meas_y.append(float(row['meas_y']))

    gt_x = np.array(gt_x)
    print("gt_x:", gt_x)
    gt_y = np.array(gt_y)
    meas_x = np.array(meas_x)
    meas_y = np.array(meas_y)

    plt.figure(figsize=(8, 8))
    #plt.quiver(meas_x, meas_y, gt_x - meas_x, gt_y - meas_y, angles='xy', scale_units='xy', scale=1, color='r')
    #plt.quiver(gt_x, gt_y, meas_x - gt_x, meas_y - gt_y, scale_units='xy', color='r')
    plt.quiver(gt_x, gt_y, meas_x - gt_x, meas_y - gt_y, angles='xy', scale_units='xy', scale=1, color='r')
    plt.scatter(gt_x, gt_y, color='g', label='Ground Truth')
    plt.scatter(meas_x, meas_y, color='b', label='Measured')
    plt.xlabel('X Coordinate (meters)')
    plt.ylabel('Y Coordinate (meters)')
    plt.xlim(-3.6, 3.6)
    plt.ylim(-3.6, 3.6)
    #plt.title('Error Vectors from Measured Points to Ground Truth Points')
    plt.title(title)
    plt.legend()

    #plt.axis('equal')
    ax = plt.gca()
    ax.xaxis.set_major_locator(MultipleLocator(0.6))
    ax.yaxis.set_major_locator(MultipleLocator(0.6))

    plt.grid()
    plt.show()


if __name__ == "__main__":
    csv_file = 'test_1.csv'  # Replace with your CSV file path
    plot_error_vectors(csv_file)
    plot_error_vectors('test_0.csv')
    plot_error_vectors('test_2.csv', title='Error Vectors from Measured Points to Ground Truth Points (height adj)')
    plot_error_vectors('test_3.csv', title='Error Vectors from Measured Points to Ground Truth Points (default)')
    plot_error_vectors('test_4.csv', title='Error Vectors from Measured Points to Ground Truth Points (calib, height adj)')


