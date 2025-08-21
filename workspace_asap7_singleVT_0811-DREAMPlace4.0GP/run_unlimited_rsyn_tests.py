import os
import subprocess
import datetime
import sys
from pathlib import Path

def get_git_short_hash(repo_path):
    """Gets the short git hash of the repository."""
    if not (Path(repo_path) / ".git").exists():
        return "nogit"
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            cwd=repo_path,
            universal_newlines=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "nogit"

def get_unique_output_dir(base_dir, git_hash):
    """Finds a unique directory name to store outputs."""
    counter = 0
    while True:
        dir_name = f"unlimited_rsyn_results/{git_hash}_{counter}"
        output_dir = base_dir / dir_name
        if not output_dir.exists():
            return output_dir
        counter += 1

def log(message):
    """Prints a log message with a timestamp."""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def main():
    """Main function to run the tests."""
    # --- Configuration ---
    script_dir = Path(__file__).resolve().parent
    # The project root is assumed to be one level up from the script directory
    project_root = script_dir.parent
    rsyn_executable = project_root / "build" / "bin" / "rsyn"
    rsyn_scripts_dir = script_dir / "rsyn_scripts"

    # --- Pre-run Checks ---
    log("Starting script...")

    if not rsyn_executable.is_file():
        log(f"Error: RSYN executable not found at '{rsyn_executable}'")
        log("Please ensure the project has been built.")
        sys.exit(1)
    log("Rsyn executable found.")

    if not rsyn_scripts_dir.is_dir():
        log(f"Error: Rsyn scripts directory not found at '{rsyn_scripts_dir}'")
        sys.exit(1)

    # --- Output Directory Setup ---
    git_hash = get_git_short_hash(project_root)
    output_dir = get_unique_output_dir(script_dir, git_hash)
    log(f"Creating output directory at '{output_dir}'...")
    output_dir.mkdir(parents=True, exist_ok=True)

    # --- Main Logic ---
    log(f"Searching for '*-unlimited.rsyn' files in '{rsyn_scripts_dir}'...")
    rsyn_scripts = sorted(list(rsyn_scripts_dir.glob("*-unlimited.rsyn")))

    if not rsyn_scripts:
        log("No '*-unlimited.rsyn' scripts found.")
        sys.exit(0)

    success_count = 0
    failure_count = 0
    failed_cases = []

    for rsyn_script in rsyn_scripts:
        case_name = rsyn_script.stem
        log(f"Processing '{rsyn_script.name}'...")

        case_output_dir = output_dir / case_name
        case_output_dir.mkdir(exist_ok=True)
        output_log = case_output_dir / "run.log"

        # This command is equivalent to [mode #2] in the original shell script.
        command = [
            "stdbuf", "-o0", "gdb", "--batch", "-ex", "run", "-ex", "bt", "--args",
            str(rsyn_executable), "--no-gui", "-script", str(rsyn_script)
        ]

        try:
            with open(output_log, 'w') as f:
                # Use check=False to handle non-zero exit codes manually
                result = subprocess.run(
                    command,
                    stdout=f,
                    stderr=subprocess.STDOUT
                )

            if result.returncode == 0:
                log(f"SUCCESS: '{rsyn_script.name}' processed. See log: '{output_log}'")
                success_count += 1
            else:
                log(f"ERROR: '{rsyn_script.name}' failed with exit code {result.returncode}. See log: '{output_log}'")
                failure_count += 1
                failed_cases.append(rsyn_script.name)

        except FileNotFoundError as e:
            # This handles cases where a command like 'stdbuf' or 'gdb' is not found
            log(f"ERROR: Command not found during execution for '{rsyn_script.name}'. See log: '{output_log}'")
            with open(output_log, 'a') as f:
                f.write(f"\n\nExecution failed: {e}\n")
            failure_count += 1
            failed_cases.append(rsyn_script.name)

        # Move generated output files to the case directory
        base_name = rsyn_script.name.replace('-unlimited.rsyn', '')
        generated_files_to_move = [
            f"{base_name}.def",
            f"{base_name}-cada085.ops"
        ]

        for filename in generated_files_to_move:
            source_path = script_dir / filename
            if source_path.is_file():
                dest_path = case_output_dir / filename
                log(f"Moving generated file '{source_path}' to '{dest_path}'")
                try:
                    source_path.rename(dest_path)
                except OSError as e:
                    log(f"ERROR: Failed to move file '{source_path}': {e}")


    # --- Summary ---
    log("----------------------------------------")
    log("All tasks completed.")
    log(f"Results are stored in '{output_dir}'.")
    log(f"Summary: {success_count} succeeded, {failure_count} failed.")

    if failure_count > 0:
        log("Failed cases:")
        for case in failed_cases:
            log(f"  - {case}")
    log("----------------------------------------")

if __name__ == "__main__":
    main()
