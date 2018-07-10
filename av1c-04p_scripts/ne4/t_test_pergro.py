#!/usr/bin/python

#Python version: python 2.7.8 and python/anaconda2

from netCDF4 import Dataset
from math import sqrt
from sklearn.metrics import mean_squared_error
import pylab as pl
import numpy as np
import sys
from scipy.stats import ttest_ind

#---------------------------------------------------------------------
# Paths,cntl and test cases
#---------------------------------------------------------------------
cmn_path = '/pic/scratch/sing201/csmruns/'
paths    = ['','','']

cases = ['ne4_av1c04p2_const_int','ne4_av1c04p2_zmconv_c0_ocn_0.045_const_int','ne4_av1c04p2_const_int']

case_flag = [0,1,1] #just a test
icase_cntl = 0      # index from the "cases" array
rmse_or_diff   = 1  #0: DIFF 1: RMSE
#---------------------------------------------------------------------
#History files related info
#---------------------------------------------------------------------
acme_hist_dir  = 'run'
cam_hist_str   = '.cam.h0.'
time           = '00000'
perturb_str    = ['wopert','pospert','negpert']
#---------------------------------------------------------------------
#Other files needed
#---------------------------------------------------------------------
inic_cond_file = 'inic_cond_file_list_se_ne4.txt'
var_file       = 'physup_calls_av1c.txt'

if(rmse_or_diff == 0):
   ylabel = 'Maximum Error in the temperature (K) field'
elif(rmse_or_diff == 1):
   ylabel = 'RMSE Error - T(K)'

#---------------------------------------------------------------------
#Function definitions
#---------------------------------------------------------------------
def rmse_diff_var(ifile_test, ifile_cntl,  var_list, var_suffix, rmse_or_diff,vars_to_skip):
   import os.path
   
   if isinstance(var_list,basestring): var_list =[var_list]
   if ( not os.path.isfile(ifile_test)):
      print('Test file:'+ifile_test+' doesnt exists; exiting....')
      sys.exit()
   if ( not os.path.isfile(ifile_cntl)):
      print('CNTL file:'+ifile_cntl+' doesnt exists; exiting....')
      sys.exit()
      

   ftest = Dataset(ifile_test,  mode='r')
   fcntl = Dataset(ifile_cntl, mode='r')   

   i = 0 #index of res array
   j = 0 #index for vars_to_skip array

   diff = np.zeros(shape=(np.count_nonzero(var_list)))
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
         if(vars_to_skip[j] == 0):
            if(vtest.all() == 0 or vcntl.all() == 0):
               j += 1
               continue
            else:
               print('variable '+var+' is not zero in file:'+ifile_test)
               sys.exit()

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
         j += 1
         vtest = None
         vcntl = None
         var   = None
      else:
         print (var+' not in file')
   ftest.close()
   fcntl.close()
   return diff

def all_nonzero_vars(ifile,var_list,var_suffix):
   print('Extracting non-zero variable indices')
   vars_to_skip = np.empty([len(var_list)])
   vars_to_skip[:] = -1
   ifile_handle = Dataset(ifile,  mode='r')
   i = 0
   for ivar in var_list:
      var = var_suffix+ivar
      if var in ifile_handle.variables:         
         vfile    = ifile_handle.variables[var.strip()][0,...] # first dimention is time (=0)
         if(vfile.all() == 0):
            print('variable:'+var+' is zero')
            vars_to_skip[i] = 0
      i = i + 1
   return vars_to_skip

#---------------------------------------------------------------------
# Functions ENDS
#---------------------------------------------------------------------

min_all = float("inf")
#---------------------------------------------------------------------
#Check if you have all the rquired info:
#---------------------------------------------------------------------
if(len(paths) != len(cases)):
   print("ERROR: paths and cases arrays has different lengths")
   print('Paths are:'+str(len(paths))+',cases are:'+str(len(cases)) )
   sys.exit()

#---------------------------------------------------------------------
#Get list of variable suffix
#---------------------------------------------------------------------
with open(var_file, 'r') as fvar:
   var_list = fvar.readlines()
fvar.close()
var_list = map(str.strip,var_list)


