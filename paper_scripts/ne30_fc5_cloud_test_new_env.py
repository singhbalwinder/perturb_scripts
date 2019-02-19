#!/usr/bin/python

#Python version: python 2.7.8

import ntpath
from rmse_diff_var import rmse_diff_var
from time import ctime
import pylab as plt
import numpy as np
import sys
import pdb
import os

print(ctime())
#-------------------------------------------------------
# Some flags to control script behavior
#-------------------------------------------------------

#checks if ALL files are present (Set to False to produce plots)
chk_file_only = False

#use only one inital condition file to produce plots faster
single_inic = True

#time step for history file
time           = '00000'

#suffix for variables to plot
#'QV_' ,'V_' , 'T_', 'S_', 'CLDLIQ_', 'CLDICE_', 'NUMLIQ_', 'NUMICE_', 'NUM_A1_', 'NUM_A2_', 'NUM_A3_']
pltvar_sfx = ['QV_' ,'V_' , 'T_', 'S_', 'CLDLIQ_', 'CLDICE_', 'NUMLIQ_', 'NUMICE_', 'NUM_A1_', 'NUM_A2_', 'NUM_A3_']
len_pltvar_sfx = len(pltvar_sfx)
col_sbplt      = 2
row_sbplt      = int((len_pltvar_sfx+1)/col_sbplt)

#-------------------------------------------------------
# Paths and test cases to plot
#-------------------------------------------------------

#commom path string for all cases
cmn_path = '/pic/projects/climate/sing201/acme1/other_machs/other_machines_perturb'

#-------------------------------------------------------
# cases (cntl_case,tst_cases,cld_cases) are control case, test case and cases to form clouds.
# They are organized like {machine name}/{case name}:[flag to include in plotting or not, legend]
# "flag to inclide or not" is a flag with decides whether to include it(=1) in comparison
# or not (=0).
#-------------------------------------------------------
cntl_case = {'titan/ne30_fc5_dbg_titan_int_unsrtcol':[1,'Titan(Intel-DBG)']} #flag to include in plotting or not is not used for control case

tst_cases = { 'constance/csmruns/ne30_fc5_dbg_const_int_unsrtcol_dstfac_p45':[0,'Constance (Intel-DUST)'], \
                 'constance/csmruns/ne30_fc5_dbg_const_int_unsrtcol_sol_factb_int_1p0':[0,'Constance (Intel-sol_fctb)'], \
                 'constance/csmruns/ne30_fc5_dbg_const_int_unsrtcol_zmconv_c0_ocn_0p0035':[0,'Constance (Intel-zmconv_c0_ocn)'], \
                 'constance/csmruns/ne30_fc5_dbg_const_int_unsrtcol_zmconv_c0_lnd_0p0035':[0,'Constance (Intel-zmconv_c0_lnd)'], \
                 'constance/csmruns/ne30_fc5_dbg_const_int_unsrtcol_uwshcu_rpen_10p0':[0,'Constance (Intel-uwschu_rpen)'], \
                 'constance/csmruns/ne30_fc5_dbg_const_int_unsrtcol_cldfrc_dp1_0p14':[0,'Constance (Intel-cldfrc_dp1)'], \
                 'constance/csmruns/ne30_fc5_dbg_const_int_unsrtcol_nu_p_1p0x10e14':[0,'Constance (Intel-nu_p)'], \
                 'constance/csmruns/ne30_fc5_dbg_const_int_unsrtcol_nu_9p0x10e14':[0,'Constance (Intel-nu)'], \
                 'constance/csmruns/ne30_fc5_dbg_const_int_unsrtcol_cldfrc_rhminh_p9':[0,'Constance (Intel-rhminh)'] \
            }

