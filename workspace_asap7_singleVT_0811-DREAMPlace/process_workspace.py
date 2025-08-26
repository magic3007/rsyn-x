import os
import shutil
import argparse
import subprocess
import glob

def process_case(workspace_dir, case_name):
    """
    Processes a single case in the workspace.
    """
    print(f"Processing case: {case_name}...")

    bookshelf_dir = os.path.join(workspace_dir, case_name, 'pnr', 'build', case_name, 'bookshelf')

    if not os.path.isdir(bookshelf_dir):
        print(f"  [Warning] Bookshelf directory not found for case {case_name}, skipping: {bookshelf_dir}")
        return

    # 1. Copy .lib files
    print("  1. Copying .lib files...")
    try:
        for lib_file in ['asap7_Early.lib', 'asap7_Late.lib']:
            src_lib = os.path.join(workspace_dir, lib_file)
            if os.path.exists(src_lib):
                shutil.copy(src_lib, bookshelf_dir)
            else:
                print(f"  [Warning] Library file not found: {src_lib}")

    except Exception as e:
        print(f"  [Error] Could not copy .lib files: {e}")
        return

    # 2. Create .iccad2015 file
    print("  2. Creating .iccad2015 file...")
    iccad_file_path = os.path.join(bookshelf_dir, f"{case_name}.iccad2015")
    iccad_content = f"{case_name}.v {case_name}.sdc {case_name}.lef {case_name}.def asap7_Early.lib asap7_Late.lib"
    with open(iccad_file_path, 'w') as f:
        f.write(iccad_content)

    # 3. Create rsyn script
    print("  3. Creating rsyn script...")
    rsyn_scripts_dir = os.path.join(workspace_dir, 'rsyn_scripts')
    os.makedirs(rsyn_scripts_dir, exist_ok=True)
    rsyn_script_path = os.path.join(rsyn_scripts_dir, f"{case_name}.rsyn")
    
    relative_iccad_path = os.path.join(case_name, 'pnr', 'build', case_name, 'bookshelf', f"{case_name}.iccad2015")

    rsyn_content = f"""open "iccad2015" {{
	"config" : "{relative_iccad_path}",
	"maxDisplacement" : 100000000,
	"targetUtilization" : 0.6,
	"parms" : "ICCAD15.parm"
}};

run "ufrgs.ISPD16Flow" {{}}
"""
    with open(rsyn_script_path, 'w') as f:
        f.write(rsyn_content)

    # 4. Fix .def file
    print("  4. Fixing .def file...")
    def_file = os.path.join(bookshelf_dir, f"{case_name}.def")
    fix_script = os.path.join(workspace_dir, 'fix_scripts', 'unescape_def_brackets.py')
    if os.path.exists(def_file):
        subprocess.run(['python3', fix_script, def_file], check=False)
    else:
        print(f"  [Warning] .def file not found: {def_file}")

    # 5. Fix .sdc file
    print("  5. Fixing .sdc file...")
    sdc_file = os.path.join(bookshelf_dir, f"{case_name}.sdc")
    fix_script = os.path.join(workspace_dir, 'fix_scripts', 'process_sdc.py')
    if os.path.exists(sdc_file):
        subprocess.run(['python3', fix_script, sdc_file], check=False)
    else:
        print(f"  [Warning] .sdc file not found: {sdc_file}")

    # 6. Process CTE_loops.rpt if it exists
    print("  6. Checking for CTE_loops.rpt...")
    search_pattern = os.path.join(bookshelf_dir, '*', 'insta_inputs', 'CTE_loops.rpt')
    rpt_files = glob.glob(search_pattern)
    
    if rpt_files:
        rpt_file_path = rpt_files[0]
        print(f"  Found CTE_loops.rpt at: {rpt_file_path}")
        
        try:
            shutil.copy(rpt_file_path, bookshelf_dir)
            print(f"  Copied CTE_loops.rpt to {bookshelf_dir}")

            parse_script = os.path.join(workspace_dir, 'fix_scripts', 'parse_rpt.py')
            copied_rpt_path = os.path.join(bookshelf_dir, 'CTE_loops.rpt')
            
            print(f"  Running parse_rpt.py on {copied_rpt_path}")
            subprocess.run(['python3', parse_script, copied_rpt_path], check=False)
        except Exception as e:
            print(f"  [Error] Failed to process CTE_loops.rpt: {e}")
    else:
        print("  CTE_loops.rpt not found.")
    
    print(f"Finished processing case: {case_name}\n")


def main():
    parser = argparse.ArgumentParser(description="Process all cases in a rsyn workspace.")
    parser.add_argument("workspace_dir", help="Path to the workspace directory.")
    args = parser.parse_args()

    workspace_dir = os.path.abspath(args.workspace_dir)

    if not os.path.isdir(workspace_dir):
        print(f"Error: Workspace directory not found at {workspace_dir}")
        return

    print(f"Starting processing for workspace: {workspace_dir}")

    ignore_dirs = ['rsyn_scripts', 'fix_scripts']
    all_items = sorted(os.listdir(workspace_dir)) # Sort for deterministic order

    for item in all_items:
        item_path = os.path.join(workspace_dir, item)
        if os.path.isdir(item_path) and item not in ignore_dirs:
            process_case(workspace_dir, item)

if __name__ == "__main__":
    main()
