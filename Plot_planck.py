import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import seaborn

def planck(T,v):
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

def m2v(m):
    c = 3e8
    return np.divide(c,m)

if __name__ == "__main__":
    seaborn.set()

    font = 16

    micro = 1e-6


    sw = m2v((0.38*micro,5*micro))
    lw = m2v((5*micro,100*micro))

    print(lw,sw)
    sonne_i = np.zeros(100000)
    erde_i = sonne_i.copy()
    frequency = sonne_i.copy()



    for i,v in enumerate(np.linspace(int(1e7), int(1e16), len(sonne_i))):
        sonne_i[i] = planck(6000, v)
        erde_i[i] = planck(280,v)
        frequency[i] = v

    fig,ax = plt.subplots(nrows=1,ncols=1,figsize=(16,6))
    plt.title("Plancksches Strahlungsgesetz", fontsize=20)
    ax.plot(frequency, np.divide(sonne_i,np.max(sonne_i)), color="orange",label="Sonne")
    ax.plot(frequency,np.divide(erde_i,np.max(erde_i)),color="blue",label="Erde")

    trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    ax.fill_between(frequency,0,1,where=((lw[1]<frequency) & (frequency<lw[0])),facecolor="red",alpha=0.5,transform=trans, label="langwelliger Bereich")
    ax.fill_between(frequency,0,1,where=((sw[1]<frequency) & (frequency<sw[0])),facecolor="yellow",alpha=0.5,transform=trans, label="kurzwelliger Bereich")


    ax.set_xlim(1e7,0.2e16)
    # ax.set_ylim(1e-20,1e-5)

    ax.set_xlabel("Frequenz [Hz]",fontsize=font)
    ax.set_ylabel("Intensität [$W\,m^{-2}\,sr^{-1}\,Hz^{-1}$]",fontsize=font)
    plt.gca().tick_params(axis='both', which='major', labelsize=16)

    ax.legend(loc="upper left", fontsize=font)
    plt.tight_layout()
    plt.savefig("Planck-funktion.png", dpi=200)
    plt.show()
