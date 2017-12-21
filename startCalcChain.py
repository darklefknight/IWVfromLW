import os


os.system("python ../../python_svn/sfc_fluxes2.py")
os.chdir("/scratch/uni/u237/users/tmachnitzki/psrad/python_svn/")


print("============================")
print("Starting BSRN2IWV.py")
print("============================")
os.system("python BSRN2IWV.py")

print("============================")
print("Starting plotResults.py")
print("============================")
try:
    os.system("python plotResults.py ")
except:
    print("------------------------------------")
    print("ERROR: Something went wrong while plotting results")
    print("------------------------------------")

print("============================")
print("Starting Statistics.py")
print("============================")
try:
    os.system("python Statistics.py ")
except:
    print("------------------------------------")
    print("ERROR: Something went wrong while plotting statistics")
    print("------------------------------------")

print("============================")
print("Starting plotPSRADResult.py")
print("============================")
try:
    os.system("python plotPSRADResult.py ")
except:
    print("------------------------------------")
    print("ERROR: Something went wrong while plotting psrad results")
    print("------------------------------------")
