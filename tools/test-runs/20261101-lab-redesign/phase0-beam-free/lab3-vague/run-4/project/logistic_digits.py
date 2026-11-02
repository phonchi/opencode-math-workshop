import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss, confusion_matrix

# ---------- 資料：digits 的 3 vs 8 ----------
digits = load_digits()
mask = (digits.target == 3) | (digits.target == 8)
X = digits.data[mask].astype(float)
y = (digits.target[mask] == 8).astype(int)  # 1 -> 8, 0 -> 3

Xtr, Xte, ytr, yte = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)
scaler = StandardScaler()
Xtr_s = scaler.fit_transform(Xtr)
Xte_s = scaler.transform(Xte)

# ---------- 手刻 logistic 迴歸（L2 正則化，全批次梯度下降） ----------
def sigmoid(z):
    out = np.empty_like(z, dtype=float)
    pos = z >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    ez = np.exp(z[~pos])
    out[~pos] = ez / (1.0 + ez)
    return out

class HandLogistic:
    """L2-regularized logistic regression, matched to sklearn default (C=1.0)."""

    def __init__(self, C=1.0, lr=0.5, n_iter=20000, tol=1e-12):
        self.C = C
        self.lr = lr
        self.n_iter = n_iter
        self.tol = tol

    def fit(self, X, y):
        n, d = X.shape
        Xa = np.hstack([np.ones((n, 1)), X])
        self.w = np.zeros(d + 1)
        self.losses = []
        alpha = 1.0 / (self.C * n)  # 對應 sklearn 的 (1/2)||w||^2 + C*sum loss
        for it in range(self.n_iter):
            p = sigmoid(Xa @ self.w)
            grad = Xa.T @ (p - y) / n
            grad[1:] += alpha * self.w[1:]  # L2 對權重；截距不正則
            self.w -= self.lr * grad
            eps = 1e-12
            data_loss = -np.mean(y * np.log(p + eps) + (1 - y) * np.log(1 - p + eps))
            reg_loss = (1.0 / (2 * self.C * n)) * np.sum(self.w[1:] ** 2) * n  # = ||w||^2/(2C)
            # 紀錄與 sklearn 相同尺度的目標 (mean loss + (1/(2Cn))||w||^2 *? ) -> 用 mean 目標
            reg_mean = (1.0 / (2 * self.C * n)) * np.sum(self.w[1:] ** 2)
            self.losses.append(data_loss + reg_mean)
            if it > 0 and abs(self.losses[-2] - self.losses[-1]) < self.tol:
                break
        self.n_iter_ = it + 1
        return self

    def predict_proba(self, X):
        n = X.shape[0]
        Xa = np.hstack([np.ones((n, 1)), X])
        p = sigmoid(Xa @ self.w)
        return np.column_stack([1 - p, p])

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)

hand = HandLogistic(C=1.0, lr=0.5, n_iter=20000, tol=1e-12)
hand.fit(Xtr_s, ytr)

# ---------- sklearn ----------
sk = LogisticRegression(C=1.0, solver="lbfgs", max_iter=10000, tol=1e-12)
sk.fit(Xtr_s, ytr)

# ---------- 比較 ----------
ph_te = hand.predict_proba(Xte_s)[:, 1]
ps_te = sk.predict_proba(Xte_s)[:, 1]
yh = hand.predict(Xte_s)
ys = sk.predict(Xte_s)

w_hand = hand.w
w_sk = np.concatenate([[sk.intercept_[0]], sk.coef_[0]])

print("hand iters:", hand.n_iter_)
print("hand train acc:", accuracy_score(ytr, hand.predict(Xtr_s)))
print("sk   train acc:", accuracy_score(ytr, sk.predict(Xtr_s)))
print("hand test  acc:", accuracy_score(yte, yh))
print("sk   test  acc:", accuracy_score(yte, ys))
print("pred agreement:", np.mean(yh == ys))
print("max |p_hand - p_sk| (test):", np.max(np.abs(ph_te - ps_te)))
print("mean |p_hand - p_sk| (test):", np.mean(np.abs(ph_te - ps_te)))
print("coef corr:", np.corrcoef(w_hand, w_sk)[0, 1])
print("max |w_hand - w_sk|:", np.max(np.abs(w_hand - w_sk)))
print("cosine:", (w_hand @ w_sk) / (np.linalg.norm(w_hand) * np.linalg.norm(w_sk)))
print("hand logloss (test):", log_loss(yte, ph_te))
print("sk   logloss (test):", log_loss(yte, ps_te))
print("confusion hand:\n", confusion_matrix(yte, yh))
print("confusion sk:\n", confusion_matrix(yte, ys))

# ---------- 圖 ----------
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(hand.losses)
ax.set_xlabel("iteration")
ax.set_ylabel("regularized loss (mean)")
ax.set_title("Hand-coded logistic regression: training loss")
fig.tight_layout()
fig.savefig("figs/logistic_loss.png", dpi=150)
plt.close(fig)

fig, ax = plt.subplots(figsize=(6, 6))
ax.scatter(w_sk[1:], w_hand[1:], s=20)
lims = [min(w_sk[1:].min(), w_hand[1:].min()), max(w_sk[1:].max(), w_hand[1:].max())]
ax.plot(lims, lims, "r--", lw=1)
ax.set_xlabel("sklearn coef")
ax.set_ylabel("hand coef")
ax.set_title("Coefficients: hand vs sklearn")
fig.tight_layout()
fig.savefig("figs/logistic_coef.png", dpi=150)
plt.close(fig)

fig, ax = plt.subplots(figsize=(6, 6))
ax.scatter(ps_te, ph_te, s=20, alpha=0.7)
ax.plot([0, 1], [0, 1], "r--", lw=1)
ax.set_xlabel("sklearn P(y=1|x)")
ax.set_ylabel("hand P(y=1|x)")
ax.set_title("Test probabilities: hand vs sklearn")
fig.tight_layout()
fig.savefig("figs/logistic_proba.png", dpi=150)
plt.close(fig)
print("done")
