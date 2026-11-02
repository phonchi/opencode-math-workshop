"""手刻 logistic 迴歸：digits 3 vs 8，與 sklearn 比較。

手刻部分使用與 sklearn 預設一致的 L2 正則化（C=1），
以 batch gradient descent 求解，避免資料可分離時 MLE 發散。
"""
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix

# ---------- 資料 ----------
digits = load_digits()
mask = (digits.target == 3) | (digits.target == 8)
X = digits.data[mask].astype(float)
y = (digits.target[mask] == 8).astype(int)  # 1=8, 0=3

Xtr, Xte, ytr, yte = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)
scaler = StandardScaler()
Xtr_s = scaler.fit_transform(Xtr)
Xte_s = scaler.transform(Xte)

# ---------- 數值工具 ----------
def sigmoid(z):
    out = np.empty_like(z, dtype=float)
    pos = z >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    ez = np.exp(z[~pos])
    out[~pos] = ez / (1.0 + ez)
    return out

# ---------- 手刻 logistic 迴歸（L2, C=1，batch gradient descent） ----------
class HandLogistic:
    def __init__(self, lr=0.5, n_iter=50000, tol=1e-12):
        self.lr = lr
        self.n_iter = n_iter
        self.tol = tol

    def fit(self, X, y):
        n, d = X.shape
        Xb = np.column_stack([np.ones(n), X])
        self.w = np.zeros(d + 1)  # [b, w1..wd]
        self.losses = []
        prev = np.inf
        for i in range(self.n_iter):
            z = Xb @ self.w
            p = sigmoid(z)
            # 目標：0.5*||w||^2 + sum logloss；梯度（含 bias 不正則化）
            g = np.zeros(d + 1)
            g[0] = Xb[:, 0] @ (p - y)
            g[1:] = self.w[1:] + Xb[:, 1:].T @ (p - y)
            self.w -= self.lr * g / n
            # loss
            eps = 1e-12
            nll = -np.mean(y * np.log(p + eps) + (1 - y) * np.log(1 - p + eps))
            reg = 0.5 * np.dot(self.w[1:], self.w[1:]) / n
            loss = nll + reg
            self.losses.append(loss)
            if abs(prev - loss) < self.tol:
                break
            prev = loss
        self.n_iter_used = len(self.losses)
        return self

    def predict_proba(self, X):
        Xb = np.column_stack([np.ones(len(X)), X])
        return sigmoid(Xb @ self.w)

    def predict(self, X):
        return (self.predict_proba(X) >= 0.5).astype(int)

hand = HandLogistic(lr=0.5, n_iter=50000, tol=1e-14)
hand.fit(Xtr_s, ytr)

# ---------- sklearn ----------
sk = LogisticRegression(l1_ratio=0, C=1.0, solver="lbfgs",
                        max_iter=100000, tol=1e-12)
sk.fit(Xtr_s, ytr)

# ---------- 比較 ----------
wh, bh = hand.w[1:], hand.w[0]
ws, bs = sk.coef_.ravel(), sk.intercept_[0]

print("=== 係數比較 ===")
print("iterations used (hand):", hand.n_iter_used)
print("max |w_hand - w_sk| =", np.max(np.abs(wh - ws)))
print(" |b_hand - b_sk|    =", abs(bh - bs))
print("corr(w_hand, w_sk)  =", np.corrcoef(wh, ws)[0, 1])
print()
ph = hand.predict(Xte_s)
ps = sk.predict(Xte_s)
print("=== 預測一致率 (test) ===")
print("prediction agreement:", np.mean(ph == ps))
print("hand acc:", accuracy_score(yte, ph))
print("sk   acc:", accuracy_score(yte, ps))
print()
print("=== 機率差 (test) ===")
print("max |p_hand - p_sk| =", np.max(np.abs(hand.predict_proba(Xte_s) - sk.predict_proba(Xte_s)[:, 1])))
print()
print("confusion hand:\n", confusion_matrix(yte, ph))
print("confusion sk:\n", confusion_matrix(yte, ps))

# ---------- 有限差分梯度檢查（65 維全檢） ----------
def _loss_at(w, Xb, y):
    n = len(y)
    z = Xb @ w
    p = sigmoid(z)
    eps = 1e-12
    nll = -np.mean(y * np.log(p + eps) + (1 - y) * np.log(1 - p + eps))
    reg = 0.5 * np.dot(w[1:], w[1:]) / n
    return nll + reg


