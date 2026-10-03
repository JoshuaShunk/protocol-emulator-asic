// 8N1 UART transmitter for testing the verification flow. Not part of the chip.
`default_nettype none

module uart_tx #(
    parameter integer CLKS_PER_BIT = 8
) (
    input  wire       clk,
    input  wire       rst_n,
    input  wire [7:0] data,
    input  wire       valid,
    output wire       ready,
    output reg        tx
);
  localparam integer CW = $clog2(CLKS_PER_BIT);

  reg [CW-1:0] clk_count;
  reg [3:0]    bit_index;   // 0 = start, 1..8 = data, 9 = stop
  reg [7:0]    shift;
  reg          busy;

  assign ready = !busy;

  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      tx        <= 1'b1;
      busy      <= 1'b0;
      clk_count <= 0;
      bit_index <= 0;
      shift     <= 8'h00;
    end else if (!busy) begin
      if (valid) begin
        busy      <= 1'b1;
        shift     <= data;
        tx        <= 1'b0;
        clk_count <= 0;
        bit_index <= 0;
      end
    end else if (clk_count != CLKS_PER_BIT - 1) begin
      clk_count <= clk_count + 1'b1;
    end else begin
      clk_count <= 0;
      if (bit_index == 4'd9) begin
        busy <= 1'b0;
      end else begin
        bit_index <= bit_index + 1'b1;
        if (bit_index == 4'd8) begin
          tx <= 1'b1;
        end else begin
          tx    <= shift[0];
          shift <= {1'b0, shift[7:1]};
        end
      end
    end
  end
endmodule
