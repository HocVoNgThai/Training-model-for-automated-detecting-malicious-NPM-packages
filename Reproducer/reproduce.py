import csv
import subprocess
import os
import argparse
import shutil

def run_reproduce_package(package, version, output_dir):
    working_dir = "working"  # Đường dẫn đến folder 'working'
    # Xóa folder 'working' nếu tồn tại
    if os.path.exists(working_dir):
        print(f"Cleaning up: Removing folder '{working_dir}'...")
        shutil.rmtree(working_dir, ignore_errors=True)
    try:
        # Tạo command gọi file reproduce-package.sh
        command = ["bash", "reproduce-package.sh", f"{package}@{version}", output_dir]
        # Thực thi lệnh, redirect stderr và stdout để ghi log
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)

        # In ra kết quả nếu cần
        print(f"Successfully reproduced {package}@{version}: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        # Ghi lỗi vào log
        return False
def normalize_package_name(package_name):
    if package_name.count('@') > 1:
        parts = package_name.split('@')
        return f"{parts[0]}@{parts[1]}/{parts[2]}"
    return package_name
def process_packages(input_csv, output_csv, output_dir):
    failed_packages = []

    # Đọc file CSV đầu vào
    with open(input_csv, "r") as infile:
        reader = csv.DictReader(infile)
        
        # Duyệt qua từng hàng trong file CSV
        for row in reader:
            original_package = row["package"]
            package = normalize_package_name(original_package)
            version = row["version"]

            print(f"Processing {package}@{version}...")

            # Chạy tập lệnh reproduce-package.sh
            success = run_reproduce_package(package, version, output_dir)

            if not success:
                print(f"Failed to reproduce {package}@{version}.")
                failed_packages.append({"package": package, "version": version})

    # Ghi các gói thất bại vào file CSV đầu ra
    with open(output_csv, "w", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["package", "version"])
        writer.writeheader()
        writer.writerows(failed_packages)

    print(f"Done! Failed reproductions are saved to {output_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reproduce npm packages and log failures.")
    parser.add_argument("input_csv", help="Input CSV file containing 'package' and 'version' columns.")
    parser.add_argument("output_dir", help="Directory to save reproduction results.")
    parser.add_argument("output_csv", help="Output CSV file to log failed reproductions.")
    args = parser.parse_args()

    # Kiểm tra tồn tại của file input
    if not os.path.isfile(args.input_csv):
        print(f"Lỗi: File đầu vào '{args.input_csv}' không tồn tại.")
        exit(1)

    # Tạo thư mục output nếu chưa tồn tại
    os.makedirs(args.output_dir, exist_ok=True)

    # Chạy chương trình
    process_packages(args.input_csv, args.output_csv, args.output_dir)
