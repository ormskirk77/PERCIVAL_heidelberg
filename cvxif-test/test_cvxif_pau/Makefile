# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0

VERILOG_SOURCES = $(shell pwd)/../rtl/cvxif_pau.sv \
	$(shell pwd)/../rtl/pau/add/posit_add.v \
	$(shell pwd)/../rtl/pau/div/posit_div.v \
	$(shell pwd)/../rtl/pau/mult/posit_mult.v \
	$(shell pwd)/../rtl/pau/*.v
VERILOG_INCLUDE_DIRS = $(shell pwd)/../rtl/include

MODULE = test_cvxif
TOPLEVEL = cvxif_pau

WAVES = 1

include $(shell cocotb-config --makefiles)/Makefile.sim