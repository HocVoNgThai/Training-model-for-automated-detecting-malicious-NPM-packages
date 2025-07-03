#!/bin/bash

# ==============================================================================
# Automated script to download and extract malicious npm packages from DataDog's repository.
# ==============================================================================


set -e

# --- Cấu hình ---
REPO_URL="https://github.com/DataDog/malicious-software-packages-dataset.git"
REPO_DIR="malicious-software-packages-dataset" 
NPM_SAMPLES_DIR="$REPO_DIR/samples/npm"       
TARGET_DIR="dataset/malicious"                

# --- Bắt đầu Script ---
echo "--- Start downloading and extracting malicious npm packets---"

# 1. Kiểm tra các công cụ cần thiết (git, unzip)
if ! command -v git &> /dev/null || ! command -v unzip &> /dev/null; then
    echo "Error: Need to download 'git' và 'unzip'."
    echo "On Ubuntu/Debian, run: sudo apt update && sudo apt install -y git unzip"
    exit 1
fi

if [ ! -d "$REPO_DIR" ]; then

    git clone "$REPO_URL" "$REPO_DIR"
    echo "Cloning successfully."
else
    echo "Repository does not exist"
fi

mkdir -p "$TARGET_DIR"


find "$NPM_SAMPLES_DIR" -type f -name '*.zip' | while read sample; do

    unzipDir="$TARGET_DIR/$(basename "$sample" .zip)"
    

    mkdir -p "$unzipDir"

    unzip -o -P infected "$sample" -d "$unzipDir" >/dev/null 2>&1
done

EXTRACTED_COUNT=$(find "$TARGET_DIR" -mindepth 1 -maxdepth 1 -type d | wc -l)

echo ""
echo "Finish!"
echo "Successfully extracting $EXTRACTED_COUNT npm packages into '$TARGET_DIR' folder."
