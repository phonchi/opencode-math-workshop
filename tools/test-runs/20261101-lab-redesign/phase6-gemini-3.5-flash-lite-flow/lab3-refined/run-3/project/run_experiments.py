import numpy as np
from sklearn.datasets import load_digits
from sklearn.preprocessing import StandardScaler

# 1. 準備資料與檢查點 w0 (共 65 維)
digits = load_digits()
X_all = digits.data
y_all = digits.target
mask = (y_all == 3) | (y_all == 8)
X = X_all[mask]
y = np.where(y_all[mask] == 8, 1, 0)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
m, d = X_scaled.shape

rng = np.random.RandomState(0)
w0 = rng.normal(size=d + 1) * 0.01

# 原始 BCE Loss 與 Gradient 函數
def compute_bce(params, X, y):
    m = X.shape[0]
    w = params[:-1]
    b = params[-1]
    z = np.clip(np.dot(X, w) + b, -500, 500)
    eps = 1e-15
    y_pred = np.clip(1.0 / (1.0 + np.exp(-z)), eps, 1 - eps)
    cost = -np.mean(y * np.log(y_pred) + (1 - y) * np.log(1 - y_pred))
    
    grad_w = np.dot(X.T, (y_pred - y)) / m
    grad_b = np.sum(y_pred - y) / m
    grad = np.append(grad_w, grad_b)
    return cost, grad

# 實驗 A: MSE Loss 與正確梯度
def compute_mse_experiment(params, X, y):
    m = X.shape[0]
    w = params[:-1]
    b = params[-1]
    z = np.clip(np.dot(X, w) + b, -500, 500)
    y_pred = 1.0 / (1.0 + np.exp(-z))
    
    # Loss = mean((y_pred - y)^2)
    cost = np.mean((y_pred - y) ** 2)
    
    # 正確的梯度
    # d(Loss)/dz = 2/m * (y_pred - y) * y_pred * (1 - y_pred)
    dz = (2.0 / m) * (y_pred - y) * y_pred * (1.0 - y_pred)
    grad_w = np.dot(X.T, dz)
    grad_b = np.sum(dz)
    grad = np.append(grad_w, grad_b)
    return cost, grad

# 實驗 B: Loss 不變 (BCE)，但 grad 乘以 2
def compute_bce_double_grad(params, X, y):
    cost, grad = compute_bce(params, X, y)
    grad = 2.0 * grad
    return cost, grad

# 梯度檢查函數 (使用中央差分，h = 1e-5)
def gradient_check(cost_grad_func, name, h=1e-5):
    cost, grad_analytic = cost_grad_func(w0, X_scaled, y)
    
    grad_numeric = np.zeros_like(w0)
    for j in range(len(w0)):
        p_plus = w0.copy()
        p_plus[j] += h
        c_plus, _ = cost_grad_func(p_plus, X_scaled, y)
        
        p_minus = w0.copy()
        p_minus[j] -= h
        c_minus, _ = cost_grad_func(p_minus, X_scaled, y)
        
        grad_numeric[j] = (c_plus - c_minus) / (2 * h)
        
    max_abs_err = np.max(np.abs(grad_analytic - grad_numeric))
    status = "PASS" if max_abs_err < 1e-8 else "FAIL"
    
    print(f"實驗 {name}: 最大絕對誤差 = {max_abs_err:.4e} -> 狀態: {status}")

print("=== 執行實驗 A 與實驗 B 梯度檢查 (h = 1e-5) ===")
gradient_check(compute_mse_experiment, "A (MSE Loss & Correct Grad)")
gradient_check(compute_bce_double_grad, "B (BCE Loss & 2 * Grad)")
