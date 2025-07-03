import os
import hashlib
import json
import pandas as pd

def hash_package(root):

    m = hashlib.md5()
   
    for dirpath, dirnames, filenames in sorted(os.walk(root)):
        dirnames.sort()
        for filename in sorted(filenames):
            path = os.path.join(dirpath, filename)
            
            m.update(f"{os.path.relpath(path, root)}\n".encode("utf-8"))
            
            if filename == "package.json":
                try:
                    with open(path, "r", encoding='utf-8') as f:
                        pkg = json.load(f)
                  
                    pkg["name"] = ""
                    pkg["version"] = ""
                    m.update(json.dumps(pkg, sort_keys=True).encode("utf-8"))
                except (json.JSONDecodeError, UnicodeDecodeError):
                  
                    with open(path, "rb") as f:
                        m.update(f.read())
            else:
                with open(path, "rb") as f:
                    m.update(f.read())
    return m.hexdigest()

def process_malicious_directory(directory, output_csv):
    
    print(f"Start hashing npm packages: '{directory}'")
    all_hashes = []
    

    for package_name in os.listdir(directory):
        package_path = os.path.join(directory, package_name)
        if os.path.isdir(package_path):
            print(f"  -> Processing: {package_name}")
            package_hash = hash_package(package_path)
            all_hashes.append({
                "package_name": package_name,
                "hash": package_hash
            })
            
    if not all_hashes:
        print("Not found any packages")
        return

    # Lưu kết quả ra file CSV
    df = pd.DataFrame(all_hashes)
    df.to_csv(output_csv, index=False)
    print(f"\nFinish! Save {len(df)} hash malicious to file '{output_csv}'")

if __name__ == "__main__":
    MALICIOUS_DIR = 'dataset/malicious'
    OUTPUT_FILE = 'malicious_hashes.csv'
    process_malicious_directory(MALICIOUS_DIR, OUTPUT_FILE)
