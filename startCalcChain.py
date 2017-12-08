import os


os.system("python ../../python_svn/sfc_fluxes3.py")
os.chdir("/scratch/uni/u237/users/tmachnitzki/psrad/python_svn/")
print("============================")
print("Starting BSRN2IWV.py")
print("============================")
os.system("python BSRN2IWV.py")


