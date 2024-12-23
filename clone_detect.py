import os
import hashlib
import json
import csv
import pandas as pd

def hash_package(root):
    """
    Compute an md5 hash of all files under root, visiting them in deterministic order.
    `package.json` files are stripped of their `name` and `version` fields.
    """
    m = hashlib.md5()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for filename in sorted(filenames):
            path = os.path.join(dirpath, filename)
            m.update(f"{os.path.relpath(path, root)}\n".encode("utf-8"))
            if filename == "package.json":
                with open(path, "r") as f:
                    pkg = json.load(f)
                    pkg["name"] = ""
                    pkg["version"] = ""
                    m.update(json.dumps(pkg, sort_keys=True).encode("utf-8"))
            else:
                with open(path, "rb") as f:
                    m.update(f.read())
    return m.hexdigest()

def hash_versions(directory):
    """
    Traverse all packages and versions in the given directory, and compute hash for each version.
    Returns a dictionary: {hash: (package_name, version)}.
    """
    hashes = {}
    for package in os.listdir(directory):
        package_path = os.path.join(directory, package)
        if os.path.isdir(package_path):
            for version in os.listdir(package_path):
                version_path = os.path.join(package_path, version)
                if os.path.isdir(version_path):
                    package_hash = hash_package(version_path)
                    hashes[package_hash] = (package, version)
    return hashes

def detect_clones(basic_corpus_csv, new_packages_dir, output_csv="results.csv"):
    """
    Compare hashes from new packages against malicious hashes in the basic corpus.
    Write results to a CSV file and print matches on terminal.
    """
    # Đọc basic_corpus.csv và lấy các hash malicious
    print("Reading basic corpus...")
    basic_corpus = pd.read_csv(basic_corpus_csv)
    malicious_hashes = basic_corpus[basic_corpus['analysis'] == 'malicious']['hash'].tolist()

    print(f"Found {len(malicious_hashes)} malicious hashes in the basic corpus.")

    # Hash tất cả các gói trong new packages
    print("Hashing new packages...")
    new_hashes = hash_versions(new_packages_dir)

    print("\nDetecting clones...")
    results = []

    for new_hash, (package, version) in new_hashes.items():
        if new_hash in malicious_hashes:
            print(f"Clone detected: {package}@{version} matches a malicious package in the basic corpus.")
            clone_detected = "yes"
            results.append({
                "package": package,
                "version": version,
                "hash": new_hash,
                "clone_detect": clone_detected
            })

    # Write results to CSV
    with open(output_csv, mode="w", newline="") as csv_file:
        fieldnames = ["package", "version", "hash", "clone_detect"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    print(f"\nResults have been written to {output_csv}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <basic-corpus-csv> <new-packages-directory> <output-csv-file>")
        sys.exit(1)

    basic_corpus_csv = sys.argv[1]
    new_packages_dir = sys.argv[2]
    output_csv_file = sys.argv[3]

    detect_clones(basic_corpus_csv, new_packages_dir, output_csv_file)