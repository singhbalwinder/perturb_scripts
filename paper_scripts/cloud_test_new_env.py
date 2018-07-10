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
case_flag = [0,1,0,0,0,0,0,0,0,0,0,0,0] #just a test
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
   ylabel = 'RMSE Error [T(K)]'

ymin  = -1
ymax  = 10.0
xmin  = 0
clr   = [[1.0,0.4,0.6],'c','g','r','m','b','k','y',[1,0.4,0.6],[0.4,0.4,0.4],[0.6,0.5,0.4],[0.7,0.5,0.8],[0.6,0.9,0.4],[0.2,0.5,1.0],[0.7,1.0,0.4]] # for each case
lgnds = ['Constance (Intel,O0)','Mira(XLF-O0)','Mira(XLF-O3)','YS(Intel-O3)','Cascade(Intel-O0)','YS(Intel-O0)','YS(PGI-O0)','YS(Intel-O3-default)','YS(PGI-O3)','YS(Intel-O4)','YS(PGI-O4)','YS(PGI-O4-Kieee)','YS(PGI-O4-fastsse)']
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
xmax = len(var_list)

#get xticklabel
with open(xlabel_file, 'r') as flbl:
   xlabels = flbl.readlines()
flbl.close()
#xlabels = map(str.strip,xlabels)

#get list of inital condition files
with open(inic_cond_file, 'r') as finic:
   inic_list = finic.readlines()
finic.close()
#inic_list = map(str.strip,inic_list)
inic_list = inic_list[0:1] #temporary ##UNCOMMENT THIS LINE TO FASTER TURNAROUND!!!!!!#####################################


#create an empty array with dims[# of cases, # of inic conds, # of perts, # of check point vars]
#currently hardwired 2 for negpert and pospert
res = np.empty([len(cases),len(inic_list),len(perturb_str),len(var_list)])

####Logic for 12 subplots on a plot####
#f, axarr = pl.subplots(2, 6)
#isp = 0 
#jsp = 0
######################################

ax = pl.gca()
axf = pl.gcf()
axf.set_facecolor('white') #set color of the plot
#ax.set_title(title, fontsize=35)

ipath_cntl = cmn_path+'/'+paths[icase_cntl]

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
         if(rmse_or_diff == 0):
            res[icase,icond,ipert,0:len(var_list)]  = max_diff_var(ifile, ifile_cntl, var_list, 'T_')         
         elif(rmse_or_diff == 1):
            res[icase,icond,ipert,0:len(var_list)]  = rmse_var(ifile, ifile_cntl, var_list, 'T_')         
         else:
            print('Error: Not a valid value for rmse_or_diff; rmse_or_diff is:'+str(rmse_or_diff))
            sys.exit()
         min_all = min(min_all,min(res[icase,icond,ipert,0:len(var_list)]))

         nzeroind = np.nonzero(res[icase,icond,ipert,:])
         res_nzero = res[icase,icond,ipert,[nzeroind]]
         #xlabels_nzero = [xlabels[i] for i in nzeroind]

         #ax.semilogy(res[icase,icond,ipert,:],clr[icase+ipert]+'.-',label=lgnds[icase]+pert_lgnd[ipert])
         #Bax.semilogy(res[icase,icond,ipert,:],color=clr[icase],linestyle='-',marker='.',label=lgnds[icase], linewidth = 2) 
         ax.semilogy(res_nzero[0][0],color=clr[icase],linestyle='-',marker='.',label=lgnds[icase], linewidth = 2) 
         ax.set_ylim([ymin,ymax])
         ax.set_xlim([xmin,xmax])
         #Bax.set_xticks(range(xmin, xmax))
         #Bax.set_xticklabels(xlabels, rotation=40, ha='left', fontsize=35, multialignment='right')
         #Btick_locs = [1,2,3,4,5,6,7,8,9,10,11]
         #Bpl.xticks(tick_locs, xlabels)
         #ax.set_xlabel('Process # during a time Step', fontsize=35)
         #Bax.set_ylabel(ylabel, fontsize=35)
         #Bfor label in ax.get_yticklabels():
         #B   label.set_fontsize(35)
         #Bpl.hold(True)




#logic for printing 12 plots for 12 inic conds in one page using subplots
#The code goes under the "apert" for loop. See the indent at "pl.hold(False)" 
# the code after this indent is under "acond" for loop and finallu "pl.show"
# is at the end of the code
#          print(str(isp)+' '+str(jsp))
#          axarr[isp,jsp].plot(res[icase,icond,ipert,:],'g.-')
#          axarr[isp,jsp].set_ylim([0.,10.e-6])
#          pl.hold(True)
#       pl.hold(False)
#       jsp += 1
#       if(jsp == 6):
#          isp += 1
#          jsp = 0

#Draw plot
min_diff = np.ones(len(var_list))* max(min_all,1e-16) #use 1e-16 to avoid min_all to become zero as the shadded or hatched region looks funny otherwise (hint:semilog plots and log(0) is undefined)
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



print(len(range(xmin, xmax)))
print(len(min_diff))
#ax.semilogy(min_diff,'k.-', linewidth = 1)
#ax.semilogy(max_diff,'k.-', linewidth = 1)
#Bax.fill_between(range(xmin, xmax), min_diff, max_diff, facecolor='grey', lw=0, alpha=0.5 )

handles, labels = pl.gca().get_legend_handles_labels()
labels, ids = np.unique(labels, return_index=True)
handles = [handles[i] for i in ids]
pl.legend(handles, labels, loc='best', fontsize = 35)
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
