import os
import subprocess
import json

packages_file = "benign_packages.txt"
base_dir = "benign_dataset"
os.makedirs(base_dir, exist_ok=True)

# Hàm kiểm tra gói đã tồn tại trong thư mục chưa
def package_exists(package_name, version):
    package_dir = os.path.join(base_dir, package_name, version)
    return os.path.exists(package_dir)

# Hàm tải và lưu package
def download_package(package_name):
    try:
        # Lấy thông tin package từ npm
        print(f"Đang tải thông tin cho gói: {package_name}")
        result = subprocess.run(
            ["npm", "view", package_name, "versions", "--json"],
            capture_output=True, text=True, check=True
        )
        # Kiểm tra nếu có lỗi xảy ra khi lấy thông tin
        if result.returncode != 0:
            print(f"Lỗi khi lấy thông tin package {package_name}: {result.stderr}")
            return
        versions = json.loads(result.stdout)
        if not versions:
            print(f"Không tìm thấy phiên bản nào cho gói: {package_name}")
            return

        # Tải tất cả các phiên bản của package
        for version in versions:
            if package_exists(package_name, version):
                print(f"Gói {package_name}@{version} đã tồn tại, bỏ qua tải xuống.")
                continue  # Bỏ qua nếu gói đã tồn tại

            package_dir = os.path.join(base_dir, package_name, version)
            os.makedirs(package_dir, exist_ok=True)

            print(f"Đang tải: {package_name}@{version}")
            subprocess.run(
                ["npm", "pack", f"{package_name}@{version}"],
                cwd=package_dir, check=True
            )

            # Giải nén nội dung .tgz vào thư mục
            tgz_file = next((f for f in os.listdir(package_dir) if f.endswith(".tgz")), None)
            if tgz_file:
                tgz_path = os.path.join(package_dir, tgz_file)
                subprocess.run(["tar", "-xzf", tgz_path, "--strip-components=1", "-C", package_dir], check=True)
                os.remove(tgz_path)  # Xóa file .tgz sau khi giải nén
                print(f"Đã giải nén và xóa file .tgz: {tgz_file}")

    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi xử lý package {package_name}: {e}")
    except Exception as e:
        print(f"Lỗi không xác định khi xử lý package {package_name}: {e}")
with open(packages_file, "r") as f:
    # Loại bỏ từ "benign" trong tên gói trước khi thêm vào danh sách
    packages = [line.strip().replace("benign", "").strip() for line in f if line.strip()]

# Tải từng package trong danh sách
for i, package in enumerate(packages, start=1):
    print(f"\nĐang tải package {i}/{len(packages)}: {package}")
    download_package(package)

print("Hoàn tất tải tất cả các gói!")
