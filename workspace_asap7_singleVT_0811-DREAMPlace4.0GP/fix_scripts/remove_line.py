import os
import sys

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <file_path>")
    sys.exit(1)

file_path = sys.argv[1]
temp_file_path = file_path + '.tmp'

with open(file_path, 'r') as f_in, open(temp_file_path, 'w') as f_out:
    for line in f_in:
        if 'driver_waveform_fall' not in line and 'driver_waveform_rise' not in line:
            f_out.write(line)

os.remove(file_path)
os.rename(temp_file_path, file_path)