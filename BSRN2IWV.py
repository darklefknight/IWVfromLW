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


def getBSRNData(file):
    print("Get data from %s..." % file)

    g=open(file,"rb")
    lines = g.readlines()
    liste = []
    for line in lines:
        liste.append(line.decode())
    g.close()

    #Removing the header:
    for i,line in enumerate(liste):
        if "*/" in line:
            break

    liste = liste[i+1:]
    splitted = liste[0].split("\t")
    for key in splitted: print(key)
    date_index = splitted.index('Date/Time')
    T_index = splitted.index('T2 [°C]')
    LW_index = splitted.index('LWD [W/m**2]')

    T = []
    LW = []
    date = []
    data_list =[]
    for i,element in enumerate(liste[1:]):
        splitted = element.split("\t")
        date_line = splitted[date_index]
        T_line = splitted[T_index]
        LW_line = splitted[LW_index]
        line_year = int(date_line[:4])
        line_month = int(date_line[5:7])
        line_day = int(date_line[8:10])
        line_hour = int(date_line[-5:-3])
        line_min = int(date_line[-2:])
        date_line_date = dt(line_year,line_month,line_day,line_hour,line_min)

        date.append(date_line_date)

        if T_line != "":
            T.append(float(T_line))
        else:
            T.append(np.nan)

        if LW_line != "":
            LW.append(float(LW_line))
        else:
            LW.append(np.nan)

        data_list.append((T[i],LW[i]))

    array = np.array([x for x in data_list],dtype=([("T","f8"),("LW","f8")]))
    date = np.asarray(date)
    result_array = np.stack((date,array['T'],array['LW']),axis=1)
    return result_array


def BSRN2IWV(datestr,station,tag,atm_name):

    aeronet = get_iwv_from_aeronet(aeronetPath=aeronetPath, station=station)
    aeronet_at_date = getIWVAtDate(datestr,aeronet)
    # aeronet_good_dates = searchGoodDate(aeronet_at_date)
    aeronet_good_dates = aeronet_at_date
    if len(aeronet_good_dates) == 0:
        print("No good dates found in aeronet for this month")
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

    #TODO: Filtern von -777 values
    #TODO: Filtern von Werten bei nacht



