import pickle

# Load mô hình từ file pickle
with open("trained_dt.pkl", "rb") as f:
    model = pickle.load(f)

# Kiểm tra thông tin về mô hình
print("Model type:", type(model))
print("Model parameters:", model.get_params())  # Nếu hỗ trợ get_params()