cld_cases = {'cori/ne30_fc5_ndbg_cori_has_int_unsrtcol':[0,'Cori Has(Intel-NDBG)'], \
                'cori/ne30_fc5_ndbg_cori_knl_int_unsrtcol':[0,'Cori KNL(Intel-NDBG)'], \
                'cori/ne30_fc5_ndbg_cori_has_gnu_unsrtcol':[0,'Cori Has(GNU-NDBG)'], \
                'cori/ne30_fc5_dbg_cori_has_int_unsrtcol':[0,'Cori Has(Intel-DBG)'], \
                'cori/ne30_fc5_dbg_cori_knl_int_unsrtcol':[0,'Cori KNL(Intel-DBG)'], \
                'cori/ne30_fc5_dbg_cori_has_gnu_unsrtcol':[0,'Cori Has(GNU-DBG)'], \
                'titan/ne30_fc5_ndbg_titan_int_unsrtcol':[0,'Titan(Intel-NDBG)'], \
                'titan/ne30_fc5_ndbg_titan_pgi_unsrtcol':[0,'Titan(PGI-NDBG) '], \
                'titan/ne30_fc5_dbg_titan_pgi_unsrtcol':[0,'Titan(PGI-DBG) '], \
                'constance/csmruns/ne30_fc5_ndbg_const_int_unsrtcol':[0,'Constance (Intel-NDBG)'], \
                 'constance/csmruns/ne30_fc5_dbg_const_int_unsrtcol':[1,'Constance (Intel-DBG)'] \
            }

rmse_or_diff   = 1 #0: DIFF 1: RMSE

#history files related info to form file names in a loop
acme_hist_dir  = 'run'
cam_hist_str   = '.cam.h0.'
perturb_str    = ['wopert','pospert','negpert']

#other files needed
inic_cond_file = 'inic_cond_file_list_ne30.txt'
var_file       = 'physup_calls_fc5_no_none.txt'

#plot related info
xlabel_file = 'xlabels_fc5_no_none.txt'
if(rmse_or_diff == 0):
   ylabel = 'Maximum Error in the temperature (K) field'
elif(rmse_or_diff == 1):
   ylabel = 'Normalized RMSE Error'

ymin  = -1
ymax  = 10.0
xmin  = 0
clr   = ['b', 'g', 'r', 'c', 'm', 'y', 'k', [0.5,0.5,0.5]] # for each case
mrk   = ['o','*','x','s']
pert_lgnd = ['_wo','_P+','_P-']
title = "Compared against "+cntl_case[cntl_case.keys()[0]][1]+" at time:"+ time

#counters
cld_ires = 0
tst_ires = 0
iclr = 0
imrk = 0

#===================================================
# Functions
#===================================================

