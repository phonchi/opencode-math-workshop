# lab3_grad_check_experiments.py — MSE loss 與「grad 乘 2」的梯度檢查實驗
# 不修改 lab3_logistic.py 的 loss / grad
import numpy as np

# ---------- 資料（同 lab3_logistic.py） ----------
raw = np.genfromtxt("data/line_faults.csv", delimiter=",", names=True)
feature_names = ["temp_c", "vibration_mm_s", "pressure_kpa", "flow_lpm", "current_a", "speed_rpm"]
X_raw = np.column_stack([raw[name] for name in feature_names])
y = raw["fault"].astype(float)
n, d = X_raw.shape

mu = X_raw.mean(axis=0)
sd = X_raw.std(axis=0)
X = np.column_stack([(X_raw - mu) / sd, np.ones(n)])

def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -500, 500)))

# ---------- 梯度檢查（同一段：中央差分, h=1e-5） ----------
def grad_check(loss_fn, grad_fn):
    rng = np.random.default_rng(0)
    w_check = rng.normal(scale=0.5, size=d + 1)
    g = grad_fn(w_check)
    g_num = np.zeros_like(g)
    h = 1e-5
    for i in range(len(w_check)):
        wp, wm = w_check.copy(), w_check.copy()
        wp[i] += h
        wm[i] -= h
        g_num[i] = (loss_fn(wp) - loss_fn(wm)) / (2 * h)
    err = np.max(np.abs(g - g_num))
    return err

def report(name, err):
    print(f"{name}: max abs grad error = {err:.3e} -> {'PASS' if err < 1e-6 else 'FAIL'}")

# ---------- 實驗 A：MSE loss 與其正確梯度 ----------
# L = mean((sigma(z)-y)^2), dL/dw = 2 X^T (sigma(z)-y)*sigma(z)*(1-sigma(z)) / n
def loss_mse(w):
    return np.mean((sigmoid(X @ w) - y) ** 2)

def grad_mse(w):
    p = sigmoid(X @ w)
    return 2 * X.T @ ((p - y) * p * (1 - p)) / n

# ---------- 實驗 B：log-loss 不變，grad 乘 2 ----------
def loss_log(w):
    p = sigmoid(X @ w)
    eps = 1e-12
    return -np.mean(y * np.log(p + eps) + (1 - y) * np.log(1 - p + eps))

def grad_log_double(w):
    return 2 * X.T @ (sigmoid(X @ w) - y) / n

err_A = grad_check(loss_mse, grad_mse)
err_B = grad_check(loss_log, grad_log_double)
report("A (MSE loss + 正確梯度)", err_A)
report("B (log-loss + grad 乘 2)", err_B)
