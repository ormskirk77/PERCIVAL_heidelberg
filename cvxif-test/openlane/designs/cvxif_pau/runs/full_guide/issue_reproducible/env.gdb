set env LIB_SYNTH_COMPLETE_NO_PG ./tmp/synthesis/1-sky130_fd_sc_hd__tt_025C_1v80.no_pg.lib
set env LIB_SYNTH_NO_PG ./tmp/synthesis/1-trimmed.no_pg.lib
set env PACKAGED_SCRIPT_0 openlane/scripts/yosys/synth.tcl
set env SAVE_NETLIST ./results/synthesis/cvxif_pau.v
set env synth_report_prefix ./reports/synthesis/1-synthesis