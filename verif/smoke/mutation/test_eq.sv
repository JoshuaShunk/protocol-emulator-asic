// Original (mutsel=0) vs mutant (mutsel=1). The clock is derived from the
// global formal clock so clock-polarity mutations are modelled.
module miter (
    input wire [7:0] data,
    input wire       valid
);
  (* gclk *) wire gclk;

  reg clk = 1'b0;
  always @(posedge gclk) clk <= !clk;

  reg init = 1'b1;
  always @(posedge clk) init <= 1'b0;
  wire rst_n = !init;

  wire ref_tx, uut_tx, ref_ready, uut_ready;

  uart_tx ref (
      .mutsel(8'd0), .clk(clk), .rst_n(rst_n),
      .data(data), .valid(valid), .ready(ref_ready), .tx(ref_tx)
  );

  uart_tx uut (
      .mutsel(8'd1), .clk(clk), .rst_n(rst_n),
      .data(data), .valid(valid), .ready(uut_ready), .tx(uut_tx)
  );

  always @* if (!init) assert (ref_tx == uut_tx && ref_ready == uut_ready);
endmodule
