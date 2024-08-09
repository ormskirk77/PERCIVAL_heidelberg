import cocotb
from cocotb.binary import BinaryValue
from cocotb.triggers import Timer
from cocotb.binary import BinaryRepresentation
from cocotb.runner import get_runner

import random
from pathlib import Path
import softposit as sp


@cocotb.test()
async def posit_add_test(dut):
    succeeded_results = 0
    failed_results = 0
    # TODO use these to print out returned values where add fails:
    expexted = sp.posit32(0.0)
    dut_posit_result = sp.posit32(0.0)

    n_sums = 1000
    for i in range(0, n_sums, 1):
     
        test_val1 = random.uniform(0.0, 10.0)
        test_val2 = random.uniform(0.0, 10.0)

        op1 = sp.posit32(test_val1)
        op2 = sp.posit32(test_val2)

        dut.in1.value = op1.v.v
        dut.in2.value = op2.v.v

        await Timer(100, units='ns')

        result = op1 + op2
        expected = BinaryValue(value=int(result.v.v), n_bits=32, bigEndian=False, binaryRepresentation=BinaryRepresentation.UNSIGNED)

        # Print out all the sums and actual results to see if there is a pattern:
        if dut.out.value == expected:
            print(f"SUCCEEDED: {op1} + {op2} = {result}")
            succeeded_results += 1
        elif dut.out.value != expected:
            print(f"FAILED   : {op1} + {op2} = {result}")
            failed_results += 1
    print(f"{succeeded_results}/{n_sums} correct, {failed_results}/{n_sums} wrong ")

        # TODO Fix this below to print out the sum that has a failed. Need to convert dut.out.value to a decimal
        # if dut.out.value != expected:
        #     dut_result = BinaryValue(value=int(dut.out.value), n_bits=32, bigEndian=False, binaryRepresentation=BinaryRepresentation.UNSIGNED)
        #     print(f"FAILED at: {op1} + {op2}")
        #     print(f"Expected {result}, but got: {dut_posit_result.fromBits(dut_result.integer)}")
        #     print(f"EXP bits: {expected}")
        #     print(f"DUT bits: {dut.out.value}")
            
        # TODO Uncomment actual test statement
        # assert dut.out.value == expected





def test_posit_runner():
    proj_path = Path(__file__).resolve().parent.parent

    sources = [ proj_path / "test_posit" / "rtl" / "posit_add.v"]

    runner = get_runner("icarus")
    runner.build(
        sources=sources,
        hdl_toplevel="posit_add",
        always=True,
        build_args=[],
    )
    runner.test(
        hdl_toplevel="posit_add", test_module="test_posit_add", test_args=[]
    )


if __name__ == "__main__":
    test_posit_runner()

















