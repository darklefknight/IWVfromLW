from netCDF4 import Dataset
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdate
from joblib import Parallel, delayed
from datetime import datetime as dt
from read_iwv_aeronet import get_iwv_from_aeronet,searchGoodDate,getIWVAtDate
from download_bsrn import download_bsrn
import sys
import os
import shutil
from functools import lru_cache
import locale
locale.setlocale(locale.LC_ALL, 'de_DE')
import socket


def getValueAtDate(date, array):
    return_list = []
    for line in array:
        delta = line[0] - date
        # print(delta)
        # print(line[0])
        # print(date)
        # print("")
        if delta.days == 0:
            # print("Delta.days == 0")
            if abs(delta.seconds) <=60 :
                return_list.append(line)
                # print(delta)
                continue

    return_array = np.asarray(return_list)
    return return_array


def getIWVFromTable(date, temp, flx, atm_name, atm):
    # print(atm_name + "Date: " + date.strftime("%x") + ", Temp: " + str(temp) + ", FLX:" + str(flx) + "...")
    temp_indices = np.where(abs(atm['Temperature'] - 273.15 - temp) < 0.7)

    temp_run = atm[temp_indices]

    distance = 10
    flx_run = temp_run[np.where(abs(temp_run['flxd'] - flx) < distance)]

    flx_cl = -777
    iwv_cl = -777
    temp_cl = -777
    for i, element in enumerate(flx_run):
        if (abs(element[3] - flx) < distance):
            flx_cl = element[3]
            iwv_cl = element[2]
            temp_cl = element[0]
            distance = abs(element[3] - flx)

    if iwv_cl == -777:
        temp_cl = temp
        flx_cl = flx

    return (date, temp_cl, flx_cl, iwv_cl, distance)


def getAtm(atm_name):
    if socket.gethostname() == "thunder7":
        PATH = "/scratch/uni/u237/users/tmachnitzki/psrad/python_svn/wv_tables/"
    else:
        PATH = "/Users/u300844/t7home/tmachnitzki/psrad/python_svn/wv_tables/"

    # FILE = atm_name + "_dependent.csv"
    FILE = atm_name + "_dependent_sadata.csv"


    with open(PATH + FILE, "rb") as f:
        atm = np.genfromtxt(f,
                            dtype=None,
                            names=True,
                            delimiter=";"
                            )
    return atm


@lru_cache(maxsize=256)
def BSRN2IWV(datestr,station,tag,station_height,atm_name,verbose):
    line_counter = 0

    aeronet = get_iwv_from_aeronet(aeronetPath=aeronetPath, station=station,verbose=verbose)
    aeronet_at_date = getIWVAtDate(datestr,aeronet)
    # aeronet_good_dates = searchGoodDate(aeronet_at_date)
    aeronet_good_dates = aeronet_at_date
    if len(aeronet_good_dates) == 0:
        if verbose >= 3:
            print("No good dates found in AERONET for this month.")
            print("--------------------------------------------------")
        return None

    BSRN_FILE_NAME = tag + "_radiation_" + datestr[:4] + "-" + datestr[4:6] + ".tab"
    FILE = BSRN_FILE_PATH + station + "/" + BSRN_FILE_NAME

    if verbose >= 2:
        print(station + ", " + tag + ", " + atm_name + ", " + datestr)

    bsrn_raw = download_bsrn(tag,datestr,verbose)
    if np.all(bsrn_raw) == None:
        if verbose >= 3:
            print("No data in BSRN to continue")
            print("--------------------------------------------------")
        return None

    atm = getAtm(atm_name)  # reads the _dependent.csv file

    #prepare File for writing out data:

    result_path = "results/"+station+"_sadata/"+atm_name+"/"
    # result_path = "results/" + station + "/" + atm_name + "/"

    write_file = result_path + station + datestr[0:6] + ".csv"
    with open(write_file,"w") as f:
        f.write("#Calculated and measured integrated watervapor for %s.\n" %station)
        f.write("#Used atmosphere: %s\n"%atm_name)
        f.write("\n")
        f.write("Date ; Time ; T[K] ; LWdown[W/m2] ; Calculated_IWV[kg/m2] ; aeronet_IWV[kg/m2] ; Distance\n")

        for good_date in aeronet_good_dates:
            # print(good_date)
            good_str = good_date
            # print(good_date)

            bsrn = getValueAtDate(good_date[0], bsrn_raw)
            # print(bsrn)
            # elements_cl = Parallel(n_jobs=2, verbose=0)(delayed(getIWVFromTable)(bsrn[i,0],bsrn[i,1],bsrn[i,2], atm_name,atm) for i in range(0,len(bsrn[:]),1))
            elements_cl = [getIWVFromTable(bsrn[i,0],bsrn[i,1],bsrn[i,2], atm_name,atm) for i in range(0,len(bsrn[:]),1)]

            date_cl = []
            for element in elements_cl:
                    date_cl.append(element[0])
            dates = np.asarray(date_cl)

            array = np.array([x for x in elements_cl],dtype=([("date", "S20"), ("T", "f8"), ("LW", "f8"), ("iwv", "f8"),("distance","f8")]))

            IWV = {}
            IWV['date'] = dates
            IWV["T"] = array['T']
            IWV["LW"] = array['LW']
            IWV["IWV"] = np.multiply(array["iwv"],height_correction(station_height))
            # IWV["IWV"] = array["iwv"]
            IWV["distance"] = array["distance"]
            IWV["IWV_AERONET"] =good_date[1] * 10

            if len(IWV['IWV']) == 0:
                if verbose >= 1:
                    print('weird mistake.')
                continue

            if IWV['IWV'][0] > -20:
                if 0 < IWV['date'][0].hour <24:
                    line_counter += 1
                    f.write(
                        IWV['date'][0].strftime("%x") + " ; " +
                        IWV['date'][0].strftime("%X") + " ; " +
                        str(IWV['T'][0]) + " ; " +
                        str(IWV['LW'][0]) + " ; " +
                        str(IWV['IWV'][0]) + " ; " +
                        str(IWV['IWV_AERONET']) + " ; " +
                        str(IWV['distance'][0]) +
                        "\n")

    if line_counter == 0:
        os.remove(write_file)
        if verbose >= 3:
            print("No valid Data written for this month")
    if verbose >= 2:
        print("----------------------------------------------------")

