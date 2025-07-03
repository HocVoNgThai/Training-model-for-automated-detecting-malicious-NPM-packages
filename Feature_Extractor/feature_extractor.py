import os
import json
import re
import math
import esprima 
import pandas as pd
from collections import Counter


def calculate_entropy(s):
    """Tính toán entropy của một chuỗi ký tự."""
    if not s:
        return 0
    # Đếm tần suất xuất hiện của mỗi ký tự
    p, lns = Counter(s), float(len(s))
    # Công thức Shannon entropy
    return -sum(count / lns * math.log(count / lns, 2) for count in p.values())


# --- Các hàm trích xuất đặc tính chính ---

def extract_metadata_features(package_path):
    """Trích xuất đặc tính từ file package.json."""
    features = {
        'has_install_scripts': 0, # Có script 'preinstall' hoặc 'postinstall' không?
        'has_dependencies': 0,
        'has_dev_dependencies': 0,
        'num_dependencies': 0,
        'num_dev_dependencies': 0,
    }
    pkg_json_path = os.path.join(package_path, 'package.json')
    if not os.path.exists(pkg_json_path):
        return features

    try:
        with open(pkg_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Kiểm tra các script cài đặt có thể nguy hiểm
            if 'scripts' in data and ('preinstall' in data['scripts'] or 'postinstall' in data['scripts']):
                features['has_install_scripts'] = 1
            
            if 'dependencies' in data:
                features['has_dependencies'] = 1
                features['num_dependencies'] = len(data['dependencies'])
                
            if 'devDependencies' in data:
                features['has_dev_dependencies'] = 1
                features['num_dev_dependencies'] = len(data['devDependencies'])

    except (json.JSONDecodeError, UnicodeDecodeError):
        # Bỏ qua nếu file JSON bị lỗi
        pass
        
    return features

def extract_static_code_features(package_path):
    """
    Trích xuất các đặc tính từ mã nguồn JavaScript bằng cách phân tích tĩnh.
    Chúng ta sẽ duyệt qua các tệp, phân tích AST và dùng regex.
    """
    features = {
        'num_files': 0,
        'total_code_size': 0,
        'avg_entropy': 0.0,
        'max_entropy': 0.0,
        'num_urls': 0,
        'num_ips': 0,
        # Các hàm API đáng ngờ
        'has_eval': 0,
        'has_child_process': 0,
        'has_fs_access': 0, # Truy cập file system
        'has_network_access': 0, # Truy cập mạng
        'has_os_access': 0, # Truy cập thông tin hệ điều hành
    }
    
    total_entropy = 0
    file_count = 0
    
    # Biểu thức chính quy để tìm URL và địa chỉ IP
    url_pattern = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
    ip_pattern = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')

    for root, _, files in os.walk(package_path):
        for file in files:
            file_path = os.path.join(root, file)
            # Chỉ phân tích các tệp JavaScript
            if not file.endswith('.js'):
                continue
                
            file_count += 1
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    features['total_code_size'] += len(content)
                    
                    # Tính toán entropy
                    entropy = calculate_entropy(content)
                    total_entropy += entropy
                    if entropy > features['max_entropy']:
                        features['max_entropy'] = entropy
                    
                    # Tìm URL và IP bằng regex
                    features['num_urls'] += len(url_pattern.findall(content))
                    features['num_ips'] += len(ip_pattern.findall(content))
                    
                    # Phân tích AST để tìm các lệnh gọi hàm nguy hiểm
                    ast = esprima.parseScript(content, tolerant=True)
                    for node in ast.body:
                        if hasattr(node, 'type') and node.type == 'ExpressionStatement':
                            expr = node.expression
                            if hasattr(expr, 'type') and expr.type == 'CallExpression':
                                callee = expr.callee
                                if hasattr(callee, 'name'):
                                    if 'eval' in callee.name:
                                        features['has_eval'] = 1
                                elif hasattr(callee, 'type') and callee.type == 'MemberExpression':
                                    obj_name = callee.object.name if hasattr(callee.object, 'name') else ''
                                    prop_name = callee.property.name if hasattr(callee.property, 'name') else ''
                                    
                                    if obj_name == 'require':
                                        arg = expr.arguments[0].value if expr.arguments else ''
                                        if arg == 'child_process':
                                            features['has_child_process'] = 1
                                        elif arg == 'fs' or arg == 'fs-extra':
                                            features['has_fs_access'] = 1
                                        elif arg == 'http' or arg == 'https' or arg == 'net':
                                            features['has_network_access'] = 1
                                        elif arg == 'os':
                                            features['has_os_access'] = 1

            except Exception:
                # Bỏ qua các tệp không thể đọc hoặc phân tích cú pháp
                continue

    if file_count > 0:
        features['num_files'] = file_count
        features['avg_entropy'] = total_entropy / file_count
        
    return features


def process_package(package_path):
    """Hàm tổng hợp để xử lý một gói duy nhất."""
    all_features = {}
    metadata_features = extract_metadata_features(package_path)
    code_features = extract_static_code_features(package_path)
    
    all_features.update(metadata_features)
    all_features.update(code_features)
    all_features['package_name'] = os.path.basename(package_path)
    
    return all_features

# --- Hàm main để chạy toàn bộ quá trình ---

if __name__ == '__main__':
    malicious_dir = 'dataset/malicious'
    benign_dir = 'dataset/benign'
    
    all_package_features = []

    print("--- Processing Malicious Packages ---")
    malicious_packages = [os.path.join(malicious_dir, d) for d in os.listdir(malicious_dir) if os.path.isdir(os.path.join(malicious_dir, d))]
    for pkg_path in malicious_packages:
        print(f"Extracting from: {os.path.basename(pkg_path)}")
        features = process_package(pkg_path)
        features['label'] = 1  # 1 là độc hại
        all_package_features.append(features)

    print("\n--- Processing Benign Packages ---")
    benign_packages = [os.path.join(benign_dir, d) for d in os.listdir(benign_dir) if os.path.isdir(os.path.join(benign_dir, d))]
    for pkg_path in benign_packages:
        print(f"Extracting from: {os.path.basename(pkg_path)}")
        features = process_package(pkg_path)
        features['label'] = 0  # 0 là an toàn
        all_package_features.append(features)

    # Chuyển đổi danh sách các dict thành DataFrame của pandas và lưu ra file CSV
    df = pd.DataFrame(all_package_features)
    
    # Điền các giá trị bị thiếu (NaN) bằng 0
    df.fillna(0, inplace=True)
    
    output_csv = 'npm_features_dataset.csv'
    df.to_csv(output_csv, index=False)
    
    print(f"\nFeature extraction complete. Dataset saved to {output_csv}")
    print(f"Total packages processed: {len(df)}")
    print("Columns:", df.columns.tolist())
