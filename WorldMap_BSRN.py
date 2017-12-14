from WorldMap_Sites import Site
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
import glob

def AERONET2Site():
    AE_sites = []
    PATH = "/scratch/uni/u237/users/tmachnitzki/psrad/aeronet_inversion/INV/DUBOV/ALL_POINTS/"
    for file in glob.glob(PATH + "*"):
        with open(file,"r") as f:
            line = f.readline()
            splitted = line.split(",")

        # print(line)
        lat,lon = -9999,-9999
        for split in splitted:
            if "Locations" in split:
                ind = split.index("=") + 1
                name = split[ind:]

            elif "lat=" in split:
                ind = split.index("=") +1
                lat = float(split[ind:])
            elif "long=" in split:
                ind = split.index("=") +1
                lon = float(split[ind:])


        AE_sites.append(Site(name,lat,lon,0))
    return AE_sites

if __name__ == "__main__":
    sites = []
    test_sites = []
    AERONET = AERONET2Site()
    FILE = "/scratch/uni/u237/users/tmachnitzki/psrad/python_svn/BSRN_stations.csv"
    stations = ["Barrow", "Sede Boqer", "Southern Great Plains", "Cabauw", "Gobabeb", "Darwin"]

    with open(FILE,"rb") as f:
        data = np.genfromtxt(f,
                      names=True,
                      delimiter=";",
                      dtype=None
                      )

    for d in data:
        if not d["station"].decode() in stations:
            sites.append(Site(d["station"].decode(),d["lat"],d["lon"],d["height"]))
        else:
            test_sites.append(Site(d["station"].decode(),d["lat"],d["lon"],d["height"]))

    # =================================
    # BSRN sites:
    # =================================

    xx = []
    yy = []
    for site in sites:
        xx.append(site.lon())
        yy.append(site.lat())

    # PLotting:
    fig = plt.figure(figsize=(16, 9))
    m = Basemap(projection='cyl', llcrnrlat=-85, urcrnrlat=85, llcrnrlon=-180, urcrnrlon=180, resolution=None)
    parallels = np.arange(-180., 180., 45.)
    meridians = np.arange(-120., 140., 60.)

    m.drawmeridians(meridians, labels=[0, 0, 0, 1], fontsize=20)
    m.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=0, xoffset=-18)

    label_props = dict(boxstyle='round', facecolor='white',linewidth=0, alpha=1)
    for i,y,s in zip(range(-45,50,45),[-45,0,45],["S","","N"]):
        x = -170
        plt.text(x,y-2,"%s$^\circ$%s"%(abs(i),s),bbox=label_props,fontsize=20)

    x, y = m(xx, yy)


    # m.drawcoastlines()
    m.drawlsmask(land_color="dimgrey",ocean_color="white",lakes=True)
    # m.fillcontinents(color='grey', lake_color="white")
    # m.drawmapboundary(fill_color='white')
    # m.scatter(x, y, 30, color="blue", marker="x", zorder=3)
    m.scatter(x, y, 250, color="cyan",alpha=0.8, marker="o", zorder=2,linewidth=1,edgecolor="black", label="BSRN")

    #=================================
    #AERONET SITES:
    #=================================

    xx = []
    yy = []
    for site in AERONET:
        xx.append(site.lon())
        yy.append(site.lat())

    x, y = m(xx, yy)
    m.scatter(x, y, 100, color="yellow", alpha=0.6, marker="o", zorder=2, linewidth=1, edgecolor="black", label="AERONET")

    #=================================
    # Test sites:
    #=================================

    xx = []
    yy = []
    for site in test_sites:
        xx.append(site.lon())
        yy.append(site.lat())

    x, y = m(xx, yy)

    x1 = x.copy()
    for i,element in enumerate(x1):
        x1[i] += 300000

    m.scatter(x, y, 250, color="orangered", alpha=0.8, marker="o", zorder=2, linewidth=1, edgecolor="black", label="Test Stationen")

    props = dict(boxstyle='round', facecolor='orangered', alpha=0.8)
    for i,site in enumerate(test_sites):
        plt.text(x[i] + 5, y[i] - 1, site.name(), bbox=props, fontsize=20)


    # plt.title("Cylindrical Equal-Area Projection")
    # plt.show()

    #=================================
    # LEGEND:
    #=================================
    plt.legend(loc="lower left", fontsize=20)
    plt.tight_layout()



    plt.savefig("/scratch/uni/u237/users/tmachnitzki/psrad/python_svn/BSRN_sites.png",bbox_inches="tight")