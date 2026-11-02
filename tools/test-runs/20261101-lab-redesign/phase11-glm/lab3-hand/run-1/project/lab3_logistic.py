# lab3_logistic.py — numpy 手刻 logistic 迴歸（無正則化）
import numpy as np

# ---------- 資料 ----------
raw = np.genfromtxt("data/line_faults.csv", delimiter=",", names=True)
feature_names = ["temp_c", "vibration_mm_s", "pressure_kpa", "flow_lpm", "current_a", "speed_rpm"]
X_raw = np.column_stack([raw[name] for name in feature_names])
y = raw["fault"].astype(float)
n, d = X_raw.shape

# ---------- 標準化 + 截距 ----------
mu = X_raw.mean(axis=0)
sd = X_raw.std(axis=0)
X_std = (X_raw - mu) / sd
X = np.column_stack([X_std, np.ones(n)])  # 最後一欄 1 當截距
w = np.zeros(d + 1)

# ---------- loss / gradient ----------
def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -500, 500)))

def loss(w):
    p = sigmoid(X @ w)
    eps = 1e-12
    return -np.mean(y * np.log(p + eps) + (1 - y) * np.log(1 - p + eps))

def grad(w):
    return X.T @ (sigmoid(X @ w) - y) / n

# ---------- 梯度檢查（中央差分） ----------
# 檢查點：故意取一個非零的 w（每個維度都發揮作用），而不是全零。
# 全零時 p=0.5 對所有樣本，梯度各分量會互相抵消得較「平淡」，測不出 scale 問題。
# 步長：h=1e-5。中央差分誤差 O(h^2) ≈ 1e-10 量級，但 float64 在 1e-5 時
# 捨入誤差約 1e-11/(2e-5)~1e-6 量級，兩者平衡；太小(1e-8以下)會被浮點捨入主導，
# 太大(1e-3以上)會有 O(h^2) 偏誤，1e-5 是常見甜點區。
rng = np.random.default_rng(0)
w_check = rng.normal(scale=0.5, size=d + 1)

g = grad(w_check)
g_num = np.zeros_like(g)
h = 1e-5
for i in range(len(w_check)):
    wp, wm = w_check.copy(), w_check.copy()
    wp[i] += h
    wm[i] -= h
    g_num[i] = (loss(wp) - loss(wm)) / (2 * h)

max_err = np.max(np.abs(g - g_num))
tol = 1e-6
print("max abs grad error =", max_err)
print("PASS" if max_err < tol else "FAIL")

# ---------- 訓練（全批次梯度下降） ----------
lr = 0.1
for it in range(20000):
    w -= lr * grad(w)
    if it % 5000 == 0:
        print(f"iter {it:5d}  loss = {loss(w):.6f}")

print("final loss =", loss(w))
print("weights =", np.round(w, 4))
acc = np.mean((sigmoid(X @ w) >= 0.5) == (y == 1))
print("train accuracy =", acc)
