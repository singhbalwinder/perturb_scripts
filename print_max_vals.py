#!/usr/bin/python
#---------------------------------------------------------------------
#Python version: Load python/2.7.9(default) and python_anaconda3/2.3.0
#---------------------------------------------------------------------

from netCDF4 import Dataset
from math import sqrt
from sklearn.metrics import mean_squared_error
import pylab as pl
import numpy as np
import sys


cmn_path       = '/pic/scratch/mawe927/csmruns/'
case1          = 'ne30_fc5_new01_default_const_int_init_gen_clim_FC5_default.cam.i.2008-01-01-00000_wopert'
case2          = 'ne30_fc5_new01_default_const_int_init_gen_clim_FC5_default.cam.i.2008-01-01-00000_pospert'
rmse_or_diff   = 1 #0: DIFF 1: RMSE

#---------------------------------------------------------------------
#history files related info
#---------------------------------------------------------------------   
acme_hist_dir  = 'run'
cam_hist_str   = '.cam.h0.'
time           = '00000'#'00000' 
#---------------------------------------------------------------------
#other files needed
#---------------------------------------------------------------------
var_file       = 'physup_calls_fc5.txt'

# USER INPUT ENDS
#---------------------------------------------------------------------
#=====================================================================

#---------------------------------------------------------------------
#Functions
#---------------------------------------------------------------------
def rmse_diff_var(ifile_test, ifile_cntl,  var_list, var_suffix, rmse_or_diff ):
   import os.path
   
   if ( not os.path.isfile(ifile_test)):
      print('Test file: '+ifile_test+' doesnt exists; exiting....')
      sys.exit()
   if ( not os.path.isfile(ifile_cntl)):
      print('CNTL file: '+ifile_cntl+' doesnt exists; exiting....')
      sys.exit()
   ftest = Dataset(ifile_test,  mode='r')
   fcntl = Dataset(ifile_cntl, mode='r')

   diff = np.zeros(shape=(len(var_list)))#
   i = 0
   if (rmse_or_diff == 1):
      is_se = (len(ftest.variables[var_suffix+var_list[i]].dimensions)==3) # see if it is SE grid
      nz = 1
   else:
      eps = 1.e-16
   for ivar in var_list:
      var = var_suffix+ivar
      if var in ftest.variables:
         vtest    = ftest.variables[var.strip()][0,...] # first dimention is time (=0)
         vcntl    = fcntl.variables[var.strip()][0,...] # first dimention is time (=0)
         if(rmse_or_diff == 0):
            tmp  = np.amax(abs(vtest[...] - vcntl[...]), axis=None, out=None, keepdims=False)
            diff[i] = max([tmp,eps])
         else:
            #reshape for RMSE
            if(is_se ):
               nx, ny = vtest.shape #shape will be same for both arrays
            else:
               nx, ny, nz = vtest.shape #shape will be same for both arrays
            diff[i]  = sqrt(mean_squared_error(vtest.reshape((nx,ny*nz)), vcntl.reshape((nx,ny*nz))))
         i += 1
         vtest = None
         vcntl = None
         var   = None
      else:
         print (var+' not in file')
      
   ftest.close()
   fcntl.close()
   return diff

##===============================================# Functions ENDS #================================================##


#get list of variable suffix
with open(var_file, 'r') as fvar:
   var_list = fvar.readlines()
fvar.close()
var_list = list(map(str.strip,var_list))

i = 0

extract_date   = list(reversed(case2.rsplit('.')))[0].split('-00000')[0]

fn_path1 = cmn_path+'/'+case1+'/'+acme_hist_dir+'/'+case1+cam_hist_str+extract_date+'-'+time+'.nc'
fn_path2 = cmn_path+'/'+case2+'/'+acme_hist_dir+'/'+case2+cam_hist_str+extract_date+'-'+time+'.nc'

res      = rmse_diff_var(fn_path1,fn_path2,var_list,'NUM_A3_',rmse_or_diff)
print (res)
