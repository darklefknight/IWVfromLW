import matplotlib.pyplot as plt
import numpy as np
from glob import glob


if __name__ == "__main__":
    result_path =  "results/"
    station_tag = "bar"
    station = "Barrow"
    IWV = {}
    IWV['date'] = []
    IWV["T"] = []
    IWV["LW"] = []
    IWV["IWV"] = []
    IWV["distance"] = []
    IWV["IWV_AERONET"] = []

    for file in glob(result_path + "*" + station + "*"):
        with open(file,"r") as f:
            results = np.genfromtxt(f,
                                    skip_header=2,
                                    delimiter=";",
                                    names=True,
                                    comments="#",
                                    dtype=None,
                                    )
        for line in results:
            date = line[0]
            time = line[1]
