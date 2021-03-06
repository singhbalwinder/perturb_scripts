#!/usr/bin/python

#Python version: python 2.7.8

from netCDF4 import Dataset
from math import sqrt
from sklearn.metrics import mean_squared_error
import pylab as pl
import numpy as np
import sys

cmn_path = '/pic/projects/climate/sing201/acme1/other_machs/other_machines_perturb'
paths    = ['constance/archive','mira/archive','mira/archive','ys/archive','cascade/archive','ys/archive','ys/archive','ys/archive','ys/archive','ys/archive','ys/archive','ys/archive','ys/archive']

cases = ['acme_pert_mltscr_qsmall_mic_int_cnstnc','ilchnk_omp_fix_w_offline_mods_xlf','o3_xlf_perturb_test_mira','o3_with_ncar_flags_ys','acme_pert_mltscr_qsmall_mic_int_test','ilchnk_omp_fix_w_offline_mods_ys','o0_pgi13p9_ys','o3_ilchnk_omp_fix_w_offline_mods_ys','o3_pgi13p9_kieee_flag_ys','o4_ilchnk_omp_fix_w_offline_mods_ys','o4_pgi13p9_kieee_flag_ys','o4_pgi13p9_nokieee_fast_mfprelaxed_ys','o4_pgi13p9_nokieee_fastsse_mfprelaxed_ys']

#case_flag = [0,1,1,1,0,0,1,0,1,0,1,1,1] #for cases that show failure                                                                                                        
case_flag = [0,1,1,1,0,0,1,1,1,0,1,0,0] #just a test 

icase_cntl = 0 # index from the "cases" array
rmse_or_diff   = 1 #0: DIFF 1: RMSE

#history files related info
acme_hist_dir  = 'atm/hist'
cam_hist_str   = '.cam.h0.'
time           = '00000'
perturb_str    = ['wopert','pospert','negpert']

#other files needed
inic_cond_file = 'inic_cond_file_list.txt'
var_file       = 'physup_calls_fc5.txt'

#plot related info
xlabel_file = 'xlabels_fc5.txt'

if(rmse_or_diff == 0):
   ylabel = 'Maximum Error in the temperature (K) field'
elif(rmse_or_diff == 1):
   ylabel = 'RMSE Error - T(K)'

ymin  = 10e-12
ymax  = 10.0
xmin  = 0
clr   = ['g','c','r','m','b','k','y',[1,0.4,0.6],[0.4,0.4,0.4],[0.6,0.5,0.4],[0.7,0.5,0.8],[0.6,0.9,0.4],[0.2,0.5,1.0],[0.7,1.0,0.4]] # for each case
lgnds = ['Constance (Intel,O0)','Mira(XLF-O0)','Mira(XLF-O3)','YS(Intel-O3)','Cascade(Intel-O0)','YS(Intel-O0)','YS(PGI-O0)','YS(Intel-O3-default)','YS(PGI-O3)','YS(Intel-O4)','YS(PGI-O4)','YS(PGI-O4-Kieee)','YS(PGI-O4-fastsse)']
pert_lgnd = ['_wo','_P+','_P-']
title = "Compared against "+lgnds[icase_cntl]

#---------------------------------------------------------------------
#Functions
#---------------------------------------------------------------------
def rmse_diff_var(ifile_test, ifile_cntl,  var_list, var_suffix, rmse_or_diff,vars_to_skip):
   import os.path
   
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

   diff = np.zeros(shape=(np.count_nonzero(vars_to_skip)))
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
   print('extracting non-zero variable indices')
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

   

##===============================================# Functions ENDS #================================================##

min_all = float("inf")
#check if you have all the rquired info:
if(len(paths) != len(cases)):
   print("ERROR: paths and cases arrays has different lengths")
   print('Paths are:'+str(len(paths))+',cases are:'+str(len(cases)) )
   sys.exit()
if(len(paths) > len(clr)):
   print("ERROR: paths and clr arrays has different lengths")
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

#get list of inital condition files
with open(inic_cond_file, 'r') as finic:
   inic_list = finic.readlines()
finic.close()
inic_list = map(str.strip,inic_list)
#inic_list = inic_list[0:1] #temporary ##UNCOMMENT THIS LINE FOR FASTER TURNAROUND!!!!!!#####################################

#Check variables which are all zero in (preassumably) all files; we will skip these variable
#Form a single file name (lets take a file from control case)
case_name_cntl = cases[icase_cntl] + '_'+ inic_list[0].split('.nc')[0]+'_'+perturb_str[0]
extract_date   = list(reversed(inic_list[0].rsplit('.')))[1].split('-00000')[0]
fpath          = cmn_path+'/'+paths[icase_cntl]+'/'+case_name_cntl+'/'+acme_hist_dir+'/'+case_name_cntl+cam_hist_str+extract_date+'-'+time+'.nc'

vars_to_skip = all_nonzero_vars(fpath,var_list,'T_')
nzero_var_list_len = np.count_nonzero(vars_to_skip)
xmax = nzero_var_list_len
xlabels_nzero= [xlabels[j] for j in range(len(vars_to_skip)) if(vars_to_skip[j]==-1)] #remove xlabels where vars are all zero
#create an empty array with dims[# of cases, # of inic conds, # of perts, # of check point vars]
#currently hardwired 2 for negpert and pospert
res = np.empty([len(cases),len(inic_list),len(perturb_str),nzero_var_list_len])

ax = pl.gca()
axf = pl.gcf()
axf.set_facecolor('white') #set color of the plot
ax.set_title(title, fontsize=20)

