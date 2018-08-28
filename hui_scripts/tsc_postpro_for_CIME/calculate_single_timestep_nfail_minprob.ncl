load "./read_rmsd.ncl"

undef("calculate_nfail_minprob")
procedure calculate_single_timestep_nfail_minprob( \
          tstRunCaseName:string, refRunCaseName:string, \
          tstModelOutDir:string, refModelOutDir:string, \
          rmsdOutputRoot:string, \
          out_time_sec:integer,  \
          tval0:float, \
          lmake_boxplot:logical, \
          nfail_out:integer, minprob_out:float  \
          )
begin

  regionList  = (/"LAND","OCEAN"/)
  nregions = dimsizes(regionList)

  lnormalize = True
  ldebug     = False
  
  ;--------------------
  out_time_str = "_"+sprinti("%05d",out_time_sec)

  print("")
  print("-------------------------")
  print("output time = "+out_time_str)
  print("-------------------------")
  print("")

  ;==============================================================================
  ; 1. Read in previously calculated RMSDs
  ;==============================================================================
  ; Read rmsds of the reference runs
  ;---------------------------------------------------
  rmsd_filename_prefix = refRunCaseName+"__vs__"+refRunCaseName
  rmsd_filename_suffix = out_time_str+".txt"

  rmsd_ref = read_rmsd_file( rmsdOutputRoot+"/"+"TSC_rmsd_output__"+rmsd_filename_prefix, \
                             "rmsd__"+rmsd_filename_prefix+"__", rmsd_filename_suffix, \
                             regionList, ldebug )

  if (lnormalize) then
     rmsd_ref_avg = dim_avg(rmsd_ref)  ; ensemble avg of each region and member
     rmsd_ref = rmsd_ref / conform(rmsd_ref,rmsd_ref_avg,(/0,1/))
  end if

  varnames = rmsd_ref@varnames
  nvars = dimsizes(varnames)

  ;---------------------------------------------------
  ; read rmsds of the test runs
  ;---------------------------------------------------
  rmsd_filename_prefix = tstRunCaseName+"__vs__"+refRunCaseName
  rmsd_filename_suffix = out_time_str+".txt"

  rmsd_exp = read_rmsd_file( rmsdOutputRoot+"/TSC_rmsd_output__"+rmsd_filename_prefix, \
                             "rmsd__"+rmsd_filename_prefix+"__", rmsd_filename_suffix, \
                             regionList, ldebug)

  nexpmembers = rmsd_exp@nmembers

  ; sanity checks 
  if (any(dimsizes(rmsd_exp).ne.dimsizes(rmsd_ref))) then
     print("Aborted! Experiment RMSD data does not have assumed size!")
     print("Check file "+rmsdOutputRoot+"/TSC_rmsd_output__"+rmsd_filename_prefix+"/"+rmsd_filename_prefix+regionList(0)+rmsd_filename_suffix)
     exit
  end if

  if (any(rmsd_exp@varnames.ne.rmsd_ref@varnames)) then
     print("Aborted! Reference and experiment RMSD data files contain different variables!")
     exit
  end if

  ; normalize
  if (lnormalize) then
     rmsd_exp = rmsd_exp / conform( rmsd_exp, rmsd_ref_avg, (/0,1/) )
  end if

  if (ldebug) then
     print("")
     print(" Reading of RMSDs done.")
     print("")
  end if

  ;==============================================================================
  ; 2. statistical testing
  ;==============================================================================
  if (ldebug) then
     lgflag = where( rmsd_exp.gt.rmsd_ref, 1., 0.)
     lgflagavg = dim_sum(lgflag)/nexpmembers
     print(" # of members with RMSD_exp > RMSD_ref")
     write_matrix(lgflagavg,nvars+"f5.2",False)
     delete(lgflag)
     delete(lgflagavg)
  end if

  ;---------------------------------------------------
  ; Calculate delta RMSD and the ensemble mean/stddev
  ;---------------------------------------------------
  rmsd_diff = rmsd_exp - rmsd_ref
  diff_avg  = dim_avg(rmsd_diff)
  diff_std  = dim_stddev(rmsd_diff)
  diff_std@_FillValue = -999.

  if (ldebug) then
     print(" RMSD diff")
     do jj = 0,nregions-1
        write_matrix(rmsd_diff(jj,:,:),nexpmembers+"E13.5",False)
     end do
  end if

  ;---------------------------------------------------
  ; Calculate t-statistic
  ;---------------------------------------------------
  allzeros = diff_avg.eq.0. .and. diff_std.eq.0.
  diff_std_tmp = where( .not.allzeros, diff_std, diff_std@_FillValue )
  tval = where( .not.allzeros, diff_avg*sqrt(1.*nexpmembers)/diff_std_tmp, 0.)

  ;---------------------------------------------------
  ; calculate p-value 
  ;---------------------------------------------------
  paramA = tval    ; initialize
  paramB = tval    ; initialize

  df     = nexpmembers - 1
  paramA = df/2.0  ; see example 2 at https://www.ncl.ucar.edu/Document/Functions/Built-in/betainc.shtml
  paramB = 0.5     ; see example 2 at https://www.ncl.ucar.edu/Document/Functions/Built-in/betainc.shtml
  prob = where( .not.allzeros, betainc( df/(df+tval^2), paramA, paramB), 2. )
  prob = prob*0.5 ; one-sided

  if (ldebug) then
    ;write_matrix(diff_avg,nexpmembers+"f8.3",False)
    ;write_matrix(diff_std/sqrt(12.),nexpmembers+"f8.3",False)
     print(" t-values")
     write_matrix(tval(:,:),nexpmembers+"f10.3",False)
     print(" probability")
     write_matrix(prob(:,:),nexpmembers+"g10.3",False)
  end if

  ;------------------------------------
  ; Pass/fail flags, and result summary
  ;------------------------------------
  flag_all = where( tval.gt.tval0, 1, 0 )

  prob_tmp = where( tval.gt.0, prob, -999. )
  prob_tmp@_FillValue = -999.

  if (ldebug) then
     print("")
     print(" Exp name = "+tstRunCaseName)
     print(" # of variables failing criterion = "+sum(flag_all))
     print(" min. probability = "+(min(prob_tmp)*100)+" %")
     print("")
  end if

  nfail_out   = sum(flag_all)
  minprob_out = min(prob_tmp)

  ;====================================
  ; plot dRMSD of individual variables 
  ;====================================
  if (lmake_boxplot) then

     ;------------------------------------------------------------------------------------
     ; use different colors to indicate pass or fail for individual regions and variables
     ;------------------------------------------------------------------------------------
     colormap = "StepSeq25"

     fillcolor_pass = 20
     fillcolor_fail = 6

     markcolor_pass = 17
     markcolor_fail = 3

     color = where( tval.gt.tval0, markcolor_fail, markcolor_pass )

     ;------------------------------------------------------------------------------------
     ; Create plot file
     ;------------------------------------------------------------------------------------
     plotdir      = rmsdOutputRoot+"/figures/"
     system("mkdir -p "+plotdir)

     plotFileName = "fig__"+tstRunCaseName+"__vs__"+refRunCaseName+"__boxplot"+out_time_str
     plotFormat   = "pdf"

     print("Single-timestep box plot done. See "+plotdir+plotFileName+"."+plotFormat)

     wks = gsn_open_wks(plotFormat,plotdir+"/"+plotFileName)
     gsn_merge_colormaps(wks,colormap,"gsltod")

     load "./plot_single_timestep_dRMSD_mean_stddev_boxplot_onesided.ncl"

  end if

  delete(varnames)
end
