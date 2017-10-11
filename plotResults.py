import matplotlib.pyplot as plt
import numpy as np
from glob import glob
from datetime import datetime as dt
import locale
locale.setlocale(locale.LC_ALL,'de_DE')
import seaborn

def get_results(station,atm):
    result_path = "results/" + station + "_sadata/" + atm + "/"
    IWV = {}
    IWV['date'] = []
    IWV["T"] = []
    IWV["LW"] = []
    IWV["IWV"] = []
    IWV["distance"] = []
    IWV["IWV_AERONET"] = []

    for file in sorted(glob(result_path + "*" + station + "*")):
        # print(file)
        with open(file, "rb") as f:
            results = np.genfromtxt(f,
                                    skip_header=4,
                                    delimiter=";",
                                    # names=False,
                                    comments="#",
                                    dtype=None
                                    )
        # print(np.shape(results))
        if np.shape(results) != ():
            for line in results:
                # get date:
                line_date = line[0]
                line_time = line[1]
                line_date_time = line_date + line_time
                line_date_time = line_date_time.decode().replace(" ", "")
                line_date = dt.strptime(line_date_time, "%x%X")

                # get data:
                line_temp = line[2]
                line_LW = line[3]
                line_calculatedIWV = line[4]
                line_aeronetIWV = line[5]
                line_distance = line[6]

                IWV['date'].append(line_date)
                IWV["T"].append(line_temp)
                IWV["LW"].append(line_LW)
                IWV["IWV"].append(line_calculatedIWV)
                IWV["distance"].append(line_distance)
                IWV["IWV_AERONET"].append(line_aeronetIWV)

        else:
            # get date:
            line_date = results[()][0]
            line_time = results[()][1]
            line_date_time = line_date + line_time
            line_date_time = line_date_time.decode().replace(" ", "")
            line_date = dt.strptime(line_date_time, "%x%X")

            # get data:
            line_temp = results[()][2]
            line_LW = results[()][3]
            line_calculatedIWV = results[()][4]
            line_aeronetIWV = results[()][5]
            line_distance = results[()][6]

            IWV['date'].append(line_date)
            IWV["T"].append(line_temp)
            IWV["LW"].append(line_LW)
            IWV["IWV"].append(line_calculatedIWV)
            IWV["distance"].append(line_distance)
            IWV["IWV_AERONET"].append(line_aeronetIWV)

    return IWV


def makeHist(IWV):
    try:
        fig = plt.figure(figsize=(4.5,4.5))
        fig.suptitle("Results for " + station + "\nUsed atmosphere: " + atm)
        ax1 = plt.subplot(111)
        ax1.plot(IWV['IWV'],IWV['IWV_AERONET'], lw=0, marker=".")

        m, b = np.polyfit(IWV['IWV'],IWV['IWV_AERONET'], 1)
        print(m,b)
        x = IWV['IWV'][:].copy()
        y = np.add(np.multiply(m,x),b)
        ax1.plot(x, y, '-',label="m={} \nb={}".format(m,b))

        x_line = np.linspace(0,60,61)

        ax1.plot(x_line,x_line,color="black",lw=1)
        # ax1.grid()

        ax1.set_xlabel("Calculated IWV")
        ax1.set_ylabel("IWV from AERONET")

        ax1.set_xlim([0, 50])
        ax1.set_ylim([0, 50])
        ax1.legend(loc="upper left")

        plt.savefig("figures/hist/" + station + "_" + atm + "_hist.png", dpi=600)
        plt.close(fig)

    except:
        plt.close(fig)


if __name__ == "__main__":
    # atms = ['midlatitude-summer', 'midlatitude-winter', 'subarctic-summer', 'subarctic-winter', 'tropical']
    atms= ['US-standard','subtropic-winter','subtropic-summer','midlatitude-summer', 'midlatitude-winter', 'subarctic-summer', 'subarctic-winter', 'tropical']
    seaborn.set()
    # atm = "tropical"
    # atm= "midlatitude-summer"
    # atm = "midlatitude-winter"
    # atm = "subarctic-winter"
    # atm= "subarctic-summer"


    # station = "Barrow"
    # station="SEDE_BOKER"
    # station = "Cart_Site"
    # station = "Gobabeb"

    stations = ["Barrow","SEDE_BOKER","Cart_Site","Cabauw","Gobabeb","Tiksi","Toravere","Darwin","Fukuoka"]

    # stations = ["Cart_Site"]
    # atms = ["subtropic-winter","US-standard"]

    correlation_file = "statistics/correlation.csv"
    f = open(correlation_file,"w")
    f.write(";")
    f.write(";".join(atms))
    f.write(";")
    for station in stations:
        f.write("\n" + station + ";")
        for atm in atms:

            IWV = get_results(station,atm)

            fig = plt.figure(figsize=(10,5.5))
            fig.suptitle("Results for " + station + "\nUsed atmosphere: " + atm)
            ax1 = plt.subplot(211)
            ax1.plot(IWV['date'],IWV['IWV'],label="Calculated IWV",lw=1, color = "#728A19")
            ax1.plot(IWV['date'],IWV['IWV_AERONET'],label="AERONET-Data",lw=1, color = "#FE2712")
            ax1.legend(loc="upper left")
            # ax1.grid()
            ax1.set_xlabel("Time")
            ax1.set_ylabel("IWV [kg/m2]")
            ax1.set_ylim([0,60])

            ax2 = plt.subplot(212)
            ax2.plot(IWV['date'],np.subtract(IWV['IWV'],IWV['IWV_AERONET']),color="#347B98",lw=1, label="Difference")
            ax2.set_ylim([-20,20])
            # ax2.grid()
            ax2.set_xlabel("Time")
            ax2.set_ylabel("Difference [kg/m2]")

            ax2mean = np.mean(np.subtract(IWV['IWV'],IWV['IWV_AERONET']))
            ax2.plot(IWV['date'],[ax2mean for i in range(len(IWV['date']))],ls="--", color="#347B98", label="Mean Difference = %f kg/m2" %ax2mean)
            ax2.plot(IWV['date'], [ax2mean+5 for i in range(len(IWV['date']))], ls="--", color="g")
            ax2.plot(IWV['date'], [ax2mean - 5 for i in range(len(IWV['date']))], ls="--", color="g")
            ax2.legend(loc="upper left")

            plt.savefig("figures/" + station+"_" + atm+".png", dpi=600)
            plt.close(fig)




            correlation= np.corrcoef(IWV['IWV'],IWV['IWV_AERONET'])[0,1]
            f.write("%f ;" % correlation)

            makeHist(IWV)


    f.close()

