from sfc_fluxes2 import get_sadata_atmosphere
import matplotlib.pyplot as plt
import numpy as np
import seaborn
from wv_converter import *

if __name__ == "__main__":
    font = 18
    seaborn.set()
    atm = get_sadata_atmosphere(season="US-standard")

    fig,(ax1,ax2,ax3) = plt.subplots(nrows=1,ncols=3,figsize=(16,9),sharey=True)
    fig.suptitle("Manipulation der Temperatur- und Feuchteprofile",fontsize=22)

    temperaturverschiebung = 20

    #==============================
    # 1. Plot: Temperatur
    #==============================
    ax1.semilogy(atm["t"],atm["p"],label="$T_0$", color="b")
    ax1.semilogy(np.add(atm["t"],temperaturverschiebung),atm["p"],label="$T_1 = T_0 + %i\,K$"%temperaturverschiebung, color="b",ls="dashed")

    ax1.invert_yaxis()
    ax1.set_ylim(100000,0)

    ax1.set_xlabel("Temperatur [K]\n\n(a)", fontsize=font)
    ax1.set_ylabel("Druck [Pa]",fontsize=font)
    legend = ax1.legend(loc="upper right",fontsize=font,frameon=True)
    legend.set_facecolor = "white"
    ax1.set_title("Temperaturverschiebung",fontsize=font)

    for tick in ax1.xaxis.get_major_ticks():
        tick.label.set_fontsize(16)

    for tick in ax1.yaxis.get_major_ticks():
        tick.label.set_fontsize(16)

    #==============================
    # 2. Plot: H2O Multiplikation
    #==============================

    ax2.loglog(atm["H2O"],atm["p"],label="$H2O_{0}$ bei $T_{0}$",color="red")

    RH = VMR2RH(atm["H2O"],atm["p"],atm["t"])
    RH = np.multiply(RH,1.5)
    VMR = RH2VMR(RH,atm["p"],atm["t"])
    ax2.loglog(VMR,atm["p"],label="$H2O_1$ bei $T_0$",color="green")


    atm["t_new"] = np.add(atm["t"],temperaturverschiebung)




    RH = VMR2RH(atm["H2O"],atm["p"],atm["t"])
    ax2.loglog(RH2VMR(RH,atm["p"],atm["t_new"]), atm["p"], label="$H2O_0$ bei $T_1$", ls="dashed", color="red")

    RH = np.multiply(RH,3)
    VMR = RH2VMR(RH,atm["p"],atm["t_new"])
    ax2.loglog(VMR,atm["p"],label="$H2O_1$ bei $T_1$",ls="dashed",color="green")


    ax2.set_xlabel("Wasserdampfgehalt [VMR]\n\n(b)",fontsize=font)
    legend = ax2.legend(loc="upper right",fontsize=font,frameon=True)
    legend.set_facecolor = "white"
    ax2.set_title("H2O Multiplikation",fontsize=font)

    for tick in ax2.xaxis.get_major_ticks():
        tick.label.set_fontsize(16)





    #==============================
    # 3. Plot: H2O Addition
    #==============================

    ax3.loglog(atm["H2O"],atm["p"],label="$H2O_0$ bei $T_0$",color="red")

    RH = VMR2RH(atm["H2O"],atm["p"],atm["t"])
    RH[:3] = 0.90
    VMR = RH2VMR(RH,atm["p"],atm["t"])
    ax3.loglog(VMR,atm["p"],label="$H2O_1$ bei $T_0$",color="green")


    atm["t_new"] = np.add(atm["t"],temperaturverschiebung)




    RH = VMR2RH(atm["H2O"],atm["p"],atm["t"])
    ax3.loglog(RH2VMR(RH,atm["p"],atm["t_new"]), atm["p"], label="$H2O_0$ bei $T_1$", ls="dashed", color="red")
    RH[:3] = 0.90
    VMR = RH2VMR(RH,atm["p"],atm["t_new"])
    ax3.loglog(VMR,atm["p"],label="$H2O_1$ bei $T_1$",ls="dashed",color="green")



    ax3.set_xlabel("Wasserdampfgehalt [VMR]\n\n(c)",fontsize=font)
    legend = ax3.legend(loc="upper right",fontsize=font,frameon=True)
    legend.set_facecolor = "white"
    ax3.set_title("H2O Addition",fontsize=font)

    for tick in ax3.xaxis.get_major_ticks():
        tick.label.set_fontsize(16)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig("WV_displacement.png",dpi=400)


