load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
begin
  ;;==== USER INPUT BEGINS ====

  ;;Read full description of variable
  filename_desc = "pergro_ptend_names.txt"
  varsRead_desc = asciiread(filename_desc,-1,"string")

  ;;Read variable subscript
  filename = "pergro_ptend_names.txt"
  varsRead = asciiread(filename,-1,"string")

  ;;Form temprature variable names
  vars = varsRead
  do i = 0, dimsizes(varsRead) - 1
    vars(i) = "t_"+str_left_strip(varsRead(i))
  end do

  ;;Case names

  casename1 = "ne30_av1c_rebased_03032018_nopert"
  casename2 = "ne30_av1c_rebased_03032018_pospert"

  tstep     = "00000"
  date      = "0001-01-02"
  
  ;;Path strings
  path1Str  = "/pic/scratch/sing201/csmruns/"+casename1+"/run/"+casename1+".cam.h0."+date+"-"+tstep+".nc"
  path2Str  = "/pic/scratch/sing201/csmruns/"+casename2+"/run/"+casename2+".cam.h0."+date+"-"+tstep+".nc"

  ;;path1Str  = "/dtemp/sing201/archive/"+casename1+"/atm/hist/"+casename1+".cam.h0."+date+"-"+tstep+".nc"
  ;;path2Str  = "/dtemp/sing201/archive/"+casename2+"/atm/hist/"+casename2+".cam.h0."+date+"-"+tstep+".nc"

  ;;path1Str  = "/lustre/sing201/csmruns/"+casename1+"/run/"+casename1+".cam2.h0."+date+"-"+tstep+".nc"
  ;;path2Str  = "/lustre/sing201/csmruns/"+casename2+"/run/"+casename2+".cam2.h0."+date+"-"+tstep+".nc"

  ;;=== USER INPUT ENDS ===

  do ivar = 0,dimsizes(vars)-1

    ;;Variable name in the climo file
    var=str_strip(vars(ivar))

    ;Read in two files
    f1=addfile(path1Str,"r")
    f2=addfile(path2Str,"r")

    ;;See if variable exist in the file or not
    if(isfilevar(f1, var)) then
      var1_nc=f1->$var$
    else
      print("Variable: "+var+" is not present in "+casename1+"...skipping")
      print(""+path1Str)
      continue
    end if
    if(isfilevar(f2, var)) then
      var2_nc=f2->$var$
    else
      delete(var1_nc);;delete var1_nc as we are skipping the calc.
      print("Variable: "+var+" is not present in "+casename2+"...skipping")
      continue
    end if

    ;;For first time stamp only
    it = 0 

    ;;== Extract maximum value ==
     
    ;;Difference the matricies and take absolute
    diffmat = abs(var1_nc(it,:,:) - var2_nc(it,:,:))
    dimsz   = dimsizes(diffmat)
    mat_1d  = ndtooned(diffmat)
    indmax  = maxind(mat_1d)
    indices = ind_resolve(indmax,dimsz)
                       
    lev  = indices(0,0)
    nlat = indices(0,1)
    nlon = indices(0,2)
    diffval = var1_nc(it,lev,nlat,nlon)-var2_nc(it,lev,nlat,nlon)
    print("MAX Val:"+varsRead_desc(ivar)+"["+vars(ivar)+"]"+"- CASE A:"+sprintf("%5.16g",var1_nc(it,lev,nlat,nlon)) \
    +"; CASE B:"+sprintf("%5.16g",var2_nc(it,lev,nlat,nlon))+ "; DIFF:"+sprintf("%5.16g",diffval) + " Lev:"+lev+";  [cam]Lev:"+(lev+1)+"; Lat:"+var1_nc&lat(nlat)+"; Lon:"+var1_nc&lon(nlon))
    
  end do    

end