def check_fix_min(output):
   dim0 = output.shape[0]
   for idim in range(dim0):
      if(all(iout <= 0.0 for iout in output[idim,:])):
         print("All diffs are <= zero , reseting last element to 1e-16")
         output[idim,-1] = 1.e-16

         for iout in output[idim,:]:
            if(iout <= 0.0 ):
               print("Diff/RMSE is <= zero , reseting element to 1e-16")
               output[idim,iout] = 1.e-16            
   return output


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
   #perturb_str_lp   = perturb_str
   perturb_str_lp   = perturb_str[1:len(perturb_str)]

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
         #apert_cntl = apert
         apert_cntl =  perturb_str[0]
         if(case_typ == 'cloud'):
            apert_cntl = perturb_str[0] #'wopert' should be the cntl case for cloud cases
         #form case name
         tmp_case_name  = icase_name + '_'+ acond.split('.nc')[0]+'_'+apert
         tmp_case_name_cntl = cntl_casename + '_'+ acond.split('.nc')[0]+'_'+apert_cntl
         ifile      = ipath+'/'+tmp_case_name+'/'+acme_hist_dir+'/'+tmp_case_name+cam_hist_str+acond_2+'-'+time+'.nc'
         ifile_cntl = ipath_cntl+'/'+tmp_case_name_cntl+'/'+acme_hist_dir+'/'+tmp_case_name_cntl+cam_hist_str+acond_2+'-'+time+'.nc'
         if(not chk_file_only):
            if(case_typ == 'cloud'):
               output_tmp = rmse_diff_var(ifile, ifile_cntl, var_list, pltvar_sfx, rmse_or_diff)
               output     = check_fix_min(output_tmp)
               cld_res[cld_ires,icond,ipert,0:len_pltvar_sfx,0:len_var_list]  = output
               for isfx in range(len_pltvar_sfx):
                  ax_sub = plt.subplot(row_sbplt,col_sbplt,isfx+1)
                  ax_sub.semilogy(cld_res[cld_ires,icond,ipert,isfx,:],color=clr[iclr],linestyle='-',marker=mrk[imrk],label=ival[1], linewidth = 2, alpha = 0.7) 
                  ax_sub.set_title(pltvar_sfx[isfx]) 

               #find min max for cloud hashed region
               #for iout in range(len(var_list)):
               #   if(mncld[iout] > output[iout]):
               #      mncld[iout] = output[iout]
               #   if(mxcld[iout] < output[iout]):
               #      mxcld[iout] = output[iout]                     
            else:
               output_tmp  = rmse_diff_var(ifile, ifile_cntl, var_list, pltvar_sfx, rmse_or_diff)         
               output     = check_fix_min(output_tmp)
               tst_res[tst_ires,icond,ipert,0:len_pltvar_sfx,0:len_var_list]  = output
               for isfx in range(len_pltvar_sfx):
                  ax_sub = plt.subplot(row_sbplt,col_sbplt,isfx+1)
                  ax_sub.semilogy(tst_res[tst_ires,icond,ipert,isfx,:],color=clr[iclr],linestyle='-',marker=mrk[imrk],label=ival[1], linewidth = 2, alpha = 0.7)
                  ax_sub.set_title(pltvar_sfx[isfx]) 

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
         else:
            if ( not os.path.isfile(ifile)):
               print('Test file:'+ifile+' doesnt exists; exiting....')
               sys.exit()
            if ( not os.path.isfile(ifile_cntl)):
               print('CNTL file:'+ifile_cntl+' doesnt exists; exiting....')
               sys.exit()
   if(case_typ == 'cloud'):
      cld_ires += 1
   else:
      tst_ires += 1

   iclr += 1
   if (iclr == len(clr) - 1):
      imrk += 1
      iclr  = 0


#get list of variable suffix
with open(var_file, 'r') as fvar:
   var_list = fvar.readlines()
fvar.close()
var_list     = map(str.strip,var_list)
len_var_list = len(var_list)
xmax         = len_var_list 

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

mncld = np.empty(len_var_list)
mxcld = np.empty(len_var_list)
mncld.fill(float("inf"))
mxcld.fill(float("-inf"))


#create an empty array with dims[# of tst_cases, # of inic conds, # of perts, # of check point vars]
tst_res = np.empty([len(tst_cases),len(inic_list),len(perturb_str)-1,len_pltvar_sfx,len_var_list])
cld_res = np.empty([len(cld_cases),len(inic_list),len(perturb_str)-1,len_pltvar_sfx,len_var_list]) #cntl case is 'wopert' in this case

ax = plt.gca()
axf = plt.gcf()
axf.set_facecolor('white') #set color of the plot

ipath_cntl = cmn_path+'/'+cntl_case.keys()[0]

cntl_casename = ntpath.basename(ipath_cntl)

print('Control case is: '+cntl_casename)
#Loop through each case and prepare P+ and P- curves

#pdb.set_trace()
for icase_pth, ival in cld_cases.iteritems():
   compute_res(icase_pth,ival,'cloud')
   #Bif (not chk_file_only) :
      #Bax.fill_between(range(xmin, xmax), mncld, mxcld, facecolor='gray', lw=0, alpha=0.5 )

for icase_pth, ival in tst_cases.iteritems():
   compute_res(icase_pth,ival, 'test')


print(ctime())
if (not chk_file_only) :
   print("Plots are being generated...")

   #Bax.fill_between(range(xmin, xmax), mncld, mxcld, facecolor='gray', lw=0, alpha=0.5 )

   handles, labels = plt.gca().get_legend_handles_labels()
   labels, ids = np.unique(labels, return_index=True)
   handles = [handles[i] for i in ids]
   plt.legend(handles, labels, loc='best')#, fontsize = 35)
   plt.ylabel(ylabel)
   plt.suptitle(title) 
   #plt.savefig('data.png') 
   plt.show()
