"""手刻 logistic 迴歸（digits 3 vs 8），並與 sklearn 比較。

執行：uv run python logistic_handmade.py
"""
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import numpy as np
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss

# ---------- 資料 ----------
digits = load_digits()
X_all, y_all = digits.data, digits.target
mask = (y_all == 3) | (y_all == 8)
X = X_all[mask].astype(float)
y = (y_all[mask] == 8).astype(int)  # 1 = digit 8, 0 = digit 3

# ---------- 手刻：L2 正則化 logistic（Newton-Raphson / IRLS） ----------
# 目標（與 sklearn 一致）：min (1/2)||w||^2 + C * sum_i log(1+exp(-y'_i z_i))
# C 與 sklearn 的 C 相同。
def sigmoid(z):
    out = np.empty_like(z, dtype=float)
    pos = z >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    ez = np.exp(z[~pos])
    out[~pos] = ez / (1.0 + ez)
    return out

class HandLogistic:
    def __init__(self, C=1.0, max_iter=100, tol=1e-12):
        self.C = C
        self.max_iter = max_iter
        self.tol = tol

    def fit(self, X, y):
        n, d = X.shape
        col_std = X.std(axis=0)
        keep = col_std > 0
        Xk = X[:, keep]
        dk = Xk.shape[1]
        Xa = np.hstack([Xk, np.ones((n, 1))])          # 最後一欄為截距
        theta = np.zeros(dk + 1)
        reg = np.ones(dk + 1); reg[-1] = 0.0            # 截距不正則化
        n = X.shape[0]
        sw_sum = float(n)
        l2 = 1.0 / (self.C * sw_sum)                  # sklearn 的 l2_reg_strength
        for it in range(self.max_iter):
            z = Xa @ theta
            p = sigmoid(z)
            r = y - p
            grad = (Xa.T @ (p - y)) / n + l2 * reg * theta   # 最小化梯度
            W = p * (1 - p)
            H = (Xa * W[:, None]).T @ Xa / n + np.diag(l2 * reg)
            delta = np.linalg.solve(H, grad)
            theta = theta - delta
            if np.linalg.norm(delta) < self.tol:
                break
        full = np.zeros(d + 1)
        full[np.r_[np.where(keep)[0], d]] = theta
        self.theta_ = full
        self.coef_ = full[:-1].reshape(1, -1)
        self.intercept_ = np.array([full[-1]])
        self.n_iter_ = it + 1
        return self

    def predict_proba(self, X):
        n = X.shape[0]
        Xa = np.hstack([X, np.ones((n, 1))])
        p = sigmoid(Xa @ self.theta_)
        return np.column_stack([1 - p, p])

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)

hand = HandLogistic(C=1.0)
hand.fit(X, y)

# ---------- sklearn（newton-cg，與手刻同為 Newton 法，用於驗證） ----------
sk = LogisticRegression(C=1.0, solver="newton-cg", max_iter=10000, tol=1e-12)
sk.fit(X, y)

# ---------- sklearn（預設 lbfgs，實務常用） ----------
sk_lbfgs = LogisticRegression(C=1.0, solver="lbfgs", max_iter=10000, tol=1e-12)
sk_lbfgs.fit(X, y)

# ---------- 比較 ----------
print("hand n_iter:", hand.n_iter_, "| sklearn n_iter:", sk.n_iter_)
print("coef max abs diff:", np.max(np.abs(hand.coef_ - sk.coef_)))
print("intercept abs diff:", np.abs(hand.intercept_[0] - sk.intercept_[0]))
ph = hand.predict_proba(X)[:, 1]
ps = sk.predict_proba(X)[:, 1]
print("proba max abs diff:", np.max(np.abs(ph - ps)))
print("pred agreement:", np.mean(hand.predict(X) == sk.predict(X)))
print("hand acc:", accuracy_score(y, hand.predict(X)),
      "| sk acc:", accuracy_score(y, sk.predict(X)))
print("hand logloss:", log_loss(y, ph), "| sk logloss:", log_loss(y, ps))
# 與預設 lbfgs 的差異（實務參考）
print("[lbfgs] coef max abs diff:", np.max(np.abs(hand.coef_ - sk_lbfgs.coef_)),
      "| proba max abs diff:", np.max(np.abs(ph - sk_lbfgs.predict_proba(X)[:,1])),
      "| pred agreement:", np.mean(hand.predict(X) == sk_lbfgs.predict(X)))

tol_coef = 1e-6
same = (
    np.max(np.abs(hand.coef_ - sk.coef_)) < tol_coef
    and np.abs(hand.intercept_[0] - sk.intercept_[0]) < tol_coef
    and np.max(np.abs(ph - ps)) < 1e-6
    and np.array_equal(hand.predict(X), sk.predict(X))
)
print("SAME MODEL?", same)