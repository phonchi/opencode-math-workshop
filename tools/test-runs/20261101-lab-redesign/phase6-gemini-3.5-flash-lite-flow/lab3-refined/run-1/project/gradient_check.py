import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# 1. 載入資料並標準化
digits = load_digits()
mask = (digits.target == 3) | (digits.target == 8)
X = digits.data[mask]
y = (digits.target[mask] == 8).astype(int)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

# 2. 定義損失函數與解析梯度（吃 65 維參數向量：前 64 維為 weights，最後 1 維為 bias）
C_val = 1.0
n_samples = X_train_scaled.shape[0]

def sigmoid(z):
    z = np.clip(z, -500, 500)
    return 1.0 / (1.0 + np.exp(-z))

def compute_loss(params, X, y):
    weights = params[:-1]
    bias = params[-1]
    linear_pred = np.dot(X, weights) + bias
    predictions = sigmoid(linear_pred)
    
    epsilon = 1e-15
    predictions = np.clip(predictions, epsilon, 1 - epsilon)
    
    bce_loss = -np.mean(y * np.log(predictions) + (1 - y) * np.log(1 - predictions))
    l2_loss = 0.5 * np.sum(weights ** 2) / (C_val * n_samples)
    return bce_loss + l2_loss

def compute_analytic_gradient(params, X, y):
    weights = params[:-1]
    bias = params[-1]
    linear_pred = np.dot(X, weights) + bias
    predictions = sigmoid(linear_pred)
    
    dw = (1 / n_samples) * np.dot(X.T, (predictions - y)) + (1.0 / C_val) * (weights / n_samples)
    db = (1 / n_samples) * np.sum(predictions - y)
    
    return np.append(dw, db)

# 3. 設置檢查點 w0 (65維)
np.random.seed(0)
w0 = np.random.RandomState(0).normal(size=65) * 0.01

# 計算解析梯度
ana_grad = compute_analytic_gradient(w0, X_train_scaled, y_train)

# 4. 步長 h 掃過 1e-2 到 1e-9
h_list = [1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8, 1e-9]

print("| Step size ($h$) | Max Absolute Error | Max Relative Error | Status |")
print("|-----------------|--------------------|--------------------|--------|")

for h in h_list:
    num_grad = np.zeros_like(w0)
    # 中央差分檢查全部 65 個維度
    for j in range(len(w0)):
        w_plus = w0.copy()
        w_minus = w0.copy()
        w_plus[j] += h
        w_minus[j] -= h
        
        loss_plus = compute_loss(w_plus, X_train_scaled, y_train)
        loss_minus = compute_loss(w_minus, X_train_scaled, y_train)
        
        num_grad[j] = (loss_plus - loss_minus) / (2 * h)
        
    abs_errors = np.abs(ana_grad - num_grad)
    max_abs_err = np.max(abs_errors)
    
    denom = np.maximum(np.maximum(np.abs(ana_grad), np.abs(num_grad)), 1e-12)
    rel_errors = abs_errors / denom
    max_rel_err = np.max(rel_errors)
    
    status = "PASS" if max_abs_err < 1e-8 else "INVESTIGATE"
    print(f"| {h:e} | {max_abs_err:.4e} | {max_rel_err:.4e} | {status} |")
