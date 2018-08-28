 out_time_sec_List = ispan(out_time_sec_start+out_time_sec_int,out_time_sec_end,out_time_sec_int)

 xyres = True
 xyres@gsnDraw  = False
 xyres@gsnFrame = False
;xyres@vpWidthF   = 0.6    ; Make long and
;xyres@vpHeightF  = 0.36     ; narrow

 FontHeight = 0.022
 xyres@gsnStringFontHeightF = FontHeight
 xyres@tmXBLabelFontHeightF = FontHeight*0.8
 xyres@tmYLLabelFontHeightF = FontHeight*0.8
 xyres@tmYRLabelFontHeightF = FontHeight*0.8
 xyres@tiMainFontHeightF    = FontHeight
 xyres@tiXAxisFontHeightF   = FontHeight
 xyres@tiYAxisFontHeightF   = FontHeight

 xyres@xyMarkLineMode      =  "Marklines"
 xyres@xyMarker            = 16 
 xyres@xyMarkerColor       = markcolor 
 xyres@xyLineColor         = linecolor 
 xyres@xyMarkerThicknessF  = 1.
 xyres@xyMarkerSizeF       = FontHeight*0.4 

 xyres@xyDashPattern       = 0
 xyres@xyLineThicknessF    = 1

 xyres@tmXTOn = False
 xyres@tmYROn = False

  xyres@tiXAxisString = "Integration time (minutes)"
  xyres@tmXBLabelFontHeightF = FontHeight*0.9
  xyres@gsnStringFontHeightF = FontHeight
  xyres@tmXBLabelFontHeightF = FontHeight
  xyres@tmYLLabelFontHeightF = FontHeight
  xyres@tmYRLabelFontHeightF = FontHeight
  xyres@tiMainFontHeightF    = FontHeight*1.1
  xyres@tiXAxisFontHeightF   = FontHeight
  xyres@tiYAxisFontHeightF   = FontHeight


 xyres@trYLog = False
 xyres@trYMinF = -1.
 xyres@trYMaxF =  21.

 xyres@trXMinF = 0.
 xyres@trXMaxF = max(out_time_sec_List/60) + 1 


 xyplot = new(2,"graphic")

 xyres@tiMainString = "Number of failing variables"
 xyplot(0) = gsn_csm_xy(wks,out_time_sec_List/60.,nfail,xyres)

;---------
 passfail_res = True

 gg = 0.6
 passfail_res@gsLineColor = NhlNewColor(wks,gg,gg,gg) 
 passfail_res@gsLineThicknessF = 2.5
 passfail_res@gsLineDashPattern = 5.

 xyres@trYLog = True
 xyres@trYMinF = 1e-16
 xyres@trYMaxF = 1e2 
 xyres@tiMainString = "~F9~P~F~~B~min,t~N~ (%)"
 xyplot(1) = gsn_csm_xy(wks,out_time_sec_List/60.,minprob*100,xyres)

 passfail_dum1 = gsn_add_polyline(wks,xyplot(1),(/passfail_start_minute,passfail_end_minute/), \
                                                (/prob0,prob0/)*100,passfail_res)


 tx_res = True
 tx_res@txFontHeightF = FontHeight

 tx_res@txFontColor = markcolor_pass
 txdum1 = gsn_add_text(wks,xyplot(1),"Pass",0.5*(passfail_start_minute+passfail_end_minute), \
                                            prob0*100*4,tx_res)
 tx_res@txFontColor = markcolor_fail
 txdum1 = gsn_add_text(wks,xyplot(1),"Fail",0.5*(passfail_start_minute+passfail_end_minute), \
                                            prob0*100/4,tx_res)
 

     resp = True
    ;resp@gsnMaximize = True ;False
     resp@gsnPanelYWhiteSpacePercent = 5 
     resp@gsnPanelXWhiteSpacePercent = 4

 gsn_panel(wks,xyplot((/0,1/)),(/1,2/),resp)
