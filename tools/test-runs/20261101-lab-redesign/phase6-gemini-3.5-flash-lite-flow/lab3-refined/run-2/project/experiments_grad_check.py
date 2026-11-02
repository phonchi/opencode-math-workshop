import numpy as np
from sklearn.datasets import load_digits

# 載入資料並預處理
digits = load_digits()
mask = (digits.target == 3) | (digits.target == 8)
X = digits.data[mask]
y = (digits.target[mask] == 8).astype(int)

X_mean = X.mean(axis=0)
X_std = X.std(axis=0)
X_std[X_std == 0] = 1.0
X_scaled = (X - X_mean) / X_std
n_samples = X_scaled.shape[0]

rng = np.random.RandomState(0)
theta_0 = rng.normal(size=65) * 0.01
h = 1e-5  # 使用數值誤差最小的典型步長進行快速準確檢查

print("=== 實驗 A：MSE Loss 與其正確梯度 ===")

def cost_mse(theta):
    w = theta[:-1]
    b = theta[-1]
    z = np.dot(X_scaled, w) + b
    z = np.clip(z, -500, 500)
    p = 1.0 / (1.0 + np.exp(-z))
    return np.mean((p - y) ** 2)

def grad_mse(theta):
    w = theta[:-1]
    b = theta[-1]
    z = np.dot(X_scaled, w) + b
    z = np.clip(z, -500, 500)
    p = 1.0 / (1.0 + np.exp(-z))
    
    # d(MSE)/dz = 2 * (p - y) * p * (1 - p) / N
    factor = (2.0 / n_samples) * (p - y) * p * (1.0 - p)
    dw = np.dot(X_scaled.T, factor)
    db = np.sum(factor)
    return np.hstack([dw, db])

ana_grad_a = grad_mse(theta_0)
num_grad_a = np.zeros_like(theta_0)
for j in range(len(theta_0)):
    tp, tm = theta_0.copy(), theta_0.copy()
    tp[j] += h
    tm[j] -= h
    num_grad_a[j] = (cost_mse(tp) - cost_mse(tm)) / (2 * h)

max_abs_err_a = np.max(np.abs(num_grad_a - ana_grad_a))
status_a = "PASS" if max_abs_err_a < 1e-8 else "FAIL"
print(f"h = {h:.0e} | Max Absolute Error: {max_abs_err_a:.2e} | Status: {status_a}")


print("\n=== 實驗 B：原 Loss 不變，但梯度乘以 2 ===")

C = 1.0
def cost_original(theta):
    w = theta[:-1]
    b = theta[-1]
    z = np.dot(X_scaled, w) + b
    z = np.clip(z, -500, 500)
    p = 1.0 / (1.0 + np.exp(-z))
    eps = 1e-15
    p = np.clip(p, eps, 1 - eps)
    bce = -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))
    l2_reg = 0.5 * (1.0 / (C * n_samples)) * np.sum(w ** 2) if C else 0.0
    return bce + l2_reg

def grad_original_times_2(theta):
    w = theta[:-1]
    b = theta[-1]
    z = np.dot(X_scaled, w) + b
    z = np.clip(z, -500, 500)
    p = 1.0 / (1.0 + np.exp(-z))
    
    dw = (1 / n_samples) * np.dot(X_scaled.T, (p - y))
    if C:
        dw += (1.0 / (C * n_samples)) * w
    db = (1 / n_samples) * np.sum(p - y)
    
    # 刻意乘以 2
    return 2.0 * np.hstack([dw, db])

ana_grad_b = grad_original_times_2(theta_0)
num_grad_b = np.zeros_like(theta_0)
for j in range(len(theta_0)):
    tp, tm = theta_0.copy(), theta_0.copy()
    tp[j] += h
    tm[j] -= h
    num_grad_b[j] = (cost_original(tp) - cost_original(tm)) / (2 * h)

max_abs_err_b = np.max(np.abs(num_grad_b - ana_grad_b))
status_b = "PASS" if max_abs_err_b < 1e-8 else "FAIL"
print(f"h = {h:.0e} | Max Absolute Error: {max_abs_err_b:.2e} | Status: {status_b}")
