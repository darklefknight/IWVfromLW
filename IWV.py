from BSRN2IWV import getValueAtDate, getIWVFromTable, height_correction, download_bsrn, getAtm
import numpy as np
from functools import lru_cache
import os
import ftplib
import urllib
from joblib import delayed, Parallel
import shutil
import socket

# ----------------------------------------------------------------------------------------------------------------------

def getGoodDates(bsrn_file):
    date = []
    lw = []
    temp = []
    sw = []
    dif = []
    for line in bsrn_file:
        if np.logical_and(line[4] > 20, line[3] < 1): #direct radiation > 20W/m2 and diffuse < 1 W/m2
            date.append(line[0])
            lw.append(line[1])
            temp.append(line[2])
            sw.append(line[3])
            dif.append(line[4])

    date = np.asarray(date)
    lw = np.asarray(lw)
    sw = np.asarray(sw)
    dif = np.asarray(dif)
    temp = np.asarray(temp)
    array = np.stack((date, lw, temp, sw, dif), axis=1)
    # print("got good dates")
    return array

# ----------------------------------------------------------------------------------------------------------------------

def BSRN2IWV(datestr, station, tag, station_height, atm, atm_name, verbose):
    line_counter = 0

    # aeronet = get_iwv_from_aeronet(aeronetPath=aeronetPath, station=station,verbose=verbose)
    # aeronet_at_date = getIWVAtDate(datestr,aeronet)
    # # aeronet_good_dates = searchGoodDate(aeronet_at_date)
    # aeronet_good_dates = aeronet_at_date
    # if len(aeronet_good_dates) == 0:
    #     if verbose >= 3:
    #         print("No good dates found in AERONET for this month.")
    #         print("--------------------------------------------------")
    #     return None



    BSRN_FILE_NAME = tag + "_radiation_" + datestr[:4] + "-" + datestr[4:6] + ".tab"
    FILE = BSRN_FILE_PATH + station + "/" + BSRN_FILE_NAME

    if verbose >= 2:
        print(station + ", " + tag + ", " + atm_name + ", " + datestr)

    bsrn_raw = download_bsrn(tag, datestr, verbose, verify=False)
    if np.all(bsrn_raw) == None:
        if verbose >= 3:
            print("No data in BSRN to continue")
            print("--------------------------------------------------")
        return None

    good_dates = getGoodDates(bsrn_raw)

    # prepare File for writing out data:

    result_path = "/scratch/uni/u237/users/tmachnitzki/psrad/python_svn/" + "results_BSRN/" + station + "/" + atm_name + "/"
    if not os.path.isdir(result_path):
        os.mkdir(result_path)

    write_file = result_path + station + datestr[0:6] + ".csv"
    with open(write_file, "w") as f:
        f.write("#Calculated and measured integrated watervapor for %s.\n" % station)
        f.write("#Used atmosphere: %s\n" % atm_name)
        f.write("\n")
        f.write("Date ; Time ; T[K] ; LWdown[W/m2] ; Calculated_IWV[kg/m2] ; Distance\n")

        for good_date in good_dates:

            good_str = good_date
            # print(good_date)

            bsrn = getValueAtDate(good_date[0], bsrn_raw)
            # print(bsrn)
            # elements_cl = Parallel(n_jobs=2, verbose=0)(delayed(getIWVFromTable)(bsrn[i,0],bsrn[i,1],bsrn[i,2], atm_name,atm) for i in range(0,len(bsrn[:]),1))
            elements_cl = [getIWVFromTable(bsrn[i, 0], bsrn[i, 1], bsrn[i, 2], atm_name, atm) for i in
                           range(0, len(bsrn[:]), 1)]

            date_cl = []
            for element in elements_cl:
                date_cl.append(element[0])
            dates = np.asarray(date_cl)

            array = np.array([x for x in elements_cl],
                             dtype=([("date", "S20"), ("T", "f8"), ("LW", "f8"), ("iwv", "f8"), ("distance", "f8")]))

            IWV = {}
            IWV['date'] = dates
            IWV["T"] = array['T']
            IWV["LW"] = array['LW']
            IWV["IWV"] = np.multiply(array["iwv"], height_correction(station_height))
            # IWV["IWV"] = array["iwv"]
            IWV["distance"] = array["distance"]
            IWV["IWV_AERONET"] = good_date[1] * 10

            if len(IWV['IWV']) == 0:
                if verbose >= 1:
                    print('weird mistake.')
                continue

            if IWV['IWV'][0] > -20:
                if 0 < IWV['date'][0].hour < 24:
                    line_counter += 1
                    f.write(
                        IWV['date'][0].strftime("%x") + " ; " +
                        IWV['date'][0].strftime("%X") + " ; " +
                        str(IWV['T'][0]) + " ; " +
                        str(IWV['LW'][0]) + " ; " +
                        str(IWV['IWV'][0]) + " ; " +
                        # str(IWV['IWV_AERONET']) + " ; " +
                        str(IWV['distance'][0]) +
                        "\n")

    if line_counter == 0:
        try:
            os.remove(write_file)
            if verbose >= 3:
                print("No valid Data written for this month")
        except:
            print("File %s not found for removal" %write_file)
    if verbose >= 2:
        print("----------------------------------------------------")

