import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
import seaborn
from plotResults import get_results
from sklearn.metrics import mean_squared_error
from math import sqrt


def atmHist():
    """
    plots a histogram containing the correlation-coefficient for each atmosphere and station.

    """
    correlation_file = "statistics/correlation.csv"

    with open(correlation_file) as f:
        table = pd.read_table(f, sep=';', index_col=0,
                              lineterminator='\n')

    df = table.drop('Unnamed: 9', 1)
    df = df.drop('Tiksi', 0)
    df = df.drop('Toravere', 0)

    df = df.apply(pd.to_numeric)

    df.index.name = "Station"
    df.columns.name = "Atmosphere"

    cols = ['US-standard','midlatitude-summer','midlatitude-winter','subarctic-summer','subarctic-winter','subtropic-summer','subtropic-winter','tropical']
    df =df[cols]

    df = df.reindex(["Barrow", "SEDE_BOKER", "Cart_Site", "Cabauw", "Gobabeb", "Darwin"])
    df = df[df.index != "Fukuoka"]

    # df1 = pd.DataFrame(df.stack(), columns=["data"]).reset_index()

    # ag = df1.groupby(['Atmosphere','Station']).sum().unstack()

    # ag.columns = ag.columns.droplevel()
    plot = df.plot(kind='bar', colormap=cm.Accent, width=.8, figsize=(8, 6))
    plot.set_ylabel("Correlation coefficient")
    plot.set_xlabel("Station")
    legend = plot.legend(frameon=True, loc="lower left")
    legend.set_facecolor = "white"
    plt.tight_layout()
    plt.savefig("statistics/Correlation.png", dpi=600)

    plt.show()


def RMSEHIST():
    atms = ['US-standard', 'subtropic-winter', 'subtropic-summer', 'midlatitude-summer', 'midlatitude-winter',
            'subarctic-summer', 'subarctic-winter', 'tropical']
    stations = ["Barrow", "SEDE_BOKER", "Cart_Site", "Cabauw", "Gobabeb", "Darwin"]

    RMSE_list = []
    station_list = []
    atm_list = []

    cmap = cm.get_cmap('Accent')
    colors = {
            'US-standard': cmap(0),
            'subtropic-winter': cmap(0.125),
            'subtropic-summer':cmap(0.25),
            'midlatitude-summer':cmap(0.375),
            'midlatitude-winter':cmap(0.5),
            'subarctic-summer':cmap(0.625),
            'subarctic-winter':cmap(0.75),
            'tropical':cmap(0.875)
    }

    for atm in atms:
        for station in stations:
            IWV = get_results(station, atm)
            df = pd.DataFrame(IWV)
            RMSE = sqrt(mean_squared_error(df['IWV_AERONET'], df['IWV']))
            RMSE_list.append(RMSE)
            station_list.append(station)
            atm_list.append(atm)

    df = pd.DataFrame({
        'Station': station_list,
        'Atmosphere': atm_list,
        'RMSE': RMSE_list
    })


    df = df.groupby(['Station', 'Atmosphere']).sum().unstack()
    df.columns = df.columns.droplevel() # get rid of the "RMSE" in the labels
    df =df.reindex(["Barrow", "SEDE_BOKER", "Cart_Site", "Cabauw", "Gobabeb", "Darwin"])
    print(df)
    df.to_csv("statistics/RMSE.csv", sep=";")



    plot = df.plot(kind='bar', colormap=cm.Accent, width=.8, figsize=(8, 6))
    plot.set_ylabel("RMSE [kg/m2]")
    plot.set_xlabel("Station")
    legend = plot.legend(frameon=True, loc="lower left")
    legend.set_facecolor = "white"
    plt.tight_layout()
    plt.savefig("statistics/RMSE.png", dpi=600)

    plt.show()


if __name__ == "__main__":
    seaborn.set()


    RMSEHIST()
    atmHist()
