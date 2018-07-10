#!/usr/bin/python

from netCDF4 import Dataset
from math import sqrt
from sklearn.metrics import mean_squared_error
import numpy as np
import os
import sys


def rmse_diff_var(ifile_test, ifile_cntl,  var_list, var_suffix, rmse_or_diff ):
   #pdb.set_trace()
   if ( not os.path.isfile(ifile_test)):
      print('Test file:'+ifile_test+' doesnt exists; exiting....')
      sys.exit()
   if ( not os.path.isfile(ifile_cntl)):
      print('CNTL file:'+ifile_cntl+' doesnt exists; exiting....')
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
         #print(str(var)+":"+str(diff[i]))
         i += 1
         vtest = None
         vcntl = None
         var   = None
      else:
         print (var+' not in file')

   ftest.close()
   fcntl.close()
   return diff
