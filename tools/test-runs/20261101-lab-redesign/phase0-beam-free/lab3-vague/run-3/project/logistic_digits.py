import numpy as np
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------- 資料：digits 的 3 vs 8 ----------
d = load_digits()
mask = (d.target == 3) | (d.target == 8)
X = d.data[mask].astype(float)
y = (d.target[mask] == 8).astype(int)   # 8 -> 1, 3 -> 0
Xtr, Xte, ytr, yte = train_test_split(
    X, y, test_size=0.2, random_state=0, stratify=y
)

# ---------- 手刻 logistic regression ----------
# 目標 (與 sklearn C=1 一致): min 0.5*||w||^2 + C * sum_i log(1+exp(-y'_i z_i))
# z_i = w·x_i + b,  y'_i in {-1,+1}; p_i = σ(z_i)
# 梯度: g_w = w + C X^T(p-y);  g_b = C sum(p-y)
# Hessian: H_ww = C X^T diag(p(1-p)) X + I;  H_wb = C X^T(p(1-p));  H_bb = C sum(p(1-p))
class HandLogistic:
    def __init__(self, C=1.0, max_iter=100, tol=1e-12):
        self.C = C
        self.max_iter = max_iter
        self.tol = tol

    def fit(self, X, y):
        X = np.asarray(X, float)
        y = np.asarray(y, float).ravel()
        n, p = X.shape
        self.w = np.zeros(p)
        self.b = 0.0
        for it in range(self.max_iter):
            z = X @ self.w + self.b
            pp = 1.0 / (1.0 + np.exp(-z))
            r = pp - y
            grad_w = self.w + self.C * (X.T @ r)
            grad_b = self.C * r.sum()
            s = pp * (1 - pp)
            H_ww = self.C * (X.T @ (X * s[:, None])) + np.eye(p)
            H_wb = self.C * (X.T @ s)
            H_bb = self.C * s.sum()
            H = np.block([[H_ww, H_wb[:, None]],
                          [H_wb[None, :], np.array([[H_bb]])]])
            g = np.concatenate([grad_w, [grad_b]])
            delta = np.linalg.solve(H, g)
            self.w -= delta[:p]
            self.b -= delta[p]
            if np.linalg.norm(delta) < self.tol:
                self.n_iter_ = it + 1
                break
        else:
            self.n_iter_ = self.max_iter
        return self

    def predict_proba(self, X):
        z = np.asarray(X, float) @ self.w + self.b
        pp = 1.0 / (1.0 + np.exp(-z))
        return np.column_stack([1 - pp, pp])

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)

def acc(m, X, y):
    return float(np.mean(m.predict(X) == y))

# ---------- 訓練 ----------
hand = HandLogistic(C=1.0, tol=1e-12, max_iter=100)
hand.fit(Xtr, ytr)

sk = LogisticRegression(C=1.0, solver="newton-cholesky", max_iter=100000, tol=1e-12)
sk.fit(Xtr, ytr)

sk_default = LogisticRegression(C=1.0)   # sklearn 預設: lbfgs, tol=1e-4
sk_default.fit(Xtr, ytr)

# ---------- 比較 ----------
print("=== 收斂資訊 ===")
print("hand n_iter:", hand.n_iter_)
print("sklearn(newton-cholesky, tol=1e-12) n_iter:", sk.n_iter_)
print("sklearn(default lbfgs, tol=1e-4) n_iter:", sk_default.n_iter_)

print("\n=== 手刻 vs sklearn(高精度) ===")
print("coef allclose (rtol=1e-10):", np.allclose(hand.w, sk.coef_.ravel(), rtol=1e-10, atol=1e-12))
print("intercept allclose:", np.allclose(hand.b, sk.intercept_[0], rtol=1e-10, atol=1e-12))
print("coef max abs diff:", np.max(np.abs(hand.w - sk.coef_.ravel())))
print("intercept diff:", abs(hand.b - sk.intercept_[0]))

ph = hand.predict_proba(Xte)[:, 1]
ps = sk.predict_proba(Xte)[:, 1]
print("proba allclose:", np.allclose(ph, ps, rtol=1e-10, atol=1e-12))
print("proba max abs diff:", np.max(np.abs(ph - ps)))
print("pred equal:", np.array_equal(hand.predict(Xte), sk.predict(Xte)))

print("\n=== 手刻 vs sklearn(預設) ===")
phd = sk_default.predict_proba(Xte)[:, 1]
print("coef max abs diff:", np.max(np.abs(hand.w - sk_default.coef_.ravel())))
print("proba max abs diff:", np.max(np.abs(ph - phd)))
print("pred equal:", np.array_equal(hand.predict(Xte), sk_default.predict(Xte)))

print("\n=== 準確率 ===")
for name, m in [("hand", hand), ("sk-high", sk), ("sk-default", sk_default)]:
    print(f"{name}: train={acc(m,Xtr,ytr):.4f} test={acc(m,Xte,yte):.4f}")

# 殘差檢查 (手刻在訓練集上應 ~0)
pptr = hand.predict_proba(Xtr)[:, 1]
r = pptr - ytr
print("\n=== 殘差 (手刻, 訓練集) ===")
print("sum (p-y):", r.sum(), "grad norm:", np.linalg.norm(hand.w + Xtr.T @ r))

# ---------- 圖 ----------
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
axes[0].scatter(sk.coef_.ravel(), hand.w, s=12)
mn = min(sk.coef_.min(), hand.w.min()); mx = max(sk.coef_.max(), hand.w.max())
axes[0].plot([mn, mx], [mn, mx], "r--")
axes[0].set_xlabel("sklearn coef"); axes[0].set_ylabel("hand coef")
axes[0].set_title("Coefficients")
axes[1].scatter(ps, ph, s=12)
axes[1].plot([0, 1], [0, 1], "r--")
axes[1].set_xlabel("sklearn proba"); axes[1].set_ylabel("hand proba")
axes[1].set_title("Predicted proba")
# confusion-ish: 決策值分佈
dec = Xte @ hand.w + hand.b
axes[2].hist(dec[yte == 0], bins=20, alpha=0.6, label="digit 3")
axes[2].hist(dec[yte == 1], bins=20, alpha=0.6, label="digit 8")
axes[2].axvline(0, color="k", linestyle="--")
axes[2].set_title("Decision values (test)")
axes[2].legend()
fig.tight_layout()
fig.savefig("figs/logistic_digits_compare.png", dpi=150)
print("\nsaved fig: figs/logistic_digits_compare.png")
