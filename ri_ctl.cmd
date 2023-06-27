set ri_report_empty_modules_in_BLACK_BOX true
read_design_db pd_dptx adclk -project ./meridian_project
read_env ri_env.cmd
analyze_intent -disable_auto_intent_generation
verify_rdc
report_policy ALL -verbose -compat -output ClockDomain.rpt
