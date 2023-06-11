#!/usr/bin/env python3

import rospy
import time
import matplotlib.pyplot as plt
from nav_msgs.msg import OccupancyGrid
from std_msgs.msg import *
from collections import Counter


map_count = []
occ_grid_counter = {}

def grapher(data):
        
    global occ_grid
    occ_grid = data.data
   
    occ_grid_counter = Counter(occ_grid)    

    print(occ_grid_counter)

    discovered_area = occ_grid_counter[0] + occ_grid_counter[100]
    
    map_count.append(discovered_area)

    print(map_count)


    plt.plot(map_count, 'r')
    plt.gcf().subplots_adjust(bottom=0.15, left=0.20)
    plt.ylabel('Area Discovered [number of pixels]')
    plt.xlabel('Time [s]')

    plt.savefig('result_large_high_rrt.png')
    
def listener():

    rospy.init_node('grapher', anonymous=True)

    rospy.Subscriber('/map', OccupancyGrid, grapher)

    rospy.spin()

    occ_grid_counter

if __name__ == '__main__':
    listener()