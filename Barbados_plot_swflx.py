from netCDF4 import Dataset
import matplotlib.pyplot as plt
import datetime as dt
import matplotlib.dates as mdate
import numpy as np


def print_nc(nc_file):
    print(nc_file)
    print("----------------------------------------------")

    print([str(key) for key in nc_file.variables.keys()])


if __name__ == "__main__":
    # FILE_PATH = "/scratch/uni/u237/users/tmachnitzki/Barbados_Radiation/201601/"
    FILE_PATH = "/Users/u300844/t7home/tmachnitzki/Barbados_Radiation/201607/"
    FILE_NAME = "Radiation__Deebles_Point__DownwellingRadiation__1s__201607.nc"

    nc = Dataset(FILE_PATH + FILE_NAME)
    print_nc(nc)
    LWflx = nc.variables["LWdown_diffuse"][:].copy()
    SWflx = nc.variables["SWdown_global"][:].copy()
    raw_time = nc.variables["time"][:].copy()
    nc.close()

    time = mdate.num2date(mdate.epoch2num(raw_time))
    # time = dt.datetime(raw_time)

    month_str = str(time[0].month)
    year_str = str(time[0].year)

    fig1 = plt.figure(num=1, figsize=(20, 15))
    fig1.suptitle(year_str + "/" + month_str + "\nBarbados")
    ax = fig1.add_subplot(4, 10, 1)

    day_last = 1
    last_ende = 0

    for i, element in enumerate(time + [dt.datetime(2000,1,1,1,1)]):
        day = element.day

        if day != day_last:
            print(day-1)

            start = last_ende
            ende = i-1

            print(time[start],time[ende])
            ax.plot(time[start:ende],SWflx[start:ende], color='black', lw=0.5)
            # ax.fmt_xdata = mdate.AutoDateFormatter("%X")

            xformatter = mdate.DateFormatter('%H')
            xlocator = mdate.HourLocator(interval=6)
            ax.xaxis.set_major_locater = xlocator
            ax.xaxis.set_minor_locator = xlocator
            plt.gcf().axes[day-2].xaxis.set_major_formatter(xformatter)

            ax.set_title(str(day_last))
            ax.set_ylim([-5,1700])
            ax.set_xlim([time[start],time[ende]])



            ax = fig1.add_subplot(4, 10, day)
            last_ende = ende
        day_last = day

    plt.savefig("SW_down_Barbados_" + year_str + "_" + month_str + ".png" )

