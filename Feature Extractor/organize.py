import os
import csv
from pathlib import Path
from feature_extractor import extract_package_features

def organize_and_extract_features_with_tree_sitter(npm_packages_dir, output_dir):
    npm_packages_dir = Path(npm_packages_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for package_name_dir in npm_packages_dir.iterdir():
        if package_name_dir.is_dir():  # `package_name` level
            package_name = package_name_dir.name
            for version_dir in package_name_dir.iterdir():
                if version_dir.is_dir():  # `version` level
                    version = version_dir.name
                    try:
                        # Đường dẫn output cho package_name/version
                        package_output_dir = output_dir / package_name / version
                        package_output_dir.mkdir(parents=True, exist_ok=True)

                        # Trích xuất đặc tính và lưu thành change-features.csv
                        features = extract_package_features(version_dir)
                        change_features_path = package_output_dir / "change-features.csv"
                        with open(change_features_path, "w", newline="") as f:
                            writer = csv.writer(f)
                            writer.writerow(["feature", "value"])  # Ghi tiêu đề cột
                            for feature, value in features.items():
                                writer.writerow([feature, value])  # Ghi từng cặp feature-value

                        print(f"Processed {package_name}/{version} -> {change_features_path}")

                    except Exception as e:
                        print(f"Error processing {package_name}/{version}: {e}")

    print(f"All packages organized and features extracted to {output_dir}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Organize NPM packages and extract features using Tree-sitter.")
    parser.add_argument("npm_packages_dir", help="Directory containing unzipped NPM packages.")
    parser.add_argument("output_dir", help="Directory to organize packages and save features.")
    args = parser.parse_args()

    organize_and_extract_features_with_tree_sitter(args.npm_packages_dir, args.output_dir)
