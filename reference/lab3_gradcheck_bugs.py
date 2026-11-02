"""Lab 3 講師備援：梯度檢查能證明什麼，不能證明什麼。

所有錯誤都是講師注入，不是 AI 自己犯的。
"""
import numpy as np
from sklearn.datasets import load_digits

X, y = load_digits(return_X_y=True)
m = (y == 3) | (y == 8)
A = X[m] / 16.0
t = (y[m] == 8).astype(float)
Xb = np.c_[A, np.ones(len(A))]
n = len(t)
w0 = np.random.RandomState(0).normal(size=65) * 0.01
sig = lambda z: 1 / (1 + np.exp(-z))


def loss(w):
    z = Xb @ w
    return np.mean(np.logaddexp(0, z) - t * z)


def grad(w):
    return Xb.T @ (sig(Xb @ w) - t) / n


def mse(w):
    return np.mean((sig(Xb @ w) - t) ** 2)


def mse_grad(w):
    p = sig(Xb @ w)
    return Xb.T @ (2 * (p - t) * p * (1 - p)) / n


def check(L, G, h=1e-5):
    fd = np.array([(L(w0 + h * e) - L(w0 - h * e)) / (2 * h) for e in np.eye(65)])
    return np.abs(G(w0) - fd).max()


print(f"{'情境（講師注入）':<30}{'最大絕對誤差':>14}  判定（門檻 1e-8）")
for name, L, G in [("正確的 loss 與 grad", loss, grad),
                   ("loss、grad 一起換成 MSE", mse, mse_grad),
                   ("只把 grad 乘 2", loss, lambda w: 2 * grad(w))]:
    e = check(L, G)
    print(f"{name:<30}{e:>14.2e}  {'PASS' if e < 1e-8 else 'FAIL'}")

g = grad(w0)
zero = np.flatnonzero(A.std(0) == 0)
fd = np.array([(loss(w0 + 1e-5 * e) - loss(w0 - 1e-5 * e)) / 2e-5 for e in np.eye(65)])
with np.errstate(all="ignore"):
    rel = np.abs(g - fd) / np.abs(g)
print(f"\n在 3 和 8 中恆為常數的像素：{len(zero)} 個，{zero.tolist()}")
print(f"這些維度的解析梯度全為 0：{bool((g[zero] == 0).all())}")
print(f"相對誤差直接除以 |grad| 時出現 nan：{bool(np.isnan(rel).any())}")
