load "./calculate_single_timestep_solution_rmsd.ncl"
load "./calculate_single_timestep_nfail_minprob.ncl"
begin

  ;#######################################################################################################
  ; Section 1. Minimum information needed from the user.
  ;#######################################################################################################

  ;-------------------------------------------------------------
  ; Type of postprocessing
  ;-------------------------------------------------------------
  postpro_type = 0   ; postprocessing baseline simulations. Only calculate solution RMSDs
  postpro_type = 1   ; postprocessing simulations conducted with a test code or in a test environment.
                     ; First calculate solution RMSDs, then compare with those from the baseline
                     ; and get a pass/fail.
  
  ;-------------------------------------------------------------
  ; Case names and paths to multi-instance simulation output 
  ;-------------------------------------------------------------
  ; Case name and output location of the reference run (1s time step).

  refRunCaseName = "SRC.ne4_ne4.FC5AV1C-04P2.constance_intel.G.2018-02-08-033447-557834470"
  refModelOutDir = "/pic/scratch/wanh895/csmruns/"+refRunCaseName+"/run/"

  ; Case name and output location of the test run (2s time step).
  ;  - When postpro_type = 0, the test run is expected to have the same and path as the reference run;
  ;  - When postpro_type = 1, the test run is expected to have a difference case name.

 ;tstRunCaseName = "SRC.ne4_ne4.FC5AV1C-04P2.constance_intel.G.2018-02-08-033447-557834470"
  tstRunCaseName = "SRC.ne4_ne4.FC5AV1C-04P2.constance_intel.2018-02-08-040842-290920643_c0_ocn_0045"
  tstModelOutDir = "/pic/scratch/wanh895/csmruns/"+tstRunCaseName+"/run/"

  ;----------------------------------------------------------------
  ; Root dir in which ASCII output and figures will be generated
  ;----------------------------------------------------------------
  rmsdOutputRoot = "./"

  ;#######################################################################################################
  ; Section 2. For developers who want to try variants of the TSC test. 
  ;#######################################################################################################

  ;-------------------------------------------------------------
  ; Ensemble members: start and end indices
  ;-------------------------------------------------------------
  ims = 1
  ime = 12

  ;-------------------------------------------------------------
  ; Start and end vertical levels used in the RMSD calculation
  ;-------------------------------------------------------------
  ilevS =  0  ;  0 is the first level (model top)
  ilevE = -1  ; -1 means all levels

  ;--------------------------------------------------------------------------------------------------------
  ; Model output time (seconds). Solution RMSD will be calculated at each output time step specified here.
  ;--------------------------------------------------------------------------------------------------------
  out_time_sec_start = 0     ; not included
  out_time_sec_end   = 600   ; included
  out_time_sec_int   = 10    ; interval

  ; Time window within which the timestep-by-timestep results will be used to determine an overall pass/fail

  passfail_start_minute = 5    ; unit is minute
  passfail_end_minute   = 10

  ; Model output time at which box plots will be created to show the pass/fail of individual regions and variables
 
  boxplot_sec_List = (/300,600/)  ; unit is second

  ;----------------------------------------------------------
  ; Threshold probability and the corresponding t-statistic
  ;----------------------------------------------------------
  prob0 = 0.5 *0.01  ; = 0.5%
  tval0 = 3.106

  ;----------------
  ; Plot settings
  ;----------------
  colormap = "StepSeq25"

  fillcolor_pass = 20
  fillcolor_fail = 6

  markcolor_pass = 17
  markcolor_fail = 3

  plotFormat = "pdf"
  plotDir = rmsdOutputRoot+"/figures/"
  system("mkdir -p "+plotDir)

  ;#######################################################################################################
  ; End of user specification section. 
  ;#######################################################################################################

  ;--------------------------------------------------------------------------------------------------------
  ; Set switches based on postpro_type
  ;--------------------------------------------------------------------------------------------------------
  if (postpro_type.eq.0) then  ; baseline
     lcalculate_rmsd = True
     ltest_pass_fail = False
  else
  if (postpro_type.eq.1) then  ; test code or env.
     lcalculate_rmsd = True
     ltest_pass_fail = True
  else
     print("Unrecognized postpro_type. Abort.")
     exit
  end if
  end if
  
  ;--------------------------------------------------------------------------------------------------------
  ; Total number of time steps for which RMSD will be calculated and dRMSD will be evaluated
  ;--------------------------------------------------------------------------------------------------------
  ntime_slice = (out_time_sec_end - out_time_sec_start)/out_time_sec_int

  ;--------------------------------------------------------------------------------------------------------
  ; Calculate RMSD
  ;--------------------------------------------------------------------------------------------------------
  if (lcalculate_rmsd) then
     do itime = 0,ntime_slice-1

        out_time_sec = out_time_sec_start + (itime+1)*out_time_sec_int  ; current model time

        calculate_single_timestep_solution_rmsd(tstRunCaseName, refRunCaseName, \
                                                tstModelOutDir, refModelOutDir, \
                                                rmsdOutputRoot, out_time_sec,   \
                                                ims, ime, ilevS, ilevE )
     end do
  end if

  ;--------------------------------------------------------------------------------------------------------
  ; Test pass/fail
  ;--------------------------------------------------------------------------------------------------------
  if (ltest_pass_fail) then

     ; Arrays that will contain tests results for all time steps

     nfail   = new( (/ntime_slice/),"integer" )   ; number of failing variables at each time slice
     minprob = new( (/ntime_slice/),"float" )     ; min. probability of RMSD being equal

     nfail@_FillValue = -9
     minprob@_FillValue = -999.

     nfail   = nfail@_FillValue
     minprob = minprob@_FillValue

     ; Perform statistical test for each time step. 
     ; Determine the number of failing variables and the min. probability for each time step.

     do itime = 0,ntime_slice-1

        out_time_sec  = out_time_sec_start + (itime+1)*out_time_sec_int  ; current time slice
        lmake_boxplot = any(out_time_sec.eq.boxplot_sec_List)            ; make box plot?

        calculate_single_timestep_nfail_minprob(tstRunCaseName, refRunCaseName,      \ ; in
                                                tstModelOutDir, refModelOutDir,      \ ; in
                                                rmsdOutputRoot, out_time_sec, tval0, \ ; in
                                                lmake_boxplot,                       \ ; in
                                                nfail(itime), minprob(itime)  )        ; out
     end do

     ; Determine the overall pass/fail. Write result to ASCII file.

     its = passfail_start_minute*60/out_time_sec_int - 1
     ite = passfail_end_minute  *60/out_time_sec_int - 1
     
     l_overall_fail   =  all(nfail(its:ite).ge.1)
     overall_passfail = where( l_overall_fail, "FAIL", "PASS")

     filename = rmsdOutputRoot+"/TSC_PassFail__"+tstRunCaseName+"__vs__"+refRunCaseName
     asciiwrite(filename,overall_passfail)

     ; Plot nfail and minprob time series

     if (l_overall_fail) then
        linecolor = fillcolor_fail
        markcolor = markcolor_fail
     else
        linecolor = fillcolor_pass
        markcolor = markcolor_pass
     end if 

     filename = "fig__"+tstRunCaseName+"__vs__"+refRunCaseName+"_time_series"

     wks = gsn_open_wks(plotFormat,plotDir+"/"+filename)
     gsn_define_colormap(wks,colormap)
     load "./plot_time_series_nfail_minprob.ncl"

     print("Time series plots done. See "+plotDir+"/"+filename+"."+plotFormat)
     delete(wks)

  end if
end
