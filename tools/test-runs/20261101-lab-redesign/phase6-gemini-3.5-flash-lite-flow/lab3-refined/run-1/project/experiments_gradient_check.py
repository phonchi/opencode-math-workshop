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

C_val = 1.0
n_samples = X_train_scaled.shape[0]

def sigmoid(z):
    z = np.clip(z, -500, 500)
    return 1.0 / (1.0 + np.exp(-z))

# 設置檢查點 w0 (65維)
np.random.seed(0)
w0 = np.random.RandomState(0).normal(size=65) * 0.01
h_list = [1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8, 1e-9]

print("="*60)
print("實驗 A: 均方誤差 (MSE) Loss 與正確梯度")
print("="*60)
print("| Step size ($h$) | Max Absolute Error | Status |")
print("|-----------------|--------------------|--------|")

def compute_loss_mse(params, X, y):
    weights = params[:-1]
    bias = params[-1]
    linear_pred = np.dot(X, weights) + bias
    predictions = sigmoid(linear_pred)
    mse_loss = np.mean((predictions - y) ** 2)
    l2_loss = 0.5 * np.sum(weights ** 2) / (C_val * n_samples)
    return mse_loss + l2_loss

def compute_analytic_gradient_mse(params, X, y):
    weights = params[:-1]
    bias = params[-1]
    linear_pred = np.dot(X, weights) + bias
    predictions = sigmoid(linear_pred)
    
    # MSE 搭配 sigmoid 的梯度： dJ/dz = (2/N) * (y_hat - y) * y_hat * (1 - y_hat)
    error_term = (2 / n_samples) * (predictions - y) * predictions * (1 - predictions)
    dw = np.dot(X.T, error_term) + (1.0 / C_val) * (weights / n_samples)
    db = np.sum(error_term)
    return np.append(dw, db)

ana_grad_mse = compute_analytic_gradient_mse(w0, X_train_scaled, y_train)

for h in h_list:
    num_grad = np.zeros_like(w0)
    for j in range(len(w0)):
        w_plus = w0.copy()
        w_minus = w0.copy()
        w_plus[j] += h
        w_minus[j] -= h
        
        loss_plus = compute_loss_mse(w_plus, X_train_scaled, y_train)
        loss_minus = compute_loss_mse(w_minus, X_train_scaled, y_train)
        num_grad[j] = (loss_plus - loss_minus) / (2 * h)
        
    max_abs_err = np.max(np.abs(ana_grad_mse - num_grad))
    status = "PASS" if max_abs_err < 1e-8 else "FAIL"
    print(f"| {h:e} | {max_abs_err:.4e} | {status} |")


print("\n" + "="*60)
print("實驗 B: 原本 Loss，但解析梯度乘以 2 (grad * 2)")
print("="*60)
print("| Step size ($h$) | Max Absolute Error | Status |")
print("|-----------------|--------------------|--------|")

def compute_loss_bce(params, X, y):
    weights = params[:-1]
    bias = params[-1]
    linear_pred = np.dot(X, weights) + bias
    predictions = sigmoid(linear_pred)
    epsilon = 1e-15
    predictions = np.clip(predictions, epsilon, 1 - epsilon)
    bce_loss = -np.mean(y * np.log(predictions) + (1 - y) * np.log(1 - predictions))
    l2_loss = 0.5 * np.sum(weights ** 2) / (C_val * n_samples)
    return bce_loss + l2_loss

def compute_analytic_gradient_bce_times2(params, X, y):
    weights = params[:-1]
    bias = params[-1]
    linear_pred = np.dot(X, weights) + bias
    predictions = sigmoid(linear_pred)
    
    dw = (1 / n_samples) * np.dot(X.T, (predictions - y)) + (1.0 / C_val) * (weights / n_samples)
    db = (1 / n_samples) * np.sum(predictions - y)
    
    # 刻意乘以 2
    return 2.0 * np.append(dw, db)

ana_grad_bce2 = compute_analytic_gradient_bce_times2(w0, X_train_scaled, y_train)

for h in h_list:
    num_grad = np.zeros_like(w0)
    for j in range(len(w0)):
        w_plus = w0.copy()
        w_minus = w0.copy()
        w_plus[j] += h
        w_minus[j] -= h
        
        loss_plus = compute_loss_bce(w_plus, X_train_scaled, y_train)
        loss_minus = compute_loss_bce(w_minus, X_train_scaled, y_train)
        num_grad[j] = (loss_plus - loss_minus) / (2 * h)
        
    max_abs_err = np.max(np.abs(ana_grad_bce2 - num_grad))
    status = "PASS" if max_abs_err < 1e-8 else "FAIL"
    print(f"| {h:e} | {max_abs_err:.4e} | {status} |")
