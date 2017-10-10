from sfc_fluxes2 import get_fascod_atmosphere,get_sadata_atmosphere
import matplotlib.pyplot as plt

if __name__ == "__main__":
    FASCOD_PATH = "/scratch/uni/u237/users/tlang/arts-xml-data/planets/Earth/Fascod/"
    home = "/scratch/uni/u237/users/tmachnitzki/psrad/python_svn/"

    fas = get_fascod_atmosphere(FASCOD_PATH, "midlatitude-winter")
    sad = get_sadata_atmosphere("midlatitude-winter")

    fig = plt.figure(figsize=(16,9))
    ax1 =fig. add_subplot(9, 1, 1)
    ax2 = fig.add_subplot(9, 1, 2)
    ax3 = fig.add_subplot(9, 1, 3)
    ax4 = fig.add_subplot(9, 2, 1)
    ax5 = fig.add_subplot(9, 2, 2)
    ax6 = fig.add_subplot(9, 2, 3)
    ax7 = fig.add_subplot(9, 3, 1)
    ax8 = fig.add_subplot(9, 3, 2)
    ax9 = fig.add_subplot(9, 3, 3)
    axes= [ax1,ax2,ax3,ax4,ax5,ax6,ax7,ax8,ax9]
    for ax,key in zip(axes,fas.keys()):
        ax.plot(fas[key],fas['p'], color="r")
        ax.plot(sad[key],sad['p'], color="b")
        ax.title = key

    plt.savefig(home+ "test.png")