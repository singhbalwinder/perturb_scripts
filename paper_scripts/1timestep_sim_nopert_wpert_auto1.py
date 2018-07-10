#!/usr/bin/python


#meld this script with 1timestep_sim_nopert_wpert.py to see the diffs, mainly it read a new text file


#Python version: Load python/2.7.9(default) and python_anaconda3/2.3.0

from netCDF4 import Dataset
from math import sqrt
from sklearn.metrics import mean_squared_error
import pylab as pl
import numpy as np
import sys
import pdb

###
# NOTE: This script assumes that simulation is run for a few days only and output is every day!! Limitation is imposed by varibale "ndays"
###

cmn_path  = '/pic/scratch/sing201/csmruns/'
cntl_case = ['ne30_av1c_rebased_03032018_nopert']
test_case = ['ne30_av1c_rebased_03032018_pospert']
rmse_or_diff   = 1 #0: DIFF 1: RMSE

#history files related info
hist_path_str  = 'run/'  #'run/' #'run/regrided/regrided_'
cam_hist_str   = '.cam.h0.'
suffix         = '.nc'
year           = '0001' #year  is a str as I don't anticipate that it will change
month          = '01'   #month is a str as I don't anticipate that it will change
day            = '02'   #day   is a str as I don't anticipate that it will change
ts             = '00000' #'07200'#'01800'

#other files needed
var_file       = cmn_path+"".join(cntl_case)+ '/run/pergro_ptend_names.txt' #'physup_calls_fc5.txt' #'physup_calls_av1c.txt'

#plot related info
xlabel_file = var_file #'pergro_ptend_names.txt' #'xlabels_fc5.txt' #'xlabels_av1c.txt'
ylabel      = 'Maximum Error in the temperature (K) field'
if(rmse_or_diff == 1):
   ylabel = 'RMSE Error [T(K)]'

ymin  = 'N' #-1    # Use 'N' to unset it 
ymax  = 'N' #10.0  # Use 'N' to unset it 
xmin  = 0
title = 'CAM5 error growth (1 time step)'
clr   = ['c','g'] # for each case
lgnds = ['CAM5-revised', 'CAM5-default']


### USER INPUT ENDS ###
#Functions
def rmse_diff_var(ifile_test, ifile_cntl,  var_list, var_suffix, rmse_or_diff ):
   #pdb.set_trace()
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
         print(str(var)+":"+str(diff[i]))
         i += 1
         vtest = None
         vcntl = None
         var   = None
      else:
         print (var+' not in file')
      
   ftest.close()
   fcntl.close()
   return diff

#Functions ENDS!!!

if(len(cntl_case) != len(test_case)):
   print('Length of cntl_case and test_case is not same; cntl_case='+str(len(cntl_case))+' test_case='+str(len(test_case)))
   sys.exit()

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
#ax.set_title(title, fontsize=15)
fn_cmn  = cam_hist_str+year + '-' + month + '-' + str(day) + '-'+ ts+suffix

for icase in range(0,len(test_case)):
   fn_cntl = cntl_case[icase] + fn_cmn
   fn_test = test_case[icase] + fn_cmn
   
   fn_path_test = cmn_path+'/'+test_case[icase]+'/'+hist_path_str+fn_test
   fn_path_cntl = cmn_path+'/'+cntl_case[icase]+'/'+hist_path_str+fn_cntl
   print(fn_path_test)
   print(fn_path_cntl)
   res         = rmse_diff_var(fn_path_test,fn_path_cntl,var_list,'t_',rmse_or_diff)
   print(res)
   #pdb.set_trace()
   
nzeroind = np.nonzero(res)[0]
res_nzero = res[[nzeroind]]
xlabels_nzero = [xlabels[i] for i in nzeroind]

ax.semilogy(res_nzero,color=clr[icase],linestyle='-',marker='.',label=lgnds[icase], linewidth=1)

ax.set_xlim([0,len(res_nzero)])
ax.set_xticks(range(0,len(res_nzero)))
ax.set_xticklabels(xlabels_nzero, rotation=40, ha='center', fontsize=15)
ax.set_xlabel('Physical processes in the first time step', fontsize=15)
if(ymin != 'N' and ymax !='N'):
   ax.set_ylim([ymin,ymax])

ax.set_ylabel(ylabel, fontsize=15)
for label in ax.get_yticklabels(): 
   label.set_fontsize(15) 



#Draw plot
handles, labels = pl.gca().get_legend_handles_labels()
pl.legend(handles, labels, loc='best',fontsize=15)

pl.show()
