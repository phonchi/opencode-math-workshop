"""Lab 3 參考程式：手刻 logistic 迴歸，看準確率能證明什麼。

loans.csv 是為工作坊設計的合成資料。case_no 的產生方式與下一批資料只在揭曉時提供。
"""
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, recall_score
from sklearn.model_selection import train_test_split


def data_file(name, reveal=False):
    """先找學生專案的 data/，再找教材 repo 的 assets/data/。"""
    repo = Path(__file__).resolve().parents[1] / "assets" / "data"
    for p in (Path("data") / name, (repo / "reveal" if reveal else repo) / name):
        if p.exists():
            return p
    raise FileNotFoundError(f"找不到 {name}，請先把它下載到 data/")


D = np.genfromtxt(data_file("loans.csv"), delimiter=",", skip_header=1)
N = np.genfromtxt(data_file("loans_new_batch.csv", reveal=True), delimiter=",", skip_header=1)
X, y = D[:, :-1], D[:, -1].astype(int)
sig = lambda z: 1 / (1 + np.exp(-z))
print(f"資料形狀 {X.shape}；逾期比例 {y.mean():.4f}")


def design(A, mu, sd):
    return np.c_[(A - mu) / sd, np.ones(len(A))]


def loss(w, Xb, t):
    z = Xb @ w
    return np.mean(np.logaddexp(0, z) - t * z)


def grad(w, Xb, t):
    return Xb.T @ (sig(Xb @ w) - t) / len(t)


def fit(Xb, t, lr=0.5, steps=20000):
    w = np.zeros(Xb.shape[1])
    for _ in range(steps):
        w -= lr * grad(w, Xb, t)
    return w


Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
print("永遠猜「不會逾期」的準確率:", round(accuracy_score(yte, np.zeros_like(yte)), 3))
for name, c in [("含 case_no", slice(0, None)), ("不含 case_no", slice(1, None))]:
    mu, sd = Xtr[:, c].mean(0), Xtr[:, c].std(0)
    A, B, C = design(Xtr[:, c], mu, sd), design(Xte[:, c], mu, sd), design(N[:, :-1][:, c], mu, sd)
    w = fit(A, ytr)
    sk = LogisticRegression(C=np.inf, max_iter=20000, tol=1e-10).fit(A[:, :-1], ytr)
    wsk = np.r_[sk.coef_[0], sk.intercept_]
    for tag, Z, t in [("測試集", B, yte), ("下一批", C, N[:, -1].astype(int))]:
        p = (sig(Z @ w) > 0.5).astype(int)
        print(f"{name} {tag}: 準確率 {accuracy_score(t, p):.3f} recall {recall_score(t, p, zero_division=0):.3f} 混淆矩陣 {confusion_matrix(t, p).tolist()}")
    print(f"{name} 手刻與 sklearn 權重最大差: {np.abs(w - wsk).max():.2e}；訓練損失 {loss(w, A, ytr):.6f}")

mu, sd = Xtr[:, 1:].mean(0), Xtr[:, 1:].std(0)
A = design(Xtr[:, 1:], mu, sd)
w0 = np.random.RandomState(0).normal(size=A.shape[1]) * 0.01
print("    步長 h      最大絕對誤差")
for h in [1e-2, 1e-3, 1e-5, 1e-7, 1e-9]:
    fd = np.array([(loss(w0 + h * e, A, ytr) - loss(w0 - h * e, A, ytr)) / (2 * h) for e in np.eye(A.shape[1])])
    print(f"{h:>10.0e} {np.abs(fd - grad(w0, A, ytr)).max():>16.3e}")

w = fit(A, ytr)
T, Yt = design(Xte[:, 1:], mu, sd), yte
C, Yn = design(N[:, 1:-1], mu, sd), N[:, -1].astype(int)
print("門檻｜測試集：警報 抓到 漏掉 誤報｜下一批：警報 抓到 漏掉 誤報")
for t in [0.5, 0.3, 0.2, 0.1, 0.05]:
    row = []
    for Z, Y in [(T, Yt), (C, Yn)]:
        h = sig(Z @ w) >= t
        row += [int(h.sum()), int((h & (Y == 1)).sum()), int((~h & (Y == 1)).sum()), int((h & (Y == 0)).sum())]
    print(t, row)