def _grad_at(w, Xb, y):
    n = len(y)
    z = Xb @ w
    p = sigmoid(z)
    g = np.zeros_like(w)
    g[0] = Xb[:, 0] @ (p - y)
    g[1:] = w[1:] + Xb[:, 1:].T @ (p - y)
    return g / n


rng = np.random.RandomState(0)
w0 = rng.normal(size=65) * 0.01
Xb_tr = np.column_stack([np.ones(len(ytr)), Xtr_s])
g_anal = _grad_at(w0, Xb_tr, ytr)

print("=== 有限差分梯度檢查 (65 維) ===")
print(f"{'h':>10} {'max_abs_err':>14} {'max_rel_err':>14} {'status':>6}")
for h in np.logspace(-2, -9, 8):
    g_fd = np.zeros(65)
    for i in range(65):
        wp = w0.copy()
        wm = w0.copy()
        wp[i] += h
        wm[i] -= h
        g_fd[i] = (_loss_at(wp, Xb_tr, ytr) - _loss_at(wm, Xb_tr, ytr)) / (2 * h)
    abs_err = np.abs(g_fd - g_anal)
    rel_err = abs_err / np.maximum(np.maximum(np.abs(g_anal), np.abs(g_fd)), 1e-12)
    max_abs = float(np.max(abs_err))
    max_rel = float(np.max(rel_err))
    status = "PASS" if max_abs < 1e-8 else "需調查"
    print(f"{h:10.0e} {max_abs:14.3e} {max_rel:14.3e} {status:>6}")

# ---------- 圖 ----------
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(hand.losses)
ax.set_xlabel("iteration")
ax.set_ylabel("regularized NLL")
ax.set_title("Hand logistic regression (L2) training loss")
fig.tight_layout()
fig.savefig("figs/logistic_loss.png", dpi=120)
plt.close(fig)

fig, ax = plt.subplots(figsize=(6, 6))
ax.scatter(wh, ws, s=12)
lim = max(np.max(np.abs(wh)), np.max(np.abs(ws))) * 1.05
ax.plot([-lim, lim], [-lim, lim], "k--", alpha=0.5)
ax.set_xlabel("hand weight")
ax.set_ylabel("sklearn weight")
ax.set_title("Coefficients: hand vs sklearn")
fig.tight_layout()
fig.savefig("figs/logistic_coef.png", dpi=120)
plt.close(fig)

np.savez("figs/logistic_result.npz",
         w_hand=wh, b_hand=bh, w_sk=ws, b_sk=bs,
         losses=np.array(hand.losses))
# ---------- 實驗 A：MSE loss + 正確梯度 ----------
def _loss_mse(w, Xb, y):
    p = sigmoid(Xb @ w)
    return float(np.mean((p - y) ** 2))


def _grad_mse(w, Xb, y):
    n = len(y)
    p = sigmoid(Xb @ w)
    return (2.0 / n) * (Xb.T @ ((p - y) * p * (1.0 - p)))


def _run_check(loss_fn, grad_fn, label):
    g_anal = grad_fn(w0, Xb_tr, ytr)
    print(f"=== 實驗 {label} ===")
    print(f"{'h':>10} {'max_abs_err':>14} {'status':>6}")
    for h in np.logspace(-2, -9, 8):
        g_fd = np.zeros(65)
        for i in range(65):
            wp = w0.copy()
            wm = w0.copy()
            wp[i] += h
            wm[i] -= h
            g_fd[i] = (loss_fn(wp, Xb_tr, ytr) - loss_fn(wm, Xb_tr, ytr)) / (2 * h)
        max_abs = float(np.max(np.abs(g_fd - g_anal)))
        status = "PASS" if max_abs < 1e-8 else "FAIL"
        print(f"{h:10.0e} {max_abs:14.3e} {status:>6}")


_run_check(_loss_mse, _grad_mse, "A (MSE loss + correct grad)")

# ---------- 實驗 B：loss 不變，grad 乘以 2 ----------
def _grad_x2(w, Xb, y):
    return 2.0 * _grad_at(w, Xb, y)


_run_check(_loss_at, _grad_x2, "B (original loss, grad x2)")

print("done")
