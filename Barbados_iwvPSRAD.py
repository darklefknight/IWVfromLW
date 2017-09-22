from netCDF4 import Dataset
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdate
from joblib import Parallel,delayed

def getValueAtDate(datestr, array):
    year_str = datestr[:4]
    month_str = datestr[4:6]
    day_str = datestr[6:]

    return_list = []

    for line in array:
        if line[0].strftime("%Y%m%d") == datestr:
            return_list.append(line)
            continue

    return_array = np.asarray(return_list)
    return return_array


def getIWVFromTable(temp, flx, atm_name, atm):
    print(atm_name + ", Temp: " + str(temp) + ", FLX:" + str(flx) + "...")
    temp_run = []
    for i, element in enumerate(atm["Temperature"]):
        if (abs(element - 273.15 - temp) < 1):
            temp_run.append(atm[i])

    if temp_run == []:
        return -999

    temp_run = np.asarray(temp_run)

    distance = 5
    flx_cl = -777
    iwv_cl = -777
    temp_cl = -777
    for i, element in enumerate(temp_run):
        if (abs(element[3] - flx) < distance):
            flx_cl = element[3]
            iwv_cl = element[2]
            temp_cl= element[0]
            distance = abs(element[3] - flx)

    if iwv_cl == -777:
        temp_cl = temp
        flx_cl = flx

    return (temp_cl, flx_cl,iwv_cl)

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


if __name__ == "__main__":
    FILE_PATH = "/Users/u300844/t7home/tmachnitzki/Barbados_Radiation/201602/"
    FILE_NAME = "Radiation__Deebles_Point__DownwellingRadiation__1s__201602.nc"
    WEATHER_PATH = "/Users/u300844/t7home/tmachnitzki/Barbados_Radiation/temp201602/"
    WEATHER_FILE = "Meteorology__Deebles_Point__2m_10s__201602.nc"
    datestr = "20160204"

    print("Get data from Weatherfile...")
    ncw = Dataset(WEATHER_PATH + WEATHER_FILE)
    temp = ncw.variables['T'][:].copy()
    raw_time = ncw.variables["time"][:].copy()
    ncw.close()
    temp_time = mdate.num2date(mdate.epoch2num(raw_time))

    temp_array = np.stack((temp_time, temp), axis=1)
    del temp_time, temp

    print("Get data from Radiationfile...")
    nc = Dataset(FILE_PATH + FILE_NAME)
    LWflx = nc.variables["LWdown_diffuse"][:].copy()
    raw_time = nc.variables["time"][:].copy()
    nc.close()
    flx_time = mdate.num2date(mdate.epoch2num(raw_time))

    flx_array = np.stack((flx_time, LWflx), axis=1)
    del LWflx, flx_time

    print("Reduce data to %s..." % datestr)
    temp = getValueAtDate(datestr, temp_array)
    flx = getValueAtDate(datestr, flx_array)

    iwv = []
    atms = ['midlatitude-summer','midlatitude-winter','subarctic-summer','subarctic-winter','tropical']
    atms = ['midlatitude-summer']
    for atm_name in atms:
        atm = getAtm(atm_name) #reads the _dependent.csv file
        elements_cl = Parallel(n_jobs=-1, verbose=5)(delayed(getIWVFromTable)(temp[i,1],flx[i*10,1], atm_name,atm) for i in range(0,len(temp),100))

        flx_cl = []
        temp_cl = []
        iwv_cl = []
        for element in elements_cl:
                flx_cl.append(element[1])
                temp_cl.append(element[0])
                iwv_cl.append(element[2])

        with open(("file_elements_" + atm_name + "_.txt"),"w") as f:
            f.write("Barbados " + atm_name + "\n")
            f.write("temp,flx,iwv")
            for i in range(len(flx_cl)):
                f.write("\n" + str(temp_cl[i]) + "," + str(flx_cl[i]) + "," + str(iwv_cl[i]))

        f.close()


