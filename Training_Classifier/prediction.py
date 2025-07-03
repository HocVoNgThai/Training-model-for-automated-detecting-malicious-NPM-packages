import os
import csv
import pickle

def classify_packages_from_csv(npm_packages_dir, classifier_file, output_csv_file):
    """
    Phân loại các gói NPM từ các file change-features.csv và lưu kết quả vào tệp CSV.

    Args:
        npm_packages_dir (str): Thư mục chứa các gói NPM (với các file change-features.csv).
        classifier_file (str): Đường dẫn đến file mô hình đã được huấn luyện.
        output_csv_file (str): Đường dẫn đến tệp CSV lưu kết quả phân loại.
    """
    # Tải mô hình đã được lưu
    with open(classifier_file, "rb") as f:
        model_data = pickle.load(f)
    
    feature_names = model_data["feature_names"]
    booleanize = model_data["booleanize"]
    classifier = model_data["classifier"]

    # Mở tệp CSV để ghi kết quả
    with open(output_csv_file, "w", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        # Ghi tiêu đề cột
        csv_writer.writerow(["package", "version", "label"])

        # Duyệt qua tất cả các gói trong thư mục
        for package_dir in os.listdir(npm_packages_dir):
            package_path = os.path.join(npm_packages_dir, package_dir)
            if os.path.isdir(package_path):
                for version_dir in os.listdir(package_path):
                    version_path = os.path.join(package_path, version_dir)
                    if os.path.isdir(version_path):
                        change_features_path = os.path.join(version_path, "change-features.csv")
                        if os.path.exists(change_features_path):
                            try:
                                # Đọc các đặc tính từ file change-features.csv
                                raw_features = {}
                                with open(change_features_path, "r", encoding="utf-8") as f:
                                    reader = csv.reader(f)
                                    next(reader)
                                    for row in reader:
                                        feature, value = row
                                        raw_features[feature] = float(value)  # Hoặc float(value) nếu giá trị không phải số nguyên

                                # Đảm bảo tính nhất quán với các đặc tính đã sử dụng khi huấn luyện
                                feature_vector = [raw_features.get(feature, 0) for feature in feature_names]

                                if booleanize:
                                    feature_vector = [1 if x else 0 for x in feature_vector]

                                # Dự đoán nhãn (0 = lành tính, 1 = độc hại)
                                prediction = classifier.predict([feature_vector])[0]
                                label = "Malicious" if prediction == 1 else "Benign"

                                # Ghi kết quả vào CSV
                                csv_writer.writerow([package_dir, version_dir, label])

                                print(f"Processed {package_dir}@{version_dir}: {label}")

                            except Exception as e:
                                print(f"Error processing {package_dir}@{version_dir}: {e}")

    print(f"Classification completed. Results saved to {output_csv_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Classify NPM packages using pre-extracted features.")
    parser.add_argument("npm_packages_dir", help="Directory containing NPM packages with change-features.csv files.")
    parser.add_argument("classifier_file", help="Trained classifier file (e.g., classifier.pkl).")
    parser.add_argument("output_csv_file", help="File to save classification results in CSV format.")
    args = parser.parse_args()

    classify_packages_from_csv(args.npm_packages_dir, args.classifier_file, args.output_csv_file)
