import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='_pytest.assertion.rewrite|cocotb.runner|get_runner')

import cocotb
from cocotb.binary import BinaryValue
from cocotb.triggers import Timer, RisingEdge, FallingEdge
from cocotb.clock import Clock
from cocotb.binary import BinaryRepresentation
from cocotb.runner import get_runner

from random import uniform, getrandbits, randint
from pathlib import Path
import softposit, random

# import pydevd_pycharm
# pydevd_pycharm.settrace('localhost', port=5678, stdoutToServer=True, stderrToServer=True)

def convert_to_binaryValue(value):


    return BinaryValue(int(softposit.posit32(value).v.v),n_bits=32,bigEndian=False,binaryRepresentation=BinaryRepresentation.UNSIGNED)

def form_instruction(op):
    instr = BinaryValue(n_bits=32,bigEndian=False)
    instr[31:25] = 0
    instr[24:20] = 12
    instr[19:15] = 14
    instr[14:12] = op
    instr[11:7] = 14
    instr[6:0] = 0b1111011
    return instr

def reset_values(dut):
    dut.rst.value = 1
    dut.issue_valid.value = 0
    dut.issue_req_instr.value = 0
    dut.register_valid.value = 0
    dut.register_rs.value = [0, 0]
    dut.register_rs_valid.value = 0
    dut.result_ready.value = 0


async def start_clock(dut):
    c = Clock(dut.clk, 10, "ns")
    await cocotb.start(c.start())


async def wait_reset_cycle(dut):
    for i in range(3):
        await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.rst.value = 0

def register_bitmask(num):
    return 0b01 | (0b10 if num > 1 else 0)

async def test_instruction(dut, instr, accepted, operands, result):
    # Test issue interface
    dut.issue_valid.value = 1
    dut.issue_req_instr.value = instr
    await RisingEdge(dut.clk) # clock edge ends cycle
    while dut.issue_ready.value == 0: # handshake?
        await RisingEdge(dut.clk) # no, maybe next cycle

    dut.issue_valid.value = 0 # only one instruction
    assert dut.issue_resp_accept.value == (1 if accepted else 0), f"Wrong acceptance for {instr}: {dut.issue_resp_accept.value}"
    if dut.issue_resp_accept.value == 0:
        return # not accepter, CPU aborts
    # Those are only valid with accepted
    assert dut.issue_resp_writeback.value == 1, f"Writeback not requested for {instr}"
    assert dut.issue_resp_register_read == register_bitmask(len(operands)), f"Wrong register read bitmask for {instr}: {dut.issue_resp_register_read}"

    await FallingEdge(dut.clk)

    # Test register interface
    dut.register_valid.value = 1
    dut.register_rs.value = [convert_to_binaryValue(operands[0]), convert_to_binaryValue(operands[1]) if len(operands) > 1 else 0]
    dut.register_rs_valid.value = register_bitmask(len(operands))
    await RisingEdge(dut.clk)
    while dut.register_ready.value == 0:
        await RisingEdge(dut.clk)
    dut.register_valid.value = 0

    await FallingEdge(dut.clk)

    # Test result interface
    # We add some backpresure here, we randomly accept the result or not
    # It must still work of course
    dut.result_ready.value = getrandbits(1)
    await RisingEdge(dut.clk)
    while dut.result_ready.value == 0 or dut.result_valid.value == 0:
        dut.result_ready.value = getrandbits(1)
        await RisingEdge(dut.clk)
    await Timer(100, units='ns')
    dut.result_ready.value = 0
    assert dut.result_data.value == convert_to_binaryValue(result), f"Wrong result for {instr}: {dut.result_data.value} should be {convert_to_binaryValue(result)}"

    await FallingEdge(dut.clk)

'''
localparam ADD_OP = 3'b00;
localparam SUB_OP = 3'b01;
localparam MUL_OP = 3'b10;
localparam DIV_OP = 3'b11;
'''
ADD_OP = 0
SUB_OP = 1
MUL_OP = 2
DIV_OP = 3

@cocotb.test()
async def mul_test(dut):
    reset_values(dut)
    await start_clock(dut)
    await wait_reset_cycle(dut)
    A = 3
    B = 3
    C = 9.0
    await test_instruction(dut, form_instruction(MUL_OP), True, [A, B], C)

@cocotb.test()
async def div_test(dut):
    reset_values(dut)
    await start_clock(dut)
    await wait_reset_cycle(dut)
    A = 4
    B = 2
    C = 2
    await test_instruction(dut, form_instruction(DIV_OP), True, [A, B], C)

@cocotb.test()
async def add_test(dut):
    reset_values(dut)
    await start_clock(dut)
    await wait_reset_cycle(dut)

    n_sums = 2
    for i in range(0, n_sums):

        test_val1 = random.uniform(0.0, 10.0)
        test_val2 = random.uniform(0.0, 10.0)

        await Timer(100, units='ns')

        await test_instruction(dut, form_instruction(ADD_OP), True, [test_val1, test_val2], (test_val1 + test_val2))




def test_cvxif_runner():
    proj_path = Path(__file__).resolve().parent.parent
    sources = list(proj_path.glob("postGermany/src/*.*"))

    hdl_tl = "pau"

    runner = get_runner("icarus")
    runner.build(
        sources=sources,
        hdl_toplevel=hdl_tl,
        always=True,
        build_args=[],
    )
    runner.test(
        hdl_toplevel=hdl_tl, test_module="pos_add_tb", test_args=[]
    )


if __name__ == "__main__":
    test_cvxif_runner()

