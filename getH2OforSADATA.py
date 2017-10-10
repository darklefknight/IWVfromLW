import numpy as np
from sfc_fluxes2 import get_fascod_atmosphere, get_sadata_atmosphere
import matplotlib.pyplot as plt

def getCO2values(sadata,fascod):
    FASCOD_PATH = "/scratch/uni/u237/users/tlang/arts-xml-data/planets/Earth/Fascod/"


    fas = fascod
    sad = sadata

    CO2 = fas['CO2'].copy()
    p = fas['p']

    fit = np.polyfit(p,CO2,8)
    poly = np.poly1d(fit)
    values = poly(sad['p'])
    return values

if __name__ == "__main__":
    home = "/scratch/uni/u237/users/tmachnitzki/psrad/python_svn/"
    fig = plt.figure(figsize=(16,9))


    ax1 = fig.add_subplot(111)

    ax1.plot(h2o,p,color="r", label="fascod")
    ax1.plot(values,sad['p'],color="b", label="sadata")
    ax1.legend(loc="best")

    plt.savefig(home+"polytest.png")






