import pandas as pd
import sys
import os

def find_clones_in_files(malicious_hashes_csv, new_hashes_csv):

    print("--- Start Clone Detection ---")


    for f_path in [malicious_hashes_csv, new_hashes_csv]:
        if not os.path.exists(f_path):
            print(f"Error: Not found file '{f_path}'")
            return

    try:
        malicious_df = pd.read_csv(malicious_hashes_csv)
        # Chuyển hash độc hại vào một set để tra cứu cực nhanh (O(1))
        malicious_hashes_set = set(malicious_df['hash'])
        print(f"Loaded {len(malicious_hashes_set)} hash malicious from '{malicious_hashes_csv}'")
        
        new_hashes_df = pd.read_csv(new_hashes_csv)
        if new_hashes_df.empty:
            print("File new hash is empty ")
            return
        print(f"Loaded {len(new_hashes_df)} new hash from '{new_hashes_csv}'")
    except Exception as e:
        print(f"Error loading file CSV: {e}")
        return

    detected_clones = []
    for index, row in new_hashes_df.iterrows():
        if row['hash'] in malicious_hashes_set:
            detected_clones.append(row)

    if not detected_clones:
        print("\nNot detect any clone packages.")
    else:
        print(f"\nALERT: Detected {len(detected_clones)} clone of known malicious packages!")
        clones_df = pd.DataFrame(detected_clones)   
        print(clones_df.to_string(index=False))
       
        base_name = os.path.basename(new_hashes_csv)
        name, ext = os.path.splitext(base_name)
        output_csv_path = f"../prediction_result/{name}_clones_detected{ext}"
        
        clones_df.to_csv(output_csv_path, index=False)
        print(f"\nSaved to file: '{output_csv_path}'")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 clone_detector.py <path_to_malicious_hashes.csv> <path_to_new_hashes.csv>")
        sys.exit(1)
        
    malicious_file = sys.argv[1]
    new_hashes_file = sys.argv[2]
    
    find_clones_in_files(malicious_file, new_hashes_file)
