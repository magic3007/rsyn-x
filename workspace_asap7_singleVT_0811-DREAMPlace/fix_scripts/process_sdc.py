import re
import sys
import os
import shutil

def process_sdc_file(input_file):
    """
    Processes an SDC file to unify set_input_delay and set_output_delay commands.

    先将原来的sdc备份
    
    1）
    删除形如
    current_design aes
    所在的行

    2）
    create_clock [get_ports {clk}]  -name clk -period 160.000000 -waveform {0.000000 80.000000}
    改成形如
    create_clock -name clk -period 160.000000 [get_ports {clk}]

    3)
    It converts pairs of lines like:
    set_input_delay -add_delay 2 -min -clock [get_clocks {clk}] [get_ports {wb_addr_i[0]}]
    set_input_delay -add_delay 4 -max -clock [get_clocks {clk}] [get_ports {wb_addr_i[0]}]
    into a single line:
    set_input_delay 0.0 [get_ports {wb_addr_i[0]}] -clock clk

    4)
    And similarly for set_output_delay:
    set_output_delay -add_delay 2 -min -clock [get_clocks {clk}] [get_ports {wb_data_o[21]}]
    set_output_delay -add_delay 4 -max -clock [get_clocks {clk}] [get_ports {wb_data_o[21]}]
    into:
    set_output_delay 0.0 [get_ports {wb_data_o[21]}] -clock clk

    5)
    删除
    set_input_transition所在行

    """
    # Backup the original file
    backup_file = input_file + ".bak"
    if not os.path.exists(backup_file):
        shutil.copyfile(input_file, backup_file)
        print(f"Original file backed up to {backup_file}")
    else:
        print(f"Backup file {backup_file} already exists.")

    with open(input_file, 'r') as f:
        lines = f.readlines()

    header_lines = []
    body_lines = []
    in_header = True
    for line in lines:
        if in_header and (line.strip().startswith('#') or not line.strip()):
            header_lines.append(line)
        else:
            in_header = False
            body_lines.append(line)

    # Separate lists for different command types
    clock_lines = []
    input_delay_lines = []
    output_delay_lines = []
    other_lines = []

    ports_seen_input = set()
    ports_seen_output = set()

    for line in body_lines:
        stripped_line = line.strip()

        if not stripped_line or stripped_line.startswith('#END OF CLOCK SECTION#'):
            continue

        # 1) Delete lines containing 'current_design'
        if stripped_line.startswith('current_design'):
            continue
            
        # 5) Delete lines containing 'set_input_transition'
        if 'set_input_transition' in stripped_line:
            continue

        # Delete 'set_max_fanout' lines
        if stripped_line.startswith('set_max_fanout'):
            continue

        # 2) Reformat 'create_clock' lines
        create_clock_match = re.match(r'create_clock\s+\[get_ports\s+\{(.*?)\}\]\s+-name\s+(.*?)\s+-period\s+(.*?)\s+.*', stripped_line)
        if create_clock_match:
            port, name, period = create_clock_match.groups()
            new_line = f"create_clock -name {name} -period {period} [get_ports {{{port}}}]"
            clock_lines.append(new_line + '\n')
            continue
            
        # 3) Process 'set_input_delay' lines
        if stripped_line.startswith('set_input_delay'):
            input_delay_match = re.search(r'\[get_ports\s+(?:\{([^}]+)\}|(\S+))\]', stripped_line)
            if input_delay_match:
                port = (input_delay_match.group(1) or input_delay_match.group(2)).strip()
                if port not in ports_seen_input:
                    clock_match = re.search(r'-clock\s+(?:\[get_clocks\s+\{?(.*?)\}?\]|(\w+))', stripped_line)
                    clock_name = "clk"
                    if clock_match:
                        # group 1 is for [get_clocks {clk}], group 2 is for bare clock name
                        clock_name = clock_match.group(1) or clock_match.group(2)
                    
                    input_delay_lines.append(f"set_input_delay 0.0 [get_ports {{{port}}}] -clock {clock_name}\n")
                    ports_seen_input.add(port)
            continue

        # 4) Process 'set_output_delay' lines
        if stripped_line.startswith('set_output_delay'):
            output_delay_match = re.search(r'\[get_ports\s+(?:\{([^}]+)\}|(\S+))\]', stripped_line)
            if output_delay_match:
                port = (output_delay_match.group(1) or output_delay_match.group(2)).strip()
                if port not in ports_seen_output:
                    clock_match = re.search(r'-clock\s+(?:\[get_clocks\s+\{?(.*?)\}?\]|(\w+))', stripped_line)
                    clock_name = "clk"
                    if clock_match:
                        # group 1 is for [get_clocks {clk}], group 2 is for bare clock name
                        clock_name = clock_match.group(1) or clock_match.group(2)

                    output_delay_lines.append(f"set_output_delay 0.0 [get_ports {{{port}}}] -clock {clock_name}\n")
                    ports_seen_output.add(port)
            continue
            
        other_lines.append(line)

    # Assemble the final file content
    processed_lines = header_lines
    if clock_lines:
        processed_lines.append("# clock definition\n")
        processed_lines.extend(clock_lines)
    
    if input_delay_lines:
        processed_lines.append("#input delays\n")
        processed_lines.extend(input_delay_lines)
        processed_lines.append("#input drivers\n")

    if output_delay_lines:
        processed_lines.append("#output delays\n")
        processed_lines.extend(output_delay_lines)
        processed_lines.append("#output loads\n")
        
    processed_lines.extend(other_lines)
    
    with open(input_file, 'w') as f:
        f.writelines(processed_lines)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python process_sdc.py <input_sdc_file>")
        sys.exit(1)
    
    input_sdc_file = sys.argv[1]
    
    process_sdc_file(input_sdc_file)
    print(f"Processed SDC file saved to {input_sdc_file}")
