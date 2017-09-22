#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 11 15:33:10 2017

@author: Tobias Machnitzki
"""

from os.path import join
import matplotlib.pyplot as plt
import numpy as np
import typhon as tp
import os
import psrad
from wv_converter import VMR2RH, RH2VMR
from joblib import Parallel,delayed

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

def calc_hr(soundings, spec_range, const_albedo=0.05, zenith_angle=53):
    """Computes the lw radiation for a given sounding.

    Parameters:
        soundings:   profiles of pressure, Temperature, altitude and VMRs of
                     apsorption species in a dictionary
        spec_range   spectral range: 'lw' (longwave) or 'sw' (shortwave)
        const_albedo:surface albedo (constant for all wavelengths)
        zenith_angle:solar zenith angle in degrees (between 0 and 90)
    """
    H2O = soundings['H2O'][:] * 1e6  # in ppm
    CO2 = soundings['CO2'][:] * 1e6
    O3 = soundings['O3'][:] * 1e6
    N2O = soundings['N2O'][:] * 1e6
    CO = soundings['CO'][:] * 1e6
    CH4 = soundings['CH4'][:] * 1e6
    Z = soundings['z'][:]  # in m
    T = soundings['t'][:]  # in K
    P = soundings['p'][:] / 100   # in hPa
    
    
    dmy_indices = np.asarray([0])
    ic = dmy_indices.astype("int32") + 1
    c_lwc = np.asarray([0.])
    c_iwc = np.asarray([0.])
    c_frc = np.asarray([0.])

    P_sfc = soundings['p'][0] / 100
    T_sfc = T[0]

    albedo = const_albedo
    zenith = zenith_angle
    nlev = len(P)

    psrad.setup_single(nlev, len(ic), ic, c_lwc, c_iwc, c_frc, zenith, albedo,
                       P_sfc, T_sfc, Z, P, T, H2O, O3, CO2, N2O, CO, CH4)

    if spec_range == 'lw':
        psrad.advance_lrtm()
        hr, hr_clr, flxd, flxd_clr, flxu, flxu_clr = psrad.get_lw_fluxes()

        xhr = hr[0, :]
        xhr_clr = hr_clr[0, :]
        xhr[0] = 0
        xhr_clr[0] = 0

        data = {}
        data['hr'] = xhr
        data['hr_clr'] = xhr_clr
        data['flxu'] = flxu[0, :]
        data['flxd'] = flxd[0, :]
        data['flxu_clr'] = flxu_clr[0, :]
        data['flxd_clr'] = flxd_clr[0, :]

    else:
        psrad.advance_srtm()
        (hr, hr_clr, flxd, flxd_clr, flxu, flxu_clr, vis_frc,
         par_dn, nir_dff, vis_diff, par_diff) = psrad.get_sw_fluxes()

        xhr = hr[0, :]
        xhr_clr = hr_clr[0, :]
        xhr[0] = 0
        xhr_clr[0] = 0

        data = {}
        data['hr'] = xhr[::-1]
        data['hr_clr'] = xhr_clr[::-1]
        data['flxu'] = flxu[0, ::-1]
        data['flxd'] = flxd[0, ::-1]
        data['flxu_clr'] = flxu_clr[0, ::-1]
        data['flxd_clr'] = flxd_clr[0, ::-1]
        
    H2O *= 1e-6  #Konvertiere H2O wieder zu vmr

    return data,H2O,T_sfc

# ======================================================================================================================

def start_calculations(fascod_atm_raw,temp, h2o_low,h2o_high,h2o_step, LIMIT_HEIGHT=False):
    fascod_atm = fascod_atm_raw.copy()
    fascod_atm['t'] = np.add(fascod_atm['t'],
                             temp)  # adding the temperature change to the original temperature (moving the temperature profile to the right/left in a skew-t diagram)
    return_string = []
    for h2o in np.arange(h2o_low, h2o_high + 1e-9, h2o_step):  # iterating over relative humidity corrections

        # fascod_atm['H2O'] = RH2VMR(h2o, fascod_atm['p'], fascod_atm['t'])  #change relative humidity in all hights to be the same
        fascod_atm['H2O'][0:3] = RH2VMR(h2o, fascod_atm['p'][0:3],
                                        fascod_atm['t'][0:3])  # change relative humidity in all hights to be the same
        result_temp, H2O, T = calc_hr(fascod_atm, 'lw')  # <------------- PSRAD calculation. T = surface temperature

        if LIMIT_HEIGHT:
            RH = VMR2RH(H2O[:12], fascod_atm['p'][:12], fascod_atm['t'][:12])  # Relative Humidity in all hights
            H2O_integrated = tp.atmosphere.iwv(H2O[:12], fascod_atm['p'][:12], fascod_atm['t'][:12],
                                               fascod_atm['z'][:12])  # integrated water vapor

        else:
            RH = VMR2RH(H2O, fascod_atm['p'], fascod_atm['t'])
            H2O_integrated = tp.atmosphere.iwv(H2O, fascod_atm['p'], fascod_atm['t'], fascod_atm['z'])

        return_string_line = str(T) + ";" + str(h2o) + ";" + str(H2O_integrated) + ";" + str(result_temp['flxd_clr'][0])
        return_string.append(return_string_line)

    return return_string



# ======================================================================================================================

if __name__ == '__main__':
    write_file = '/scratch/uni/u237/users/tmachnitzki/psrad/python_svn/wv_tables/'
    atm_names =  sorted((os.listdir('/scratch/uni/u237/users/tlang/arts-xml-data/planets/Earth/Fascod') ))
    del atm_names[atm_names.index('README')]
    
    LIMIT_HEIGHT = False  #if True: iwv just up to 10 Km. Else up to 95 Km
    Rw = tp.atmosphere.constants.gas_constant_water_vapor #Gaskonstante von Wasserdampf

    t_low =  -30  #Darf nicht größer 0 sein
    t_high = 30    
    t_step = 0.1
    
    h2o_low = 0
    h2o_high = 1
    h2o_step = 0.001
    
    #for testing:
    # atm_names = ['midlatitude-summer']  #<-- Das hier auskommentieren um alle Atmosphären zu berechnen

    for fas_atm in atm_names:   #iterating over all fascod-atmospheres
        fascod_atm_raw = get_fascod_atmosphere("/scratch/uni/u237/users/tlang/arts-xml-data/planets/Earth/Fascod/",season=fas_atm)
        print('Now calculating: ',fas_atm)
        temp_counter = 0

        for key in fascod_atm_raw.keys():
            fascod_atm_raw[key] = fascod_atm_raw[key][1:] #removing the 1st value of each atmosphere

        atm_result = np.zeros([int((h2o_high-abs(h2o_low))*int(1/h2o_step))+1,int(1+(abs(t_low)+t_high)*int(1/t_step))])  #Legt die Größe des Ergebnis-Arrays fest
        result_string_head = ["Temperature;RH;IWV;flxd"] #Creating header of the resulting .csv-file
        Tsfc = []
        H2O_result = []

        # for temp in np.arange(t_low,t_high+1e-9,t_step):    #iterating over temperature corrections
        elements_cl = Parallel(n_jobs=-1, verbose=5)(delayed(start_calculations)(fascod_atm_raw,temp,h2o_low,h2o_high,h2o_step) for temp in np.arange(t_low,t_high+1e-9,t_step))

        result_string = result_string_head + sum(elements_cl,[])

        with open(write_file+fas_atm+"_dependent.csv","w") as f:
            for line in result_string:
                f.write(line + "\n")

        f.close()