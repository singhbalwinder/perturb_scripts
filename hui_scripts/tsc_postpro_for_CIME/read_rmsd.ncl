undef("read_rmsd_file")
function read_rmsd_file( filepath,filename_prefix, filename_suffix, regionList, ldebug )

local asciiFileName, nrows, lines, splitline0, nmembers, splitline1, nvars, \
      varnames, nregions, jj, iln, ir, iv, split1, split2, rmsd_out_avg

begin
  ;-------------------------------------
  ; Inquire size of data matrix
  ;-------------------------------------
  asciiFileName = filepath+"/"+filename_prefix+regionList(0)+filename_suffix

  nrows = numAsciiRow(asciiFileName)
  lines = asciiread(asciiFileName,nrows,"string")
  splitline0 = str_split(lines(0)," ")
  nmembers = toint(splitline0(2))

  splitline1 = str_split(lines(1)," ")
  nvars = toint(splitline1(2))

  delete(lines)
  delete(splitline0)
  delete(splitline1)

  ;-------------------------------------
  ; read in data matrix
  ;-------------------------------------
  nregions = dimsizes(regionList)
  varnames = new(nvars,"string")
  rmsd_out = new((/nregions,nvars,nmembers/),"float")

  do jj = 0,nregions-1

     asciiFileName = filepath+"/"+filename_prefix+regionList(jj)+filename_suffix
     nrows = numAsciiRow(asciiFileName)
     lines = asciiread(asciiFileName,nrows,"string")

     ; real data starting at line 3. 

     iln = 2 
     do ir = 0,nmembers-1
       do iv = 0,nvars-1

          split1 = str_split(lines(iln),":")
          varnames(iv) = split1(0)

          split2 = str_split(split1(1),",")
          rmsd_out(jj,iv,ir) = tofloat(split2(0))

          iln = iln + 1
       end do
     end do

     if (ldebug) then
     print("")
     print("data file: "+asciiFileName)
     print("varnames (rows): "+oneDtostring(varnames))
     print("columns are ensemble members")
     write_matrix(rmsd_out(jj,:,:),nmembers+"E12.5",False)
     end if

     delete(lines)
     delete(split1)
     delete(split2)
  end do ; jj: region loop

  ;------------------------
  ; pack additional info
  ;------------------------
  rmsd_out@varnames = varnames
  rmsd_out@nmembers = nmembers

  return(rmsd_out)
end
