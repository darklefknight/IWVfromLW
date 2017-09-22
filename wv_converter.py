import numpy as np

def e2mv(e, p, T):
    """
    konvertiert partialdruck zu (Massen-)Mischungsverhältnis.
    Quelle: www.schweizer-fn.de/lueftung/feuchte/feuchte.php
    """
    Rw = 461.51  # J/kg*k
    Rl = 287.058

    Rho_w = np.divide(e, np.multiply(Rw, T))  # Dichte des Wasserdampfs
    Rho_t = np.divide(np.subtract(p, e), np.multiply(Rl, T))  # Dichte der trockenen Luft

    mv = np.divide(Rho_w, Rho_t)
    return mv


def e2q(e, p):
    q = np.divide(np.multiply(0.622, e), np.subtract(p, np.multiply(0.378, e)))
    return q


def q2VMR(q):
    MwMd = 0.622  # Mw/Md = 0.622
    VMR = np.divide(q, (np.add(np.multiply(np.subtract(1, q), MwMd), q)))

    return VMR


def e2Rho_v(e, T):
    """
    Konvertiert Partialdruck von Wasserdampf zu Massendichte.
    Quelle: Vorlesung Wolkenphysik (Bühler) 03-Wasserdampf Folie 15
    """
    Rw = 461.51  # J/kg*k
    Rho_v = np.divide(e, np.multiply(Rw, T))
    return Rho_v


def VMR2q(VMR):
    MdMw = 1 / 0.622  # Mw/Md = 0.622
    q = np.divide(VMR, (np.add(np.multiply(np.subtract(1, VMR), MdMw), VMR)))

    return q


def q2e(q, p):
    factor = np.add(np.multiply(0.378, q), 0.622)
    e = np.divide(np.multiply(q, p), factor)
    return e


def VMR2RH(vmr, p, T):
    """
    stolen from typhon
    """
    import typhon as tp
    return np.divide(np.multiply(vmr, p), tp.atmosphere.thermodynamics.e_eq_water_mk(T))


def RH2VMR(RH, p, T):
    import typhon as tp
    return np.divide(np.multiply(RH, tp.atmosphere.thermodynamics.e_eq_water_mk(T)), p)


def ppm2e(ppm, P):  # TODO: Check all wv-functions for correctness
    """
    Convertes Watervapor measured in ppm to Watervaporpressure.
    P in Pa!
    """
    R = 8.314510  # J/mol*k
    Rw = 461.5  # J/kg*k
    M = 18.02 * 1e-3  # kg/mol

    factor = (Rw / R) * M

    e = np.multiply(np.multiply(np.multiply(ppm, P), factor), 1e-6)
    return e


def ppm2gpcm2(ppm):
    pass


def es(T):
    """
    T in Kelvin!!
    returns es in Pa.

    Formel von: www.schweizer-fn.de/lueftung/feuchte/feuchte.php
    """
    T = np.add(T, -273.15)
    power = np.multiply(17.62, np.divide(T, np.add(T, 243.12)))
    return np.multiply(611.2, np.exp(power))


def e2ppm(e, P):
    R = 8.314510  # J/mol*k
    Rw = 461.51  # J/kg*k
    M = 18.02 * 1e-3  # kg/mol

    factor = 1e6 * (R / (Rw * M))

    ppm = np.multiply(np.multiply(e, P), factor)
    return ppm


def e2RH(e, es):
    RH = np.divide(e, es)
    return RH


def RH2e(RH, es):
    e = np.multiply(RH, es)
    return e


def RH2Td(T, RH):
    '''
    Calculates the Dewpointtemperature from a given Temperature T and Relative Humidity RH
    #z_e = water vapor pressure
    #z_es = saturation water vapor pressure
    #T = temperature
    #tempd = dewpoint temperature
    #RH = relative Humidity '''

    z_es = 610.78 * np.exp(17.08085 * (T) / (235 + (T)))
    z_e = RH * z_es / 100
    tempd = (235 * np.log(z_e / 610.5)) / (17.1 - np.log(z_e / 610.78))
    return tempd