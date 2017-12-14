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
try:
    import psrad
except:
    print("PSRAD NOT LOADED")
from wv_converter import VMR2RH, RH2VMR
from joblib import Parallel,delayed
from scipy.interpolate import interp1d
import socket

def get_sadata_atmosphere(season):
    from getH2OforSADATA import getCO2values

    if socket.gethostname() == "apple262.cen.uni-hamburg.de":
        path0 = "/Users/u300844/t7home/tmachnitzki/"
    else:
        path0 = "/scratch/uni/u237/users/tmachnitzki/"

    sadata_file = path0+"psrad/python_svn/sadata.d"
    columns = ['z','p','t','RHO','H2O','O3','N2O','CO','CH4'] # without CO2
    atmosphere = {}

    for name in columns:
        atmosphere[name] = []

    startline = {
        "tropical": 7,
        'midlatitude-summer': 87,
        'midlatitude-winter': 167,
        'subarctic-summer': 247,
        'subarctic-winter': 327,
        "US-standard" : 407,
        "subtropic-summer": 487,
        "subtropic-winter": 567
    }

    with open(sadata_file,"rb") as f:
        for i in range(startline[season]-1):
            f.readline()

        for i in range(59):
            line = f.readline().split()
            for i,name in enumerate(columns):
                atmosphere[name].append(float(line[i].decode()))

    for key in atmosphere.keys():
        atmosphere[key] = np.asarray(atmosphere[key])


    # corrections:
    atmosphere["z"] *= 1000 #km -> m
    atmosphere["p"] *= 100 #hpa -> pa
    atmosphere["H2O"] *= 1e-6 #_->ppmv
    atmosphere["O3"] *= 1e-6 #_->ppmv
    atmosphere["N2O"] *= 1e-6  # _->ppmv
    atmosphere["CO"] *= 1e-6  # _->ppmv
    atmosphere["CH4"] *= 1e-6  # _->ppmv

    del atmosphere['RHO']

    if np.logical_or(np.logical_or((season == "subtropic-summer"), (season == "subtropic-winter")),season == "US-standard"):
        with open(path0+"psrad/python_svn/midlatitude_winter_CO2.txt", "rb") as f:
            CO2_file = np.genfromtxt(f,dtype=None)
        atmosphere["CO2"] = CO2_file
    else:
        fas_atm = get_fascod_atmosphere("/scratch/uni/u237/users/tlang/arts-xml-data/planets/Earth/Fascod/",
                                        season=season)
        # print(atmosphere)
        values = getCO2values(fas_atm, atmosphere)
        atmosphere['CO2'] = np.asarray(values)

    for key in atmosphere.keys():
        atmosphere[key] = np.asarray(atmosphere[key])

    return atmosphere


def moreLowerLevelsForAtm(atm,h2o,method='linear'):
    """
    NOT USED!!!!
    :param atm:
    :param h2o:
    :param method:
    :return:
    """
    for key in atm.keys():
        curKey = atm[key][0:4] # between 0 and 3 km

        if key == "H2O":
            continue

        elif key == "z":
            newKey = np.arange(0,3001,250)

        else:
            x = [i for i in range(len(curKey))]
            y = curKey
            f = interp1d(x, y)
            xnew = np.linspace(x[0],x[-1],13)
            newKey = f(xnew)

        atm[key] = np.append(newKey,atm[key][4:])

    # H2O  needs to be fitted last:
    curKey = VMR2RH(atm['H2O'][0:4], atm['p'][0:4], atm['t'][0:4])  #TODO Here is something wrong! h2o is shorter then p and t
    low = np.log(h2o)
    up = np.log(curKey[-1])
    h2onew = np.exp(np.linspace(low, up, 13))
    newKey = RH2VMR(h2onew, atm['p'][0:4],atm['t'][0:4])
    atm['H2O'] = np.append(newKey,atm['H2O'][4:])
    return atm






