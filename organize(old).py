import os
import json
import math
from pathlib import Path
from collections import Counter
from feature_extractor import extract_features_from_package_with_tree_sitter

def organize_and_extract_features_with_tree_sitter(npm_packages_dir, output_dir):
    """
    Tổ chức các gói NPM thành cấu trúc thư mục và trích xuất change-features.csv.
    Sử dụng tính năng phân tích sâu từ Tree-sitter.

    Args:
        npm_packages_dir (str): Thư mục chứa các gói NPM đã tải về hoặc giải nén.
        output_dir (str): Thư mục đích để tổ chức lại và lưu các tệp change-features.csv.
    """
    npm_packages_dir = Path(npm_packages_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for package_dir in npm_packages_dir.iterdir():
        if package_dir.is_dir():
            try:
                # Giả định thư mục là `package-name@version` (e.g., lodash@4.17.21)
                package_name, version = package_dir.name.rsplit("@", 1)
                package_output_dir = output_dir / package_name / version
                package_output_dir.mkdir(parents=True, exist_ok=True)

                # Trích xuất đặc tính và lưu thành change-features.csv
                features = extract_features_from_package_with_tree_sitter(package_dir)
                change_features_path = package_output_dir / "change-features.csv"
                with open(change_features_path, "w", encoding="utf-8") as f:
                    for feature, value in features.items():
                        f.write(f"{feature},{value}\n")

                print(f"Processed {package_name}@{version} -> {change_features_path}")

            except Exception as e:
                print(f"Error processing {package_dir.name}: {e}")

    print(f"All packages organized and features extracted to {output_dir}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Organize NPM packages and extract features using Tree-sitter.")
    parser.add_argument("npm_packages_dir", help="Directory containing unzipped NPM packages.")
    parser.add_argument("output_dir", help="Directory to organize packages and save features.")
    args = parser.parse_args()

    organize_and_extract_features_with_tree_sitter(args.npm_packages_dir, args.output_dir)
