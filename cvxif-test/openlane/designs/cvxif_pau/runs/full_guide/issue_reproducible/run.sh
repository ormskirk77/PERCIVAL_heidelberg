#!/bin/sh
dir=$(cd -P -- "$(dirname -- "$0")" && pwd -P)
cd $dir;
export LIB_SYNTH_COMPLETE_NO_PG='./tmp/synthesis/1-sky130_fd_sc_hd__tt_025C_1v80.no_pg.lib';
export LIB_SYNTH_NO_PG='./tmp/synthesis/1-trimmed.no_pg.lib';
export PACKAGED_SCRIPT_0='openlane/scripts/yosys/synth.tcl';
export SAVE_NETLIST='./results/synthesis/cvxif_pau.v';
export synth_report_prefix='./reports/synthesis/1-synthesis';
TOOL_BIN=${TOOL_BIN:-yosys}
$TOOL_BIN -c $PACKAGED_SCRIPT_0
