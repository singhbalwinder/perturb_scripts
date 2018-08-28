load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"

undef("calculate_solution_rmsd")
procedure calculate_single_timestep_solution_rmsd(      \
          tstRunCaseName:string, refRunCaseName:string, \
          tstModelOutDir:string, refModelOutDir:string, \
          rmsdOutputRoot:string, \
          out_time_sec:integer,  \
          ims:integer, ime:integer, \
          ilevS:integer, ilevE:integer \
          )
begin

  ;----------------------------------------------------------------------------------------------------
  ; Model time step sizes (unit: second) used for the simulations. These have to be consistent with what
  ; was used by the CIME system test script src.py
  ;----------------------------------------------------------------------------------------------------
  tstRunDtimeLabel = ".DT0002"
  refRunDtimeLabel = ".DT0001"

  ;----------------------------------------------------------------------------------------------------
  ; Prognostic variables of the atm model and geographical regions for which RMSDs will be calculated
  ;----------------------------------------------------------------------------------------------------
  varNameList  = (/"T","Q","V","CLDLIQ","CLDICE","NUMLIQ","NUMICE","num_a1","num_a2","num_a3"/)
  nvar         = dimsizes(varNameList)

   regions = (/"LAND","OCEAN"/)
  nregions = dimsizes(regions)

  itime  = 0             ; this script assumes that each h0 file contains only 1 time step
  nmemb = ime - ims + 1  ; number of ensemble members

  out_time_str = sprinti("%0.5i",out_time_sec)

  print("")
  print(" h0 file output time = "+out_time_str)
  print("")
  ;-----------------------------
  ; Create dir for ASCII output
  ;-----------------------------
  rmsd_output_dir = rmsdOutputRoot+"TSC_rmsd_output__"+tstRunCaseName+"__vs__"+refRunCaseName+"/"
  system("mkdir -p "+rmsd_output_dir)
  print("RMSD output dir = "+rmsd_output_dir)

  ;################################
  ; Data processing starts here
  ;################################
  ; The array holding output to ASCII file
  diffnorm_table = new( (/nregions,nmemb,nvar/),"double" )

  do iv = 0,nvar-1
     print("Calculating RMSD for prognostic variable "+varNameList(iv))

     do im = 0,nmemb-1

        membID = sprinti("%04d",im+ims)
        h0FileName =  (/refModelOutDir + refRunCaseName + ".cam_"+membID+".h0.0001-01-01-"+out_time_str+".nc"+refRunDtimeLabel, \
                        tstModelOutDir + tstRunCaseName + ".cam_"+membID+".h0.0001-01-01-"+out_time_str+".nc"+tstRunDtimeLabel  /)
        nfiles = dimsizes(h0FileName)

        diffnorm = new( (/nregions/), "double" )

        do ifile = 0,nfiles-1

           ;------------------------------------------------------------
           ; Open model output file and get some basic info.
           ;------------------------------------------------------------
           File     = addfile(h0FileName(ifile),"r")

           ; Get cell area and land fraction. These will be used as weights for horizontal averaging
           area     = File->area
           landfrac = File->LANDFRAC(itime,:)

           ; Get prognostic variable
           varName  = varNameList(iv)
           ndims    = dimsizes(dimsizes(File->$varName$))

           ; For a spatially 3D variable array, the dimensions in h0 file are expected to be (ntime,nlev,ncol)
           ; for the spectral element dycore
           if (ndims.ne.3) then
              print("Unexpected array shape for "+varName+". Abort.")
              print("-----")
              printVarSummary(varName)
              print("-----")
              exit
           end if

           ;------------------------------------------------------------------------------------------------
           ; Compute pressure layer thickness. This needs to be done for both the ref run and the test run.
           ;------------------------------------------------------------------------------------------------
           p0    = File->P0
           ps    = File->PS(itime,:)

           hyai  = File->hyai
           hybi  = File->hybi
           nlev  = dimsizes(hyai) -1
           daAll = hyai(1:nlev) - hyai(0:nlev-1)
           dbAll = hybi(1:nlev) - hybi(0:nlev-1)

           if (ilevE.eq.-1) then
              ilevS = 0
              ilevE = nlev-1
           end if

           da = daAll( ilevS:ilevE )
           db = dbAll( ilevS:ilevE )

           var3d = File->$varName$(itime,ilevS:ilevE,:)

           dp    = conform( var3d, da, 0 )* p0 \
                 + conform( var3d, db, 0 )* conform( var3d, ps, 1 )

           ;----------------------------------
           ; RMS difference and L2 diff norm
           ;----------------------------------
           if (ifile.eq.0) then  ; save the ref solution

              var3d_ref = var3d
                 dp_ref = dp
                 ps_ref = ps

           else ; calculate solution difference

              dpw = 0.5*( dp_ref + dp )
              psw = 0.5*( ps_ref + ps )

              ; vertical integral using pressure thickness as weights
              vint = dim_sum_n( (var3d-var3d_ref)^2 *dpw, 0 )

              ; global mean
              jj = ind(regions.eq."GLOBAL")
              if (.not.ismissing(jj)) then
                 diffnorm(jj) = sqrt( dim_avg_wgt( vint, area, 0 ) \
                                      /dim_avg_wgt( psw,  area, 0 ) )
              end if

              ; land mean
              jj = ind(regions.eq."LAND")
              if (.not.ismissing(jj)) then
                 diffnorm(jj) = sqrt( dim_avg_wgt( vint, area*landfrac, 0 ) \
                                      /dim_avg_wgt( psw,  area*landfrac, 0 ) )
              end if

              ; ocean mean
              jj = ind(regions.eq."OCEAN")
              if (.not.ismissing(jj)) then
                diffnorm(jj) = sqrt( dim_avg_wgt( vint, area*(1.-landfrac), 0 ) \
                                     /dim_avg_wgt( psw,  area*(1.-landfrac), 0 ) )
              end if

           end if ;ifile = 0 or 1
        end do ; file loop (ref vs test run)

        ; copy diffnorm to a larger array for output
        ; diffnorm_table shape: (/nregions,nmemb,nvar/)
        diffnorm_table(:,im,iv) = diffnorm(:)

        delete(diffnorm)
     end do ; im
  end do ; variable loop

  ;##################################################################################
  ; All calculations done. Write results to ASCII files.
  ; We will have one ASCII file for each region and output time step.
  ; The file will contain the RMSDs of all prognostic variables and ensemble members.
  ;##################################################################################
  do jj=0,nregions-1

     output_file_name = rmsd_output_dir+"/rmsd__"+tstRunCaseName+"__vs__"+refRunCaseName+"__" \
                        +regions(jj)+"_"+out_time_str+".txt"

     array1d = new( 2+nmemb*nvar,"string" )
     array1d(0) = "nmembers   = "+nmemb
     array1d(1) = "nvariables = "+nvar
     kk = 2

     do im=0,nmemb-1
     do iv=0,nvar-1
        array1d(kk) = varNameList(iv)+": "+oneDtostring( diffnorm_table(jj,im,iv) )
        kk = kk+1
     end do
     end do

     asciiwrite(output_file_name,array1d)
     delete(array1d)

  end do
  ;##############

end
