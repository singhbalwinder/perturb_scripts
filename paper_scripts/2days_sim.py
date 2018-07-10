#!/usr/bin/python

#Python version: Load python/2.7.9(default) and python_anaconda3/2.3.0

from netCDF4 import Dataset
from math import sqrt
from sklearn.metrics import mean_squared_error
import pylab as pl
import numpy as np
import sys

###
# NOTE: This script assumes that simulation is run for a few days only and output is every day!! Limitation is imposed by varibale "ndays"
###

cmn_path  = '/pic/projects/climate/sing201/acme1/other_machs/other_machines_perturb/eos/'
cntl_case = ['acme_pergro_true','acme_pergro_false']
test_case = ['acme_pergro_true_pospert','acme_pergro_false_pospert']

rmse_or_diff   = 0 #0: DIFF 1: RMSE

#history files related info
hist_path_str  = 'run'
cam_hist_str   = '.cam.h0.'
suffix         ='.nc'
tstep          = 1800      # time step (s)
ndays          = 1         # number of days of sim

#plot related info
xlabel = 'Time step #'
if(rmse_or_diff == 0):
   ylabel = 'Maximum Error in the temperature (K) field'
elif(rmse_or_diff == 1):
   ylabel = 'RMSE Error in the temperature (K) field'

ymin  = -1
ymax  = 10.0
xmin  = 0
title = 'CAM5 error growth (2 days)'
clr   = ['c','g'] # for each case
lgnds = ['CAM5-With Fixes', 'CAM5-default']


### USER INPUT ENDS ###

#Functions
def onevar_max_diff(ifile_test, ifile_cntl,  var ):
    ftest = Dataset(ifile_test,  mode='r')
    fcntl = Dataset(ifile_cntl, mode='r')
    if var in ftest.variables:
        vtest = ftest.variables[var.strip()][0,:,:,:] # first dimention is time (=0)
        vcntl = fcntl.variables[var.strip()][0,:,:,:] # first dimention is time (=0)
        mdiff  = np.amax(abs(vtest[:,:,:] - vcntl[:,:,:]), axis=None, out=None, keepdims=False)
    else:
        print (var+' not in file')
    ftest.close()
    fcntl.close()
    return mdiff

def onevar_rmse(ifile_test, ifile_cntl,  var ):
   #print('TEST:'+ifile_test)
   #print('CNTL:'+ifile_cntl)
   ftest = Dataset(ifile_test,  mode='r')
   fcntl = Dataset(ifile_cntl, mode='r')
   if var in ftest.variables:
       vtest    = ftest.variables[var.strip()][0,:,:,:] # first dimention is time (=0)
       vcntl    = fcntl.variables[var.strip()][0,:,:,:] # first dimention is time (=0)
       #reshape
       nx, ny, nz = vtest.shape #shape will be same for both arrays
       rmse       = sqrt(mean_squared_error(vtest.reshape((nx,ny*nz)), vcntl.reshape((nx,ny*nz))))
       #rmse      = np.sqrt(np.mean((vtest[:,:,:] - vcntl[:,:,:])**2))
   else:
       print (var+' not in file')
   ftest.close()
   fcntl.close()
   return rmse

        
#Functions ENDS!!!
if(len(cntl_case) != len(test_case)):
   print('Length of cntl_case and test_case is not same; cntl_case='+str(len(cntl_case))+' test_case='+str(len(test_case)))
   sys.exit()

nhr_1day = 24
nmin_1hr = 60
nsec_1min = 60
nsteps_1day = (nhr_1day*nmin_1hr*nsec_1min)/tstep # no. of time steps in 1 day
nsteps_sim  = ndays*(nhr_1day*nmin_1hr*nsec_1min)/tstep # no. of time steps in simulation

secs_stamp = 0
year       = '0001' #year  is a str as I don't anticipate that it will change
month      = '01'   #month is a str as I don't anticipate that it will change
day        = 1      #day will change so I used an integer

res = np.empty([nsteps_sim])
ax = pl.gca()
axf = pl.gcf()
axf.set_facecolor('white') #set color of the plot
#ax.set_title(title, fontsize=35)

for icase in range(0,len(cntl_case)):
   print('processing:'+cntl_case[icase])    
   for itime in xrange(nsteps_sim): 
      fn_cmn  = cam_hist_str+year + '-' + month + '-' + str(day).zfill(2) + '-'+ str(secs_stamp).zfill(5)+suffix
      fn_cntl = cntl_case[icase] + fn_cmn
      fn_test = test_case[icase] + fn_cmn
        
      fn_path_test = cmn_path+'/'+test_case[icase]+'/'+hist_path_str+'/'+fn_test
      fn_path_cntl = cmn_path+'/'+cntl_case[icase]+'/'+hist_path_str+'/'+fn_cntl
      if(rmse_or_diff == 0 ):
         res[itime] = onevar_max_diff(fn_path_test,fn_path_cntl,'T')
      elif(rmse_or_diff == 1):
         res[itime] = onevar_rmse(fn_path_test,fn_path_cntl,'T')
         
      if(secs_stamp != 0 and (itime+1)%nsteps_1day == 0):
         secs_stamp = 0
         day = day + 1
      else:
         secs_stamp = secs_stamp +  tstep

   ax.semilogy(res,color=clr[icase],linestyle='-',marker='.',label=lgnds[icase])
   pl.hold(True)
ax.set_xticks(range(0,nsteps_sim))
ax.set_xticklabels(range(0,nsteps_sim), fontsize=10)
ax.set_ylabel(ylabel, fontsize=15)
ax.set_xlabel('Time steps', fontsize=15)


#Draw plot
handles, labels = pl.gca().get_legend_handles_labels()
pl.legend(handles, labels, loc='best')

pl.show()
