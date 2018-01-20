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


def makeHist(station,atms):
    fig, ((ax1, ax2, ax3, ax4), (ax5, ax6, ax7, ax8)) = plt.subplots(nrows=2, ncols=4,sharex=True,sharey=True ,figsize=(10,5.5))
    # fig = plt.figure(figsize=(16, 9))
    # ax1 = fig.add_subplot(411)
    # ax2 = fig.add_subplot(412)
    # ax3 = fig.add_subplot(421)
    # ax4 = fig.add_subplot(422)
    # ax5 = fig.add_subplot(812)
    # ax6 = fig.add_subplot(822)
    # ax7 = fig.add_subplot(832)
    # ax8 = fig.add_subplot(842)
    fig.suptitle("%s"%station)
    axes = [ax1,ax2,ax3,ax4,ax5,ax6,ax7,ax8]
    for atm,ax in zip(atms,axes):

        IWV = get_results(station,atm)
        ax.plot(IWV['IWV_AERONET'],IWV['IWV'], lw=0, marker=".")
        x_line = np.linspace(0, 60, 61)
        ax.plot(x_line, x_line, color="black", lw=1)
        try:

            m, b = np.polyfit(IWV['IWV_AERONET'],IWV['IWV'], 1)
            x = IWV['IWV_AERONET'][:].copy()
            y = np.add(np.multiply(m,x),b)
            ax.plot(x, y, '-',label="m={} \nb={}".format(round(m,2),round(b,2)),color="orange")


        except:
            print("FAILED")
            pass
        # ax1.grid()



        ax.set_xlim([0, 50])
        ax.set_ylim([0, 50])
        ax.legend(loc="lower right")
        ax.set_title(atm)

    ax1.set_ylabel("IWV [kg/$m^2$] BSRN")
    ax5.set_ylabel("IWV [kg/$m^2$] BSRN")

    axes_low = [ax5,ax6,ax7,ax8]
    for ax in axes_low:
        ax.set_xlabel("IWV [kg/$m^2$] AERONET")
    plt.savefig("figures/hist/" + station + "_hist.png", dpi=600)
    plt.close(fig)

if __name__ == "__main__":
    # atms = ['midlatitude-summer', 'midlatitude-winter', 'subarctic-summer', 'subarctic-winter', 'tropical']
    atms= ['US-standard','subtropic-winter','subtropic-summer','midlatitude-summer', 'midlatitude-winter', 'subarctic-summer', 'subarctic-winter', 'tropical']
    # atms = ["midlatitude-winter"]
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

    # correlation_file = "statistics/correlation.csv"
    # f = open(correlation_file,"w")
    # f.write(";")
    # f.write(";".join(atms))
    # f.write(";")
    # for station in stations:
    #     f.write("\n" + station + ";")
    #     for atm in atms:
    #
    #         IWV = get_results(station,atm)
    #
    #         fig = plt.figure(figsize=(10,5.5))
    #         fig.suptitle(station + "\nBenutzte Atmosphäre: " + atm)
    #         ax1 = plt.subplot(211)
    #         ax1.plot(IWV['date'],IWV['IWV'],label="IWV aus BSRN",lw=1, color = "#728A19")
    #         ax1.plot(IWV['date'],IWV['IWV_AERONET'],label="IWV aus AERONET",lw=1, color = "#FE2712")
    #         ax1.legend(loc="upper left")
    #         # ax1.grid()
    #         ax1.set_xlabel("Time")
    #         ax1.set_ylabel("IWV [kg/m2]")
    #         ax1.set_ylim([0,60])
    #
    #         ax2 = plt.subplot(212)
    #         ax2.plot(IWV['date'],np.subtract(IWV['IWV'],IWV['IWV_AERONET']),color="#347B98",lw=1, label="Differenz")
    #         ax2.set_ylim([-20,20])
    #         # ax2.grid()
    #         ax2.set_xlabel("Zeit")
    #         ax2.set_ylabel("Differenz [kg/m2]")
    #
    #         try:
    #             ax2mean = np.mean(np.subtract(IWV['IWV'],IWV['IWV_AERONET']))
    #             ax2percentile95 = np.nanpercentile(np.subtract(IWV['IWV'], IWV['IWV_AERONET']),95)
    #             ax2.plot(IWV['date'],[ax2mean for i in range(len(IWV['date']))],ls="--", color="#347B98", label="BIAS = %5.3f kg/m2" %ax2mean)
    #             ax2.plot(IWV['date'], [ax2mean + ax2percentile95 for i in range(len(IWV['date']))], ls="--", color="g", label="95%% Perzentil = %5.3f kg/m2" % ax2percentile95)
    #             ax2.plot(IWV['date'], [ax2mean - ax2percentile95 for i in range(len(IWV['date']))], ls="--", color="g")
    #             legend = ax2.legend(loc="lower left",frameon=True)
    #             legend.set_facecolor = "white"
    #
    #             plt.savefig("figures/" + station+"_" + atm+".png", dpi=600)
    #             plt.close(fig)
    #         except:
    #             plt.close(fig)
    #             continue
    #
    #
    #
    #
    #         correlation= np.corrcoef(IWV['IWV'],IWV['IWV_AERONET'])[0,1]
    #         f.write("%f ;" % correlation)
    # f.close()

    for station in stations:
        makeHist(station,atms)

