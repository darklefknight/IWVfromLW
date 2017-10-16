from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np

sites = []


class Site:
    def __init__(self, name, lat, lon, height):
        self.__name = name
        self.__lon = lon
        self.__lat = lat
        self.__heigt = height

        sites.append(self)

    def lat(self):
        return self.__lat

    def lon(self):
        return self.__lon

    def height(self):
        return self.__height

    def name(self):
        return self.__name


if __name__ == "__main__":
    stations = ["Barrow", "SEDE_BOKER", "Cart_Site", "Cabauw", "Gobabeb", "Tiksi", "Toravere", "Darwin", "Fukuoka"]
    Barrow = Site("Barrow", 71.3230, -156.6070, 8)
    Sede_Boker = Site("Sede Boqer", 30.8597, 34.7794, 500)
    Cart_Site = Site("Cart Site", 36.6050, -97.4850, 318)
    Cabauw = Site("Cabauw", 51.9711, 4.9267, 0)
    Gobabeb = Site("Gobabeb", -23.5614, 15.0420, 407, )
    Darwin = Site("Darwin", -12.4250, 130.8910, 30)

    xx = []
    yy = []
    for site in sites:
        xx.append(site.lon())
        yy.append(site.lat())

    # PLotting:
    plt.figure(figsize=(16, 9))
    m = Basemap(projection='merc', llcrnrlat=-70, urcrnrlat=75, llcrnrlon=-170, urcrnrlon=170, resolution=None)

    x, y = m(xx, yy)

    x1 = x.copy()
    for i,element in enumerate(x1):
        x1[i] += 300000

    # m.drawcoastlines()
    m.drawlsmask(land_color="dimgrey",ocean_color="white",lakes=True)
    # m.fillcontinents(color='grey', lake_color="white")
    # m.drawmapboundary(fill_color='white')
    # m.scatter(x, y, 30, color="blue", marker="x", zorder=3)
    m.scatter(x1, y, 100, color="cyan",alpha=0.6, marker="<", zorder=2,linewidth=1,edgecolor="black")
    props = dict(boxstyle='round', facecolor='cyan', alpha=0.6)

    for i,site in enumerate(sites):
        plt.text(x[i] + 850000, y[i] - 190000, site.name(), bbox=props, fontsize=12)

    # parallels = np.arange(-180., 180., 30.)
    # meridians = np.arange(-180., 180., 30.)
    #
    # m.drawmeridians(meridians, labels=[0, 0, 0, 1], fontsize=10)
    # m.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=10)
    # plt.title("Cylindrical Equal-Area Projection")
    plt.show()
