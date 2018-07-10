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
rmse_or_diff   = 1 #0: DIFF 1: RMSE

#history files related info
hist_path_str  = 'run'
cam_hist_str   = '.cam.h0.'
suffix         ='.nc'

#other files needed
inic_cond_file = 'inic_cond_file_list.txt'
var_file       = 'physup_calls.txt'

#plot related info
xlabel_file = 'xlabels.txt'
if(rmse_or_diff == 0):
   ylabel = 'Maximum Error in the temperature (K) field'
elif(rmse_or_diff == 1):
   ylabel = 'RMSE Error [T(K)]'

ymin  = 'N' #-1    # Use 'N' to unset it 
ymax  = 'N' #10.0  # Use 'N' to unset it 
xmin  = 0
title = 'CAM5 error growth (1 time step)'
clr   = ['c','g'] # for each case
lgnds = ['CAM5-revised', 'CAM5-default']


### USER INPUT ENDS ###
#Functions
def max_diff_var(ifile_test, ifile_cntl,  var_list, var_suffix ):
   eps = 1.e-16
   ftest = Dataset(ifile_test,  mode='r')
   fcntl = Dataset(ifile_cntl, mode='r')
   mdiff = [None] * len(var_list)
   i = 0
   for ivar in var_list:
      var = var_suffix+ivar
      if var in ftest.variables:
         vtest = ftest.variables[var.strip()][0,:,:,:] # first dimention is time (=0)
         vcntl = fcntl.variables[var.strip()][0,:,:,:] # first dimention is time (=0)
         diff  = np.amax(abs(vtest[:,:,:] - vcntl[:,:,:]), axis=None, out=None, keepdims=False)
         mdiff[i] = max([diff,eps])
         i += 1
         vtest = None
         vcntl = None
         var   = None
      else:
         print (var+' not in file')
   ftest.close()
   fcntl.close()
   return mdiff

def rmse_var(ifile_test, ifile_cntl,  var_list, var_suffix ):
   ftest = Dataset(ifile_test,  mode='r')
   fcntl = Dataset(ifile_cntl, mode='r')
   rmse = [None] * len(var_list)
   i = 0
   for ivar in var_list:
      var = var_suffix+ivar
      if var in ftest.variables:
         vtest    = ftest.variables[var.strip()][0,:,:,:] # first dimention is time (=0)
         vcntl    = fcntl.variables[var.strip()][0,:,:,:] # first dimention is time (=0)
         #reshape
         nx, ny, nz = vtest.shape #shape will be same for both arrays
         rmse[i]  = sqrt(mean_squared_error(vtest.reshape((nx,ny*nz)), vcntl.reshape((nx,ny*nz))))
         #rmse[i]  = np.sqrt(np.mean((vtest[:,:,:] - vcntl[:,:,:])**2))         
         i += 1
         vtest = None
         vcntl = None
         var   = None
      else:
         print (var+' not in file')
   ftest.close()
   fcntl.close()
   return rmse




#Functions ENDS!!!

if(len(cntl_case) != len(test_case)):
   print('Length of cntl_case and test_case is not same; cntl_case='+str(len(cntl_case))+' test_case='+str(len(test_case)))
   sys.exit()


year       = '0001' #year  is a str as I don't anticipate that it will change
month      = '01'   #month is a str as I don't anticipate that it will change
day        = '01'    #day   is a str as I don't anticipate that it will change
ts         = '00000'

#get list of variable suffix
with open(var_file, 'r') as fvar:
   var_list = fvar.readlines()
fvar.close()
var_list = map(str.strip,var_list)

#get xticklabel
with open(xlabel_file, 'r') as flbl:
   xlabels = flbl.readlines()
flbl.close()
xlabels = map(str.strip,xlabels)

ax = pl.gca()
axf = pl.gcf()
axf.set_facecolor('white') #set color of the plot
#ax.set_title(title, fontsize=35)
fn_cmn  = cam_hist_str+year + '-' + month + '-' + str(day) + '-'+ ts+suffix

for icase in range(0,len(test_case)):
   fn_cntl = cntl_case[icase] + fn_cmn
   fn_test = test_case[icase] + fn_cmn
   
   fn_path_test = cmn_path+'/'+test_case[icase]+'/'+hist_path_str+'/'+fn_test
   fn_path_cntl = cmn_path+'/'+cntl_case[icase]+'/'+hist_path_str+'/'+fn_cntl
   if(rmse_or_diff == 0):
      res         = max_diff_var(fn_path_test,fn_path_cntl,var_list,'T_')
   elif(rmse_or_diff == 1):
      res         = rmse_var(fn_path_test,fn_path_cntl,var_list,'T_')
   else:
      print('Error: Not a valid value for rmse_or_diff; rmse_or_diff is:'+str(rmse_or_diff))
      sys.exit()

   ax.semilogy(res,color=clr[icase],linestyle='-',marker='.',label=lgnds[icase], linewidth=4)
   pl.hold(True)
   

ax.set_xlim([0,len(res)])
ax.set_xticks(range(0,len(res)))
ax.set_xticklabels(xlabels, rotation=40, ha='center', fontsize=35)
ax.set_xlabel('Physical processes in the first time step', fontsize=35)
if(ymin != 'N' and ymax !='N'):
   ax.set_ylim([ymin,ymax])

ax.set_ylabel(ylabel, fontsize=35)
for label in ax.get_yticklabels(): 
   label.set_fontsize(35) 



#Draw plot
handles, labels = pl.gca().get_legend_handles_labels()
pl.legend(handles, labels, loc='best',fontsize=35)

pl.show()
