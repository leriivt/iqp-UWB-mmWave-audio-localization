'''
Reads from a CSV containing cloumns for ground truth x,y coordinates and measured x,y coordinates
and plots the error vectors from the measured points to the ground truth points.
'''
import csv
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator, FixedLocator

def plot_error_vectors(csv_file, title='Error Vectors from Measured Points to Ground Truth Points'):
    color_map = {'1': 'y', '2': 'k', '3': 'b', '4': 'c', '5': 'm'}
    color_id = []
    gt_x = []
    gt_y = []
    meas_x = []
    meas_y = []

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            
            #only plot every 10th point
            if i % 10 != 0:
                continue

            color_id.append(row['color_id'])
            gt_x.append(float(row['gt_y']))
            gt_y.append(float(row['gt_z']))
            meas_x.append(float(row['y']))
            meas_y.append(float(row['z']))

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
    plt.xlabel('Y Coordinate (meters)')
    plt.ylabel('Z Coordinate (meters)')
    
    #plt.title('Error Vectors from Measured Points to Ground Truth Points')
    plt.title(title)
    plt.legend()

    ax = plt.gca()
    ax.set_aspect('equal', adjustable='box')
    plt.xlim(-3.1, 3.1)
    plt.ylim(-0.25, 3.6)
    
    ax.xaxis.set_major_locator(MultipleLocator(0.6))
    ax.yaxis.set_major_locator(FixedLocator([0, 0.42, 1.02, 1.62, 2.22, 2.82, 3.42]))
    #circle = plt.Circle((0, 0), radius=2.5, fill=False, linestyle='--', edgecolor='blue')
    #ax.add_patch(circle)


    # Two rays from origin at 60° and 120° from x-axis (±30° from vertical)
    angle_left  = np.radians(150)
    angle_right = np.radians(30)
    r = 3  # how far the lines extend (match your circle radius)

    for angle in [angle_left, angle_right]:
        ax.plot([0, r * np.cos(angle)], [0, r * np.sin(angle)],
                'b--', linewidth=1.5)

    # Arc connecting the two rays
    theta = np.linspace(np.radians(30), np.radians(150), 200)
    ax.plot(r * np.cos(theta), r * np.sin(theta), 'b--', linewidth=1.5)

    
    plt.show()


if __name__ == "__main__":
    csv_file = 'wall_test_0.csv'  # Replace with your CSV file path
    plot_error_vectors(csv_file, title='Error Vectors from Ground Truth Points to Measured Points (Wall Mounting)')
    #plot_error_vectors('test_0_actual.csv')
    #plot_error_vectors('test_2.csv', title='Error Vectors from Measured Points to Ground Truth Points (height adj)')
    #plot_error_vectors('test_3.csv', title='Error Vectors from Measured Points to Ground Truth Points (default)')
    #plot_error_vectors('test_4.csv', title='Error Vectors from Measured Points to Ground Truth Points (calib, height adj)')


