"""手刻二元 logistic 迴歸（digits 的 3 與 8）。

損失   L(w) = (1/n) Σ [log(1+e^z) - y z],  z = X w
梯度   ∇L(w) = (1/n) X^T (σ(Xw) - y)

流程：中央差分全 65 維梯度檢查（h=1e-2..1e-9）-> 梯度下降訓練（lr=0.5, 20000 次）
      -> 與 sklearn LogisticRegression(C=np.inf) 比對。截距折進 w（X 加一欄 1）。
"""
import numpy as np
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

rng = np.random.RandomState(0)


def sigmoid(z):
    out = np.empty_like(z)
    pos = z >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    out[~pos] = np.exp(z[~pos]) / (1.0 + np.exp(z[~pos]))
    return out


def loss(w, X, y):
    z = X @ w
    return np.mean(np.logaddexp(0.0, z) - y * z)


def grad(w, X, y):
    z = X @ w
    return (X.T @ (sigmoid(z) - y)) / len(y)


def finite_diff_grad(loss_fn, w, h):
    g = np.empty_like(w)
    for j in range(w.size):
        e = np.zeros_like(w)
        e[j] = 1.0
        g[j] = (loss_fn(w + h * e) - loss_fn(w - h * e)) / (2.0 * h)
    return g


# ---------- 資料：digits 的 3 與 8，y=1 代表 8 ----------
digits = load_digits()
mask = (digits.target == 3) | (digits.target == 8)
X = digits.data[mask]
y = (digits.target[mask] == 8).astype(float)

X_b = np.hstack([np.ones((len(X), 1)), X])  # 折進截距後共 65 維
n, d = X_b.shape
print(f"樣本數 n = {n}, 維度 d = {d}（64 特徵 + 1 截距）\n")

X_tr, X_te, y_tr, y_te = train_test_split(
    X_b, y, test_size=0.3, random_state=0
)
print(f"train = {len(y_tr)} 筆, test = {len(y_te)} 筆\n")


# ---------- 1. 有限差分梯度檢查（中央差分，全部 65 維） ----------
print("=" * 88)
print("1. 有限差分梯度檢查（中央差分，全部 65 維）")
print(f"{'h':>9} {'檢查點':>10} {'最大絕對誤差':>18} {'最大相對誤差':>18}")
print("=" * 88)

for name, w0 in [("w=0", np.zeros(d)), ("隨機 w", rng.randn(d) * 0.5)]:
    g_anal = grad(w0, X_tr, y_tr)
    for h in np.logspace(-2, -9, 8):
        g_num = finite_diff_grad(lambda w: loss(w, X_tr, y_tr), w0, h)
        abs_err = np.max(np.abs(g_num - g_anal))
        denom = np.maximum(np.abs(g_anal), 1e-12)
        rel_err = np.max(np.abs(g_num - g_anal) / denom)
        print(f"{h:9.1e} {name:>10} {abs_err:18.3e} {rel_err:18.3e}")


# ---------- 2. 梯度下降訓練（lr=0.5, 20000 次） ----------
print("\n" + "=" * 88)
print("2. 梯度下降訓練（lr = 0.5, 20000 次）")
print(f"{'iteration':>10} {'||w||':>16} {'loss':>14}")
print("=" * 88)

lr = 0.5
T = 20000
w = np.zeros(d)
checkpoints = {100, 1000, 5000, 10000, 20000}
for t in range(1, T + 1):
    w = w - lr * grad(w, X_tr, y_tr)
    if t in checkpoints:
        print(f"{t:10d} {np.linalg.norm(w):16.6f} {loss(w, X_tr, y_tr):14.6f}")

# ---------- 3. 與 sklearn LogisticRegression 比對 ----------
print("\n" + "=" * 88)
print("3. 與 sklearn LogisticRegression(C=np.inf, fit_intercept=False) 比對")
print("=" * 88)

ref = LogisticRegression(
    C=np.inf, fit_intercept=False, solver="lbfgs", max_iter=20000, random_state=0
)
ref.fit(X_tr, y_tr)
w_sk = ref.coef_.ravel()

acc_hand_tr = np.mean((sigmoid(X_tr @ w) >= 0.5).astype(float) == y_tr)
acc_hand_te = np.mean((sigmoid(X_te @ w) >= 0.5).astype(float) == y_te)
acc_sk_tr = ref.score(X_tr, y_tr)
acc_sk_te = ref.score(X_te, y_te)

print(f"\n手刻   train acc = {acc_hand_tr:.4f}, test acc = {acc_hand_te:.4f}")
print(f"sklearn train acc = {acc_sk_tr:.4f}, test acc = {acc_sk_te:.4f}")
print(f"準確率完全一致？ {acc_hand_tr == acc_sk_tr and acc_hand_te == acc_sk_te}")

print(f"\n||w_hand||      = {np.linalg.norm(w):.4f}")
print(f"||w_sklearn||   = {np.linalg.norm(w_sk):.4f}")
print(f"||w_hand - w_sk||   = {np.linalg.norm(w - w_sk):.4e}")
cos = np.dot(w, w_sk) / (np.linalg.norm(w) * np.linalg.norm(w_sk))
print(f"cos(w_hand, w_sk)   = {cos:.6f}")