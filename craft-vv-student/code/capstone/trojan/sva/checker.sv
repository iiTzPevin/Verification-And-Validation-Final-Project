// Checker for secure_gate.
// Uses only the ports so it works on clean and trojan.

module secure_gate_sva #(
    parameter int DW = 8,
    parameter logic [31:0] EXPECTED_KEY = 32'hA5A5_1234
) (
    input logic clk,
    input logic rst_n,
    input logic [31:0] key,
    input logic [DW-1:0] data_in,
    input logic unlocked,
    input logic [DW-1:0] data_out,
    input logic [7:0] access_count
);

    // No other key can open the gate, so there is no secret entrance.
    no_backdoor: assert property (@(posedge clk) disable iff (!rst_n) unlocked |-> key == EXPECTED_KEY);
    no_backdoor_cover: cover property (@(posedge clk) disable iff (!rst_n) unlocked);

    // The right key always opens the gate.
    unlock: assert property (@(posedge clk) disable iff (!rst_n) key == EXPECTED_KEY |-> unlocked);
    unlock_cover: cover property (@(posedge clk) disable iff (!rst_n) key == EXPECTED_KEY);

    // A wrong key keeps data_out at 0.
    no_leak: assert property (@(posedge clk) disable iff (!rst_n) key != EXPECTED_KEY |-> data_out == 0);
    no_leak_cover: cover property (@(posedge clk) disable iff (!rst_n) key != EXPECTED_KEY && data_in != 0);

    // When unlocked data_out matches data_in.
    pass_data: assert property (@(posedge clk) disable iff (!rst_n) unlocked |-> data_out == data_in);
    pass_data_cover: cover property (@(posedge clk) disable iff (!rst_n) unlocked && data_in != 0);

    // The count goes up by 1 when unlocked.
    count_up: assert property (@(posedge clk) disable iff (!rst_n) unlocked |=> access_count == $past(access_count) + 8'd1);
    count_up_cover: cover property (@(posedge clk) disable iff (!rst_n) unlocked);

    // The count stays the same when locked.
    count_hold: assert property (@(posedge clk) disable iff (!rst_n) !unlocked |=> $stable(access_count));
    count_hold_cover: cover property (@(posedge clk) disable iff (!rst_n) !unlocked);

    // Reset sets the count to 0.
    reset_count: assert property (@(posedge clk) !rst_n |=> access_count == 0);
    reset_count_cover: cover property (@(posedge clk) !rst_n);

endmodule