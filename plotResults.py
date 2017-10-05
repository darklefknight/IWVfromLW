import matplotlib.pyplot as plt
import numpy as np
from glob import glob
from datetime import datetime as dt
import locale
locale.setlocale(locale.LC_ALL,'de_DE')


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
        print(file)
        with open(file, "rb") as f:
            results = np.genfromtxt(f,
                                    skip_header=4,
                                    delimiter=";",
                                    # names=False,
                                    comments="#",
                                    dtype=None
                                    )
        print(np.shape(results))
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

if __name__ == "__main__":
    # atms = ['midlatitude-summer', 'midlatitude-winter', 'subarctic-summer', 'subarctic-winter', 'tropical']
    atms= ['US-standard','subtropic-winter','subtropic-summer','midlatitude-summer', 'midlatitude-winter', 'subarctic-summer', 'subarctic-winter', 'tropical']

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

    stations = ["Cart_Site"]
    atms = ["midlatitude-winter"]

    for station in stations:
        for atm in atms:
            IWV = get_results(station,atm)

            fig = plt.figure(figsize=(16,9))
            fig.suptitle("Results for " + station + "\nUsed atmosphere: " + atm)
            ax1 = plt.subplot(211)
            ax1.plot(IWV['date'],IWV['IWV'],label="Calculated IWV",lw=1, color = "#728A19")
            ax1.plot(IWV['date'],IWV['IWV_AERONET'],label="AERONET-Data",lw=1, color = "#FE2712")
            ax1.legend(loc="upper left")
            ax1.grid()
            ax1.set_xlabel("Time")
            ax1.set_ylabel("IWV [kg/m2]")
            ax1.set_ylim([0,60])

            ax2 = plt.subplot(212)
            ax2.plot(IWV['date'],np.subtract(IWV['IWV'],IWV['IWV_AERONET']),color="#347B98",lw=1, label="Difference")
            ax2.set_ylim([-15,15])
            ax2.grid()
            ax2.set_xlabel("Time")
            ax2.set_ylabel("Difference between calculated and measured IWV [kg/m2]")


            ax2mean = np.mean(np.subtract(IWV['IWV'],IWV['IWV_AERONET']))
            ax2.plot(IWV['date'],[ax2mean for i in range(len(IWV['date']))],ls="--", color="#347B98", label="Mean Difference = %f kg/m2" %ax2mean)

            ax2.legend(loc="upper left")

            plt.savefig("figures/" + station+"_" + atm+".png")
            plt.close(fig)




