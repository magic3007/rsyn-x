# Synopsys Design Constraints Format
# Copyright © 2011, Synopsys, Inc. and others. All Rights reserved.

# clock definition
create_clock -name clk -period 100.0 [get_ports clk]

#input delays
set_input_delay 0.0 [get_ports {a}] -clock clk
set_input_delay 0.0 [get_ports {b}] -clock clk
set_input_delay 0.0 [get_ports {c}] -clock clk

#input drivers
set_driving_cell -lib_cell INV_X1 -pin o [get_ports {a}] -input_transition_fall 10.0 -input_transition_rise 10.0
set_driving_cell -lib_cell INV_X1 -pin o [get_ports {b}] -input_transition_fall 10.0 -input_transition_rise 10.0
set_driving_cell -lib_cell INV_X1 -pin o [get_ports {c}] -input_transition_fall 10.0 -input_transition_rise 10.0
set_driving_cell -lib_cell INV_X1 -pin o [get_ports {clk}] -input_transition_fall 10.0 -input_transition_rise 10.0

#output delays
set_output_delay 0.0 [get_ports {out}] -clock clk 

#output loads 
set_load -pin_load 10.0 [get_ports {out}]