else:
    print("ALL files are present")

############ extra codes
#clr   = [[1.0,0.4,0.6],'c','g','r','m','b','k','y',[1,0.4,0.8],[0.4,0.4,0.4],[0.6,0.5,0.4],[0.7,0.5,0.8],[0.6,0.9,0.4],[0.2,0.5,1.0],[0.7,1.0,0.4]] # for each case

#old cases:
# cntl_case = {'cori/ne30_fc5_default_cori_knl_int':[1,'Cori KNL(Intel O0)']} #flag to include in plotting or not is not used for control case

# tst_cases = {'constance/csmruns/ne30_fc5_cldfrc_dp1_0.14_const_int':[0,'PAR(dp1=0.14) '], \
#                 'constance/csmruns/ne30_fc5_code_mod_dm_const_int':[0,'MOD(DM) '], \
#                 'constance/csmruns/init_r8_ne30_fc5_code_mod_p_const_int':[0,'Init r8 MOD(P)'], \
#                 'constance/csmruns/all_r8_ne30_fc5_code_mod_p_const_int':[0,'ALL r8 MOD(P)'], \
#                 'constance/csmruns/ne30_fc5_code_mod_p_const_int':[0,'MOD(P) '], \
#                 'titan/ne30_fc5_def_ndbg_titan_pgi_unsort_cols':[1,'Titan(PGI-O2-unsort)'], \
#                 'titan/ne30_fc5_def_ndbg_titan_int_1801163_cmplr_unsort_cols':[1,'Titan(Intel-O2-unsort)'] \
#             }

# cld_cases = {'cori/ne30_fc5_default_nondbg_cori_has_int':[0,'Cori Haswell(Intel O2)'], \
#                 'cori/ne30_fc5_default_cori_has_int':[0,'Cori Haswell(Intel O0)'],\
#                 'cori/ne30_fc5_default_nondbg_cori_knl_int':[0,'Cori KNL(Intel O2)'], \
#                 'cori/ne30_fc5_default_cori_has_gnu':[0,'Cori Haswell (GNU O0)'], \
#                 'cori/ne30_fc5_default_nondbg_cori_has_gnu':[0,'Cori Haswell(GNU O2)'], \
#                 'cori/experiments/just_o0_ne30_fc5_default_nondbg_cori_has_int':[0,'Cori Haswell (Intel O2->O0-NDBG FLG)'], \
#                 'cori/experiments/o2_w_dbg_flg_ne30_fc5_default_nondbg_cori_has_int':[0,'Cori Haswell(Intel O0->O2-DBG FLG)'], \
#                 'constance/csmruns/ne30_fc5_default_nondebug_const_int':[1,'Constance(Intel O2)'], \
#                 'constance/csmruns/ne30_fc5_default_const_int':[0,'Constance(Intel O0)'], \
#                 'eos/ne30_fc5_default_nondebug_eos_int':[1,'EOS(Intel O2)'], \
#                 'titan/ne30_fc5_default_nondebug_titan_int_18_0_1_163_compiler':[0,'Titan(Intel O2_163)'], \
#                 'titan/ne30_fc5_default_titan_int':[0,'Titan(Intel O0_163)'], \
#                 'titan/ne30_fc5_default_nondebugtitan_int':[0,'Titan(Intel O2)'], \
#                 'titan/ne30_fc5_default_nondebug_titan_pgi':[0,'Titan(PGI O2)'], \
#                 'titan/ne30_fc5_default_titan_pgi':[0,'Titan(PGI O0)'], \
#                 'cascade/csmruns/ne30_fc5_default_cas_int':[0,'Cascade(Intel O0)'], \
#                 'cascade/csmruns/ne30_fc5_default_nondebug_cas_int':[0,'Cascade(Intel O2)'], \
#                 'eos/ne30_fc5_default_eos_int':[0,'EOS(Intel O0)'] \
#                 }

