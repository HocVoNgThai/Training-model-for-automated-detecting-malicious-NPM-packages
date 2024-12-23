import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.metrics import make_scorer, precision_score, recall_score
from sklearn.preprocessing import LabelEncoder

# Đọc dữ liệu
data = pd.read_csv('basic-corpus.csv')

# Bỏ cột 'hash' và chỉ giữ lại cột 'package', 'version', 'analysis'
data = data[['package', 'version', 'analysis']]

# Chuyển đổi nhãn 'benign' và 'malicious' thành 0 và 1
label_encoder = LabelEncoder()
data['analysis'] = label_encoder.fit_transform(data['analysis'])

# Chuyển đổi 'package' và 'version' thành dạng số
data['package'] = label_encoder.fit_transform(data['package'])
data['version'] = label_encoder.fit_transform(data['version'])

# Đặc trưng và nhãn
X = data[['package', 'version']]  # Các đặc trưng
y = data['analysis']  # Nhãn (benign: 0, malicious: 1)

# Khởi tạo các mô hình
models = {
    'Decision Tree': DecisionTreeClassifier(random_state=42),
    'Naive Bayes': GaussianNB(),
    'SVM': SVC(kernel='rbf', random_state=42, class_weight='balanced', C=1.0, gamma='scale')  # Đổi kernel sang RBF
}

# Sử dụng StratifiedKFold cho 10-fold cross-validation 
kf = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)

# Hàm đánh giá mô hình với precision và recall
for model_name, model in models.items():
    scores = cross_validate(model, X, y, cv=kf, 
                            scoring={'precision': make_scorer(precision_score), 
                                     'recall': make_scorer(recall_score)})
    
    # In kết quả cho từng mô hình
    print(f'[{model_name}]')
    print(f'Mean Precision: {scores["test_precision"].mean():.2f}')
    print(f'Mean Recall: {scores["test_recall"].mean():.2f}\n')
