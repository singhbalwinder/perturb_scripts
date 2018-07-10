import matplotlib.pyplot as plt
from scipy.io import netcdf


f = netcdf.netcdf_file('/dtemp/sing201/acme1/other_machines/mira/archive/acme_mltscr_qsmall_mic_ibm_YE000.cam2.i.0001-01-02-00000_wopert/atm/hist/acme_mltscr_qsmall_mic_ibm_YE000.cam2.i.0001-01-02-00000_wopert.cam.h0.0001-01-02-00000.nc', 'r')#,mmap=False)
var = f.variables['T_pcwdet']

#print time.units
#print time.shape
#print time[:]
f.close(self)








#plt.plot([1,2,3,4])
#plt.ylabel('some numbers')
#plt.show()
