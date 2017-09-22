import glob
import numpy as np
from datetime import datetime as dt
import matplotlib.pyplot as plt


def get_iwv_from_aeronet(aeronetPath, station):
    # stationPath = glob.glob(aeronetPath + "*" + station + ".lev20")[0]
    stationPath = glob.glob(aeronetPath + "*" + station + ".dubovik")[0]
    print(stationPath)
    with open(stationPath, "rb") as f:
        array = np.genfromtxt(f,
                              skip_header=3,
                              names=True,
                              dtype=None,
                              delimiter=",",
                              usecols=["Dateddmmyyyy","Timehhmmss","Watercm"]
                              )
    f.close()

    date_str_arr = array["Dateddmmyyyy"]
    time_str_arr = array["Timehhmmss"]
    dates = []

    for date_line_c, time_line_c in zip(date_str_arr,time_str_arr):
        date_line = date_line_c.decode()
        time_line = time_line_c.decode()
        day_str, month_str, year_str  = date_line.split(":")
        hour_str,min_str,sec_str  = time_line.split(":")
        date = dt(int(year_str),int(month_str),int(day_str),int(hour_str),int(min_str),int(sec_str))
        dates.append(date)

    dates = np.asarray(dates)
    result_array = np.stack((dates,array["Watercm"]),axis=1)

    return result_array

def getIWVAtDate(datestr,array):
    year_str = datestr[:4]
    month_str = datestr[4:6]
    day_str = datestr[6:]

    return_list = []

    for line in array:
        if line[0].strftime("%Y%m") == datestr[:6]:
            return_list.append(line)

    return_array = np.asarray(return_list)
    return return_array

def searchGoodDate(iwv_array): #iwv_array = station
    last_date = dt(1900,1,1,1,1,1)
    counter = 0
    date_list = []
    result_list = []
    for element in iwv_array:
        date = element[0]
        iwv = element[1]
        if date.date() == last_date.date():
            counter += 1
            date_list.append(element)
        else:
            if counter >= 4:
                result_list.append(date_list)

            counter = 0
            date_list= []

        last_date = date

    return result_list

if __name__ == "__main__":
    # aeronetPath = "/Users/u300844/t7home/tmachnitzki/psrad/aeronet/AOT/LEV20/ALL_POINTS/"
    aeronetPath = "/Users/u300844/t7home/tmachnitzki/psrad/aeronet_inversion/INV/DUBOV/ALL_POINTS/"
    stationName = "Barrow"
    datestr = "20110628"   #Day where you want to have the iwv from


    station = get_iwv_from_aeronet(aeronetPath=aeronetPath, station=stationName)

    good_dates = searchGoodDate(station)
    # iwv = getIWVAtDate(datestr,station)
    #
    # plt.plot(iwv[:,0],iwv[:,1], lw=0, marker="x", color="firebrick")