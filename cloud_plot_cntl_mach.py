#!/usr/bin/python

#Python version: python 2.7.8

from netCDF4 import Dataset
import pylab as pl
import numpy as np
import sys


cmn_path = '/pic/projects/climate/sing201/acme1/other_machs/other_machines_perturb'
paths    = ['constance/archive','mira/archive','mira/archive','ys/archive','cascade/archive']

cases = ['acme_pert_mltscr_qsmall_mic_int_cnstnc','ilchnk_omp_fix_w_offline_mods_xlf','o3_xlf_perturb_test_mira','o3_with_ncar_flags_ys','acme_pert_mltscr_qsmall_mic_int_test']


icase_cntl = 0 # index from the "cases" array

#history files related info
acme_hist_dir  = 'atm/hist'
cam_hist_str   = '.cam.h0.'
time           = '00000'
perturb_str    = ['wopert','pospert','negpert']

#other files needed
inic_cond_file = 'inic_cond_file_list.txt'
var_file       = 'physup_calls.txt'


#plot related info
xlabel_file = 'xlabels.txt'
ymin  = -1
ymax  = 10.0
xmin  = 0
clr   = ['c','g','r','m','b','k'] # for each case
lgnds = ['Constance (Intel,O0)','Mira(XLF-O0)','Mira(XLF-O3)','YS(Intel-O3)','Cascade(Intel-O0)']
pert_lgnd = ['_wo','_P+','_P-']
title = "Compared against "+lgnds[icase_cntl] 

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

#Functions ENDS!!!

#check if you have all the rquired info:
if(len(paths) != len(cases)):
   print("paths and cases arrays has different lengths")
   sys.exit()
if(len(paths) > len(clr)):
   print("paths and clr arrays has different lengths")
   sys.exit()



#get list of variable suffix
with open(var_file, 'r') as fvar:
   var_list = fvar.readlines()
fvar.close()
var_list = map(str.strip,var_list)
xmax = len(var_list)

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
#inic_list = inic_list[0:2] #temporary ##UNCOMMENT THIS LINE TO FASTER TURNAROUND!!!!!!#####################################


#create an empty array with dims[# of cases, # of inic conds, # of perts, # of check point vars]
#currently hardwired 2 for negpert and pospert
diff = np.empty([len(cases),len(inic_list),len(perturb_str),len(var_list)])

####Logic for 12 subplots on a plot####
#f, axarr = pl.subplots(2, 6)
#isp = 0 
#jsp = 0
######################################

ax = pl.gca()
axf = pl.gcf()
axf.set_facecolor('white') #set color of the plot
ax.set_title(title, fontsize=35)

ipath_cntl = cmn_path+'/'+paths[icase_cntl]

#Loop through each case and prepare P+ and P- curves
for icase in range(0,len(cases)):
   if(icase == icase_cntl):
      continue
   print( 'working on: '+ cases[icase])
   #form path
   ipath = cmn_path+'/'+paths[icase]
   icond = -1
   for acond in  inic_list: #use "for icond, acond in enumerate(inic_list, start=0):" logic here instead of icond=-1 etc.
      icond += 1
      #form location of file [acond is string is split twice to make use of "time" variable]
      acond_1 = acond.split('.')[3]
      acond_2 = acond_1.split('-00000')[0]            
      #following for loop loops through perturbations
      ipert = -1
      for apert in perturb_str: #use "for ipert, apert in enumerate(perturb_str[1:3], start=0):" logic here instead of ipert=-1 etc.
         ipert += 1
         #form case name
         case_name  = cases[icase] + '_'+ acond.split('.nc')[0]+'_'+apert
         case_name_cntl = cases[icase_cntl] + '_'+ acond.split('.nc')[0]+'_'+apert
         ifile      = ipath+'/'+case_name+'/'+acme_hist_dir+'/'+case_name+cam_hist_str+acond_2+'-'+time+'.nc'
         ifile_cntl = ipath_cntl+'/'+case_name_cntl+'/'+acme_hist_dir+'/'+case_name_cntl+cam_hist_str+acond_2+'-'+time+'.nc'

         diff[icase,icond,ipert,0:len(var_list)]  = max_diff_var(ifile, ifile_cntl, var_list, 'T_')         
      
         #ax.semilogy(diff[icase,icond,ipert,:],clr[icase+ipert]+'.-',label=lgnds[icase]+pert_lgnd[ipert])
         ax.semilogy(diff[icase,icond,ipert,:],clr[icase]+'.-',label=lgnds[icase])
         #print(diff[icase,icond,ipert,:])
         ax.set_ylim([ymin,ymax])
         ax.set_xlim([xmin,xmax])
         ax.set_xticks(range(xmin, xmax))
         ax.set_xticklabels(xlabels, rotation=40, ha='center', fontsize=35)
         #ax.set_xlabel('Process # during a time Step', fontsize=35)
         ax.set_ylabel('Maximum Error in the temperature (K) field', fontsize=35)
         pl.hold(True)




#logic for printing 12 plots for 12 inic conds in one page using subplots
#The code goes under the "apert" for loop. See the indent at "pl.hold(False)" 
# the code after this indent is under "acond" for loop and finallu "pl.show"
# is at the end of the code
#          print(str(isp)+' '+str(jsp))
#          axarr[isp,jsp].plot(diff[icase,icond,ipert,:],'g.-')
#          axarr[isp,jsp].set_ylim([0.,10.e-6])
#          pl.hold(True)
#       pl.hold(False)
#       jsp += 1
#       if(jsp == 6):
#          isp += 1
#          jsp = 0

#Draw plot
handles, labels = pl.gca().get_legend_handles_labels()
labels, ids = np.unique(labels, return_index=True)
handles = [handles[i] for i in ids]
pl.legend(handles, labels, loc='best')
pl.show()


#OLD cases

#clr   = ['r','g','c','m','b','r'] # for each case
#lgnds = ['Constance-intel-O0','Mira-xlf-','Mira-xlf-O3','YS-intel-O3','YS-intel-O0','Cascade-intel-O0']


################
#paths    = ['ys/archive','ys/archive']

#cases = ['ilchnk_omp_fix_w_offline_mods_ys','o0_pgi13p9_ys']

#lgnds = ['YS-intel-O0','YS-pgi-O0']
#pert_lgnd = ['_wo','_P+','_P-']
#################
