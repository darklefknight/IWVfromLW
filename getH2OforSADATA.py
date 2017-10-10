import numpy as np
from sfc_fluxes2 import get_fascod_atmosphere, get_sadata_atmosphere
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

def getCO2values(fas,sad):
    fas_co2 = fas['CO2'].copy()
    fas_p = fas['p'].copy()
    sad_p =sad['p'].copy()
    f = interp1d(fas_p,fas_co2)
    values = f(sad['p'])

    print(len(sad['p']),len(values))
    return values


if __name__ == "__main__":
    FASCOD_PATH = "/scratch/uni/u237/users/tlang/arts-xml-data/planets/Earth/Fascod/"
    home = "/scratch/uni/u237/users/tmachnitzki/psrad/python_svn/"

    atm_names = [ 'midlatitude-summer', 'midlatitude-winter',
                 'subarctic-summer', 'subarctic-winter', 'tropical']
    for atm in atm_names:
        print(atm)
        fas = get_fascod_atmosphere(FASCOD_PATH, atm, del0=False)
        sad = get_sadata_atmosphere(atm)

    values = getCO2values(fas,sad)

    fig = plt.figure(figsize=(16,9))
    ax1 = fig.add_subplot(111)

    ax1.plot(fas['CO2'],fas['p'],color="r", label="fascod")
    ax1.plot(values,sad['p'],color="b", label="sadata")
    ax1.legend(loc="best")

    plt.savefig(home+"polytest.png")






