import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
from matplotlib.ticker import FuncFormatter
import seaborn

def planck_v(T, v):
    h = 6.62607004e-34
    c = 3e8
    k = 1.38064852e-23

    zaehler = np.multiply(2*h,np.power(v,3))
    klammer = np.subtract(
        np.exp(
            np.divide(np.multiply(h,v),
                      np.multiply(k,T))),
        1)

    power = np.multiply(c,c)
    nenner = np.multiply(power,klammer)


    B = np.divide(zaehler,nenner)
    if B < 0:
        print(zaehler,nenner,power,klammer)
    return B

def planck_l(T,l):
    h = 6.62607004e-34
    c = 3e8
    k = 1.38064852e-23

    zaehler = np.multiply(2*h,np.power(c,2))
    klammer = np.subtract(
        np.exp(
            np.divide(np.multiply(h,c),
                      np.multiply(np.multiply(k,T),l))),
        1)
    power = np.power(l,5)
    nenner = np.multiply(power,klammer)
    B = np.divide(zaehler,nenner)

    return B

def m2v(m):
    c = 3e8
    return np.divide(c,m)

def micrometer(x,pos):
    return "%i"%int(round(x*1e6,0))

if __name__ == "__main__":
    seaborn.set()

    font = 16

    micro = 1e-6


    # sw = m2v((0.38*micro,5*micro))
    # lw = m2v((5*micro,100*micro))

    sw = (0.38 * micro, 4.3 * micro)
    lw = (4.3 * micro, 100 * micro)

    print(lw,sw)
    sonne_i = np.zeros(100000)
    erde_i = sonne_i.copy()
    length = sonne_i.copy()



    for i,l in enumerate(np.linspace(0.001*micro, 50*micro, len(sonne_i))):
        sonne_i[i] = planck_l(6000, l)
        erde_i[i] = planck_l(280, l)
        length[i] = l

    formatter = FuncFormatter(micrometer)
    sonne_area = np.trapz(y=sonne_i,x=length)
    erde_area = np.trapz(y=erde_i,x=length)
    fig,ax = plt.subplots(nrows=1,ncols=1,figsize=(16,6))
    # plt.title("Plancksches Strahlungsgesetz", fontsize=20)
    ax.plot(length, np.divide(sonne_i,sonne_area), color="orange",label="Sonne")
    ax.plot(length,np.divide(erde_i,erde_area),color="blue",label="Erde")

    trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    ax.fill_between(length,0,np.nanmax(sonne_i),where=((lw[0]<length) & (length<lw[1])),facecolor="red",alpha=0.5,transform=trans, label="langwelliger Bereich")
    ax.fill_between(length,0,np.nanmax(sonne_i),where=((sw[0]<length) & (length<sw[1])),facecolor="yellow",alpha=0.5,transform=trans, label="kurzwelliger Bereich")

    # ax.ticklabel_format(axis="x",style="sci",scilimits=(0,0))
    ax.xaxis.set_major_formatter(formatter)
    ax.set_xlim(0,50e-6)
    ax.set_ylim(0,1e5)

    ax.set_xlabel("Wellenlänge [$\mu$m]",fontsize=font)
    ax.set_ylabel("Normierte Intensität [$m^{-1}$]",fontsize=font)
    plt.gca().tick_params(axis='both', which='major', labelsize=16)

    ax.legend(loc="upper right", fontsize=font)
    plt.tight_layout()
    plt.savefig("Planck-funktion.png", dpi=200)
    plt.show()
