#!/bin/bash

# Best Practices:
# - Treat unset variables as an error when substituting.
# - Use '|| true' to prevent script exit on non-zero status, allowing error handling.
set -uo pipefail

# --- Configuration ---
# The script is now located in the 'iccad15' directory.
readonly SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# Project root is one level up.
readonly PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
readonly RSYN_EXECUTABLE="$PROJECT_ROOT/build/bin/rsyn"
# Search directory is the current directory where the script resides.
readonly SCRIPTS_DIR="$SCRIPT_DIR/rsyn_scripts"
readonly OUTPUT_DIR="$SCRIPT_DIR"

# --- State ---
declare -i success_count=0
declare -i failure_count=0
declare -a failed_cases=()

# --- Functions ---
log() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# --- Pre-run Checks ---
log "Starting script..."

if [[ ! -f "$RSYN_EXECUTABLE" ]]; then
    log "Error: RSYN executable not found at '$RSYN_EXECUTABLE'"
    log "Please ensure the project has been built."
    exit 1
fi

log "Rsyn executable found."

# --- Main Logic ---
log "Creating output directory at '$OUTPUT_DIR'..."
mkdir -p "$OUTPUT_DIR"

log "Searching for '*-unlimited.rsyn' files in '$SCRIPTS_DIR'..."
# Using find and process substitution for safer file handling
mapfile -d '' rsyn_scripts < <(find "$SCRIPTS_DIR" -maxdepth 1 -type f -name "*-unlimited.rsyn" -print0)
for rsyn_script in "${rsyn_scripts[@]}"; do
    filename=$(basename "$rsyn_script")
    output_log="$OUTPUT_DIR/${filename}.log"

    log "Processing '$filename'..."

    # Run the command and redirect stdout and stderr to the log file.
    # Always export output to output_log, regardless of success or failure.

    # [mode #1] run without gdb and redirect output to output_log
    # stdbuf -o0 "$RSYN_EXECUTABLE" --no-gui -script "$rsyn_script" > "$output_log" 2>&1

    # [mode #2] run with gdb and redirect output to output_log
    stdbuf -o0 gdb --batch -ex "run" -ex "bt" --args "$RSYN_EXECUTABLE" --no-gui -script "$rsyn_script" > "$output_log" 2>&1

    # [mode #3] run with gdb, and enter interactive mode when segmentation fault occurs
    # stdbuf -o0 gdb --args "$RSYN_EXECUTABLE" --no-gui -script "$rsyn_script"

    if [[ $? -eq 0 ]]; then
        log "SUCCESS: '$filename' processed. See log: '$output_log'"
        ((success_count++))
    else
        log "ERROR: '$filename' failed. See log: '$output_log'"
        ((failure_count++))
        failed_cases+=("$filename")
    fi

done

# --- Summary ---
log "----------------------------------------"
log "All tasks completed."
log "Results are stored in '$OUTPUT_DIR'."
log "Summary: $success_count succeeded, $failure_count failed."

if [[ $failure_count -gt 0 ]]; then
    log "Failed cases:"
    for case in "${failed_cases[@]}"; do
        log "  - $case"
    done
fi

log "----------------------------------------"