#---------------------------------------------------------------------
#Get list of inital condition files
#---------------------------------------------------------------------
with open(inic_cond_file, 'r') as finic:
   inic_list = finic.readlines()
finic.close()
inic_list = map(str.strip,inic_list)
#inic_list = inic_list[0:1] #temporary ##UNCOMMENT THIS LINE FOR FASTER TURNAROUND!!!!!!#####################################


#---------------------------------------------------------------------
#Check variables which are all zero in (preassumably) all files; we will skip these variable
#Form a single file name (lets take a file from control case)
#---------------------------------------------------------------------
case_name_cntl = cases[icase_cntl] + '_'+ inic_list[0].split('.nc')[0]+'_'+perturb_str[0]
extract_date   = list(reversed(inic_list[0].rsplit('.')))[1].split('-00000')[0]
fpath          = cmn_path+'/'+case_name_cntl+'/'+acme_hist_dir+'/'+case_name_cntl+cam_hist_str+extract_date+'-'+time+'.nc'
vars_to_skip = all_nonzero_vars(fpath,var_list,'T_')
nzero_var_list_len = np.count_nonzero(vars_to_skip)

#---------------------------------------------------------------------
# Set var_list to intended  index (last index here)
#---------------------------------------------------------------------
last_non_zero_ind = (len(vars_to_skip) - 1) - np.where(vars_to_skip[::-1]==-1)[0][0]
var_for_data = [var_list[last_non_zero_ind]] #convert to list (use of []))

#---------------------------------------------------------------------
#create an empty array with dims[# of cases, # of inic conds, # of perts, # of check point vars]
#currently hardwired 2 for negpert and pospert
#---------------------------------------------------------------------
res = np.empty([len(cases),len(inic_list),len(perturb_str)])
ipath_cntl = cmn_path+'/'+paths[icase_cntl]

#---------------------------------------------------------------------
#Loop through each case and prepare P+ and P- curves
#---------------------------------------------------------------------
for icase in range(0,len(cases)):
   if(icase == icase_cntl or case_flag[icase] != 1):
      continue
   print( 'working on: '+ cases[icase])
   #---------------------------------------------------------------------
   #Form path
   #---------------------------------------------------------------------
   ipath = cmn_path+'/'+paths[icase]
   icond = -1
   for acond in  inic_list: #use "for icond, acond in enumerate(inic_list, start=0):" logic here instead of icond=-1 etc.
      icond += 1
      #---------------------------------------------------------------------
      #Form location of file [acond is string is split twice to make use of "time" variable]
      #---------------------------------------------------------------------
      acond_1 = list(reversed(acond.rsplit('.')))[1]
      acond_2 = acond_1.split('-00000')[0]            
      case_name_cntl = cases[icase_cntl] + '_'+ acond.split('.nc')[0]+'_'+perturb_str[0]

      #---------------------------------------------------------------------
      #Following for loop loops through perturbations
      #---------------------------------------------------------------------
      ipert = -1
      for apert in perturb_str: #use "for ipert, apert in enumerate(perturb_str[1:3], start=0):" logic here instead of ipert=-1 etc.
         ipert += 1
         #---------------------------------------------------------------------
         #form case name
         #---------------------------------------------------------------------
         case_name  = cases[icase] + '_'+ acond.split('.nc')[0]+'_'+apert
         ifile      = ipath+'/'+case_name+'/'+acme_hist_dir+'/'+case_name+cam_hist_str+acond_2+'-'+time+'.nc'
         ifile_cntl = ipath_cntl+'/'+case_name_cntl+'/'+acme_hist_dir+'/'+case_name_cntl+cam_hist_str+acond_2+'-'+time+'.nc'
         res[icase,icond,ipert]  = rmse_diff_var(ifile, ifile_cntl, var_for_data, 'T_',rmse_or_diff,vars_to_skip)         
   
#---------------------------------------------------------------------   
#compute t test
#---------------------------------------------------------------------
a = res[1,:,:].flatten()         
b = res[2,:,:].flatten()         


t, p = ttest_ind(a, b, equal_var=False)
print("ttest_ind:            t = %g  p = %g" % (t, p))


