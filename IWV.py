from BSRN2IWV import getValueAtDate, getIWVFromTable, height_correction, download_bsrn, getAtm
import numpy as np
from functools import lru_cache
import os


def getGoodDates(bsrn_file):

    date = []
    lw = []
    temp = []
    sw = []
    dif = []
    for line in bsrn_file:
        if np.logical_and(-0.1 <= line[4], line[4] < 1):
            date.append(line[0])
            lw.append(line[1])
            temp.append(line[2])
            sw.append(line[3])
            dif.append(line[4])

    date = np.asarray(date)
    lw = np.asarray(lw)
    sw = np.asarray(sw)
    dif = np.asarray(dif)
    temp = np.asarray(temp)
    array = np.stack((date, lw, temp, sw, dif), axis=1)

    return array



def BSRN2IWV(datestr,station,tag,station_height,atm, atm_name,verbose):
    line_counter = 0

    # aeronet = get_iwv_from_aeronet(aeronetPath=aeronetPath, station=station,verbose=verbose)
    # aeronet_at_date = getIWVAtDate(datestr,aeronet)
    # # aeronet_good_dates = searchGoodDate(aeronet_at_date)
    # aeronet_good_dates = aeronet_at_date
    # if len(aeronet_good_dates) == 0:
    #     if verbose >= 3:
    #         print("No good dates found in AERONET for this month.")
    #         print("--------------------------------------------------")
    #     return None



    BSRN_FILE_NAME = tag + "_radiation_" + datestr[:4] + "-" + datestr[4:6] + ".tab"
    FILE = BSRN_FILE_PATH + station + "/" + BSRN_FILE_NAME

    if verbose >= 2:
        print(station + ", " + tag + ", " + atm_name + ", " + datestr)

    bsrn_raw = download_bsrn(tag,datestr,verbose,verify=False)
    if np.all(bsrn_raw) == None:
        if verbose >= 3:
            print("No data in BSRN to continue")
            print("--------------------------------------------------")
        return None

    good_dates = getGoodDates(bsrn_raw)

    #prepare File for writing out data:

    result_path = "results_BSRN/"+station+"/"+atm_name+"/"
    if not os.path.isdir(result_path):
        os.mkdir(result_path)

    write_file = result_path + station + datestr[0:6] + ".csv"
    with open(write_file,"w") as f:
        f.write("#Calculated and measured integrated watervapor for %s.\n" %station)
        f.write("#Used atmosphere: %s\n"%atm_name)
        f.write("\n")
        f.write("Date ; Time ; T[K] ; LWdown[W/m2] ; Calculated_IWV[kg/m2] ; aeronet_IWV[kg/m2] ; Distance\n")

        for good_date in good_dates:

            good_str = good_date
            # print(good_date)

            bsrn = getValueAtDate(good_date[0], bsrn_raw)
            # print(bsrn)
            # elements_cl = Parallel(n_jobs=2, verbose=0)(delayed(getIWVFromTable)(bsrn[i,0],bsrn[i,1],bsrn[i,2], atm_name,atm) for i in range(0,len(bsrn[:]),1))
            elements_cl = [getIWVFromTable(bsrn[i,0],bsrn[i,1],bsrn[i,2], atm_name,atm) for i in range(0,len(bsrn[:]),1)]

            date_cl = []
            for element in elements_cl:
                    date_cl.append(element[0])
            dates = np.asarray(date_cl)

            array = np.array([x for x in elements_cl],dtype=([("date", "S20"), ("T", "f8"), ("LW", "f8"), ("iwv", "f8"),("distance","f8")]))

            IWV = {}
            IWV['date'] = dates
            IWV["T"] = array['T']
            IWV["LW"] = array['LW']
            IWV["IWV"] = np.multiply(array["iwv"],height_correction(station_height))
            # IWV["IWV"] = array["iwv"]
            IWV["distance"] = array["distance"]
            IWV["IWV_AERONET"] =good_date[1] * 10

            if len(IWV['IWV']) == 0:
                if verbose >= 1:
                    print('weird mistake.')
                continue

            if IWV['IWV'][0] > -20:
                if 0 < IWV['date'][0].hour <24:
                    line_counter += 1
                    f.write(
                        IWV['date'][0].strftime("%x") + " ; " +
                        IWV['date'][0].strftime("%X") + " ; " +
                        str(IWV['T'][0]) + " ; " +
                        str(IWV['LW'][0]) + " ; " +
                        str(IWV['IWV'][0]) + " ; " +
                        str(IWV['IWV_AERONET']) + " ; " +
                        str(IWV['distance'][0]) +
                        "\n")

    if line_counter == 0:
        os.remove(write_file)
        if verbose >= 3:
            print("No valid Data written for this month")
    if verbose >= 2:
        print("----------------------------------------------------")

if __name__ == "__main__":
    BSRN_FILE_PATH = "/Users/u300844/t7home/tmachnitzki/psrad/BSRN/"

    datestr= "20150101"
    station = "Cabauw"
    tag = "cab"
    height = 0
    atm_name = "midlatitude-winter"
    atm = getAtm(atm_name)
    bsrn = BSRN2IWV(datestr=datestr,station=station,tag=tag,station_height=height,atm=atm, atm_name=atm_name,verbose=100)