def height_correction(height):
    """

    :param height: height in meters
    :return: correction for IWV

    Assuming that most watervapor is located in the lower 2km a correction has to be made for the station-height.
    If the station-height ist 1km for example this needs to be taken into account when calculating the IWV for the
    colmn of air above it.

    Assumption: 97% of all the wator vapor is in the lower 2km
    """
    ASSUMTPION = 0.97

    if height <= 0:
        return 1

    elif height < 2000:
        correction = 1 - (height/2000 * ASSUMTPION) #linear height correction
        return correction

    else:
        return (1-ASSUMTPION)



def startIWV(y_in,m_in,station,tag,height,atm,skip,verbose):

    if m_in<12:
        year_str = str(y_in)
        datestr = year_str + str(m_in + 1).zfill(2)

    else:
        year_str = str(y_in + int(np.mod(m_in,skip)))
        datestr = year_str + str(np.mod(m_in ,12) +1 ).zfill(2)

    if verbose >= 2:
        print(datestr)

    BSRN2IWV(datestr=datestr, station=station, tag=tag, station_height=height, atm_name=atm,verbose=verbose)



if __name__ == "__main__":
    #for local:
    # BSRN_FILE_PATH = "/Users/u300844/t7home/tmachnitzki/psrad/BSRN/"
    # aeronetPath = "/Users/u300844/t7home/tmachnitzki/psrad/aeronet_inversion/INV/DUBOV/ALL_POINTS/"

    #for thunder:
    BSRN_FILE_PATH = "/scratch/uni/u237/users/tmachnitzki/psrad/BSRN/"
    aeronetPath = "/scratch/uni/u237/users/tmachnitzki/psrad/aeronet_inversion/INV/DUBOV/ALL_POINTS/"

    atms= ['US-standard','subtropic-winter','subtropic-summer','midlatitude-summer', 'midlatitude-winter', 'subarctic-summer', 'subarctic-winter', 'tropical']
    # atms = ['midlatitude-winter']


    # station = "Barrow"
    # tag = "bar"
    # atm = "subarctic-summer"

    # station = "SEDE_BOKER"
    # tag = "sbo"
    # atm = "tropical"

    # station = "Cart_Site"
    # tag = "e13"
    # atm = "midlatitude-winter"

    # station = "Cabauw"
    # tag = "cab"

    # station = "Gobabeb"
    # tag = "gob"

    # station = "Sao_Martinho_SONDA"
    # tag = "sms"

    stations = ["Barrow","SEDE_BOKER","Cart_Site","Cabauw","Gobabeb","Tiksi","Toravere","Darwin","Fukuoka"]

    tags = ["bar", "sbo","e13","cab","gob","tik","tor","dar","fua"]
    heights = [8,500,318,0,407,48,70,30,3]

    # stations = ["Cart_Site"]
    # tags = ["e13"]
    # heigts = [318]
    # atms = ['subtropic-winter']

    RERUN = True #set TRUE if you want to delete old results and rerun everything. Else just new stations will be calculated
    verbose = 0 #between 0 and 4

    speed_up = 17 # 1 and 4

    for station, tag, height in zip(stations,tags,heights):
        for atm in atms:
            result_path = "results/" + station + "_sadata/" + atm + "/"
            # result_path = "results/" + station + "/" + atm + "/"
            if RERUN:
                if os.path.isdir(result_path):
                    shutil.rmtree(result_path) # delete old results first
                    os.makedirs(result_path)
                else:
                    os.makedirs(result_path)
            else:
                if os.path.isdir(result_path):
                    continue
                else:
                    os.makedirs(result_path)
            if verbose >=1:
                print(station, atm)
            for y in range(2000,2017,speed_up):
                Parallel(n_jobs=1,verbose=5)(delayed(startIWV)(y,m,station,tag,height,atm,speed_up,verbose) for m in range(0,12*speed_up,1))


    # TODO: interpolate between winter and summer atmosphere depending on season?