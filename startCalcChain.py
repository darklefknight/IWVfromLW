import os


os.system("python ../../python_svn/sfc_fluxes2.py")
os.chdir("/scratch/uni/u237/users/tmachnitzki/psrad/python_svn/")
os.system("python BSRN2IWV.py")


