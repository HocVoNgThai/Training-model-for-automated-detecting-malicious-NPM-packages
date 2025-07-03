#!/bin/bash

# ===================================================================================
# Script to DYNAMICALLY download and extract a large set of benign npm packages.
# ===================================================================================


TARGET_COUNT=3000 


OUTPUT_DIR="dataset/benign"     
PARALLEL_JOBS=10                
PACKAGES_PER_KEYWORD=250        


set -e 

echo "--- Dynamic Benign NPM Package Downloader (Target: $TARGET_COUNT packages) ---"

# --- 1. Dependency Checks ---
echo "[1/6] Checking for required tools (curl, jq, npm, parallel)..."
for cmd in curl jq npm parallel; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "Error: Command '$cmd' is not installed. It is required to run this script."
        echo "Please install it using your system's package manager."
        echo "On Debian/Ubuntu: sudo apt update && sudo apt install -y $cmd"
        echo "On macOS (Homebrew): brew install $cmd"
        exit 1
    fi
done
echo "All required tools are installed."

# --- 2. Create directories and prepare files ---
mkdir -p "$OUTPUT_DIR"
# Use a subshell to avoid changing the main script's directory
(
cd "$OUTPUT_DIR" || { echo "Error: Could not enter directory $OUTPUT_DIR"; exit 1; }

LOG_FILE="download_log.txt"
ALL_PACKAGES_TMP="all_packages.tmp"
UNIQUE_PACKAGES_LIST="unique_package_list.txt"

# Clean up previous runs
rm -f "$LOG_FILE" "$ALL_PACKAGES_TMP" "$UNIQUE_PACKAGES_LIST"

echo "--- Download Log ---" > "$LOG_FILE"
echo "Process started at $(date)" | tee -a "$LOG_FILE"

# --- 3. Fetch Package Names from npm Registry API ---
echo "[2/6] Fetching popular package names from npm registry..."

# A diverse set of keywords to find popular and varied packages
KEYWORDS=(
    "react" "vue" "angular" "webpack" "express" "database" "test" "util" "cli"
    "aws" "server" "typescript" "babel" "security" "authentication" "logging"
    "graphql" "api" "framework" "tool" "data" "date" "parser" "lint" "http"
    "aws-sdk" "azure" "google-cloud" "docker" "kubernetes" "pm2" "jest" "mocha"
)

# Fetch package names for each keyword
for keyword in "${KEYWORDS[@]}"; do
    echo "  -> Searching for packages with keyword: '$keyword'"
    # The npm API search endpoint. We use jq to parse the JSON and extract package names.
    # The '.objects[].package.name' query extracts the 'name' field from each package object.
    curl -s "https://registry.npmjs.org/-/v1/search?text=keywords:${keyword}&size=${PACKAGES_PER_KEYWORD}" \
        | jq -r '.objects[].package.name' >> "$ALL_PACKAGES_TMP"
done

# --- 4. De-duplicate and Finalize Package List ---
echo "[3/6] Processing and de-duplicating the fetched package list..."
# Sort the list and remove duplicates, then take the top N packages
sort -u "$ALL_PACKAGES_TMP" | head -n "$TARGET_COUNT" > "$UNIQUE_PACKAGES_LIST"
rm "$ALL_PACKAGES_TMP" # Clean up temporary file

ACTUAL_COUNT=$(wc -l < "$UNIQUE_PACKAGES_LIST")
echo "Finalized list with $ACTUAL_COUNT unique packages (target was $TARGET_COUNT)."
if [ "$ACTUAL_COUNT" -eq 0 ]; then
    echo "Error: Failed to fetch any package names. Check network connection or API status."
    exit 1
fi

# --- 5. Download and Extract Packages ---
# This function is exported to be used by GNU Parallel.
download_package() {
    local pkg_name="$1"
    echo "-> Processing '$pkg_name'"

    # 'npm pack' downloads the tarball and PRINTS THE FILENAME to stdout.
    # We capture this filename to handle it robustly.
    # We use '@latest' to ensure we get the latest benign version.
    TGZ_FILE=$(npm pack "$pkg_name@latest" 2>>"$LOG_FILE")

    if [ -n "$TGZ_FILE" ] && [ -f "$TGZ_FILE" ]; then
        # Create a directory name from the package name, replacing slashes for scoped packages
        local pkg_dir_name
        pkg_dir_name=$(echo "$pkg_name" | sed 's/\//-/g')
        mkdir -p "$pkg_dir_name"

        # Extract tarball and strip the leading 'package/' directory
        if tar -xzf "$TGZ_FILE" -C "$pkg_dir_name" --strip-components=1; then
            echo "OK: Successfully extracted $pkg_name" >> "$LOG_FILE"
        else
            echo "FAIL: Could not extract $TGZ_FILE" | tee -a "$LOG_FILE"
        fi
        # Clean up the downloaded tarball regardless of success
        rm "$TGZ_FILE"
    else
        echo "FAIL: 'npm pack' command failed for $pkg_name" | tee -a "$LOG_FILE"
    fi
}
export -f download_package
export LOG_FILE

echo "[4/6] Starting parallel download of $ACTUAL_COUNT packages ($PARALLEL_JOBS jobs)..."
echo "This will take a significant amount of time. Progress is logged in '$OUTPUT_DIR/$LOG_FILE'."

# --- 6. Main Execution ---
# Read the unique package list and pipe it to parallel for execution
cat "$UNIQUE_PACKAGES_LIST" | parallel -j"$PARALLEL_JOBS" --eta 'download_package {}'

echo "[5/6] All downloads attempted."

# --- Verification Summary ---
echo "[6/6] Verifying results and generating summary..."
successful_count=$(find . -mindepth 1 -maxdepth 1 -type d ! -name 'node_modules' | wc -l)

echo "----------------------------------------"
echo "           DOWNLOAD SUMMARY             "
echo "----------------------------------------"
echo "Requested packages: $TARGET_COUNT"
echo "Unique packages found: $ACTUAL_COUNT"
echo "Successfully extracted directories: $successful_count"
echo ""
if [ "$successful_count" -lt "$ACTUAL_COUNT" ]; then
    echo "Some packages may have failed to download or extract."
    echo "Please check the log file for details: '$OUTPUT_DIR/$LOG_FILE'"
fi
echo "Process completed at $(date)." | tee -a "$LOG_FILE"
echo "Benign packages are ready in the '$OUTPUT_DIR' directory."

) # End of subshell
