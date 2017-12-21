"""
Hier werde ich den 09.09.2014 in Oklahoma (Cart Site E13) mit Radiosondenmessungen vergleichen.
In main bei data kann die zeit "time" 0,6,12 oder 18 Uhr sein:
"""

import numpy as np
from wv_converter import VMR2RH,RH2VMR
from typhon.atmosphere import iwv

def getDataFromSoundingfile(time=12):
    FILE = "LMN_20140909_%02dz.csv"%time

    data = {}
    with open(FILE, "r") as f:
        f.readline()
        names = f.readline().split()
        f.readline()
        f.readline()
        f.readline()

        for name in names:
            data[name] = []

        for line in f:
            split = line.split()
            for element,name in zip(split,names):
                data[name].append(float(element))

        for name in names:
            data[name] = np.asarray(data[name])

        data["TEMP"] = np.add(data["TEMP"],273.15)
        data["PRES"] = np.multiply(data["PRES"],100)
        data["RELH"] = np.divide(data["RELH"],100)

    return data

if __name__ == "__main__":
    data = getDataFromSoundingfile(time=24)
    VMR = RH2VMR(data["RELH"],data["PRES"],data["TEMP"])
    IWV = iwv(VMR,data["PRES"],data["TEMP"],data["HGHT"])
    print(IWV)