# ----------------------------------------------------------------------------------------------------------------------

def by_size(words, size):
    return [word for word in words if len(word) == size]

# ----------------------------------------------------------------------------------------------------------------------

def getBSRNstats():
    with open("BSRN_stations.csv", "rb") as f:
        BSRN_file = np.genfromtxt(f,
                                  names=True,
                                  delimiter=";",
                                  dtype="S30,S3,f4,f4,f4"
                                  )
    return BSRN_file

# ----------------------------------------------------------------------------------------------------------------------

def startIWV(y_in,m_in,station,tag,height,atm_name,atm,skip,verbose):

    if m_in<12:
        year_str = str(y_in)
        datestr = year_str + str(m_in + 1).zfill(2)

    else:
        year_str = str(y_in + int(np.mod(m_in,skip)))
        datestr = year_str + str(np.mod(m_in ,12) +1 ).zfill(2)

    if verbose >= 2:
        print(datestr)

    BSRN2IWV(datestr=datestr, station=station, tag=tag, station_height=height, atm=atm, atm_name=atm_name, verbose=verbose)

# ----------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    if socket.gethostname() == "thunder7":
        BSRN_FILE_PATH = "/scratch/uni/u237/users/tmachnitzki/psrad/BSRN/"
        home =  "/scratch/uni/u237/users/tmachnitzki/psrad/python_svn/"
    else:
        BSRN_FILE_PATH = "/Users/u300844/t7home/tmachnitzki/psrad/BSRN/"
        home = "/Users/u300844/t7home/tmachnitzki/psrad/python_svn/"

    datestr = "20150101"
    atms = ["midlatitude-winter"]
    stats = getBSRNstats()
    tags,stations,heights = [],[],[]
    for line in stats:
        tags.append(line[1].decode().lower())
        stations.append(line[0].decode())
        heights.append(line[-1])

    RERUN = True  # set TRUE if you want to delete old results and rerun everything. Else just new stations will be calculated
    verbose = 0  # between 0 and 4

    speed_up = 10

    atm_name = atms[0]
    atm = getAtm(atm_name)
    for station, tag, height in zip(stations, tags, heights):
        print(station)
        for atm_name in atms:
            result_path = home + "results_BSRN/" + station + "/" + atm_name + "/"

            if RERUN:
                if os.path.isdir(result_path):
                    shutil.rmtree(result_path)  # delete old results first
                    os.makedirs(result_path)
                else:
                    os.makedirs(result_path)
            else:
                if os.path.isdir(result_path):
                    continue
                else:
                    os.makedirs(result_path)
            if verbose >= 1:
                print(station, atm_name)
            for y in range(2015, 2017, speed_up):
                Parallel(n_jobs=-1, verbose=5)(delayed(startIWV)(y, m, station, tag, height, atm_name, atm, speed_up, verbose) for m in range(0, 12 * speed_up, 1))
                # [startIWV(y, m, station, tag, height, atm_name, atm, speed_up, verbose) for m in range(0, 12 * speed_up, 1)]