def get_fascod_atmosphere(fascod_path, season,del0=True):
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

    if del0:
        for key in atmosphere.keys():
            atmosphere[key] = atmosphere[key][1:] #removing the 1st value of each atmosphere

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
    fascod_atm_rh_raw = VMR2RH(fascod_atm_raw["H2O"],fascod_atm_raw["p"],fascod_atm_raw["t"])
    fascod_atm['t'] = np.add(fascod_atm['t'],
                             temp)  # adding the temperature change to the original temperature (moving the temperature profile to the right/left in a skew-t diagram)
    return_string = []
    for h2o in np.arange(h2o_low, h2o_high + 1e-9, h2o_step):  # iterating over relative humidity corrections

        # fascod_atm['H2O'] = RH2VMR(h2o, fascod_atm['p'], fascod_atm['t'])  #change relative humidity in all hights to be the same
        fascod_atm['H2O'][0:3] = RH2VMR(h2o, fascod_atm['p'][0:3],
                                        fascod_atm['t'][0:3])  # change relative humidity in all lower hights to be the same fixed value
        fascod_atm["H2O"][3:] = RH2VMR(fascod_atm_rh_raw[3:],fascod_atm["p"][3:],fascod_atm["t"][3:])

        # next line makes results worse:
        # fascod_atm['H2O'][3:8] = RH2VMR(fascod_RH[3:8],fascod_atm['p'][3:8],fascod_atm['t'][3:8]) #change relative humidity in all upper hights to stay relative the same with changing temperature

        result_temp, H2O, T = calc_hr(fascod_atm, 'lw')  # <------------- PSRAD calculation. T = surface temperature

        if LIMIT_HEIGHT:
            RH = VMR2RH(H2O[:12], fascod_atm['p'][:12], fascod_atm['t'][:12])  # Relative Humidity in all hights
            H2O_integrated = tp.atmosphere.iwv(H2O[:12], fascod_atm['p'][:12], fascod_atm['t'][:12],
                                               fascod_atm['z'][:12])  # integrated water vapor #TODO: make h2o not linear but log when integrating

        else:
            RH = VMR2RH(H2O, fascod_atm['p'], fascod_atm['t'])
            H2O_integrated = tp.atmosphere.iwv(H2O, fascod_atm['p'], fascod_atm['t'], fascod_atm['z'])

        return_string_line = str(T) + ";" + str(h2o) + ";" + str(H2O_integrated) + ";" + str(result_temp['flxd_clr'][0])
        return_string.append(return_string_line)

    return return_string



# ======================================================================================================================

if __name__ == '__main__':
    write_file = '/scratch/uni/u237/users/tmachnitzki/psrad/python_svn/wv_tables/'
    # atm_names =  sorted((os.listdir('/scratch/uni/u237/users/tlang/arts-xml-data/planets/Earth/Fascod') ))
    # del atm_names[atm_names.index('README')]

    atm_names= ['US-standard','subtropic-winter','subtropic-summer','midlatitude-summer', 'midlatitude-winter', 'subarctic-summer', 'subarctic-winter', 'tropical']
    
    LIMIT_HEIGHT = False  #if True: iwv just up to 12 Km. Else up to 95 Km
    Rw = tp.atmosphere.constants.gas_constant_water_vapor #Gaskonstante von Wasserdampf

    t_low =  -50  #Darf nicht größer 0 sein
    t_high = 60
    t_step = 0.1
    
    h2o_low = 0.001 #should not be 0
    h2o_high = 1
    h2o_step = 0.001
    
    #for testing:
    # atm_names = ['midlatitude-summer']  #<-- Das hier auskommentieren um alle Atmosphären zu berechnen

    for fas_atm in atm_names:   #iterating over all fascod-atmospheres

        # fascod_atm_raw = get_fascod_atmosphere("/scratch/uni/u237/users/tlang/arts-xml-data/planets/Earth/Fascod/",season=fas_atm)

        fascod_atm_raw = get_sadata_atmosphere(season=fas_atm)
        print('Now calculating: ',fas_atm)
        temp_counter = 0



        fascod_RH = VMR2RH(fascod_atm_raw['H2O'],fascod_atm_raw['p'],fascod_atm_raw['t'])

        atm_result = np.zeros([int((h2o_high-abs(h2o_low))*int(1/h2o_step))+1,int(1+(abs(t_low)+t_high)*int(1/t_step))])  #Legt die Größe des Ergebnis-Arrays fest
        result_string_head = ["Temperature;RH;IWV;flxd"] #Creating header of the resulting .csv-file
        Tsfc = []
        H2O_result = []

        # for temp in np.arange(t_low,t_high+1e-9,t_step):    #iterating over temperature corrections
        elements_cl = Parallel(n_jobs=10, verbose=5)(delayed(start_calculations)(fascod_atm_raw,temp,h2o_low,h2o_high,h2o_step,LIMIT_HEIGHT) for temp in np.arange(t_low,t_high+1e-9,t_step))

        result_string = result_string_head + sum(elements_cl,[])

        with open(write_file+fas_atm+"_dependent_sadata.csv","w") as f:
            for line in result_string:
                f.write(line + "\n")

        f.close()