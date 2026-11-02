import numpy as np
from sklearn.datasets import load_digits
from sklearn.preprocessing import StandardScaler

# 1. 準備資料與檢查點 w0 (共 65 維: 64 個特徵權重 + 1 個截距)
digits = load_digits()
X_all = digits.data
y_all = digits.target
mask = (y_all == 3) | (y_all == 8)
X = X_all[mask]
y = np.where(y_raw := y_all[mask] == 8, 1, 0) # 修正 y 賦值

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
m, d = X_scaled.shape

# 檢查點 w0: 65 維 (64 個 w + 1 個 b)
rng = np.random.RandomState(0)
w0 = rng.normal(size=d + 1) * 0.01

def compute_cost_and_grad(params, X, y, C=1.0):
    m = X.shape[0]
    w = params[:-1]
    b = params[-1]
    
    z = np.clip(np.dot(X, w) + b, -500, 500)
    eps = 1e-15
    y_pred = np.clip(1.0 / (1.0 + np.exp(-z)), eps, 1 - eps)
    
    # Loss (Binary Cross Entropy + L2 regularization)
    cost = -np.mean(y * np.log(y_pred) + (1 - y) * np.log(1 - y_pred))
    if C is not None and C > 0:
        cost += 0.5 / (C * m) * np.sum(w ** 2)
        
    # Analytical Gradients
    grad_w = np.dot(X.T, (y_pred - y)) / m
    if C is not None and C > 0:
        grad_w += (1.0 / (C * m)) * w
    grad_b = np.sum(y_pred - y) / m
    
    grad = np.append(grad_w, grad_b)
    return cost, grad

# 計算解析梯度 (Analytical Gradient)
_, grad_analytic = compute_cost_and_grad(w0, X_scaled, y, C=1.0)

# 2. 掃過 h 從 1e-2 到 1e-9 的中央差分梯度檢查
h_list = [1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8, 1e-9]

print("=" * 75)
print(f"{'h 步長':<12} | {'最大絕對誤差 (Max Abs Err)':<22} | {'最大相對誤差 (Max Rel Err)':<22} | {'狀態 (Status)':<10}")
print("-" * 75)

results = []
for h in h_list:
    grad_numeric = np.zeros_like(w0)
    for j in range(len(w0)):
        params_plus = w0.copy()
        params_plus[j] += h
        cost_plus, _ = compute_cost_and_grad(params_plus, X_scaled, y, C=1.0)
        
        params_minus = w0.copy()
        params_minus[j] -= h
        cost_minus, _ = compute_cost_and_grad(params_minus, X_scaled, y, C=1.0)
        
        grad_numeric[j] = (cost_plus - cost_minus) / (2 * h)
        
    abs_errs = np.abs(grad_analytic - grad_numeric)
    max_abs_err = np.max(abs_errs)
    
    # 相對誤差分母至少取 1e-12
    denominators = np.maximum(np.maximum(np.abs(grad_analytic), np.abs(grad_numeric)), 1e-12)
    rel_errs = abs_errs / denominators
    max_rel_err = np.max(rel_errs)
    
    status = "PASS" if max_abs_err < 1e-8 else "INVESTIGATE"
    results.append((h, max_abs_err, max_rel_err, status))
    
    print(f"{h:<12.0e} | {max_abs_err:<22.4e} | {max_rel_err:<22.4e} | {status:<10}")

print("=" * 75)
