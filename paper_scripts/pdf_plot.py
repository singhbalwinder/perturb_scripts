#!/usr/bin/python

#Python version: python 2.7.8

from netCDF4 import Dataset
from math import sqrt, pow
from sklearn.metrics import mean_squared_error

import pylab as pl
import numpy as np
import sys


cmn_path = '/pic/projects/climate/sing201/acme1/other_machs/other_machines_perturb'

paths    = ['constance/archive','mira/archive','ys/archive','cascade/archive','ys/archive','ys/archive','ys/archive','ys/archive','ys/archive']

cases = ['acme_pert_mltscr_qsmall_mic_int_cnstnc','ilchnk_omp_fix_w_offline_mods_xlf','ilchnk_omp_fix_w_offline_mods_ys','acme_pert_mltscr_qsmall_mic_int_test','o0_pgi13p9_ys','o3_ilchnk_omp_fix_w_offline_mods_ys','o3_pgi13p9_kieee_flag_ys','o4_ilchnk_omp_fix_w_offline_mods_ys','o4_pgi13p9_kieee_flag_ys']

rmse_or_diff   = 0 #0: DIFF 1: RMSE

acme_hist_dir  = 'atm/hist'
cam_hist_str   = '.cam.h0.'
time           = '00000'
perturb_str    = ['wopert','pospert','negpert']

#PDF related info
process_num    = 21 #process number at which to generate pdf
nbins          = 17
min_bin_pw    = -16
max_bin_pw    = 1


#other files needed
inic_cond_file = 'inic_cond_file_list.txt'
var_file       = 'physup_calls.txt'


#plot related info
if (rmse_or_diff == 0):
   title = "PDF -Max DIFF Temperature"
elif(rmse_or_diff == 1):
   title = "PDF -RMSE Temperature"

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
   #print('TEST:'+ifile_test)
   #print('CNTL:'+ifile_cntl)
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

#check if you have all the rquired info:
if(len(paths) != len(cases)):
   print("ERROR: paths and cases arrays has different lengths")
   print('Paths are:'+str(len(paths))+',cases are:'+str(len(cases)) )
   sys.exit()

#form bins
interval = (max_bin_pw - min_bin_pw)/nbins
if(interval == 0):
   print('Error: interval is zero, please reduce nbins')
   print('nbins:'+str(nbins)+',max_bin_pw:'+str(max_bin_pw)+',min_bin_pw:'+str(min_bin_pw))
   sys.exit()
bins = [ pow(10,x) for x in np.arange(min_bin_pw,max_bin_pw,interval) ]
pdf = np.zeros(len(bins))


#get list of variable suffix
with open(var_file, 'r') as fvar:
   var_list = fvar.readlines()
fvar.close()
var_list = map(str.strip,var_list)
xmax = len(var_list)
var_process = [var_list[process_num]]

#get list of inital condition files
with open(inic_cond_file, 'r') as finic:
   inic_list = finic.readlines()
finic.close()
inic_list = map(str.strip,inic_list)
#inic_list = inic_list[0:1] #temporary



ax  = pl.gca()
axf = pl.gcf()
axf.set_facecolor('white') #set color of the plot
ax.set_title(title, fontsize=15)

#Loop through each case and prepare P+ and P- curves
for icase in range(0,len(cases)):
   print( 'working on: '+ cases[icase])
   #form path
   ipath = cmn_path+'/'+paths[icase]
   icond = -1
   for acond in  inic_list: #use "for icond, acond in enumerate(inic_list, start=0):" logic here instead of icond=-1 etc.
      icond += 1
      #form location of file [acond is string is split twice to make use of "time" variable]
      acond_1 = acond.split('.')[3]
      acond_2 = acond_1.split('-00000')[0]
      
      
      #form case name and file path for wo file
      case_name_wo = cases[icase] + '_'+ acond.split('.nc')[0]+'_'+perturb_str[0]
      ifile_wo     = ipath+'/'+case_name_wo+'/'+acme_hist_dir+'/'+case_name_wo+cam_hist_str+acond_2+'-'+time+'.nc'
      #print(ifile_wo)
       
      #following for loop just loops through positive and negative perturbation
      ipert = -1
      for apert in perturb_str[1:3]: #use "for ipert, apert in enumerate(perturb_str[1:3], start=0):" logic here instead of ipert=-1 etc.
         ipert += 1
         #form case name
         case_name = cases[icase] + '_'+ acond.split('.nc')[0]+'_'+apert
         ifile = ipath+'/'+case_name+'/'+acme_hist_dir+'/'+case_name+cam_hist_str+acond_2+'-'+time+'.nc'
         
         if(rmse_or_diff == 0):
            res  = max_diff_var(ifile, ifile_wo, var_process, 'T_')
         elif(rmse_or_diff == 1):
            res  = rmse_var(ifile, ifile_wo, var_process, 'T_')
         else:
            print('Error: Not a valid value for rmse_or_diff; rmse_or_diff is:'+str(rmse_or_diff))
            sys.exit()

            
         for ibin in range(0,len(bins)-1):
            if(res[0]>bins[ibin] and res[0]<=bins[ibin+1]):
               pdf[ibin] = pdf[ibin] + 1
               break



#normalize 
pdf = pdf[:]/sum(pdf[:])
ax.plot(range(0,len(bins)),pdf,'.-')

#xaxis
ax.set_xticks(range(0,len(bins)))
ax.set_xticklabels(bins)
ax.set_xlabel('Bins', fontsize=15)

#yaxis
ax.set_ylabel('# of points in a bin (normalized)', fontsize=15)
pl.show()




         






