##Lint
	  Ascent Compiler
	AscentCom 5.0 for RHEL7.0-64, Rev 131077, Built On 06/05/2022 At 21:01:17
	Real Intent Inc. All Rights Reserved (1998-2022)

#AIG - new tool?
//================================================================================
//	Meridian Auto Intent Generation and Verification System
//	MeridianAIG 2022.A.RC5X3 for RHEL7.0-64, Rev 134629, Built On 10/05/2022 At 14:36:34
//	Real Intent Inc. All Rights Reserved (1998-2022)

#Auto Formal? == ascentiiv
Command is: /home/release/ASCENTAFV/2018A/release/RealIntent/bin/ascentiiv -wait_license -fae -i /home/jay/trunk/regress/TestSuite/jira/AUTO-1609/src/runScript.envprop -l Verix.log
Platform is CentOS release 6.10 (Final)
	  Ascent(TM) IIV AutoFormal
	AscentIIV 2018.A.P3 for RHEL 6.0-64, Rev 105536, Built On 10/03/2019
	Real Intent Inc. All Rights Reserved (1998-2020)

#CDC
	  Meridian MultiMode CDC Verification System
	MeridianCDC 2022.A.P1 for RHEL7.0-64, Rev 152257, Built On 05/04/2023 At 09:20:58
	Real Intent Inc. All Rights Reserved (1998-2023)

#CDC with MD_ENGINE
Command is: /home/brady/do_not_backup/clean-trunk/release/RealIntent/bin/mcdc -wait_license -fae -i /home/brady/do_not_backup/regress-trunk-2023-05-04-test/regress_Thu_May_4_22_09_41_2023/runScript_jira_CDC-12191 -log /dev/null
MD_ENGINE is: /home/brady/do_not_backup/clean-trunk/bin/RHEL7.0-64/mdengine
Platform is CentOS Linux release 7.9.2009 (Core)

#RDC
Command is: /home/release/RDC/RDC_2022A/release/RealIntent_P3.4/bin/mrdc -wait_license -fae -i /home/release/do_not_backup/RDC/build_7.0_SKYE2022AP3/tests-ScKnfkj571/regress_Mon_Nov_6_15_58_56_2023/runScript_cust_large_dbs_RDC-3796_nvidia_hier_sep -auto_parallel -number_of_rdc_partitions 4 -number_of_partitions 4 -log /dev/null
Platform is CentOS Linux release 7.9.2009 (Core)
	  Meridian(TM) RDC Verification System
	MeridianRDC 2022.A.P3.4.RDC for RHEL7.0-64, Rev 167155, Built On 11/06/2023 At 15:20:38
	Real Intent Inc. All Rights Reserved (1998-2023)



#remove dummy log files from the list, example:
#######################################################
#
#   DUMMY LOGFILE USED TO IDENTIFY IMPORTED TESTCASE
#
#   REPLACE WITH REAL GOLD FILE FROM VERIFIED RESULTS
#
#######################################################

#idebug
Command is: /home/rgr/trunk/release/RealIntent/bin/idebug -wait_license -fae -project meridian_project -design eth_top -i /home/pshreyas/QA/idebug/idebug_tests/CDC/lab1Tests/CLI/set_rule_status/create_view_criteria/src/runScript.debug -cli -noversioncheck -traceivision
Platform is CentOS release 6.8 (Final)
	  Intent Debugger (iDebug) System
	iDebug 2017.A.P4 for RHEL 6.0-64, Rev 86261, Built On 08/31/2017
	Real Intent Inc. All Rights Reserved (1998-2017)

