// Black-box frame timing checker for uart_tx (CLKS_PER_BIT = 8).
// Observes only the ports. A frame starts on the clock edge where valid and
// ready are both high; k counts edges since then. Bit slot s = k / 8 covers
// k = 8s .. 8s+7: slot 0 is the start bit, slots 1..8 are data LSB first,
// slot 9 is the stop bit. ready is low for k = 0..79 and high from k = 80.
module uart_tx_props (
    input wire       clk,
    input wire [7:0] data,
    input wire       valid
);
  localparam integer CPB = 8;
  localparam integer FRAME = 10 * CPB;

  reg init = 1'b1;
  always @(posedge clk) init <= 1'b0;
  wire rst_n = !init;

  wire ready, tx;
  uart_tx #(.CLKS_PER_BIT(CPB)) dut (
      .clk(clk), .rst_n(rst_n), .data(data), .valid(valid), .ready(ready), .tx(tx)
  );

  reg       active = 1'b0;
  reg [6:0] k = 7'd0;
  reg [7:0] d = 8'd0;

  always @(posedge clk) begin
    if (!rst_n) begin
      active <= 1'b0;
    end else if (valid && ready) begin
      active <= 1'b1;
      k      <= 7'd0;
      d      <= data;
    end else if (active && k != FRAME) begin
      k <= k + 7'd1;
    end else begin
      active <= 1'b0;
    end
  end

  wire [3:0] slot = k / CPB;
  reg expected_tx;
  always @* begin
    case (slot)
      4'd0:    expected_tx = 1'b0;
      4'd1:    expected_tx = d[0];
      4'd2:    expected_tx = d[1];
      4'd3:    expected_tx = d[2];
      4'd4:    expected_tx = d[3];
      4'd5:    expected_tx = d[4];
      4'd6:    expected_tx = d[5];
      4'd7:    expected_tx = d[6];
      4'd8:    expected_tx = d[7];
      default: expected_tx = 1'b1;
    endcase
  end

  always @* begin
    if (!init) begin
      if (active && k < FRAME) begin
        assert (!ready);
        assert (tx == expected_tx);
      end else begin
        assert (ready);
        assert (tx);
      end
    end
  end

  // The checker must actually see back-to-back frames.
  always @* if (!init) cover (active && k == FRAME && valid);
endmodule
