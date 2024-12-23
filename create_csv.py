import os
import csv
import argparse

def collect_packages_versions(directory):
    """
    Duyệt qua thư mục và thu thập package và version.
    """
    data = []
    for package in os.listdir(directory):
        package_path = os.path.join(directory, package)
        if os.path.isdir(package_path):  # Kiểm tra package là thư mục
            for version in os.listdir(package_path):
                version_path = os.path.join(package_path, version)
                if os.path.isdir(version_path):  # Kiểm tra version là thư mục
                    data.append([package, version])
    return data

def main():
    # Thiết lập nhập tham số từ dòng lệnh
    parser = argparse.ArgumentParser(description="Tạo file CSV chứa package và version từ cấu trúc thư mục.")
    parser.add_argument("input_dir", help="Đường dẫn đến thư mục gốc chứa các package.")
    parser.add_argument("output_file", help="Đường dẫn file CSV đầu ra.")
    args = parser.parse_args()

    # Thu thập package và version
    package_version_data = collect_packages_versions(args.input_dir)

    # Ghi dữ liệu vào file CSV
    with open(args.output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["package", "version"])  # Header
        writer.writerows(package_version_data)  # Ghi dữ liệu

    print(f"File CSV đã được tạo: '{args.output_file}'")

if __name__ == "__main__":
    main()