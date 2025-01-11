import os
import shutil

output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

def move_contents(src_dir, dst_dir):
    os.makedirs(dst_dir, exist_ok=True)
    for item in os.listdir(src_dir):
        s = os.path.join(src_dir, item)
        d = os.path.join(dst_dir, item)
        if os.path.isdir(s):
            shutil.move(s, d)
        else:
            shutil.move(s, d)
    os.rmdir(src_dir)

for parent_dir in os.listdir("."):
    if os.path.isdir(parent_dir) and parent_dir != output_dir:
        parent_name = os.path.basename(parent_dir)
        
        if parent_name.startswith("@"):
            for subdir in os.listdir(parent_dir):
                subdir_path = os.path.join(parent_dir, subdir)
                if os.path.isdir(subdir_path):
                    new_name = f"{parent_name}@{subdir}"
                    new_dir = os.path.join(output_dir, new_name)
                    move_contents(subdir_path, new_dir)
                    print(f"Đã tạo thư mục mới và di chuyển nội dung: {subdir_path} -> {new_dir}")
        else:
            new_dir = os.path.join(output_dir, parent_name)
            move_contents(parent_dir, new_dir)
            print(f"Giữ nguyên thư mục con trong thư mục cha: {parent_dir} -> {new_dir}")

print("Hoàn tất di chuyển tất cả các thư mục!")
