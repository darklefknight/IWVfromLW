import ftplib
import gzip
import os
import numpy as np
from datetime import datetime as dt
import calendar

def download_bsrn(station_tag,datestr,verbose=4):
    path = station_tag
    year_str = datestr[:4]
    month_str = datestr[4:6]
    day_str = datestr[6:]
    MMYY = month_str + year_str[2:]
    filename = station_tag + MMYY + ".dat.gz"

    if verbose >= 4:
        print(filename)

    month = int(month_str)
    year = int(year_str)

    days_in_month = calendar.monthrange(year,month)[1]
    dates = []
    lw = []
    temp = []

    # download data from ftp-server:
    ftp = ftplib.FTP("ftp.bsrn.awi.de")
    ftp.login("bsrnftp", "bsrn1")
    ftp.cwd(path)
    if filename in ftp.nlst():
        ftp.retrbinary("RETR " + filename, open("tmp/"+filename, 'wb').write)
    else:
        if verbose >= 4:
            print("File %s does not exist on ftp.bsrn.awi.de"%filename)
        return None

    ftp.quit()

    counter = 0
    try:
        with gzip.open("tmp/"+ filename, "rb") as f:
            #skip header:
            old_line = " "
            line = f.readline().decode()
            while ((not "*C0100" in line) and (not "*U0100" in line)):
                line = f.readline().decode()
                if line == old_line:
                    counter += 1
                    if counter == 1000:
                        if verbose >= 4:
                            print("No data in file %s" %filename)
                        return None

                old_line = line


            #get data:
            for i in range(1440*days_in_month):
                line1 = f.readline().decode().split()
                line2 = f.readline().decode().split()

                #get the date:
                day = int(line1[0])
                minute_running = int(line1[1])
                hour = int(np.divide(minute_running,60))
                minute = np.mod(minute_running,60)
                line_date = dt(year,month,day,hour,minute)
                dates.append(line_date)

                #get the data:
                line_lw = float(line2[4])
                lw.append(line_lw)

                line_temp = float(line2[8])
                temp.append(line_temp)

        os.remove("tmp/" + filename)

        dates = np.asarray(dates)
        lw = np.asarray(lw)
        temp = np.asarray(temp)
        array = np.stack((dates,temp,lw),axis=1)
        return array

    except:
        if verbose >= 4:
            print("Error while trying to extract %s" %filename)
        return None
