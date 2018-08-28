  ; prep

  diff_max = dim_max(rmsd_diff)
  diff_min = dim_min(rmsd_diff)
  diff_med = dim_median(rmsd_diff)
  ;--------------------

  diff_range = new( (/2,nregions,2,nvars/),"float")

  sdscale = 1./sqrt(1.*nexpmembers)

  nsigma = tval0 
  diff_range(0,:,1,:) = diff_avg - nsigma*diff_std*sdscale
  diff_range(0,:,0,:) = diff_avg + nsigma*diff_std*sdscale

  nsigma = 2 
  diff_range(1,:,1,:) = diff_avg - nsigma*diff_std*sdscale
  diff_range(1,:,0,:) = diff_avg + nsigma*diff_std*sdscale
  ;--------------------
  if (ldebug) then
  print(" RMSD diff range ("+nsigma+" sigma)")
  do jj = 0,nregions-1
     write_matrix(diff_range(0,jj,:,:),nexpmembers+"E15.5",False)
  end do
  end if
  ;--------------------

  ; plot
 
  fontHeight = 0.016 

  res                          = True
 ;res@gsnMaximize              = True    ; Maximize plot in frame
  res@gsnDraw                  = False   ; Don't draw
  res@gsnFrame                 = False   ; Don't advance frame
  res@vpWidthF                 = 0.5    ; Make long and
  res@vpHeightF                = 0.5     ; narrow

  res@trXMinF                  = min(diff_range*1.2) 
  res@trXMaxF                  = max(diff_range*1.2) 

  if (abs(res@trXMinF).lt.abs(res@trXMaxF)*0.1) then
     res@trXMinF = -0.1*abs(res@trXMaxF)
  end if
  res@trYMinF                  = 1       - 0.5
  res@trYMaxF                  = nvars*2 + 0.5 

  res@gsnTickMarksPointOutward = True

  res@tmYLMode                 = "Explicit"
  res@tmYLValues               = ispan(1,nvars*2,1)
  res@tmYLLabels               = new(nvars*2,"string")
  res@tmYLLabels(0:nvars-1)    = varnames+" ("+regionList(0)+")" 
  res@tmYLLabels(nvars:)       = varnames+" ("+regionList(1)+")" 
  res@tmYLLabelFontHeightF     = fontHeight *0.8
  res@tmYROn                   = False
  res@tmXTOn                   = False   ; Turn off top tickmarks
  res@tiXAxisString = "Normalized ensemble mean ~F8~D~F~RMSD"
  res@tmXBLabelFontHeightF = fontHeight*0.9
  res@tiXAxisFontHeightF   = fontHeight
  res@tiYAxisFontHeightF   = fontHeight
  res@tiMainFontHeightF    = fontHeight

  res@tiMainString = res@tiXAxisString+" at t="+(out_time_sec/60.)+" min"

 ;res@tmYLMajorLengthF         = 0.
 ;res@tmYLMajorOutwardLengthF  = 0.  
 ;res@tmXBMajorLengthF         = 0.01
 ;res@tmXBMajorOutwardLengthF  = 0.01

  ;Create blank plot 

  plot = gsn_blank_plot(wks,res)


  framedum = new( (/2,nregions,nvars/),"graphic" )
    boxdum = new( (/2,nregions,nvars/),"graphic" )
    bardum = new(   (/nregions,nvars/),"graphic" )
   meandum = new(   (/nregions,nvars/),"graphic" )
 mediandum = new(   (/nregions,nvars/),"graphic" )

  plyres = True
  plyres@gsLineThicknessF = 3.5

  mkres = True
  mkres@gsMarkerIndex = 16

  icount = 1
  do jj = 0,nregions-1
  do iv = 0,nvars-1

        ;-------------------------------------
        ; add boxes showing the x-sigma ranges 
        ;-------------------------------------
        rangemin = diff_range(0,jj,1,iv)

        ; larger range . always use unfilled polygons (technically 
        ; we will use the polyline function)

        boxhalfhgt = 0.28
        kk = 0
        xx = (/diff_range(kk,jj,1,iv),diff_range(1,jj,0,iv),diff_range(1,jj,0,iv),diff_range(kk,jj,1,iv),diff_range(kk,jj,1,iv)/)
        yy = (/icount-boxhalfhgt, icount-boxhalfhgt, icount+boxhalfhgt, icount+boxhalfhgt, icount-boxhalfhgt/)

        if (rangemin.le.0.) then ; insignificant difference
            plyres@gsLineColor = fillcolor_pass
        else
            plyres@gsLineColor = fillcolor_fail
        end if
            boxdum(kk,jj,iv) = gsn_add_polyline( wks,plot,xx,yy,plyres)

        ; smaller range (2 sigma). always use filled polygons.

        boxhalfhgt = 0.3
        kk = 1
        xx = (/diff_range(kk,jj,1,iv),diff_range(kk,jj,0,iv),diff_range(kk,jj,0,iv),diff_range(kk,jj,1,iv),diff_range(kk,jj,1,iv)/)
        yy = (/icount-boxhalfhgt, icount-boxhalfhgt, icount+boxhalfhgt, icount+boxhalfhgt, icount-boxhalfhgt/)

        if (rangemin.le.0.) then ; insignificant difference
            plyres@gsFillColor = fillcolor_pass 
        else
            plyres@gsFillColor = fillcolor_fail
        end if
            boxdum(kk,jj,iv) = gsn_add_polygon( wks,plot,xx,yy,plyres)

        delete(xx)
        delete(yy)
        ;--------------------------------------
        ; add filled circles showing the mean
        ;--------------------------------------
        if (rangemin.le.0.) then ; insignificant difference
           mkres@gsMarkerColor = markcolor_pass 
        else
           mkres@gsMarkerColor = markcolor_fail
        end if
        mkres@gsMarkerThicknessF = 1.
        mkres@gsMarkerIndex = 16
        mkres@gsMarkerSizeF = 0.006
        meandum(jj,iv) = gsn_add_polymarker( wks,plot,diff_avg(jj,iv),icount,mkres)

        ;----------------------------------------------------------------
        ; add bars showing the range and open circles showing the median
        ;----------------------------------------------------------------
        laddrange = True
        laddrange = False
        if (laddrange) then

           yy = (/icount,icount/)
           xx = (/diff_min(jj,iv),diff_max(jj,iv)/)

           plyres@gsLineColor = 50 
           bardum(jj,iv) = gsn_add_polyline( wks,plot,xx,yy,plyres)
           delete(xx)
           delete(yy)

        end if
        ;--------------------
        ldrawmedian = True
        ldrawmedian = False
        if (ldrawmedian) then
        mkres@gsMarkerIndex = 4 
        mkres@gsMarkerThicknessF = 2.
        mediandum(jj,iv) = gsn_add_polymarker( wks,plot,diff_med(jj,iv),icount,mkres)
        end if
        ;--------------------

     icount = icount + 1
  end do
  end do

  ; add zero line
 
  lnres = True
  lnres@gsLineColor = NhlNewColor(wks,0.5,0.5,0.5)
  lnres@gsLineThicknessF = 2.
  lndum = gsn_add_polyline( wks,plot,(/0,0/),(/res@trYMinF,res@trYMaxF/),lnres)

  draw(plot)
  frame(wks)

  delete(plot)
  delete(wks)
  delete(diff_range)
  delete(diff_max)
  delete(diff_min)
  delete(diff_med)
