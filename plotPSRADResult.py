import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
import seaborn


def plotOneTemp(atm):
    FILE = home + "wv_tables/" + atm + "_dependent_sadata.csv"

    cmap = cm.get_cmap('Accent')

    colors = {
            'US-standard': cmap(0),
            'midlatitude-summer': cmap(0.125),
            'midlatitude-winter':cmap(0.25),
            'subarctic-summer':cmap(0.375),
            'subarctic-winter':cmap(0.5),
            'subtropic-summer':cmap(0.625),
            'subtropic-winter':cmap(0.75),
            'tropical':cmap(0.875)
    }

    with open(FILE, "rb") as f:
        result = np.genfromtxt(f,
                               names=True,
                               dtype=float,
                               delimiter=";")

    one_T_list = []
    fig = plt.figure(figsize=(8, 4.5))
    # fig.suptitle(atm)
    ax1 = fig.add_subplot(111)
    for i,T in zip(np.linspace(0,0.8,5),range(250,300,10)):
        oneT = result[np.where(result['Temperature'] == T)]
        one_T_list.append(oneT)
        ax1.plot(oneT['IWV'],oneT['flxd'], label=str(T)+"$\,K$", color=cmap(i))


    ax1.legend(loc="lower right")
    ax1.set_xlabel("IWV [kg/$m^2$]")
    ax1.set_ylabel("FLXD [W/$m^2$]")

    plt.savefig("oneTemp_%s.png"%atm, dpi=800)

def plotATMS():

    cmap = cm.get_cmap('Accent')
    colors = {
            'US-standard': cmap(0),
            'midlatitude-summer': cmap(0.125),
            'midlatitude-winter':cmap(0.25),
            'subarctic-summer':cmap(0.375),
            'subarctic-winter':cmap(0.5),
            'subtropic-summer':cmap(0.625),
            'subtropic-winter':cmap(0.75),
            'tropical':cmap(0.875)
    }


    atms = ['US-standard', 'subtropic-winter', 'subtropic-summer', 'midlatitude-summer', 'midlatitude-winter','subarctic-summer', 'subarctic-winter', 'tropical']
    # atms = ["midlatitude-winter"]

    fig = plt.figure(figsize=(8, 4.5))
    fig.suptitle("Temperatur = $280\,K$ ")
    ax1 = fig.add_subplot(111)
    for atm in atms:
        print(atm)
        FILE = home + "wv_tables/" + atm + "_dependent_sadata.csv"

        with open(FILE, "rb") as f:
            result = np.genfromtxt(f,
                                   names=True,
                                   dtype=float,
                                   delimiter=";")

        oneT = result[np.where(result['Temperature'] == 280)]
        ax1.plot(oneT['IWV'], oneT['flxd'], label=atm, color=colors[atm])


    ax1.legend(loc="lower right")
    ax1.set_xlabel("IWV [kg/$m^2$]")
    ax1.set_ylabel("FLXD [W/$m^2$]")
    plt.savefig("ATMS.png", dpi=800)


if __name__ == "__main__":
    FASCOD_PATH = "/scratch/uni/u237/users/tlang/arts-xml-data/planets/Earth/Fascod/"
    home = "/Users/u300844/t7home/tmachnitzki/psrad/python_svn/"
    seaborn.set()
    atms = ['US-standard', 'subtropic-winter', 'subtropic-summer', 'midlatitude-summer', 'midlatitude-winter',
            'subarctic-summer', 'subarctic-winter', 'tropical']
    for atm in atms:
        plotOneTemp(atm)
    plotATMS()



