import os
import hashlib
import json
import csv

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

def export_to_csv(directory, output_csv):
    """
    Compute hashes for all packages and versions in the directory and export to a CSV file.
    """
    print("Hashing packages...")
    package_hashes = hash_versions(directory)

    print("Writing results to CSV...")
    with open(output_csv, mode="w", newline="") as csv_file:
        fieldnames = ["package", "version", "hash"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for package_hash, (package, version) in package_hashes.items():
            writer.writerow({
                "package": package,
                "version": version,
                "hash": package_hash
            })

    print(f"Results have been written to {output_csv}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <packages-directory> <output-csv-file>")
        sys.exit(1)

    packages_directory = sys.argv[1]
    output_csv_file = sys.argv[2]

    export_to_csv(packages_directory, output_csv_file)