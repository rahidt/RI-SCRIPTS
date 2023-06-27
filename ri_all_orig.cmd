**> set ri_report_empty_modules_in_BLACK_BOX true
**> analyze -sv adclk.v
**> analyze -sv pd_dptx.hdr
**> elaborate pd_dptx adclk
**> analyze_intent -disable_auto_intent_generation
**> verify_rdc
**> report_policy ALL -verbose -compat -output ClockDomain.rpt
**> exit 0
