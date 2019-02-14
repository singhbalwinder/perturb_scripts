#!/usr/bin/python

from netCDF4 import Dataset
from math import sqrt
from sklearn.metrics import mean_squared_error
import numpy as np
import os
import sys


def rmse_diff_var(ifile_test, ifile_cntl,  var_list, var_suffix, rmse_or_diff, index=False ):

#------------------ARGS-------------------------
#ifile_test: path of test file
#ifile_cntl: path of control file
#var_list  : List of all variables
#var_suffix: Suffix for var_list (e.g. T_, S_ QV_ etc.)
#rmse_or_diff: Compue RMSE(1) or DIFF(0)
#index       : (Optional) if we want to print lat lon for the point having max RMSE or DIFF
#-----------------------------------------------

   #pdb.set_trace()
   # See if the files exists or not....
   if ( not os.path.isfile(ifile_test)):
      print('Test file:'+ifile_test+' doesnt exists; exiting....')
      sys.exit()
   if ( not os.path.isfile(ifile_cntl)):
      print('CNTL file:'+ifile_cntl+' doesnt exists; exiting....')
      sys.exit()


   ftest = Dataset(ifile_test,  mode='r')
   fcntl = Dataset(ifile_cntl, mode='r')

   #if max RMSE/DIFF is to be printed, extract lat lons from a file
   if(index):
      lat = ftest.variables['lat']
      lon = ftest.variables['lon']

   diff = np.zeros(shape=(len(var_list)))
   icntvar = 0
   if (rmse_or_diff == 1):
      is_se = (len(ftest.variables[var_suffix+var_list[icntvar]].dimensions)==3) # see if it is SE grid
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
            diff[icntvar] = max([tmp,eps])
         else:
            #reshape for RMSE
            if(is_se ):
               nx, ny = vtest.shape #shape will be same for both arrays
            else:
               nx, ny, nz = vtest.shape #shape will be same for both arrays
            diff[icntvar]  = sqrt(mean_squared_error(vtest.reshape((nx,ny*nz)), vcntl.reshape((nx,ny*nz))))
            
         if(index):
            diff_arr = abs(vtest[...] - vcntl[...])
            max_diff = np.amax(diff_arr)
            ind_max = np.unravel_index(diff_arr.argmax(),diff_arr.shape)
            print_str = var+' '+str(max_diff)+' '+str(vtest[ind_max])+' ' +str(vcntl[ind_max])+' '+str(lat[ind_max[1]])+' '+ str(lon[ind_max[1]])+' '+str(ind_max[0])
            print("{}".format(print_str))


         #normalize by mean values of the field in the control case
         mean_cntl = np.mean(vcntl)
         if(mean_cntl != 0.0):
            diff[icntvar] = diff[icntvar]/mean_cntl
         else:
            diff[icntvar] = 0.0
            # if mean is zero, we assume all vcntl values are zero. If they are not
            # that means it has equal no. of +ve and -ve values, which is rare and unusal
            # so STOP the script!
            if(vcntl.all()!=0.0):
               print("mean of cntl var is zero but not all values are zero. Exiting.....")
               sys.exit()

         icntvar += 1
         vtest = None
         vcntl = None
         var   = None
      else:
         print (var+' not in file')

   ftest.close()
   fcntl.close()
   return diff
