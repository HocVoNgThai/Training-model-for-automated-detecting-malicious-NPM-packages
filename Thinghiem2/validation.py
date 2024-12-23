import os
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

# 1. Đọc dữ liệu
df = pd.read_csv('basic-corpus.csv')

# 2. Kiểm tra và xử lý dữ liệu
# Chắc chắn không có dòng nào thiếu nhãn
assert df['analysis'].isnull().sum() == 0, "Dữ liệu có dòng thiếu nhãn!"
valid_labels = ['benign', 'malicious']
df = df[df['analysis'].isin(valid_labels)]  # Chỉ giữ nhãn hợp lệ

# 3. Mã hóa nhãn thành số: benign -> 1, malicious -> 0
df['analysis'] = df['analysis'].map({'benign': 1, 'malicious': 0})

# 4. Đặc trưng và nhãn
X = df[['package', 'version']]
y = df['analysis']

# 5. Mã hóa đặc trưng 'package' và 'version' (one-hot encoding)
X_encoded = pd.get_dummies(X, drop_first=True)

# 6. Cấu hình StratifiedKFold
kf = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)

# 7. Khởi tạo các mô hình
models = {
    'decision-tree': DecisionTreeClassifier(),
    'naive-bayes': GaussianNB(),
    'svm': SVC()
}

# 8. Tạo thư mục lưu kết quả
output_dir = 'cross-validation'
os.makedirs(output_dir, exist_ok=True)

# 9. Vòng lặp cross-validation
for fold, (train_index, test_index) in enumerate(kf.split(X_encoded, y)):
    print(f"Processing Fold {fold + 1}")

    # Chia tập train và test
    X_train, X_test = X_encoded.iloc[train_index], X_encoded.iloc[test_index]
    y_train, y_test = y.iloc[train_index], y.iloc[test_index]

    # Khớp đúng tập test gốc
    X_test_original = X.iloc[test_index].reset_index(drop=True)

    # Tạo thư mục cho từng fold
    fold_dir = os.path.join(output_dir, f'fold_{fold + 1}')
    os.makedirs(fold_dir, exist_ok=True)

    for model_name, model in models.items():
        # Huấn luyện mô hình
        model.fit(X_train, y_train)
        
        # Dự đoán nhãn
        y_pred = model.predict(X_test)
        
        # Tính độ chính xác
        accuracy = accuracy_score(y_test, y_pred)
        print(f"{model_name} Accuracy in Fold {fold + 1}: {accuracy:.4f}")
        
        # Kết hợp nhãn dự đoán với tập test gốc
        results = X_test_original.copy()
        results['analysis'] = pd.Series(y_pred).map({1: 'benign', 0: 'malicious'})

        # Ghi kết quả ra file .tsv
        results_file = os.path.join(fold_dir, f'{model_name}.tsv')
        results.to_csv(results_file, sep='\t', index=False, header=True)

print("Hoàn tất quá trình huấn luyện và lưu kết quả.")
