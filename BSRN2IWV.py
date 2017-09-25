from netCDF4 import Dataset
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdate
from joblib import Parallel, delayed
from datetime import datetime as dt
from read_iwv_aeronet import get_iwv_from_aeronet,searchGoodDate,getIWVAtDate
from download_bsrn import download_bsrn
import sys

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
    PATH = "/Users/u300844/t7home/tmachnitzki/psrad/python_svn/wv_tables/"
    FILE = atm_name + "_dependent.csv"

    with open(PATH + FILE, "rb") as f:
        atm = np.genfromtxt(f,
                            dtype=None,
                            names=True,
                            delimiter=";"
                            )
    return atm


def BSRN2IWV(datestr,station,tag,atm_name):

    aeronet = get_iwv_from_aeronet(aeronetPath=aeronetPath, station=station)
    aeronet_at_date = getIWVAtDate(datestr,aeronet)
    # aeronet_good_dates = searchGoodDate(aeronet_at_date)
    aeronet_good_dates = aeronet_at_date
    if len(aeronet_good_dates) == 0:
        print("No good dates found in aeronet for this month in aeronet.")
        print("--------------------------------------------------")
        return None

    BSRN_FILE_NAME = tag + "_radiation_" + datestr[:4] + "-" + datestr[4:6] + ".tab"
    FILE = BSRN_FILE_PATH + station + "/" + BSRN_FILE_NAME

    print(station + ", " + tag + ", " + atm_name + ", " + datestr)

    bsrn_raw = download_bsrn(tag,datestr)
    if bsrn_raw == None:
        print("No data to continue")
        print("--------------------------------------------------")
        return None

    atm = getAtm(atm_name)  # reads the _dependent.csv file

    #prepare File for writing out data:
    with open("results/" + station + datestr[0:6] + ".csv","w") as f:
        f.write("#Calculated and measured integrated watervapor for %s.\n" %station)
        f.write("#Used atmosphere: %s\n"%atm_name)
        f.write("\n")
        f.write("Date ; Time ; T[K] ; LWdown[W/m2] ; Calculated_IWV[kg/m2] ; aeronet_IWV[kg/m2]\n")

        for good_date in aeronet_good_dates:

            good_str = good_date
            # print(good_date)

            bsrn = getValueAtDate(good_date[0], bsrn_raw)
            # print(bsrn)
            elements_cl = Parallel(n_jobs=1, verbose=0)(delayed(getIWVFromTable)(bsrn[i,0],bsrn[i,1],bsrn[i,2], atm_name,atm) for i in range(0,len(bsrn[:]),1))

            date_cl = []
            for element in elements_cl:
                    date_cl.append(element[0])
            dates = np.asarray(date_cl)

            array = np.array([x for x in elements_cl],dtype=([("date", "S20"), ("T", "f8"), ("LW", "f8"), ("iwv", "f8"),("distance","f8")]))

            IWV = {}
            IWV['date'] = dates
            IWV["T"] = array['T']
            IWV["LW"] = array['LW']
            IWV["IWV"] = array["iwv"]
            IWV["distance"] = array["distance"]
            IWV["IWV_AERONET"] =good_date[1] * 10

            if IWV['IWV'][0] != -777:
                if 10 < IWV['date'][0].hour < 18:
                    f.write(
                        IWV['date'][0].strftime("%x") + " ; " +
                        IWV['date'][0].strftime("%X") + " ; " +
                        str(IWV['T'][0]) + " ; " +
                        str(IWV['LW'][0]) + " ; " +
                        str(IWV['IWV'][0]) + " ; " +
                        str(IWV['IWV_AERONET']) + "\n")

    print("----------------------------------------------------")


if __name__ == "__main__":
    BSRN_FILE_PATH = "/Users/u300844/t7home/tmachnitzki/psrad/BSRN/"
    aeronetPath = "/Users/u300844/t7home/tmachnitzki/psrad/aeronet_inversion/INV/DUBOV/ALL_POINTS/"
    atms = ['midlatitude-summer', 'midlatitude-winter', 'subarctic-summer', 'subarctic-winter', 'tropical']

    for y in range(2000,2017,1):
        year_str = str(y)

        # station = "Barrow"
        # tag = "bar"

        station = "SEDE_BOKER"
        tag = "sbo"

        atm = "tropical"

        for m in range(0,12,1):
            datestr = year_str + str(m+1).zfill(2)
            print(datestr)
            BSRN2IWV(datestr=datestr,station=station,tag=tag,atm_name=atm)




