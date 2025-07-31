module case1 (
a,
b,
c,
clk,
out
);

    // Start PIs
    input a;
    input b;
    input c;
    input clk;

    // Start Pos
    output out;

    // Start wires
    wire buf_inter;    // buffer中间信号
    wire buf_out;      // buffer输出
    wire nand_out;     // NAND门输出
    wire dff_out;      // D触发器输出

    // Buffer: 使用两个反相器串联
    INV_X1 buf_inv1 (
        .a(a),
        .o(buf_inter)
    );

    INV_X1 buf_inv2 (
        .a(buf_inter),
        .o(buf_out)
    );

    // NAND2门
    NAND2_X1 nand_gate (
        .a(buf_out),
        .b(b),
        .o(nand_out)
    );

    // D触发器
    DFF_X80 dff_inst (
        .d(nand_out),
        .ck(clk),
        .q(dff_out)
    );

    // NOR2门
    NOR2_X1 nor_gate (
        .a(dff_out),
        .b(c),
        .o(out)
    );

endmodule
