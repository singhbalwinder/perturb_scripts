#!/usr/bin/python

#Python version: python 2.7.8

import ntpath
from rmse_diff_var import rmse_diff_var
import pylab as pl
import numpy as np
import sys
import pdb

#-------------------------------------------------------
# Some flags to control script behavior
#-------------------------------------------------------

#checks if ALL files are present (Set to False to produce plots)
chk_file_only = False

#use only one inital condition file to produce plots faster
single_inic = False

#-------------------------------------------------------
# Paths and test cases to plot
#-------------------------------------------------------

#commom path string for all cases
cmn_path = '/pic/projects/climate/sing201/acme1/other_machs/other_machines_perturb'

#-------------------------------------------------------
# cases (cntl_case,tst_cases,cld_cases) are control case, test case and cases to form clouds.
# They are organized like {machine name}/{case name}:[flag to inclide in plotting or not, legend]
# "flag to inclide or not" is a flag with decides whether to include it(=1) in comparison
# or not (=0).
#-------------------------------------------------------
cntl_case = {'cori/ne30_fc5_default_cori_knl_int':[1,'Cori KNL(Intel O0)']} #flag to include in plotting or not is not used for control case

tst_cases = {'constance/csmruns/ne30_fc5_cldfrc_dp1_0.14_const_int':[0,'PAR(dp1=0.14) '], \
                'constance/csmruns/ne30_fc5_code_mod_dm_const_int':[0,'MOD(DM) '], \
                'constance/csmruns/init_r8_ne30_fc5_code_mod_p_const_int':[0,'Init r8 MOD(P)'], \
                'constance/csmruns/all_r8_ne30_fc5_code_mod_p_const_int':[0,'ALL r8 MOD(P)'], \
                'constance/csmruns/ne30_fc5_code_mod_p_const_int':[0,'MOD(P) '] \
            }

cld_cases = {'cori/ne30_fc5_default_nondbg_cori_has_int':[0,'Cori Haswell(Intel O2)'], \
                'cori/ne30_fc5_default_cori_has_int':[0,'Cori Haswell(Intel O0)'],\
                'cori/ne30_fc5_default_nondbg_cori_knl_int':[0,'Cori KNL(Intel O2)'], \
                'cori/ne30_fc5_default_cori_has_gnu':[0,'Cori Haswell (GNU O0)'], \
                'cori/ne30_fc5_default_nondbg_cori_has_gnu':[0,'Cori Haswell(GNU O2)'], \
                'cori/experiments/just_o0_ne30_fc5_default_nondbg_cori_has_int':[0,'Cori Haswell (Intel O2->O0-NDBG FLG)'], \
                'cori/experiments/o2_w_dbg_flg_ne30_fc5_default_nondbg_cori_has_int':[0,'Cori Haswell(Intel O0->O2-DBG FLG)'], \
                'constance/csmruns/ne30_fc5_default_nondebug_const_int':[0,'Constance(Intel O2)'], \
                'constance/csmruns/ne30_fc5_default_const_int':[0,'Constance(Intel O0)'], \
                'eos/ne30_fc5_default_nondebug_eos_int':[1,'EOS(Intel O2)'], \
                'titan/ne30_fc5_default_nondebug_titan_int_18_0_1_163_compiler':[0,'Titan(Intel O2_163)'], \
                'titan/ne30_fc5_default_titan_int':[0,'Titan(Intel O0_163)'], \
                'titan/ne30_fc5_default_nondebugtitan_int':[0,'Titan(Intel O2)'], \
                'titan/ne30_fc5_default_nondebug_titan_pgi':[1,'Titan(PGI O2)'], \
                'titan/ne30_fc5_default_titan_pgi':[0,'Titan(PGI O0)'], \
                'cascade/csmruns/ne30_fc5_default_cas_int':[0,'Cascade(Intel O0)'], \
                'cascade/csmruns/ne30_fc5_default_nondebug_cas_int':[0,'Cascade(Intel O2)'], \
                'eos/ne30_fc5_default_eos_int':[0,'EOS(Intel O0)'] \
                }

rmse_or_diff   = 1 #0: DIFF 1: RMSE

#history files related info to form file names in a loop
acme_hist_dir  = 'run'
cam_hist_str   = '.cam.h0.'
time           = '00000'
perturb_str    = ['wopert','pospert','negpert']

#other files needed
inic_cond_file = 'inic_cond_file_list_ne30.txt'
var_file       = 'physup_calls_fc5_no_none.txt'

#plot related info
xlabel_file = 'xlabels_fc5_no_none.txt'
if(rmse_or_diff == 0):
   ylabel = 'Maximum Error in the temperature (K) field'
elif(rmse_or_diff == 1):
   ylabel = 'RMSE Error [T(K)]'

ymin  = -1
ymax  = 10.0
xmin  = 0
clr   = ['b', 'g', 'r', 'c', 'm', 'y', 'k', [0.5,0.5,0.5]] # for each case
mrk   = ['o','*','x','s']
pert_lgnd = ['_wo','_P+','_P-']
title = "Compared against "+cntl_case[cntl_case.keys()[0]][1]

#counters
cld_ires = 0
tst_ires = 0
iclr = 0
imrk = 0

