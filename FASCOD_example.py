from sfc_fluxes2 import get_sadata_atmosphere, get_fascod_atmosphere
import matplotlib.pyplot as plt
from sfc_fluxes2 import calc_hr


if __name__ == "__main__":
    FASCOD_PATH = "/scratch/uni/u237/users/tlang/arts-xml-data/planets/Earth/Fascod/"
    home = "/scratch/uni/u237/users/tmachnitzki/psrad/python_svn/"

    fascod_atm = get_sadata_atmosphere("tropical")
    fascod_atm= get_fascod_atmosphere(FASCOD_PATH,"tropical")
    results_lw,H2O, Tsfc = calc_hr(fascod_atm, 'lw')

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, sharey=True, figsize=(9,9))
    fig.suptitle("US standard")
    ax1.plot(fascod_atm['t'], fascod_atm['p'] * 1e-2)
    ax1.set_ylim(1013, 0.1)
    ax1.set_ylabel('Pressure (hPa)')
    ax1.set_xlabel('Termperature (K)')

    ax2.plot(fascod_atm['H2O']*1e6,fascod_atm['p']* 1e-2)
    ax2.set_ylim(1013, 0.1)
    ax2.set_ylabel('Pressure (hPa)')
    ax2.set_xlabel('Humidity (ppmv)')
    ax2.set_yscale('log')

    ax3.plot(results_lw['flxd_clr'][:-1],fascod_atm['p'] * 1e-2)
    ax3.set_ylabel('Pressure (hPa)')
    ax3.set_xlabel('LW downward flux (W/m2)')

    plt.savefig(home +"fascod_example_us.png",dpi=500)