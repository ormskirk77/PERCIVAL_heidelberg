###############################################################################
# Created by write_sdc
# Fri Aug  9 10:11:38 2024
###############################################################################
current_design cvxif_pau
###############################################################################
# Timing Constraints
###############################################################################
create_clock -name core_clock -period 10.0000 [get_ports {clk}]
set_propagated_clock [get_clocks {core_clock}]
###############################################################################
# Environment
###############################################################################
###############################################################################
# Design Rules
###############################################################################
