#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon, Aug 28 15:33:10 2017

@author: Tobias Machnitzki
"""

from scipy.interpolate import griddata
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    FILE_PATH = '/Users/u300844/t7home/tmachnitzki/psrad/python_svn/wv_tables/'
    tropic_file = 'tropical_dependent.csv'
    midsum_file = 'midlatitude-summer_dependent.csv'
    midwin_file = 'midlatitude-winter_dependent.csv'
    subsum_file = 'subarctic-summer_dependent.csv'
    subwin_file = 'subarctic-winter_dependent.csv'

    WRITE_FILE = "_interp.csv"

    atm_file_list = [tropic_file, midsum_file, midwin_file, subsum_file, subwin_file]

    #Opening the Files:
    with open(FILE_PATH + midsum_file, 'rb') as f:
        midsum = np.genfromtxt(f, names=True, delimiter=';')
    with open(FILE_PATH + midwin_file, 'rb') as f:
        midwin = np.genfromtxt(f, names=True, delimiter=';')
    with open(FILE_PATH + tropic_file, 'rb') as f:
        tropic = np.genfromtxt(f, names=True, delimiter=';')
    with open(FILE_PATH + subsum_file, 'rb') as f:
        subsum = np.genfromtxt(f, names=True, delimiter=';')
    with open(FILE_PATH + subwin_file, 'rb') as f:
        subwin = np.genfromtxt(f, names=True, delimiter=';')

    atms = [tropic,midsum,midwin,subsum,subwin]

    for atm,atm_file in zip(atms,atm_file_list):
        min_temp = int(np.min(atm['Temperature']))
        max_temp = int(np.max(atm['Temperature'])) +1
        temp_step = complex(0, max_temp + 1-min_temp)
        grid_x, grid_y = np.mgrid[0:100:1001j, min_temp:max_temp:temp_step] #creating the grid for later
        grid = griddata((atm['IWV'], atm['Temperature']), atm['flxd'], (grid_x, grid_y), method='linear')  #interpolating the data to the previous defined grid

        #Writing the interpolated grid to file:
        with open(FILE_PATH + atm_file[:-14] + WRITE_FILE, 'w') as f:
            f.write(";")
            for element in grid_x[:, 0]:
                f.write("%s;" %element)
            f.write("\n")
            for i in range(len(grid[0, :])):
                f.write(str(round(grid_y[0, i],1)))
                f.write(';')
                for element in grid[:,i]:
                    f.write("%s;" % element)
                f.write("\n")