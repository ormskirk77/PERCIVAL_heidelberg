// Simple example of a coprocessor module that can be used with the CVXIF
// interface. This module is a simple complex number coprocessor that can add
// two complex numbers or compute the complex conjugate of a complex number.

// The CVXIF is simplefied for the purpose of this tutorial

// The two instructions are encoded as R-type as follows:
// custom-3 opcode space [6:0]: 1111011
// func3 [14:12]:
//   000 - add complex numbers
//   001 - complex conjugate
// func7 [31:25]: must be 0000000

// The register source and destination registers are the standard
// positions and don't need to be considered here.
`timescale 1ns/1ns

module cvxif_pau (
    input         clk,
    input         rst,
    input         issue_valid,
    output reg    issue_ready,
    input [31:0]  issue_req_instr,
    output reg    issue_resp_accept,
    output        issue_resp_writeback,
    output reg [1:0]  issue_resp_register_read,
    input         register_valid,
    output        register_ready,
    input [31:0]  register_rs0,
    input [31:0]  register_rs1,
    input [1:0]   register_rs_valid,
    output reg    result_valid,
    input         result_ready,
    output [31:0] result_data
);

  //  `include "/home/tim/PycharmProjects/PERCIVAL_heidelberg/cvxif-test/openlane/designs/cvxif_pau/src/pau.inc"
  localparam COUNTER_LEN = 2;
  localparam PAU_WAIT_TIME = 3;
  localparam PAU_N = 16;
  localparam PAU_ES = 1;
    reg op, next_op;
    reg [PAU_N-1:0] a, b, next_a, next_b;
    wire [PAU_N-1:0] c;
    reg start;
    wire done;
    reg [COUNTER_LEN-1:0] pau_wait_counter, next_pau_wait_counter;

    posit_add #(.N(PAU_N), .es(PAU_ES)) u_posit_add (
        .in1(a),
        .in2(b),
        .start(start),
        .out(c),
        .inf(),
        .zero(),
        .done(done));

    posit_mult #(.N(PAU_N), .es(PAU_ES)) u_posit_mult (
        .in1(a),
        .in2(b),
        .start(start),
        .out(),
        .inf(),
        .zero(),
        .done(done));

    posit_div #(.N(PAU_N), .es(PAU_ES)) u_posit_div (
        .in1(a),
        .in2(b),
        .start(start),
        .out(),
        .inf(),
        .zero(),
        .done(done));

    //`include "/home/tim/PycharmProjects/PERCIVAL_heidelberg/cvxif-test/openlane/designs/cvxif_pau/src/instruction.inc"
    localparam ADD_OP = 7'b0000000;
    localparam SUB_OP = 7'b0000001;
    localparam MUL_OP = 7'b0000010;
    localparam DIV_OP = 7'b0000011;
    logic match_instruction;
    assign match_instruction = (issue_req_instr[6:0] == 7'b1111011) &&
                                (issue_req_instr[14:13] == 2'b00) &&
                                ((issue_req_instr[31:25] == ADD_OP) ||
                                (issue_req_instr[31:25] == SUB_OP) ||
                                (issue_req_instr[31:25] == MUL_OP) ||
                                (issue_req_instr[31:25] == DIV_OP));

    assign issue_resp_writeback = 1'b1;
    assign result_data = c;

    typedef enum logic [1:0] {
        STATE_IDLE,
        STATE_WAITREGS,
        STATE_WAITPAU,
        STATE_DONE
    } state_t;

    state_t current_state;
    state_t next_state;

    always_ff @(posedge clk) begin
        if (rst) begin
            current_state <= STATE_IDLE;
            pau_wait_counter <= 0;
        end else begin
            current_state <= next_state;
            op <= next_op;
            a <= next_a;
            b <= next_b;
            pau_wait_counter <= next_pau_wait_counter;
        end
    end

    always @(*) begin
        next_state = current_state;
        next_op = op;
        next_a = a;
        next_b = b;
        next_pau_wait_counter = pau_wait_counter;
        issue_ready = 1'b0;
        issue_resp_accept = 1'b0;
        result_valid = 1'b0;
        start = 1'b0;

        case (current_state)
            STATE_IDLE: begin
                issue_ready = 1'b1;
                if (issue_valid && match_instruction) begin
                    issue_resp_accept = 1'b1;
                    next_op = issue_req_instr[12];
                    issue_resp_register_read = next_op ? 2'b01 : 2'b11;
                    next_state = STATE_WAITREGS;
                end
            end

            STATE_WAITREGS: begin
                if (register_valid && (register_rs_valid == (op ? 2'b01 : 2'b11))) begin
                    next_a = register_rs0[PAU_N-1:0];
                    next_b = register_rs1[PAU_N-1:0];
                    next_pau_wait_counter  = {COUNTER_LEN{1'b0}};
                    next_state = STATE_WAITPAU;
                end
            end

            STATE_WAITPAU: begin
                start = 1'b1;
                if (pau_wait_counter < PAU_WAIT_TIME) begin
                    next_pau_wait_counter = pau_wait_counter + 1;
                end else if (done && pau_wait_counter == PAU_WAIT_TIME) begin
                    next_state = STATE_DONE;
                end
            end

            STATE_DONE: begin
                result_valid = 1'b1;
                if (result_ready) begin
                    next_state = STATE_IDLE;
                end
            end
        endcase
    end

endmodule : cvxif_pau