#===================================================
# Functions
#===================================================
def compute_res(icase,ival,case_typ):
   global cld_ires, tst_ires, iclr, imrk 

   #Return if flag is zero (i.e. user asked not to plot this case)
   if(ival[0] != 1): 
      return

   icase_name = ntpath.basename(icase)
   print( 'Working on '+case_typ+': '+ icase_name)

   #form path
   ipath = cmn_path+'/'+icase

   #-------------------------------------------------------
   #case_typ: Test case
   #-------------------------------------------------------
   ipath_cntl_lp    = ipath_cntl
   cntl_casename_lp = cntl_casename
   perturb_str_lp   = perturb_str

   #-------------------------------------------------------
   #case_typ: cloud case
   #-------------------------------------------------------
   #if case is cloud, generate difference based on (wopert-pospert) and (wopert-negpert) only
   if(case_typ == 'cloud'):
      perturb_str_lp   = perturb_str[1:len(perturb_str)]
      ipath_cntl_lp    = ipath
      cntl_casename_lp = icase_name

   icond = -1
   for acond in  inic_list: #use "for icond, acond in enumerate(inic_list, start=0):" logic here instead of icond=-1 etc.
      icond += 1

      #form location of file [acond is string is split twice to make use of "time" variable]
      acond_1 = acond.split('.')[3]
      acond_2 = acond_1.split('-00000')[0]            
      #following for loop loops through perturbations
      ipert = -1
      for apert in perturb_str_lp: 
         ipert += 1
         apert_cntl = apert
         if(case_typ == 'cloud'):
            apert_cntl = perturb_str[0] #'wopert' should be the cntl case for cloud cases
         #form case name
         tmp_case_name  = icase_name + '_'+ acond.split('.nc')[0]+'_'+apert
         tmp_case_name_cntl = cntl_casename + '_'+ acond.split('.nc')[0]+'_'+apert_cntl
         ifile      = ipath+'/'+tmp_case_name+'/'+acme_hist_dir+'/'+tmp_case_name+cam_hist_str+acond_2+'-'+time+'.nc'
         ifile_cntl = ipath_cntl+'/'+tmp_case_name_cntl+'/'+acme_hist_dir+'/'+tmp_case_name_cntl+cam_hist_str+acond_2+'-'+time+'.nc'
         if(not chk_file_only):
            if(case_typ == 'cloud'):
               cld_res[cld_ires,icond,ipert,0:len(var_list)]  = rmse_diff_var(ifile, ifile_cntl, var_list, 'T_',rmse_or_diff)
               ax.semilogy(cld_res[cld_ires,icond,ipert,:],color=clr[iclr],linestyle='-',marker=mrk[imrk],label=ival[1], linewidth = 2, alpha = 0.7) 
            else:
               tst_res[tst_ires,icond,ipert,0:len(var_list)]  = rmse_diff_var(ifile, ifile_cntl, var_list, 'T_',rmse_or_diff)         
               ax.semilogy(tst_res[tst_ires,icond,ipert,:],color=clr[iclr],linestyle='-',marker=mrk[imrk],label=ival[1], linewidth = 2, alpha = 0.7) 

            #if(all(iresult <= 0.0 for iresult in res[ires,icond,ipert,0:len(var_list)])):
            #   print("All diffs are <= zero , reseting last element to 1e-16["+apert+" ]")
            #   res[ires,icond,ipert,len(var_list)-1] = 1.e-16
            #icnt = 0
            #for iresult in res[ires,icond,ipert,0:len(var_list)]:
            #   if(iresult <= 0.0 ):
            #      print("Diff is <= zero , reseting element to 1e-16["+var_list[icnt]+";"+apert+" ]")
            #      res[ires,icond,ipert,icnt] = 1.e-16
            #   icnt += 1

            ax.set_ylim([ymin,ymax])
            ax.set_xlim([xmin,xmax])
            ax.set_xticks(range(xmin, xmax))
            ax.set_xticklabels(xlabels, rotation=40, ha='left', fontsize=15, multialignment='right')
   cld_ires += 1
   tst_ires += 1
   iclr += 1
   if (iclr == len(clr) - 1):
      imrk += 1
      iclr  = 0



min_all = float("inf")

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

if(single_inic):
   inic_list = inic_list[0:1] 


#create an empty array with dims[# of tst_cases, # of inic conds, # of perts, # of check point vars]
tst_res = np.empty([len(tst_cases),len(inic_list),len(perturb_str),len(var_list)])
cld_res = np.empty([len(cld_cases),len(inic_list),len(perturb_str)-1,len(var_list)]) #cntl case is 'wopert' in this case

ax = pl.gca()
axf = pl.gcf()
axf.set_facecolor('white') #set color of the plot

ipath_cntl = cmn_path+'/'+cntl_case.keys()[0]

cntl_casename = ntpath.basename(ipath_cntl)

print('Control case is: '+cntl_casename)
#Loop through each case and prepare P+ and P- curves
#for icase in range(0,len(tst_cases)):

#pdb.set_trace()
for icase_pth, ival in cld_cases.iteritems():
   compute_res(icase_pth,ival,'cloud')

for icase_pth, ival in tst_cases.iteritems():
   compute_res(icase_pth,ival, 'test')



if (not chk_file_only) :
   print("Plots are being generated...")
   handles, labels = pl.gca().get_legend_handles_labels()
   labels, ids = np.unique(labels, return_index=True)
   handles = [handles[i] for i in ids]
   pl.legend(handles, labels, loc='best')#, fontsize = 35)
   pl.show()
else:
    print("ALL files are present")

############ extra codes
#clr   = [[1.0,0.4,0.6],'c','g','r','m','b','k','y',[1,0.4,0.8],[0.4,0.4,0.4],[0.6,0.5,0.4],[0.7,0.5,0.8],[0.6,0.9,0.4],[0.2,0.5,1.0],[0.7,1.0,0.4]] # for each case
