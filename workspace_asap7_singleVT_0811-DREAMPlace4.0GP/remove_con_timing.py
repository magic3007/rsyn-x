import sys
import os

def remove_con_timing_blocks(file_path):
    temp_file_path = file_path + '.tmp'
    
    in_timing_block = False
    brace_count = 0
    timing_block_buffer = []
    is_con_block = False

    with open(file_path, 'r') as f_in, open(temp_file_path, 'w') as f_out:
        for line in f_in:
            stripped_line = line.strip()

            if not in_timing_block and stripped_line.startswith("timing ()"):
                in_timing_block = True
                brace_count = line.count('{') - line.count('}')
                timing_block_buffer.append(line)
                is_con_block = False
                if brace_count == 0: # a timing block in one line. unlikely but possible
                    in_timing_block = False
                    if 'related_pin : "CON"' not in "".join(timing_block_buffer):
                         f_out.writelines(timing_block_buffer)
                    timing_block_buffer = []
                continue

            if in_timing_block:
                timing_block_buffer.append(line)
                if 'related_pin : "CON"' in stripped_line:
                    is_con_block = True
                
                brace_count += line.count('{')
                brace_count -= line.count('}')

                if brace_count == 0:
                    in_timing_block = False
                    if not is_con_block:
                        f_out.writelines(timing_block_buffer)
                    timing_block_buffer = [] # Reset buffer
            else:
                f_out.write(line)

    os.remove(file_path)
    os.rename(temp_file_path, file_path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python remove_con_timing.py <path_to_lib_file>")
        sys.exit(1)
    
    lib_file_path = sys.argv[1]
    
    if not os.path.isfile(lib_file_path):
        print(f"Error: File not found at {lib_file_path}")
        sys.exit(1)

    print(f"Processing {lib_file_path}...")
    remove_con_timing_blocks(lib_file_path)
    print("Done.")
