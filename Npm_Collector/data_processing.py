import os
import pandas as pd
import time
from datetime import datetime
from extractor import hash_package, process_package


INPUT_ROOT_DIR = "/home/kali/Documents/npm/dataset"
FEATURES_OUTPUT_DIR = "/home/kali/Documents/npm/Features_Extracted"
HASHES_OUTPUT_DIR = "/home/kali/Documents/npm/Hash_File"
SLEEP_INTERVAL = 3600  # Nghỉ 1 giờ (3600 giây) giữa các lần quét

def main():

    print("--- Start processing dataset ---")
    print("--- Click Ctrl+C to stop ---")

    os.makedirs(FEATURES_OUTPUT_DIR, exist_ok=True)
    os.makedirs(HASHES_OUTPUT_DIR, exist_ok=True)

    while True:
        current_date = datetime.now().strftime('%Y-%m-%d')
        input_dir = os.path.join(INPUT_ROOT_DIR, f"date-{current_date}")
        features_csv_path = os.path.join(FEATURES_OUTPUT_DIR, f"{current_date}.csv")
        hashes_csv_path = os.path.join(HASHES_OUTPUT_DIR, f"{current_date}.csv")

        print("------------------------------------------------------------")
        print(f"Start new process: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Working with folder: {input_dir}")

        if not os.path.exists(input_dir):
            print("  Not found input file.")
        else:
  
            try:
                processed_packages_set = set(pd.read_csv(features_csv_path)['package_name'])
            except FileNotFoundError:
                processed_packages_set = set()

  
            current_packages_in_dir = set(f for f in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, f)))
            
 
            packages_to_process = list(current_packages_in_dir - processed_packages_set)

            if not packages_to_process:
                print("  Dont have new folder to process.")
            else:
                print(f"  Find {len(packages_to_process)} new packages. Start processing...")
                new_features_list = []
                new_hashes_list = []

                for pkg_name in packages_to_process:
                    print(f"    -> Processing: {pkg_name}")
                    pkg_path = os.path.join(input_dir, pkg_name)
                    
                    # 1. Trích xuất đặc tính
                    features_dict = process_package(pkg_path)
                    if features_dict:
                        features_dict['package_name'] = pkg_name
                        new_features_list.append(features_dict)
                    
                    # 2. Tạo hash
                    package_hash = hash_package(pkg_path)
                    if package_hash:
                        new_hashes_list.append({'package_name': pkg_name, 'hash': package_hash})

                # Ghi các kết quả mới vào file CSV
                if new_features_list:
                    final_features_df = pd.DataFrame(new_features_list)
                    write_header = not os.path.exists(features_csv_path)
                    final_features_df.to_csv(features_csv_path, mode='a', header=write_header, index=False)
                    print(f"    -> Saved {len(final_features_df)} samples to '{features_csv_path}'")
                
                if new_hashes_list:
                    final_hashes_df = pd.DataFrame(new_hashes_list)
                    write_header = not os.path.exists(hashes_csv_path)
                    final_hashes_df.to_csv(hashes_csv_path, mode='a', header=write_header, index=False)
                    print(f"    -> Saved {len(final_hashes_df)} samples to '{hashes_csv_path}'")
        
        print(f"Finish processing. Continuous {SLEEP_INTERVAL // 60} mins.")
        time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    main()
