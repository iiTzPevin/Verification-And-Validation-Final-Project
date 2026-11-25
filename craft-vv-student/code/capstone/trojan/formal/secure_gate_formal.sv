// Wrapper for secure_gate.

module secure_gate_formal #(
    parameter int DW = 8,
    parameter logic [31:0] EXPECTED_KEY = 32'hA5A5_1234
) (
    input logic clk,
    input logic rst_n,
    input logic [31:0] key,
    input logic [DW-1:0] data_in
);

    logic unlocked;
    logic [DW-1:0] data_out;
    logic [7:0] access_count;

    secure_gate #(.DW(DW)) u_gate (
        .clk(clk),
        .rst_n(rst_n),
        .key(key),
        .data_in(data_in),
        .unlocked(unlocked),
        .data_out(data_out),
        .access_count(access_count)
    );

`ifdef FORMAL
    // Saves the values from last cycle.
    reg started = 1'b0;
    reg last_rst_n;
    reg last_unlocked;
    reg [7:0] last_count;

    always @(posedge clk) begin
        started <= 1'b1;
        last_rst_n <= rst_n;
        last_unlocked <= unlocked;
        last_count <= access_count;
    end

    always @(posedge clk) begin
        // No other key can open the gate.
        if (unlocked) assert (key == EXPECTED_KEY);

        // A wrong key keeps data_out at 0.
        if (key != EXPECTED_KEY) assert (data_out == 0);

        // The count goes up by 1 when unlocked.
        if (started && last_rst_n && last_unlocked) assert (access_count == last_count + 8'd1);

        // The count stays the same when locked.
        if (started && last_rst_n && !last_unlocked) assert (access_count == last_count);

        // Reset sets the count to 0.
        if (started && !last_rst_n) assert (access_count == 0);
    end
`endif

endmodule