#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 14 16:39:49 2017

@author: u300844
"""

import numpy as np
from matplotlib import use
use('agg')
import matplotlib.pyplot as plt
import matplotlib.cm as mpcm

class Atmosphere(object):
    """
    sets up an atmosphere-class with some attributes:
        name    : name of that Atmosphere
        Tsfc    : surface Temperature
        H2O     : integrated water vapor
        flx     : longwave downward flux
    """
#    _H2O = None
    
    def __init__(self,name):
        self.__name=name

    def name(self):
        return self.__name
    
    def H2O(self):
        return self._H2O
    
    def flx(self):
        return self._flx
    
    def Tsfc(self,unit='C'):
        if unit == 'C':
            return self._Tsfc
        elif unit == 'K':
            return np.add(self._Tsfc,273.15)
        else:
            print("%s not allowed. Try unit=K or unit=C" %(unit))

def plot_atm(atms,save=False):
    """
    Plots the downwelling longwave flux (flx_down) in dependence on the integrated water vapor (iwv) at constant temperature (temp). 
    """
    fig = plt.figure(figsize=(19,11))
    ax_num = 0
    cmap = mpcm.get_cmap('jet')    
    for atm in atms: 
        
        ax_num += 1
        ax = fig.add_subplot(2,3,ax_num)
        
        i = -1
        for temp in sorted(atm.Tsfc(),reverse=True)[20:70][::5]:
            ax.plot(atm.H2O(),atm.flx()[:,i],label='%s'%(temp), color=cmap((temp*4)/(300*4)))
            i -= 1
            
        ax.grid()
        ax.set_xlim(0,100)
        ax.set_ylim(0,700)
        ax.set_xlabel("IWV [mm]")
        ax.set_ylabel("Flx_dwn [Wm2]")
        ax.legend(loc='best', fontsize = 6)
        ax.set_title(atm.name())
        if save:
            plt.savefig("calced_flxs/atms.png")
        else:
            return plt.show()

def plot_atm_norm(atms,save=False):
    fig = plt.figure(figsize=(19,11))
    ax_num = 0
    cmap = mpcm.get_cmap('winter')    
    
    sigma = 5.67e-8
    
    for atm in atms: 
        
        ax_num += 1
        ax = fig.add_subplot(2,3,ax_num)
        
        flx_u = np.multiply(sigma,np.power(atm.Tsfc('K'),4)) #Gesetz von Boltzman
        
        y = np.divide(atm.flx(),flx_u)

        i = -1
        for temp in sorted(atm.Tsfc(),reverse=True):
            ax.plot(atm.H2O(),y[:,i],label='%s'%(temp), color=cmap((temp+25)/(36.5+25)))
            i -= 1
            
        ax.grid()
        ax.set_xlabel("IWV [mm]")
        ax.set_ylabel("Normalized Flx:  Flx_dwm/($\sigma * T4$) ")
        ax.legend(loc='best', fontsize = 6)
        ax.set_title(atm.name())
        if save:
            plt.savefig("calced_flxs/normed.png")
        else:
            return plt.show()

def plot_oneTemp(atms, temp):
    fig = plt.figure(figsize=(19,11))
#    cmap = mpcm.get_cmap('winter')    
    ax = fig.add_subplot(1,1,1)

    for atm in atms:
        T = np.where(np.logical_and(atm.Tsfc() <= temp, atm.Tsfc() > temp-1))[0]
        print(T,atm.Tsfc()[T])
        ax.plot(atm.H2O(),atm.flx()[:,T],label=atm.name())
            
    ax.grid()
    ax.set_xlabel("IWV [mm]")
    ax.set_ylabel("Flx_dwm [Watt]]")
    ax.legend(loc='best', fontsize = 6)
    ax.set_title(atm.name() + "   " +  str(int(temp)) +" K")
    plt.savefig("calced_flxs/" + str(int(temp))+ "K_linear.png")

    # return plt.show()


if __name__ == "__main__":
    atm_names = ['midlatitude-summer','midlatitude-winter','subarctic-summer','subarctic-winter','tropical']
    FILE_NAME = "/scratch/uni/u237/users/tmachnitzki/psrad/python_svn/wv_tables/"
    # FILE_NAME = "/Users/u300844/t7home/tmachnitzki/psrad/python_svn/wv_tables/"

    midsum,midwin,subsum,subwin,tropic = [Atmosphere(atm_name) for atm_name in atm_names]
    atms = [subwin,subsum,midwin,midsum,tropic]
    # atms = [midsum] # just for testing
    for atm in atms:
        with open(FILE_NAME + atm.name() + "_interp.csv", "r") as f:
            atm_read = f.readlines()
            
        H2O = atm_read[0].split(";")[1:-1]    
        atm_arr = np.zeros([len(atm_read[1].split(";")[:-1]),len(atm_read)-1])   
        i = 0                                                           
        for line in atm_read:
            if i > 0:
                line = line.split(";")[:-1]
                atm_arr[:,i-1] = [float(x) for x in line]
            i += 1

        atm._Tsfc = atm_arr[0]
        atm._flx = atm_arr[1:]
        atm._H2O = H2O

    plot_atm(atms=atms, save=True)
    plot_atm_norm(atms=atms)

    print("Executed correctly!")