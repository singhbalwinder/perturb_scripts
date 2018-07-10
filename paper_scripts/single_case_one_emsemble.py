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

cmn_path       = '/pic/scratch/sing201/csmruns/'
main_case      = 'ne30_av1c04p2_const_int'
cntl_case_str  = 'wopert'
test_case_str  = ['negpert','pospert']
rmse_or_diff   = 1 #0: DIFF 1: RMSE

#history files related info
hist_path_str  = 'run/'  
cam_hist_str   = '.cam.h0.'
suffix         ='.nc'

#other files needed
inic_cond_file = 'inic_cond_file_list_se.txt'
var_file       = 'physup_calls_av1c.txt'

#plot related info
xlabel_file = 'xlabels_av1c.txt'
ylabel      = 'RMSE Error [T(K)]'
if(rmse_or_diff == 0):
   ylabel = 'Maximum Error in the temperature (K) field'

ymin  = 'N' #-1    # Use 'N' to unset it 
ymax  = 'N' #10.0  # Use 'N' to unset it 
xmin  = 0
title = 'CAM5 error growth (1 time step)'
clr   = ['c','g'] # for each case
lgnds = ['CAM5-revised', 'CAM5-default']


##====================================# USER INPUT ENDS # ===========================================================##
#Functions
def rmse_diff_var(ifile_test, ifile_cntl,  var_list, var_suffix, rmse_or_diff ):

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
ts         = '01800' #'07200'#'01800'

#get list of variable suffix
with open(var_file, 'r') as fvar:
   var_list = fvar.readlines()
fvar.close()
var_list = map(str.strip,var_list)

#get list of initial condition files
with open(inic_cond_file, 'r') as fvar:
   inic_list = fvar.readlines()
fvar.close()
inic_list = map(str.strip,inic_list)

#get xticklabel
with open(xlabel_file, 'r') as flbl:
   xlabels = flbl.readlines()
flbl.close()
xlabels = map(str.strip,xlabels)

ax = pl.gca()
axf = pl.gcf()
axf.set_facecolor('white') #set color of the plot
#ax.set_title(title, fontsize=35)

i = 0
for icase in inic_list:
   main_case_name = (main_case + '_'+ inic_list[i]).split('.nc')[0] 
   yr_mn_dy = inic_list[i].split('.')[3].split('-00000')[0]
   fn_path_cntl = cmn_path+'/'+main_case_name+'_'+cntl_case_str+'/'+hist_path_str+main_case_name+'_'+cntl_case_str+cam_hist_str+yr_mn_dy+'-'+ts+suffix
   for iprt in test_case_str:
      fn_path_test = cmn_path+'/'+main_case_name+'_'+ iprt+'/'+hist_path_str+main_case_name+'_'+iprt+cam_hist_str+yr_mn_dy+'-'+ts+suffix
      res         = rmse_diff_var(fn_path_test,fn_path_cntl,var_list,'T_',rmse_or_diff)
      nzeroind = np.nonzero(res)[0]
      res_nzero = res[[nzeroind]]
      xlabels_nzero = [xlabels[j] for j in nzeroind]

      ax.semilogy(res_nzero,linestyle='-',marker='.', linewidth=4)
      ax.set_xlim([0,len(res_nzero)])
      ax.set_xticks(range(0,len(res_nzero)))
      ax.set_xticklabels(xlabels_nzero, rotation=40, ha='center', fontsize=35)
      ax.set_xlabel('Physical processes in the first time step', fontsize=35)
      if(ymin != 'N' and ymax !='N'):
         ax.set_ylim([ymin,ymax])
         
      ax.set_ylabel(ylabel, fontsize=35)
      for label in ax.get_yticklabels():
         label.set_fontsize(35)
      pl.hold(True)
      
   i = i + 1


#Draw plot
handles, labels = pl.gca().get_legend_handles_labels()
#pl.legend(handles, labels, loc='best',fontsize=35)

pl.show()
