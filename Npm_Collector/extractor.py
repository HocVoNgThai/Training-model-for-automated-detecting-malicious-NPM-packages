# processing_utils.py
import os
import hashlib
import json
import re
import math
import pandas as pd
from collections import Counter
import esprima 


def hash_package(package_path):

    m = hashlib.md5()
    if not os.path.isdir(package_path):
        return None
        
    for dirpath, dirnames, filenames in sorted(os.walk(package_path)):
        dirnames.sort()
        for filename in sorted(filenames):
            path = os.path.join(dirpath, filename)
            m.update(f"{os.path.relpath(path, package_path)}\n".encode("utf-8"))
            
            if filename == "package.json":
                try:
                    with open(path, "r", encoding='utf-8') as f:
                        pkg = json.load(f)
                    pkg["name"] = ""
                    pkg["version"] = ""
                    m.update(json.dumps(pkg, sort_keys=True).encode("utf-8"))
                except:
                    # Nếu file json lỗi, hash nội dung gốc
                    with open(path, "rb") as f:
                        m.update(f.read())
            else:
                with open(path, "rb") as f:
                    m.update(f.read())
    return m.hexdigest()



def calculate_entropy(s):
    """Tính toán entropy của một chuỗi ký tự."""
    if not s:
        return 0
    p, lns = Counter(s), float(len(s))
    return -sum(count / lns * math.log2(count / lns) for count in p.values())

def extract_metadata_features(package_path):
    """Trích xuất đặc tính từ file package.json."""
    features = {
        'has_install_scripts': 0,
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
            
        if 'scripts' in data and data['scripts'] and ('preinstall' in data['scripts'] or 'postinstall' in data['scripts']):
            features['has_install_scripts'] = 1
        
        if 'dependencies' in data and data['dependencies']:
            features['has_dependencies'] = 1
            features['num_dependencies'] = len(data['dependencies'])
            
        if 'devDependencies' in data and data['devDependencies']:
            features['has_dev_dependencies'] = 1
            features['num_dev_dependencies'] = len(data['devDependencies'])

    except (json.JSONDecodeError, UnicodeDecodeError):
        pass
        
    return features

def extract_static_code_features(package_path):
    """
    Trích xuất các đặc tính từ mã nguồn JavaScript bằng cách phân tích tĩnh.
    """
    features = {
        'num_js_files': 0,
        'total_code_size': 0,
        'avg_entropy': 0.0,
        'max_entropy': 0.0,
        'num_urls': 0,
        'num_ips': 0,
        'has_eval': 0,
        'has_child_process': 0,
        'has_fs_access': 0,
        'has_network_access': 0,
        'has_os_access': 0,
    }
    
    total_entropy = 0
    file_count = 0
    
    url_pattern = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
    ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')

    for root, _, files in os.walk(package_path):
        for file in files:
            if not file.endswith('.js'):
                continue
                
            file_count += 1
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                features['total_code_size'] += len(content)
                
                entropy = calculate_entropy(content)
                total_entropy += entropy
                if entropy > features['max_entropy']:
                    features['max_entropy'] = entropy
                
                features['num_urls'] += len(url_pattern.findall(content))
                features['num_ips'] += len(ip_pattern.findall(content))
                
                ast = esprima.parseScript(content, tolerant=True)
                # Dùng một hàm đệ quy để duyệt cây AST hiệu quả hơn
                def traverse_ast(node):
                    if not node or not isinstance(node, esprima.nodes.Node):
                        return

                    if node.type == 'CallExpression':
                        callee = node.callee
                        if hasattr(callee, 'name') and 'eval' in callee.name:
                            features['has_eval'] = 1
                        
                        if callee.type == 'MemberExpression' and hasattr(callee.object, 'name') and callee.object.name == 'require':
                            if node.arguments and hasattr(node.arguments[0], 'value'):
                                arg = node.arguments[0].value
                                if arg == 'child_process': features['has_child_process'] = 1
                                elif arg in ['fs', 'fs-extra']: features['has_fs_access'] = 1
                                elif arg in ['http', 'https', 'net']: features['has_network_access'] = 1
                                elif arg == 'os': features['has_os_access'] = 1

                    # Duyệt các nút con
                    for key in node:
                        if isinstance(getattr(node, key), list):
                            for child_node in getattr(node, key):
                                traverse_ast(child_node)
                        else:
                            traverse_ast(getattr(node, key))
                
                traverse_ast(ast)
            except Exception:
                continue

    if file_count > 0:
        features['num_js_files'] = file_count
        features['avg_entropy'] = total_entropy / file_count
        
    return features


def process_package(package_path):
    """
    Hàm tổng hợp để trích xuất tất cả đặc tính từ một gói và trả về một dictionary.
    """
    if not os.path.isdir(package_path):
        return None
        
    all_features = {}
    metadata_features = extract_metadata_features(package_path)
    code_features = extract_static_code_features(package_path)
    
    all_features.update(metadata_features)
    all_features.update(code_features)
    
    return all_features
