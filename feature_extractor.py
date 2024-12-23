import os
import json
import math
import hashlib
from pathlib import Path
from collections import Counter
from datetime import datetime
import csv
from packaging.version import Version, InvalidVersion
from tree_sitter import Language, Parser
import tree_sitter_javascript as tsjs

# Tree-sitter JavaScript setup
JS_LANGUAGE = Language(tsjs.language())

def calculate_entropy(data):
    """Calculate the Shannon entropy of a string."""
    if not data:
        return 0
    counter = Counter(data)
    length = len(data)
    return -sum((count / length) * math.log2(count / length) for count in counter.values())

def read_file(filepath):
    """Read a file and return its content as a string."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return ""

def detect_binary(filepath):
    """Detect if a file is a binary file."""
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(1024)
            return any(byte > 127 for byte in chunk)
    except Exception as e:
        print(f"Error detecting binary file {filepath}: {e}")
        return False

def extract_sensitive_code_features(js_code):
    """Extract features using Tree-sitter for sensitive JavaScript patterns."""
    parser = Parser(JS_LANGUAGE)
    tree = parser.parse(bytes(js_code, "utf8"))
    root_node = tree.root_node

    features = {
        "system_command_usage": 0,
        "file_access": 0,
        "env_variable_access": 0,
        "network_access": 0,
        "crypto_usage": 0,
        "data_encoding": 0,
        "dynamic_code_generation": 0,
    }

    def traverse(node):
        if node.type == "call_expression":
            func_node = node.child_by_field_name("function")
            if func_node:
                func_name = func_node.text.decode("utf8")
                if func_name in {"fs.readFile", "fs.writeFile", "fs.unlink"}:
                    features["file_access"] += 1
                elif func_name == "process.env":
                    features["env_variable_access"] += 1
                elif func_name in {"exec", "spawn"}:
                    features["system_command_usage"] += 1
                elif func_name in {"http.request", "https.request", "fetch"}:
                    features["network_access"] += 1
                elif func_name in {"crypto.createCipher", "crypto.createHash"}:
                    features["crypto_usage"] += 1
                elif func_name in {"eval", "Function", "setTimeout", "setInterval"}:
                    features["dynamic_code_generation"] += 1
                elif func_name in {"encodeURIComponent", "decodeURIComponent", "btoa", "atob"}:
                    features["data_encoding"] += 1

        for child in node.children:
            traverse(child)

    traverse(root_node)
    return features

def extract_dependencies_count(package_data):
    DEPENDENCY_FIELDS = [
        "dependencies",
        "devDependencies",
        "peerDependencies",
        "optionalDependencies",
        "_actualDependencies",
        "bundleDependencies",
        "bundledDependencies",  # alias
    ]

    dependencies_count = 0

    for field in DEPENDENCY_FIELDS:
        if field in package_data:
            dependencies = package_data.get(field, {})
            dependencies_count += len(dependencies)

    return dependencies_count

def extract_package_features(package_dir):
    """Extract features from an npm package directory."""
    features = {
        "max_entropy": 0,
        "avg_entropy": 0,
        "minified_files": 0,
        "binary_files": 0,
        "pii_keywords": 0,
        "dependencies_count": 0,
        "scripts_count": 0,
        "has_postinstall_script": 0,
    }

    pii_keywords = ["password", "creditcard", "cookie"]

    file_sizes = []
    entropies = []

    for root, _, files in os.walk(package_dir):
        for file in files:
            filepath = os.path.join(root, file)
            file_sizes.append(os.path.getsize(filepath))

            if detect_binary(filepath):
                features["binary_files"] += 1
                continue

            content = read_file(filepath)
            if content:
                entropy = calculate_entropy(content)
                entropies.append(entropy)

                # Detect PII
                features["pii_keywords"] += sum(keyword in content for keyword in pii_keywords)

                # Minified file detection
                if len(content.splitlines()) < 5 and len(content) > 500:
                    features["minified_files"] += 1

                if file.endswith(".js"):
                    js_features = extract_sensitive_code_features(content)
                    for key, value in js_features.items():
                        features[key] = features.get(key, 0) + value

    package_json_path = os.path.join(package_dir, "package.json")
    if os.path.isfile(package_json_path):
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)

            features["dependencies_count"] = extract_dependencies_count(package_data)
            scripts = package_data.get("scripts", {})
            features["scripts_count"] = len(scripts)
            features["has_postinstall_script"] = 1 if "postinstall" in scripts else 0

        except Exception as e:
            print(f"Error reading package.json: {e}")

    features["max_entropy"] = max(entropies) if entropies else 0
    features["avg_entropy"] = sum(entropies) / len(entropies) if entropies else 0

    return features

def analyze_version_diff(version1, version2, time1, time2):
    """Analyze differences between two versions of a package."""
    try:
        v1 = Version(version1)
        v2 = Version(version2)
        update_type = "patch"

        if v1.major != v2.major:
            update_type = "major"
        elif v1.minor != v2.minor:
            update_type = "minor"

        time_diff = (datetime.fromisoformat(time2) - datetime.fromisoformat(time1)).days

        return {
            "update_type": update_type,
            "time_between_releases": time_diff,
        }
    except (InvalidVersion, ValueError):
        return {
            "update_type": "unknown",
            "time_between_releases": None,
        }