ipath_cntl = cmn_path+'/'+paths[icase_cntl]
iclr = 0
#Loop through each case and prepare P+ and P- curves
for icase in range(0,len(cases)):
   if(icase == icase_cntl or case_flag[icase] != 1):
      continue
   print( 'working on: '+ cases[icase])
   #form path
   ipath = cmn_path+'/'+paths[icase]
   icond = -1
   for acond in  inic_list: #use "for icond, acond in enumerate(inic_list, start=0):" logic here instead of icond=-1 etc.
      icond += 1
      #form location of file [acond is string is split twice to make use of "time" variable]
      acond_1 = list(reversed(acond.rsplit('.')))[1]
      acond_2 = acond_1.split('-00000')[0]            
      case_name_cntl = cases[icase_cntl] + '_'+ acond.split('.nc')[0]+'_'+perturb_str[0]

      #following for loop loops through perturbations
      ipert = -1
      for apert in perturb_str: #use "for ipert, apert in enumerate(perturb_str[1:3], start=0):" logic here instead of ipert=-1 etc.
         ipert += 1
         #form case name
         case_name  = cases[icase] + '_'+ acond.split('.nc')[0]+'_'+apert
         ifile      = ipath+'/'+case_name+'/'+acme_hist_dir+'/'+case_name+cam_hist_str+acond_2+'-'+time+'.nc'
         ifile_cntl = ipath_cntl+'/'+case_name_cntl+'/'+acme_hist_dir+'/'+case_name_cntl+cam_hist_str+acond_2+'-'+time+'.nc'
         res[icase,icond,ipert,0:len(var_list)]  = rmse_diff_var(ifile, ifile_cntl, var_list, 'T_',rmse_or_diff,vars_to_skip)         
         min_all = min(min_all,min(res[icase,icond,ipert,0:len(var_list)]))
         ax.semilogy(res[icase,icond,ipert,:],color=clr[iclr],linestyle='-',marker='.',label=lgnds[icase], linewidth = 1) 
         ax.set_ylim([ymin,ymax])
         ax.set_xlim([xmin,xmax])
         ax.set_xticks(range(xmin, xmax))
         ax.set_xticklabels(xlabels_nzero, rotation=45)#, ha='left', fontsize=35, multialignment='right')
         tick_locs = range(0,len(xlabels_nzero))
         pl.xticks(tick_locs, xlabels_nzero)
         ax.set_ylabel(ylabel, fontsize=20)
         for label in ax.get_yticklabels():
            label.set_fontsize(20)
         for label in ax.get_xticklabels():
            label.set_fontsize(20)
         pl.hold(True)
   iclr =iclr + 1


if(rmse_or_diff == 0):
   #min_diff =[  6.35509423e-11,   6.36077857e-11,   6.36077857e-11,   3.06533821e-09,                                                                                        
   #   3.06329184e-09,   3.06334869e-09,   3.06329184e-09,   7.08905645e-09,                                                                                                  
   #   7.08905645e-09,   7.08905645e-09,   4.54002702e-09,   4.54002702e-09,                                                                                                  
   #   7.45279749e-09,   7.45279749e-09,   7.45279749e-09,   7.45279749e-09,                                                                                                  
   #   1.15548460e-08,   1.15548460e-08,   1.73955073e-08,   1.73955073e-08,                                                                                                  
   #   1.73955073e-08,   1.73955073e-08]                                                                                                                                      


   max_diff =[  8.56630322e-11,   8.56061888e-11,   8.56061888e-11,   1.56309170e-08,
                1.55338853e-08,   1.55333737e-08,   1.55333737e-08,   3.45239414e-07,
                3.45239414e-07,   3.45239414e-07,   3.53525479e-07,   3.53525479e-07,
                9.82212896e-07,   9.82212896e-07,   9.82212896e-07,   9.82212896e-07,
                2.65759058e-05,   2.65759058e-05,   2.65760906e-05,   2.65760906e-05,
                2.65760906e-05,   2.65760906e-05]
elif(rmse_or_diff == 1):
   min_diff=[  9.11961985e-12,   9.11970896e-12,   9.11970896e-12,   3.04124277e-11,
               3.04962056e-11,   3.05066752e-11,   3.05066206e-11,   5.47984075e-11,
               5.47984075e-11,   5.48311644e-11,   3.99988517e-11,   3.99988536e-11,
               5.31086094e-11,   5.31086094e-11,   5.31086094e-11,   5.31086094e-11,
               8.52208153e-11,   8.52208153e-11,   9.60576852e-11,   9.60576852e-11,
               9.60576852e-11,   9.60576376e-11]
   max_diff =[  9.40919127e-12,   9.40933773e-12,   9.40933773e-12,   5.06766068e-11,
               5.37311439e-11,   5.37457128e-11,   5.37457293e-11,   6.92835390e-10,
               6.92835390e-10,   6.92847078e-10,   7.01626760e-10,   7.01626761e-10,
               1.93471673e-09,   1.93471673e-09,   1.93471673e-09,   1.93471673e-09,
               4.28417756e-08,   4.28417756e-08,   4.28355044e-08,   4.28355044e-08,
               4.28355044e-08,   4.28355644e-08]
else:
   print('Error: Not a valid value for rmse_or_diff; rmse_or_diff is:'+str(rmse_or_diff))


ax.fill_between(range(xmin, xmax), min_diff, max_diff, facecolor='grey', lw=0, alpha=0.5 )

handles, labels = pl.gca().get_legend_handles_labels()
labels, ids = np.unique(labels, return_index=True)
handles = [handles[i] for i in ids]
pl.legend(handles, labels, loc='upper left', fontsize = 20)
pl.show()
