#!/usr/bin/python

#Python version: python 2.7.8

import ntpath
from rmse_diff_var import rmse_diff_var
#import pylab as pl
#import numpy as np
#import sys


cmn_path = '/pic/projects/climate/sing201/acme1/other_machs/other_machines_perturb'

cntl_case = 'titan/ne30_fc5_def_ndbg_titan_int_1801163_cmplr_unsort_cols'

tst_case = 'titan/ne30_fc5_def_ndbg_titan_pgi_unsort_cols'

inic_cond = 'init_gen_clim_FC5_default.cam.i.2008-01-01-00000'

perturb_str = ['wopert','wopert']

#extract date and time from inic_cond
date_time = inic_cond.split('.')[3].split('_')[0]
print('date and time is:'+date_time)

rmse_or_diff   = 1 #0: DIFF 1: RMSE

#history files related info to form file names in a loop
acme_hist_dir  = 'run'
cam_hist_str   = '.cam.h0.'
time           = '00000'

#other files needed
var_file       = 'physup_calls_fc5_no_none.txt'



#get list of variable suffix
with open(var_file, 'r') as fvar:
   var_list = fvar.readlines()
fvar.close()
var_list = map(str.strip,var_list)

ipath_cntl = cmn_path+'/'+cntl_case

cntl_casename = ntpath.basename(ipath_cntl)

ifile      = cmn_path+'/'+tst_case+'/'+ntpath.basename(tst_case)+'_'+inic_cond+'_'+perturb_str[0]+'/'+acme_hist_dir+'/'+ntpath.basename(tst_case)+'_'+inic_cond+'_'+perturb_str[0]+cam_hist_str+date_time+'.nc'
ifile_cntl = cmn_path+'/'+cntl_case+'/'+ntpath.basename(cntl_case)+'_'+inic_cond+'_'+perturb_str[1]+'/'+acme_hist_dir+'/'+ntpath.basename(cntl_case)+'_'+inic_cond+'_'+perturb_str[1]+cam_hist_str+date_time+'.nc'

tst_res  = rmse_diff_var(ifile, ifile_cntl, var_list, 'T_',rmse_or_diff,index=True)



