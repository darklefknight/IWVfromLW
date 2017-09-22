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

def calc_hr(soundings, spec_range,T_Correction, H2O_Correction=0, const_albedo=0.05, zenith_angle=53):
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
    


    
    for i in range(len(T)):
        T[i] += T_Correction
    for i in range(len(H2O)):
        H2O[i] += H2O_Correction
#    print(T[0],P[0],H2O[0])
#    RH = (ppm2e(H2O[0],P[0])) / es(T[0]) *100
#    print(RH)
    
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

    return data,H2O,T_sfc

def ppm2e(ppm,P):
    """
    Convertes Watervapor measured in ppm to Watervaporpressure.
    P in Pa!
    """
    R = 8.314510 #J/mol*k
    Rw = 461.5 #J/kg*k
    M = 18.02*1e-3 #kg/mol
        
    e = ppm * (Rw/R) * M * P * (1e-6)
    return e

def es(T):
    """
    T in Kelvin!!
    """
    T = np.add(T,-273.15)
    power = np.multiply(17.1,np.divide(T,np.add(T,235)))
    return np.multiply(610.78,np.exp(power))

def e2ppm(e,P):
    R = 8.314510 #J/mol*k
    Rw = 461.5 #J/kg*k
    M = 18.02*1e-3 #kg/mol
   
    ppm = e/(M*P) * (R/Rw) * 1e6
    return ppm

def e2RH(e,es):
    RH = e/es
    return RH

def RH2e(RH,es):
    e = RH*es
    return e

def RH2Td(T,RH):
    '''
    Calculates the Dewpointtemperature from a given Temperature T and Relative Humidity RH
    #z_e = water vapor pressure
    #z_es = saturation water vapor pressure
    #T = temperature
    #tempd = dewpoint temperature
    #RH = relative Humidity '''

    z_es = 610.78*np.exp(17.08085*(T)/(235+(T)))
    z_e = RH*z_es/100
    tempd = (235*np.log(z_e/610.5))/(17.1-np.log(z_e/610.78))
    return tempd

if __name__ == '__main__':
    write_file = '/scratch/uni/u237/users/tmachnitzki/psrad/python_scripts/wv_tables/'
    atm_names =  sorted((os.listdir('/scratch/uni/u237/users/tlang/arts-xml-data/planets/Earth/Fascod') ))
    del atm_names[atm_names.index('README')]

    t_low =  -10  #Darf nicht größer 0 sein
    t_high = 10    
    
    #for testing:
    atm_names = ['midlatitude-summer']  #<-- Das hier auskommentieren um alle Atmosphären zu berechnen

    for fas_atm in atm_names:
        fascod_atm = get_fascod_atmosphere("/scratch/uni/u237/users/tlang/arts-xml-data/planets/Earth/Fascod/",season=fas_atm)
        print('Now calculating: ',fas_atm)
        counter = 0

        with open(write_file+fas_atm+'.csv','w') as f:
            f.write(';')    #Die linke obere Ecke der Tabelle soll frei bleiben

            for temp in np.linspace(t_low,t_high,21): # +1 damit 213.25 noch included ist
#                print(temp)
                flx_result = []
                H2O_result = []
                for h2o in np.linspace(0.6,0.9,31): #linspace(0,0,20) ist erst einmal nur zu Testzwecken (Er soll 20 mal nichts verändern)    
                    fascod_atm['H2O'] = e2ppm(RH2e(h2o,es(fascod_atm['t'])),fascod_atm['p']) * 1e-6
#                    print(fascod_atm['H2O'][0])
                    result_temp,H2O,T = calc_hr(fascod_atm,'lw',T_Correction=temp,H2O_Correction=0)
                    RH = ppm2e(H2O[0],fascod_atm['p'][0])/es(T)
#                    print(RH)
                    # Integrieren des Wasserdampfes über die gesamte Luftsäule:
                    H2O_integrated_sum = []
                    for i in range(len(H2O)-1):
                        H2O_integrated_sum.append((H2O[i]+H2O[i-1]) /2) 
                    H2O_integrated = np.sum(H2O_integrated_sum) / len(H2O_integrated_sum)
#                    if counter < 40:
                    H2O_result.append(H2O_integrated) 
                    flx_result.append(result_temp['flxd_clr'][0])   #Hier wird einfach der Bodenfluss an die Liste dranngehängt
#                    print(T)
                    
                    counter += 1
                    fascod_atm = get_fascod_atmosphere("/scratch/uni/u237/users/tlang/arts-xml-data/planets/Earth/Fascod/",season=fas_atm)
                    
                if counter < 40:    #22 ist willkürlich gewählt, es muss nur kleiner als die Länge der Watervapor-Schleife +1 sein 
#                    for wv in H2O_result:
#                        f.write('%s;' % wv)
#                    for wv in np.linspace(60,90,31):
#                        f.write('%s;' % wv)
                    for wv in H2O_result:
                        f.write('%s;' % wv)
                    
                    f.write('\n')                    
                f.write('%s;' % (T-273.15))
#                print(T)
                for result in flx_result:
                    f.write('%s;' %result)
                f.write('\n')
#                result_lw['SFC_TEMP'][temp+abs(t_low)] = T
        f.close()



    



            

