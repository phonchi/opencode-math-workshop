"""Lab 3 講師備援：梯度檢查能證明什麼，不能證明什麼。

所有錯誤都是講師注入，不是 AI 自己犯的。
"""
from pathlib import Path

import numpy as np

DATA = Path(__file__).resolve().parents[1] / "assets" / "data"
D = np.genfromtxt(DATA / "line_faults.csv", delimiter=",", skip_header=1)
A = D[:, 1:-1]
A = (A - A.mean(0)) / A.std(0)
t = D[:, -1]
Xb = np.c_[A, np.ones(len(A))]
n = len(t)
d = Xb.shape[1]
w0 = np.random.RandomState(0).normal(size=d) * 0.01
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
    fd = np.array([(L(w0 + h * e) - L(w0 - h * e)) / (2 * h) for e in np.eye(d)])
    return np.abs(G(w0) - fd).max()


print(f"{'情境（講師注入）':<30}{'最大絕對誤差':>14}  判定（門檻 1e-8）")
for name, L, G in [("正確的 loss 與 grad", loss, grad),
                   ("loss、grad 一起換成 MSE", mse, mse_grad),
                   ("只把 grad 乘 2", loss, lambda w: 2 * grad(w))]:
    e = check(L, G)
    print(f"{name:<30}{e:>14.2e}  {'PASS' if e < 1e-8 else 'FAIL'}")

print("\n正確的 loss 與 grad，步長掃描")
for h in [1e-2, 1e-3, 1e-5, 1e-7, 1e-9]:
    print(f"{h:>8.0e} {check(loss, grad, h):>12.3e}")
