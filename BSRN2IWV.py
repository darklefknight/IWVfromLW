from netCDF4 import Dataset
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdate
from joblib import Parallel, delayed
from datetime import datetime as dt
from read_iwv_aeronet import get_iwv_from_aeronet

def getValueAtDate(datestr, array):
    return_list = []
    for line in array:
        if line[0].strftime("%Y%m%d") == datestr:
            return_list.append(line)
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


if __name__ == "__main__":
    BSRN_FILE_PATH = "/Users/u300844/t7home/tmachnitzki/psrad/BSRN/"
    atms = ['midlatitude-summer', 'midlatitude-winter', 'subarctic-summer', 'subarctic-winter', 'tropical']

    datestr = "20070610"
    station = "Barrow"
    tag = "BAR"
    atm_name = atms[3]

    BSRN_FILE_NAME = tag + "_radiation_" + datestr[:4] + "-" + datestr[4:6] + ".tab"
    FILE = BSRN_FILE_PATH + station + "/" + BSRN_FILE_NAME

    print(station + ", " + tag + ", " + atm_name + ", " + datestr)

    bsrn = getBSRNData(FILE)
    bsrn = getValueAtDate(datestr, bsrn)

    atm = getAtm(atm_name) #reads the _dependent.csv file
    elements_cl = Parallel(n_jobs=-1, verbose=5)(delayed(getIWVFromTable)(bsrn[i,0],bsrn[i,1],bsrn[i,2], atm_name,atm) for i in range(0,len(bsrn[:]),1))

    date_cl = []
    for element in elements_cl:
            date_cl.append(element[0])
    dates = np.asarray(date_cl)

    array = np.array([x for x in elements_cl],dtype=([("date", "S20"), ("T", "f8"), ("LW", "f8"), ("iwv", "f8"),("distance","f8")]))

    IWV = {}
    IWV['dates'] = dates
    IWV["T"] = array['T']
    IWV["LW"] = array['LW']
    IWV["IWV"] = array["iwv"]
    IWV["distance"] = array["distance"]

