import re
import csv
import os
import argparse

def parse_timing_loops(rpt_file_path):
    """
    Parses a timing loop report file to extract timing arcs that need to be broken.

    Args:
        rpt_file_path (str): The path to the .rpt file.
    """
    
    arcs_to_break = []
    
    # Regex to find the lines with timing loop warnings and extract the pins
    pattern = re.compile(r"The arc from '([^']*)' to '([^']*)' has been cut", re.DOTALL)

    try:
        with open(rpt_file_path, 'r') as f:
            content = f.read()
            # Replace newlines that are followed by spaces used for indentation in the report
            content = re.sub(r'\n\s+', ' ', content)
            matches = pattern.finditer(content)
            for match in matches:
                from_pin = match.group(1).replace(' ', '')
                to_pin = match.group(2).replace(' ', '')
                arcs_to_break.append((from_pin, to_pin))
    except FileNotFoundError:
        print(f"Error: The file '{rpt_file_path}' was not found.")
        return

    if not arcs_to_break:
        print("No timing arcs to break were found in the report.")
        return

    # Determine the output file path
    directory = os.path.dirname(rpt_file_path)
    if not directory:
        directory = '.'
    
    file_name = os.path.splitext(os.path.basename(rpt_file_path))[0]
    output_csv_path = os.path.join(directory, f'{file_name}_arcs_to_break.csv')

    # Write the extracted data to a CSV file
    try:
        with open(output_csv_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            # Write header
            csv_writer.writerow(['From Pin', 'To Pin'])
            # Write data
            csv_writer.writerows(arcs_to_break)
        print(f"Successfully extracted {len(arcs_to_break)} timing arcs to break.")
        print(f"Output saved to '{output_csv_path}'")
    except IOError:
        print(f"Error: Could not write to the file '{output_csv_path}'.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Parse a timing loop report file and extract arcs to be broken.")
    parser.add_argument("rpt_file", help="Path to the .rpt file to parse.")
    args = parser.parse_args()
    
    parse_timing_loops(args.rpt_file)
