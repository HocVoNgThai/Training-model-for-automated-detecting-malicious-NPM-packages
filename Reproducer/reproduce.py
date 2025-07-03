import os
import sys
import shutil
import subprocess
import pandas as pd
from datetime import datetime
import argparse

def run_reproduce_package(package, version, output_dir_for_package):

    working_dir = "working"  
    if os.path.exists(working_dir):
        print(f"  Cleaning up old '{working_dir}' directory...")
        shutil.rmtree(working_dir, ignore_errors=True)
        
    try:
        # Tạo command gọi file reproduce-package.sh với 2 tham số
        # Script shell của bạn không cần tham số thứ 3 cho working_dir
        command = ["bash", "reproduce-package.sh", f"{package}@{version}", output_dir_for_package]
        
        # Thực thi lệnh
        subprocess.run(
            command,
            capture_output=True,
            check=True,  # Gây ra lỗi CalledProcessError nếu script shell thất bại
            text=True,
            timeout=1200 # Timeout 20 phút
        )
        return True # Trả về True nếu thành công
        
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False # Trả về False nếu thất bại

def main(target_date, output_dir, output_csv):

    collector_log_file = os.path.join("dataset", f"date-{target_date}.log")
    
    if not os.path.exists(collector_log_file):
        print(f"Error: Not found file log of collector '{collector_log_file}'.")
        return

    # THAY ĐỔI: Đọc danh sách gói từ file log (thay vì file CSV)
    with open(collector_log_file, 'r') as f:
        packages_to_process = [line.strip() for line in f if line.strip()]
        
    if not packages_to_process:
        print("Nothing to reproduce!")
        return
        
    print(f"Found {len(packages_to_process)} packages needed to reproduce...")

    all_results = []
    for i, pkg_spec in enumerate(packages_to_process):
        print(f"\n[ {i+1}/{len(packages_to_process)} ] Reproducing: {pkg_spec}")
        
        # Tách tên và phiên bản từ chuỗi "name@version"
        # Xử lý các scoped package như @angular/core@14.0.0
        if pkg_spec.startswith('@'):
            parts = pkg_spec[1:].split('@')
            package = f"@{parts[0]}"
            version = parts[1]
        else:
            package, version = pkg_spec.split('@')

        # Tạo thư mục đầu ra riêng cho từng gói
        sanitized_name = package.replace('/', '-')
        package_output_dir = os.path.join(output_dir, target_date, f"{sanitized_name}-{version}")
        os.makedirs(package_output_dir, exist_ok=True)
            
        success = run_reproduce_package(package, version, package_output_dir)
        
        # Chuyển đổi trạng thái thành 0 (thành công) hoặc 1 (thất bại)
        status_code = 0 if success else 1
        
        print(f"  -> Status: {'SUCCESS' if success else 'FAILURE'} (Code: {status_code})")
        
        # Thêm kết quả vào danh sách
        all_results.append({"name": pkg_spec, "status": status_code})

    # Tạo DataFrame và lưu ra file CSV với 2 cột yêu cầu
    results_df = pd.DataFrame(all_results)
    results_df.to_csv(output_csv, index=False)
    
    print("\nFinish reproducing!")
    print(f"Reproductiopn status file is saved at: '{output_csv}'")


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Reproduce npm packages sequentially from a daily log.")
    
    parser.add_argument("target_date", nargs='?', default=datetime.now().strftime('%Y-%m-%d'),
                        help="Target date in YYYY-MM-DD format (defaults to today).")
                        
    parser.add_argument("--output_dir", default="reproduced_packages",
                        help="Root directory to save reproduction results.")
    parser.add_argument("--output_csv", default="prediction_result/reproduction_status.csv",
                        help="Output CSV file to log status.")
    
    args = parser.parse_args()

    # Tạo các thư mục output nếu chưa tồn tại
    os.makedirs(os.path.dirname(args.output_csv), exist_ok=True)

    # Chạy chương trình
    main(args.target_date, args.output_dir, args.output_csv)
