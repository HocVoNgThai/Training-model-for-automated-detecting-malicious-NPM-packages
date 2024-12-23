import csv
import argparse

def check_csv_files(input_files, output_file):
    """
    Kiểm tra 4 file CSV và ghi kết quả thỏa điều kiện vào một file mới.

    Args:
        input_files (list): Danh sách đường dẫn tới các file CSV.
        output_file (str): Đường dẫn tới file kết quả.
    """
    malicious_packages = set()  # Tập hợp lưu các package, version có label 'Malicious'
    clone_detect_packages = set()  # Tập hợp lưu các package, version có clone_detect 'yes'

    # Kiểm tra 3 file đầu với label 'Malicious'
    for file_path in input_files[:3]:
        with open(file_path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["label"].strip().lower() == "malicious":
                    malicious_packages.add((row["package"], row["version"]))

    # Kiểm tra file thứ 4 với clone_detect 'yes'
    with open(input_files[3], "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["clone_detect"].strip().lower() == "yes":
                clone_detect_packages.add((row["package"], row["version"]))

    # Hợp kết quả từ cả 2 điều kiện
    final_packages = malicious_packages.union(clone_detect_packages)

    # Ghi kết quả ra file CSV
    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["package", "version"])  # Header
        writer.writerows(final_packages)

    print(f"Completed! Results written to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kiểm tra 4 file CSV và ghi kết quả vào file mới.")
    parser.add_argument(
        "input_files",
        nargs=4,
        help="Đường dẫn tới 4 file CSV (3 file đầu chứa 'label', file cuối chứa 'clone_detect').",
    )
    parser.add_argument(
        "output_file",
        help="Đường dẫn tới file CSV đầu ra để lưu kết quả.",
    )
    args = parser.parse_args()

    check_csv_files(args.input_files, args.output_file)
