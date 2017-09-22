#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 13:03:46 2017

@author: u300844
"""

import typhon as tp
import numpy as np
from os.path import join
import os
import matplotlib.pyplot as plt


file = "/scratch/uni/u237/users/tmachnitzki/Bachelor_Thesis/Verschiedenes/sadata_stefan_kinne.csv"
#file = "/Users/u300844/Downloads/sadata_stefan_kinne.d"

with open(file, 'r') as f:
    sk = f.readlines()
    
tropical,midsum,midwin,subsum,subwin = [{} for x in range(5)]
atms = [tropical,midsum,midwin,subsum,subwin]

#atms = [tropical]
    
counter = 0
for atm in atms:
    add = counter*80
    atm['read'] = sk[6+add:80+add]
    counter += 1
    
    
    atm['z'] = np.array([])
    atm['p'] = np.array([])
    atm['t'] = np.array([])
    atm['H2O'] = np.array([])
    
    for line in atm['read']:
        atm['z'] = np.append(atm['z'],float(line.split()[0])*1000)
        atm['p'] = np.append(atm['p'],float(line.split()[1])*100)
        atm['t'] = np.append(atm['t'],float(line.split()[2]))
        atm['H2O'] = np.append(atm['H2O'],float(line.split()[4])*1e-6)
        
    
    H2O_integrated_stefan = tp.atmosphere.iwv(atm['H2O'][:11],atm['p'][:11],atm['t'][:11],atm['z'][:11])
    print('Value from Stefans data: %f' %(H2O_integrated_stefan))


#%%

def get_fascod_atmosphere(fascod_path, season):
    """Returns the temperature profile and mixing ratio profiles for H2O, O3,
    N2O, CO, CH4 from a standard sounding or any other giving sounding.
    Instead of returning specific values, interpolated functions are returned.

    Parameters:
        fascod_path (str):
        season (str):

    Returns:
        dict:
    """
    columns = ['t', 'z', 'H2O', 'CO2', 'O3', 'N2O', 'CO', 'CH4']
    atmosphere = {}

    for name in columns:
        path = join(fascod_path, season, '{}.{}.xml'.format(season, name))
        f = tp.arts.xml.load(path)
        pres = f.grids[0]
        atmosphere[name] = f.data.reshape(-1)

    atmosphere['p'] = pres

    return atmosphere

fas_path = '/scratch/uni/u237/users/tlang/arts-xml-data/planets/Earth/Fascod/'

atm_names =  sorted((os.listdir('/scratch/uni/u237/users/tlang/arts-xml-data/planets/Earth/Fascod') ))
del atm_names[atm_names.index('README')]
#atm_names = ["tropical"]

for atm in atm_names:
    fascod_atm = get_fascod_atmosphere(fas_path,season=atm)
    
    H2O_integrated = tp.atmosphere.iwv(fascod_atm['H2O'][1:12],fascod_atm['p'][1:12],fascod_atm['t'][1:12],fascod_atm['z'][1:12])
    print('H2O from fascod %s: %f' %(atm,H2O_integrated))
  
    
#%%   
#fig = plt.figure(figsize =(16,9)) 
#plt.suptitle("Tropical atmosphere compare")   
#ax1 = fig.add_subplot(2,2,1)
#ax2 = fig.add_subplot(2,2,2)
#ax3 = fig.add_subplot(2,2,3)
#ax4 = fig.add_subplot(2,2,4)
#
#ax1.plot(fascod_atm['H2O'],fascod_atm['z'],color='b',label='fascod')
#ax1.plot(tropical['H2O'],tropical['z'],color='red', ls = "--",label='Stefan')
#ax1.set_xlabel("IWV")
#ax1.set_ylabel("Height")
#ax1.legend(loc='best')
#ax1.grid(True)
#
#ax2.plot(fascod_atm['p'],fascod_atm['z'],color='b',label='fascod')
#ax2.plot(tropical['p'],tropical['z'],color='red', ls = "--",label='Stefan')
#ax2.set_xlabel("Pressure")
#ax2.set_ylabel("Height")
#ax2.legend(loc='best')
#ax2.grid(True)
#
#
#ax3.plot(fascod_atm['t'],fascod_atm['z'],color='b',label='fascod')
#ax3.plot(tropical['t'],tropical['z'],color='red', ls = "--",label='Stefan')
#ax3.set_xlabel("Temperature")
#ax3.set_ylabel("Height")
#ax3.legend(loc='best')
#ax3.grid(True)
#
#ax4.set_visible = False
#ax4.axis('off')
#
#
#
#plt.show()
