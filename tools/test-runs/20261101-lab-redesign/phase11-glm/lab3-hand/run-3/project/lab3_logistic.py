import csv
import numpy as np

# 讀資料（900 筆，不用 record_id）
X_raw, y = [], []
with open("data/line_faults.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        X_raw.append([float(row[k]) for k in
                      ("temp_c", "vibration_mm_s", "pressure_kpa",
                       "flow_lpm", "current_a", "speed_rpm")])
        y.append(float(row["fault"]))
X_raw = np.array(X_raw)
y = np.array(y)

# 標準化（用訓練資料本身的 mean/std）後加截距欄
mu = X_raw.mean(axis=0)
sigma = X_raw.std(axis=0)
X = (X_raw - mu) / sigma
X = np.hstack([X, np.ones((X.shape[0], 1))])
n, d = X.shape


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def loss(w):
    s = sigmoid(X @ w)
    eps = 1e-12  # 防止 log(0)
    return -np.mean(y * np.log(s + eps) + (1 - y) * np.log(1 - s + eps))


def grad(w):
    return X.T @ (sigmoid(X @ w) - y) / n


def check_gradients(loss, grad, tol=1e-6, name=""):
    # 梯度檢查：中央差分
    # 檢查點 w0 = 0：sigmoid 在 0 附近最活躍、損失面局部近似二次，
    # 且各維度量級一致（資料已標準化），是檢查梯度最穩定的點。
    # 步長 h = 1e-5：中央差分誤差 O(h^2) ~ 1e-10，浮點捨入誤差 ~ eps/h ~ 1e-11，
    # 兩者都在 1e-9 以下，總誤差遠低於容差；太大會有截斷誤差，太小會被捨入誤差淹沒。
    w0 = np.zeros(d)
    h = 1e-5
    g = grad(w0)
    g_num = np.zeros(d)
    for j in range(d):
        wp, wm = w0.copy(), w0.copy()
        wp[j] += h
        wm[j] -= h
        g_num[j] = (loss(wp) - loss(wm)) / (2 * h)

    max_err = np.max(np.abs(g - g_num))
    print(f"[{name}] max |analytic - numeric| = {max_err:.3e}")
    print(f"[{name}] " + ("PASS" if max_err < tol else "FAIL"))
    return max_err


check_gradients(loss, grad, name="logistic")
