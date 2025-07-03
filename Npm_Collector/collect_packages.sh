#!/bin/bash


OUTPUT_ROOT="/home/kali/Documents/npm/dataset"
SLEEP_INTERVAL=3600
MAX_PACKAGES_PER_CHECK=2000


echo "--- Start collecting NPM packages ---"
echo "--- Click Ctrl+C to stop ---"


while true; do

    CURRENT_DATE=$(date +%Y-%m-%d)
    DAILY_DIR="$OUTPUT_ROOT/date-$CURRENT_DATE"
    DAILY_LOG_FILE="$OUTPUT_ROOT/date-$CURRENT_DATE.log"
    
    echo "------------------------------------------------------------"
    echo "Start collecting at: $(date)"
    echo "Working at folder: '$DAILY_DIR'"
    
    mkdir -p "$DAILY_DIR"
    touch "$DAILY_LOG_FILE"

    # Lấy danh sách gói mới từ API
    API_URL="https://registry.npmjs.org/-/v1/search?text=created:$CURRENT_DATE..$CURRENT_DATE&size=$MAX_PACKAGES_PER_CHECK"
    mapfile -t PACKAGES_WITH_VERSIONS < <(curl -s "$API_URL" | jq -r '.objects[].package | "\(.name)@\(.version)"')

    if [ ${#PACKAGES_WITH_VERSIONS[@]} -eq 0 ]; then
        echo "  Not found any packages this time."
    else
        echo "  Found ${#PACKAGES_WITH_VERSIONS[@]} packages. Start downloading..."
        

        (
            cd "$DAILY_DIR" || exit 1
            
            NEW_PACKAGES_FOUND=0
            for pkg_version_string in "${PACKAGES_WITH_VERSIONS[@]}"; do
                # Kiểm tra trạng thái từ file log trong thư mục gốc
                if grep -Fxq "$pkg_version_string" "../$(basename $DAILY_LOG_FILE)"; then
                    continue
                fi
                
                ((NEW_PACKAGES_FOUND++))
                echo "    -> Found new packages/version: $pkg_version_string."
                
                if TGZ_FILE=$(npm pack "$pkg_version_string" 2>/dev/null); then
                    if [ -n "$TGZ_FILE" ] && [ -f "$TGZ_FILE" ]; then
                        pkg_name_scoped=$(echo "$pkg_version_string" | cut -d'@' -f1-$(($(echo "$pkg_version_string" | tr '@' '\n' | wc -l)-1)))
                        pkg_version=$(echo "$pkg_version_string" | awk -F'@' '{print $NF}')
                        pkg_dir_name=$(echo "${pkg_name_scoped}-${pkg_version}" | sed 's/\//-/g')
                        
                        mkdir -p "$pkg_dir_name"
                        
                        if tar -xzf "$TGZ_FILE" -C "$pkg_dir_name" --strip-components=1 &>/dev/null; then
                            echo "      Successfull"
                            # Ghi vào file log trong thư mục gốc
                            echo "$pkg_version_string" >> "../$(basename $DAILY_LOG_FILE)"
                        else
                            echo "      Fail to extract: $pkg_version_string. Clean."
                            rm -rf "$pkg_dir_name"
                        fi
                        
                        rm "$TGZ_FILE"
                    else
                        echo "      Create file error: npm pack fail for $pkg_version_string."
                    fi
                else
                    echo "      Download error: Cannot download $pkg_version_string."
                fi
            done
            
            if [ "$NEW_PACKAGES_FOUND" -eq 0 ]; then
                 echo "  Dont have new package at this scanning."
            fi
        ) # Kết thúc subshell
    fi
    
    echo "  Finish scanning. Continuous after $(($SLEEP_INTERVAL / 60)) mins."
    sleep "$SLEEP_INTERVAL"
done
