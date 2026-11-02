import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

# 1. 載入資料並預處理
digits = load_digits()
mask = (digits.target == 3) | (digits.target == 8)
X = digits.data[mask]
y = (digits.target[mask] == 8).astype(int)

X_mean = X.mean(axis=0)
X_std = X.std(axis=0)
X_std[X_std == 0] = 1.0
X_scaled = (X - X_mean) / X_std

# 2. 定義成本函數與分析梯度 (修正 L2 正則化梯度中的 1/N 係數)
C = 1.0
n_samples = X_scaled.shape[0]

def cost_func(theta):
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

def grad_func(theta):
    w = theta[:-1]
    b = theta[-1]
    z = np.dot(X_scaled, w) + b
    z = np.clip(z, -500, 500)
    p = 1.0 / (1.0 + np.exp(-z))
    
    dw = (1 / n_samples) * np.dot(X_scaled.T, (p - y))
    if C:
        dw += (1.0 / (C * n_samples)) * w
    db = (1 / n_samples) * np.sum(p - y)
    
    return np.hstack([dw, db])

# 3. 設定檢查點 theta_0
rng = np.random.RandomState(0)
theta_0 = rng.normal(size=65) * 0.01

# 計算分析梯度
analytical_grad = grad_func(theta_0)

# 4. 步長 h 掃過 1e-2 到 1e-9，使用中央差分檢查全部 65 個維度
h_list = [10.0**(-i) for i in range(2, 10)]

print(f"{'h':<10} | {'Max Absolute Error':<20} | {'Max Relative Error':<20} | {'Status':<10}")
print("-" * 68)

for h in h_list:
    numerical_grad = np.zeros_like(theta_0)
    for j in range(len(theta_0)):
        theta_plus = theta_0.copy()
        theta_minus = theta_0.copy()
        theta_plus[j] += h
        theta_minus[j] -= h
        
        loss_plus = cost_func(theta_plus)
        loss_minus = cost_func(theta_minus)
        
        numerical_grad[j] = (loss_plus - loss_minus) / (2 * h)
    
    abs_diff = np.abs(numerical_grad - analytical_grad)
    max_abs_err = np.max(abs_diff)
    
    # 相對誤差分母至少取 1e-12
    denom = np.maximum(np.maximum(np.abs(numerical_grad), np.abs(analytical_grad)), 1e-12)
    max_rel_err = np.max(abs_diff / denom)
    
    status = "PASS" if max_abs_err < 1e-8 else "INVESTIGATE"
    
    print(f"{h:<10.0e} | {max_abs_err:<20.2e} | {max_rel_err:<20.2e} | {status:<10}")
