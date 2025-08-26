
import re
import sys
import os

def remove_power_info(file_path):
    temp_file_path = file_path + '.tmp'
    
    # Keywords that identify blocks to be removed
    block_starters = [
        "power_lut_template",
        "leakage_power",
        "internal_power",
        "rise_power",
        "fall_power",
        "passive_power"
    ]

    # Keywords that identify single lines to be removed
    line_keywords = [
        "leakage_power_unit",
        "default_cell_leakage_power",
        "power_down_function",
        "related_power_pin",
    ]

    in_block = False
    brace_count = 0

    with open(file_path, 'r') as f_in, open(temp_file_path, 'w') as f_out:
        for line in f_in:
            stripped_line = line.strip()

            if in_block:
                brace_count += line.count('{')
                brace_count -= line.count('}')
                if brace_count == 0:
                    in_block = False
                continue

            # Check for block starters
            if any(starter in stripped_line for starter in block_starters):
                if '{' in stripped_line:
                    brace_count = line.count('{') - line.count('}')
                    if brace_count > 0:
                        in_block = True
                continue

            # Check for single line keywords
            if any(keyword in stripped_line for keyword in line_keywords):
                continue
            
            # If none of the above, write the line to the output file
            f_out.write(line)

    # Replace the original file with the temporary file
    os.remove(file_path)
    os.rename(temp_file_path, file_path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python remove_power_info.py <path_to_lib_file>")
        sys.exit(1)
    
    lib_file_path = sys.argv[1]
    
    if not os.path.isfile(lib_file_path):
        print(f"Error: File not found at {lib_file_path}")
        sys.exit(1)

    print(f"Processing {lib_file_path}...")
    remove_power_info(lib_file_path)
    print("Done.")
