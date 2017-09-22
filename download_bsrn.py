import ftplib
import gzip
import os
import numpy as np
from datetime import datetime as dt
import calendar

def download_bsrn(station_tag,MMYYYY):
    station_tag = "bar"
    path = station_tag
    MMYY = MMYYYY[:2] + MMYYYY[-2:]
    filename = station_tag + MMYY + ".dat.gz"

    print(filename)

    month = int(MMYY[:2])
    year = int(MMYYYY[-4:])

    days_in_month = calendar.monthrange(year,month)[1]
    dates = []
    lw = []

    # download data from ftp-server:
    ftp = ftplib.FTP("ftp.bsrn.awi.de")
    ftp.login("bsrnftp", "bsrn1")
    ftp.cwd(path)
    ftp.retrbinary("RETR " + filename, open("tmp/"+filename, 'wb').write)
    ftp.quit()

    counter = 0
    with gzip.open("tmp/"+ filename, "rb") as f:
        #skip header:
        old_line = " "
        line = f.readline().decode()
        while not "*C0100" in line:
            line = f.readline().decode()
            if line == old_line:
                counter += 1
                if counter == 100:
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
            line_lw = line2[4]
            lw.append(line_lw)

    os.remove("tmp/" + filename)

    dates = np.asarray(dates)
    lw = np.asarray(lw)
    array = np.stack((dates,lw),axis=1)
    return array